const { app, BrowserWindow, Menu } = require('electron');
const path = require('path');
const isDev = require('electron-is-dev');
const express = require('express');
const http = require('http');
const socketIO = require('socket.io');

let mainWindow;
let expressApp;
let server;

// Créer la fenêtre Electron
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1920,
    height: 1080,
    minWidth: 1024,
    minHeight: 768,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false
    },
    icon: path.join(__dirname, '../assets/icon.ico')
  });

  // Charger l'application
  const startUrl = isDev
    ? 'http://localhost:3000'
    : `file://${path.join(__dirname, '../build/index.html')}`;

  mainWindow.loadURL(startUrl);

  // DevTools en développement
  if (isDev) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// Démarrer le serveur Express
function startExpressServer() {
  expressApp = express();
  server = http.createServer(expressApp);
  const io = socketIO(server, {
    cors: {
      origin: '*'
    }
  });

  // Servir les fichiers statiques
  expressApp.use(express.static(path.join(__dirname, '../public')));

  // Routes de base
  expressApp.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '../public/login.html'));
  });

  expressApp.get('/game-world-1.html', (req, res) => {
    res.sendFile(path.join(__dirname, '../public/game-world-1.html'));
  });

  // Socket.IO - Gestion des connexions
  io.on('connection', (socket) => {
    console.log('🎮 Joueur connecté:', socket.id);

    socket.on('join-game', (data) => {
      console.log('✅ Joueur rejoint:', data.name);
      io.emit('player-joined', {
        id: socket.id,
        name: data.name,
        world: data.world
      });
    });

    socket.on('player-move', (data) => {
      io.emit('player-moved', {
        id: socket.id,
        ...data
      });
    });

    socket.on('chat-message', (data) => {
      io.emit('chat-message', {
        playerName: data.playerName,
        message: data.message,
        timestamp: new Date()
      });
    });

    socket.on('disconnect', () => {
      console.log('❌ Joueur déconnecté:', socket.id);
      io.emit('player-left', { id: socket.id });
    });
  });

  // Démarrer le serveur sur le port 3001
  server.listen(3001, () => {
    console.log('🚀 Serveur PYT WORLD lancé sur http://localhost:3001');
  });
}

// Créer le menu de l'application
function createMenu() {
  const template = [
    {
      label: 'Fichier',
      submenu: [
        {
          label: 'Quitter',
          accelerator: 'CmdOrCtrl+Q',
          click: () => {
            app.quit();
          }
        }
      ]
    },
    {
      label: 'Affichage',
      submenu: [
        {
          label: 'Recharger',
          accelerator: 'CmdOrCtrl+R',
          click: () => {
            if (mainWindow) {
              mainWindow.reload();
            }
          }
        },
        {
          label: 'DevTools',
          accelerator: 'CmdOrCtrl+Shift+I',
          click: () => {
            if (mainWindow) {
              mainWindow.webContents.toggleDevTools();
            }
          }
        }
      ]
    },
    {
      label: 'Aide',
      submenu: [
        {
          label: 'À propos',
          click: () => {
            console.log('PYT WORLD v1.0.0');
          }
        }
      ]
    }
  ];

  Menu.setApplicationMenu(Menu.buildFromTemplate(template));
}

// Événements Electron
app.on('ready', () => {
  startExpressServer();
  createWindow();
  createMenu();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

// Arrêter le serveur à la fermeture
app.on('quit', () => {
  if (server) {
    server.close(() => {
      console.log('Serveur fermé');
    });
  }
});
