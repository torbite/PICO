import sys
import json
from pico_main import sendUserInput


def main():
    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            request_id = request.get("id")
            prompt = request.get("prompt", "")
            as_system = 0
            speak_out_loud = bool(request.get("speak", True))

            text_response = sendUserInput(prompt, as_system, speak_out_loud)

            response = {
                "ok": True,
                "id": request_id,
                "text": text_response,
            }
        except Exception as e:
            response = {
                "ok": False,
                "id": request.get("id") if isinstance(request, dict) else None,
                "error": str(e),
            }

        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
