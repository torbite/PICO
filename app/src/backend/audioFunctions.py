# speaker_thing.py
from __future__ import annotations

import threading
import queue
import platform
import subprocess
from typing import Iterable, Optional, Union

# On non-macOS systems we use pyttsx3. On macOS, we prefer the `say` CLI for reliability in background threads.
_IS_MAC = platform.system() == "Darwin"
_engine_import_error: Optional[Exception] = None
if not _IS_MAC:
    try:
        import pyttsx3  # type: ignore
    except Exception as e:  # pragma: no cover
        _engine_import_error = e
        pyttsx3 = None  # type: ignore


class speakerThing:
    """
    Threaded TTS helper.
    - On macOS: uses the built-in `say` command (reliable from background threads).
    - On Linux/Windows: uses pyttsx3.

    API:
      speak(text or [texts])   -> enqueue speech
      stop()                   -> stop current utterance
      flush_queue()            -> clear pending (not-yet-spoken) items
      wait_until_done()        -> block until queue drained & not speaking
      set_rate(rate)           -> adjust speed (pyttsx3) / via `say -r` on macOS
      set_volume(volume)       -> adjust volume (pyttsx3 only)
      set_voice(name_or_id)    -> select voice (best-effort on macOS via -v)
      list_voices()            -> list voices (pyttsx3 only)
      shutdown()               -> clean shutdown

    Notes:
      * Use as a context manager to guarantee cleanup.
      * macOS volume control via `say` isn't directly supported; use system volume.
    """

    def __init__(
        self,
        rate: int = 180,
        volume: float = 0.9,
        voice: Optional[str] = None,
        queue_maxsize: int = 0,
        thread_name: str = "speakerThingWorker",
        debug: bool = False,
    ) -> None:
        self.debug = debug
        self._q: "queue.SimpleQueue[Optional[str]]" = queue.SimpleQueue()
        self._alive = threading.Event()
        self._alive.set()

        self._rate = int(rate)
        self._volume = float(volume)
        self._voice = voice

        self._using_mac_say = _IS_MAC
        self._engine = None

        if not self._using_mac_say:
            if _engine_import_error is not None:
                raise RuntimeError(
                    "pyttsx3 is required on non-macOS systems. "
                    "Install with `pip install pyttsx3`. "
                    f"Import error: {_engine_import_error}"
                )
            self._engine = pyttsx3.init()  # type: ignore
            self._engine.setProperty("rate", self._rate)
            self._engine.setProperty("volume", max(0.0, min(1.0, self._volume)))
            if voice:
                try:
                    self.set_voice(voice, strict=False)
                except Exception:
                    pass

        self._worker = threading.Thread(
            target=self._worker_loop,
            name=thread_name,
            daemon=True,
        )
        self._worker.start()

    # ----------------------- Core worker -----------------------
    def _worker_loop(self) -> None:
        while self._alive.is_set():
            text = self._q.get()
            if text is None:
                break  # sentinel -> shutdown
            if text == "":  # ignore empty strings
                continue
            try:
                if self._using_mac_say:
                    self._speak_mac(text)
                else:
                    self._speak_pyttsx3(text)
            except Exception as e:
                # if self.debug:
                    # print(f"[speakerThing] speak error: {e!r}")
                # Best-effort stop on failure to keep thread alive
                try:
                    if self._engine:
                        self._engine.stop()
                except Exception:
                    pass

        # final stop
        try:
            if self._engine:
                self._engine.stop()
        except Exception:
            pass

    def _speak_mac(self, text: str) -> None:
        # Build args for `say`. Use -r for rate, -v for voice if provided.
        args = ["say", "-r", str(self._rate)]
        if self._voice:
            args += ["-v", self._voice]
        args.append(text)
        # if self.debug:
        #     print(f"[speakerThing] macOS say: {' '.join(args)}")
        # Run synchronously so queue order is preserved
        subprocess.run(args, check=False)

    def _speak_pyttsx3(self, text: str) -> None:
        assert self._engine is not None
        self._engine.say(text)
        self._engine.runAndWait()

    # ----------------------- Public API ------------------------
    def speak(self, text: Union[str, Iterable[str]]) -> None:
        if isinstance(text, str):
            self._q.put(text)
        else:
            for t in text:
                self._q.put(str(t))

    def stop(self) -> None:
        """
        Stop current utterance.
        macOS: terminates any active `say` process by best-effort (no handle kept).
        Non-mac: uses pyttsx3.stop().
        """
        if self._using_mac_say:
            # There's no direct handle to kill here; users can rely on flush_queue
            # and a new utterance will preempt after current one completes.
            # if self.debug:
            #     print("[speakerThing] stop() on macOS uses best-effort only.")
            return
        try:
            if self._engine:
                self._engine.stop()
        except Exception:
            pass

    def flush_queue(self) -> None:
        try:
            while True:
                item = self._q.get_nowait()
                if item is None:
                    self._q.put_nowait(None)
                    break
        except queue.Empty:
            pass

    def is_speaking(self) -> bool:
        if self._using_mac_say:
            # We don't track the `say` subprocess handle here; conservatively return False.
            return False
        try:
            return bool(self._engine.isBusy()) if self._engine else False
        except Exception:
            return False

    def set_rate(self, rate: int) -> None:
        self._rate = int(rate)
        if not self._using_mac_say and self._engine:
            self._engine.setProperty("rate", self._rate)

    def set_volume(self, volume: float) -> None:
        self._volume = max(0.0, min(1.0, float(volume)))
        if not self._using_mac_say and self._engine:
            self._engine.setProperty("volume", self._volume)

    def list_voices(self) -> list[dict]:
        if self._using_mac_say:
            # Suggest `say -v ?` to list voices
            return []
        out = []
        try:
            for v in self._engine.getProperty("voices") or []:  # type: ignore
                out.append({
                    "id": getattr(v, "id", ""),
                    "name": getattr(v, "name", ""),
                    "languages": [str(l) for l in getattr(v, "languages", [])],
                })
        except Exception:
            pass
        return out

    def set_voice(self, voice: str, *, strict: bool = True) -> None:
        self._voice = voice
        if self._using_mac_say:
            # Voice is applied via `say -v` at speak time.
            return
        try:
            voices = self._engine.getProperty("voices") or []  # type: ignore
            for v in voices:
                if getattr(v, "id", None) == voice:
                    self._engine.setProperty("voice", v.id)  # type: ignore
                    return
            voice_lower = voice.lower()
            for v in voices:
                name = getattr(v, "name", "") or ""
                if voice_lower in name.lower():
                    self._engine.setProperty("voice", v.id)  # type: ignore
                    return
            if strict:
                raise ValueError(f"Voice not found: {voice!r}")
        except Exception:
            if strict:
                raise

    def wait_until_done(self, poll_interval: float = 0.05) -> None:
        """
        Block until the queue is empty. On macOS we don't track `say` busy state,
        so we wait for queue drain only.
        """
        import time as _time
        while True:
            if self._q.empty() and (self._using_mac_say or not self.is_speaking()):
                break
            _time.sleep(max(0.0, float(poll_interval)))

    def shutdown(self) -> None:
        if not self._alive.is_set():
            return
        self._alive.clear()
        self._q.put(None)
        # best-effort stop for pyttsx3
        try:
            if self._engine:
                self._engine.stop()
        except Exception:
            pass
        self._worker.join(timeout=1.0)

    def __enter__(self) -> "speakerThing":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.shutdown()


if __name__ == "__main__":
    spk = speakerThing(rate=180, volume=0.9, debug=True)
    try:
        print("a")
        spk.speak("Hi there, this is a test")
        print("b")
        spk.speak(["First frase", "Third frase."])
        spk.wait_until_done()
    finally:
        spk.shutdown()
