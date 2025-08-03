import { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  AppBar,
  Toolbar,
  Typography,
  Box,
} from '@mui/material';
import AgentSelector from './components/AgentSelector';
import AgentChat from './components/AgentChat';
import ExamplePrompts from './components/ExamplePrompts';
import CommunicationFlow from './components/CommunicationFlow';
import { useAgentCommunication } from './hooks/useAgentCommunication';
import { Message, CommunicationEvent } from './types/agent.types';

export default function App() {
  const [selectedAgent, setSelectedAgent] = useState<string>('product-catalog');
  const [messages, setMessages] = useState<Message[]>([]);
  const [communicationEvents, setCommunicationEvents] = useState<CommunicationEvent[]>([]);
  
  const { agents, sendQuery, isLoading } = useAgentCommunication();

  // Listen for WebSocket events
  useEffect(() => {
    const ws = new WebSocket(`ws://${window.location.hostname}:3001/ws`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'query_complete' || data.type === 'query_error') {
        setCommunicationEvents((prev) => [...prev, data as CommunicationEvent]);
      }
    };

    return () => ws.close();
  }, []);

  const handleSendMessage = async (content: string) => {
    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date(),
    };
    
    setMessages((prev) => [...prev, userMessage]);

    try {
      const response = await sendQuery(selectedAgent, content);
      
      const agentMessage: Message = {
        id: `msg-${Date.now()}-resp`,
        role: 'agent',
        content: response.response,
        agent: selectedAgent,
        timestamp: new Date(),
        responseTime: response.responseTime,
      };
      
      setMessages((prev) => [...prev, agentMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  const handleExamplePrompt = (prompt: string) => {
    handleSendMessage(prompt);
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Multi-Agent System Interface
          </Typography>
          <Typography variant="body2">
            Stage 3: A2A Protocol Implementation
          </Typography>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 3 }}>
        <Grid container spacing={3}>
          {/* Left Column: Agent Selection and Example Prompts */}
          <Grid item xs={12} md={3}>
            <Paper sx={{ p: 2, mb: 2 }}>
              <AgentSelector
                agents={agents}
                selectedAgent={selectedAgent}
                onSelectAgent={setSelectedAgent}
              />
            </Paper>
            
            <Paper sx={{ p: 2 }}>
              <ExamplePrompts
                selectedAgent={selectedAgent}
                onSelectPrompt={handleExamplePrompt}
              />
            </Paper>
          </Grid>

          {/* Middle Column: Chat Interface */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2, height: '80vh' }}>
              <AgentChat
                messages={messages}
                onSendMessage={handleSendMessage}
                isLoading={isLoading}
                selectedAgent={selectedAgent}
              />
            </Paper>
          </Grid>

          {/* Right Column: Communication Flow */}
          <Grid item xs={12} md={3}>
            <Paper sx={{ p: 2, height: '80vh', overflow: 'auto' }}>
              <CommunicationFlow events={communicationEvents} />
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
}