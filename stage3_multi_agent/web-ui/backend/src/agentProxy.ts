import { Express } from 'express';
import axios from 'axios';
import { WebSocketServer } from 'ws';
import { broadcastMessage } from './websocket';

interface Agent {
  name: string;
  port: number;
  host: string;
}

const AGENTS: Agent[] = [
  { name: 'product-catalog', port: 8001, host: process.env.PRODUCT_AGENT_HOST || 'product-agent' },
  { name: 'inventory-management', port: 8002, host: process.env.INVENTORY_AGENT_HOST || 'inventory-agent' },
  { name: 'sales-analytics', port: 8003, host: process.env.SALES_AGENT_HOST || 'sales-agent' },
];

export function setupAgentProxy(app: Express, wss: WebSocketServer) {
  // Get all agents status
  app.get('/api/agents/status', async (req, res) => {
    const statuses = await Promise.all(
      AGENTS.map(async (agent) => {
        try {
          const response = await axios.get(
            `http://${agent.host}:${agent.port}/.well-known/agent-card.json`,
            { timeout: 5000 }
          );
          return {
            name: agent.name,
            status: 'online',
            card: response.data,
          };
        } catch (error) {
          return {
            name: agent.name,
            status: 'offline',
            error: error instanceof Error ? error.message : 'Unknown error',
          };
        }
      })
    );
    res.json(statuses);
  });

  // Send query to specific agent
  app.post('/api/agent/:agentName/query', async (req, res) => {
    const { agentName } = req.params;
    const { query } = req.body;

    const agent = AGENTS.find(a => a.name === agentName);
    if (!agent) {
      return res.status(404).json({ error: 'Agent not found' });
    }

    const messageId = `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const requestId = `req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

    // Broadcast query start
    broadcastMessage(wss, {
      type: 'query_start',
      agent: agentName,
      query,
      messageId,
      timestamp: new Date().toISOString(),
    });

    try {
      const startTime = Date.now();
      
      // Prepare A2A protocol message
      const payload = {
        jsonrpc: '2.0',
        method: 'message/send',
        params: {
          message: {
            messageId,
            role: 'user',
            parts: [{ text: query }],
          },
        },
        id: requestId,
      };

      // Send to agent
      const response = await axios.post(
        `http://${agent.host}:${agent.port}/`,
        payload,
        { 
          timeout: 60000, // 60 second timeout
          headers: { 'Content-Type': 'application/json' }
        }
      );

      const responseTime = Date.now() - startTime;

      // Extract response text
      let responseText = 'No response';
      if (response.data?.result?.parts?.[0]?.text) {
        responseText = response.data.result.parts[0].text;
      }

      // Broadcast query complete
      broadcastMessage(wss, {
        type: 'query_complete',
        agent: agentName,
        query,
        response: responseText,
        responseTime,
        messageId,
        timestamp: new Date().toISOString(),
      });

      res.json({
        success: true,
        agent: agentName,
        query,
        response: responseText,
        responseTime,
        messageId,
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      
      // Broadcast error
      broadcastMessage(wss, {
        type: 'query_error',
        agent: agentName,
        query,
        error: errorMessage,
        messageId,
        timestamp: new Date().toISOString(),
      });

      res.status(500).json({
        success: false,
        agent: agentName,
        query,
        error: errorMessage,
        messageId,
      });
    }
  });

  // Discover agents (for agent-to-agent communication visualization)
  app.get('/api/agents/discover', async (req, res) => {
    try {
      // This would be enhanced to show actual agent discovery
      const agents = AGENTS.map(agent => ({
        name: agent.name,
        endpoint: `http://${agent.host}:${agent.port}`,
      }));
      res.json(agents);
    } catch (error) {
      res.status(500).json({ error: error instanceof Error ? error.message : 'Unknown error' });
    }
  });
}