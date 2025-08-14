import { app, ipcMain, BrowserWindow, shell } from "electron";
import { dirname, join } from "node:path";
import { existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { spawn } from "node:child_process";
import readline from "node:readline";
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
let win = null;
let py = null;
let lastPyStderr = "";
const pending = /* @__PURE__ */ new Map();
let nextId = 1;
function resolvePythonScriptPath() {
  const candidates = [
    // dev: from dist-electron to app/src/backend
    join(__dirname, "..", "..", "..", "..", "src", "backend", "pico_stdio.py"),
    // alt dev: if run from project root
    join(process.cwd(), "app", "src", "backend", "pico_stdio.py"),
    join(process.cwd(), "src", "backend", "pico_stdio.py")
  ];
  for (const p of candidates) {
    if (existsSync(p)) return p;
  }
  return candidates[0];
}
function startPythonChild() {
  const pythonCmd = process.env.PYTHON_BIN || "python3";
  const scriptPath = resolvePythonScriptPath();
  const cwd = dirname(scriptPath);
  console.log("[PY] Spawning", pythonCmd, scriptPath, "cwd=", cwd);
  lastPyStderr = "";
  py = spawn(pythonCmd, [scriptPath], { stdio: ["pipe", "pipe", "pipe"], cwd });
  const rl = readline.createInterface({ input: py.stdout });
  rl.on("line", (line) => {
    try {
      const msg = JSON.parse(line);
      const id = String(msg.id);
      const waiter = pending.get(id);
      if (waiter) {
        pending.delete(id);
        if (msg.ok) {
          waiter.resolve(msg);
        } else {
          waiter.reject(new Error(msg.error || "Unknown Python error"));
        }
      }
    } catch (e) {
    }
  });
  py.stderr.on("data", (buf) => {
    const s = buf.toString();
    lastPyStderr += s;
    if (lastPyStderr.length > 5e3) lastPyStderr = lastPyStderr.slice(-5e3);
    console.error("[PY STDERR]", s);
    try {
      win?.webContents.send("pico:stderr", s);
    } catch {
    }
  });
  py.on("exit", (code, signal) => {
    const err = new Error(`Python exited: ${code ?? ""} ${signal ?? ""}
${lastPyStderr}`);
    for (const [, waiter] of pending) waiter.reject(err);
    pending.clear();
    py = null;
  });
  py.on("error", (e) => {
    console.error("[PY ERROR]", e);
    try {
      win?.webContents.send("pico:stderr", String(e));
    } catch {
    }
  });
}
async function callPython(prompt, opts) {
  if (!py) startPythonChild();
  console.log("Calling Python with prompt:", prompt);
  const id = String(nextId++);
  const payload = JSON.stringify({ id, prompt, asSystem: !!opts?.asSystem, speak: opts?.speak ?? true }) + "\n";
  return await new Promise((resolve, reject) => {
    if (!py || !py.stdin.writable) return reject(new Error("Python process not available"));
    pending.set(id, {
      resolve: (msg) => resolve(String(msg.text ?? "")),
      reject
    });
    py.stdin.write(payload);
  });
}
async function createWindow() {
  win = new BrowserWindow({
    width: 1100,
    height: 720,
    title: "PICO",
    backgroundColor: "#111416",
    webPreferences: {
      preload: join(__dirname, "preload.mjs"),
      contextIsolation: true,
      nodeIntegration: false
    }
  });
  const devUrl = process.env.VITE_DEV_SERVER_URL;
  if (devUrl) {
    await win.loadURL(devUrl);
  } else {
    await win.loadFile(join(__dirname, "../renderer/index.html"));
  }
  win.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: "deny" };
  });
}
app.whenReady().then(createWindow);
app.whenReady().then(() => {
  ipcMain.handle("pico:send", async (_evt, prompt, opts) => {
    console.log("Python calculation?");
    const text = await callPython(String(prompt ?? ""), opts);
    console.log("Python response:", text);
    return text;
  });
});
app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
app.on("before-quit", () => {
  try {
    py?.kill();
  } catch {
  }
});
