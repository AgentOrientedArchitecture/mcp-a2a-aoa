import { WebSocketServer, WebSocket } from 'ws';

interface WSMessage {
  type: string;
  [key: string]: any;
}

export function setupWebSocket(wss: WebSocketServer) {
  wss.on('connection', (ws: WebSocket) => {
    console.log('New WebSocket connection');

    // Send welcome message
    ws.send(JSON.stringify({
      type: 'connected',
      message: 'Connected to Agent Communication Hub',
      timestamp: new Date().toISOString(),
    }));

    // Handle incoming messages
    ws.on('message', (data) => {
      try {
        const message = JSON.parse(data.toString());
        console.log('Received message:', message);
        
        // Echo back for now
        ws.send(JSON.stringify({
          type: 'echo',
          original: message,
          timestamp: new Date().toISOString(),
        }));
      } catch (error) {
        console.error('WebSocket message error:', error);
      }
    });

    ws.on('close', () => {
      console.log('WebSocket connection closed');
    });

    ws.on('error', (error) => {
      console.error('WebSocket error:', error);
    });
  });
}

export function broadcastMessage(wss: WebSocketServer, message: WSMessage) {
  const messageStr = JSON.stringify(message);
  
  wss.clients.forEach((client) => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(messageStr);
    }
  });
}