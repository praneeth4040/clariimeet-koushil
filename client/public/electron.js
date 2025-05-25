const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

let mainWindow;
let overlayWindow;

function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
    },
  });
  mainWindow.loadURL('http://localhost:3000');
}

function createOverlayWindow() {
  overlayWindow = new BrowserWindow({
    width: 400,
    height: 100,
    alwaysOnTop: true,
    frame: false,
    transparent: true,
    skipTaskbar: true,
    resizable: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
    },
  });
  overlayWindow.loadURL('http://localhost:3000/overlay');
  overlayWindow.hide(); // Start hidden
}

app.whenReady().then(() => {
  createMainWindow();
  createOverlayWindow();

  // Listen for IPC messages to show/hide overlay window
  ipcMain.on('show-overlay', () => overlayWindow.show());
  ipcMain.on('hide-overlay', () => overlayWindow.hide());

  // Optional: Hide overlay when main window is closed
  mainWindow.on('closed', () => {
    if (overlayWindow) overlayWindow.close();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});