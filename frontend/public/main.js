const { app, BrowserWindow } = require("electron");
const path = require("path");

// Ensure dynamic import for electron-is-dev
let isDev;
(async () => {
  isDev = (await import("electron-is-dev")).default;
})();

require("@electron/remote/main").initialize();

function createWindow() {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true,
      enableRemoteModule: true,
      contextIsolation: false, // Add this line
    },
  });

  // Enable remote module on the window instance
  require("@electron/remote/main").enable(win.webContents);

  win.loadURL(
    isDev
      ? "http://localhost:3000"
      : `file://${path.join(__dirname, "../build/index.html")}`
  );
}

app.on("ready", createWindow);

app.on("window-all-closed", function () {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("activate", function () {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
