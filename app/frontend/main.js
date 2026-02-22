const { app, BrowserWindow, ipcMain, screen } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

let mainWindow;
let pythonProcess;

function findPython() {
  const possiblePaths = [
    '/opt/homebrew/bin/python3.11', // Apple Silicon Homebrew
    '/usr/local/bin/python3.11',    // Intel Homebrew
    '/Library/Frameworks/Python.framework/Versions/3.11/bin/python3.11', // Python.org
    'python3.11', // Try command directly if in PATH
    'python3'     // Fallback
  ];

  for (const p of possiblePaths) {
    if (p.startsWith('/')) {
        if (fs.existsSync(p)) {
            return p;
        }
    }
  }
  return 'python3'; // Fallback to generic python3
}

function createWindow() {
  const { width, height } = screen.getPrimaryDisplay().workAreaSize;

  // Create the browser window.
  mainWindow = new BrowserWindow({
    width: 400,
    height: 600,
    x: width - 420,
    y: 50,
    frame: false, // Frameless for overlay look
    transparent: true, // Transparent background
    alwaysOnTop: true, // Keep on top
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: true,
      contextIsolation: false // For simple prototype, enable node integration
    }
  });

  mainWindow.loadFile('index.html');

  // Open the DevTools.
  // mainWindow.webContents.openDevTools();
}

function startPythonBackend() {
  const scriptPath = path.join(__dirname, 'python_backend/server.py');
  const backendDir = path.join(__dirname, 'python_backend');
  const pythonCmd = findPython();

  console.log(`Starting Python backend: ${scriptPath} in ${backendDir} using ${pythonCmd}`);
  
  // Assuming 'python3' is in PATH and has dependencies installed
  // In a real app, you'd bundle a python runtime or use a venv
  pythonProcess = spawn(pythonCmd, [scriptPath], {
    cwd: __dirname,
    // Inherit PATH and other env vars
    env: { ...process.env }
  });

  pythonProcess.stdout.on('data', (data) => {
    console.log(`Backend stdout: ${data}`);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Backend stderr: ${data}`);
  });

  pythonProcess.on('close', (code) => {
    console.log(`Backend process exited with code ${code}`);
  });
}

app.whenReady().then(() => {
  startPythonBackend();
  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});

app.on('will-quit', () => {
  if (pythonProcess) {
    pythonProcess.kill();
  }
});
