export function showOverlay() {
  window.electron?.ipcRenderer?.send('show-overlay');
}
export function hideOverlay() {
  window.electron?.ipcRenderer?.send('hide-overlay');
}
