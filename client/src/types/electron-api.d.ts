export {};

declare global {
  interface Window {
    electron?: {
      ipcRenderer: {
        send: (channel: string, ...args: any[]) => void;
        // Add more methods if needed
      };
    };
  }
}
