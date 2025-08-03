import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  TextField,
  IconButton,
  Typography,
  Paper,
  CircularProgress,
  Chip,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import { Message } from '../types/agent.types';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface AgentChatProps {
  messages: Message[];
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  selectedAgent: string;
}

const AgentChat: React.FC<AgentChatProps> = ({
  messages,
  onSendMessage,
  isLoading,
  selectedAgent,
}) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = () => {
    if (input.trim() && !isLoading) {
      onSendMessage(input);
      setInput('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const renderMessageContent = (content: string) => {
    // Check if content looks like JSON
    try {
      const parsed = JSON.parse(content);
      return (
        <Box>
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 1 }}>
            <IconButton
              size="small"
              onClick={() => copyToClipboard(content)}
              title="Copy"
            >
              <ContentCopyIcon fontSize="small" />
            </IconButton>
          </Box>
          <SyntaxHighlighter language="json" style={vscDarkPlus}>
            {JSON.stringify(parsed, null, 2)}
          </SyntaxHighlighter>
        </Box>
      );
    } catch {
      // Not JSON, render as plain text
      return (
        <Typography variant="body1" style={{ whiteSpace: 'pre-wrap' }}>
          {content}
        </Typography>
      );
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <Typography variant="h6" gutterBottom>
        Chat with {selectedAgent}
      </Typography>

      <Box sx={{ flexGrow: 1, overflow: 'auto', mb: 2 }}>
        {messages.length === 0 && (
          <Box sx={{ textAlign: 'center', mt: 4 }}>
            <Typography variant="body2" color="text.secondary">
              Start a conversation by typing a message or selecting an example prompt
            </Typography>
          </Box>
        )}

        {messages.map((message) => (
          <Paper
            key={message.id}
            sx={{
              p: 2,
              mb: 2,
              backgroundColor: message.role === 'user' ? '#e3f2fd' : '#f5f5f5',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                {message.role === 'user' ? 'You' : message.agent}
              </Typography>
              {message.responseTime && (
                <Chip
                  label={`${message.responseTime}ms`}
                  size="small"
                  sx={{ ml: 1 }}
                />
              )}
              <Typography variant="caption" color="text.secondary" sx={{ ml: 'auto' }}>
                {new Date(message.timestamp).toLocaleTimeString()}
              </Typography>
            </Box>
            {renderMessageContent(message.content)}
          </Paper>
        ))}

        {isLoading && (
          <Box sx={{ display: 'flex', alignItems: 'center', p: 2 }}>
            <CircularProgress size={20} sx={{ mr: 2 }} />
            <Typography variant="body2" color="text.secondary">
              Agent is thinking...
            </Typography>
          </Box>
        )}

        <div ref={messagesEndRef} />
      </Box>

      <Box sx={{ display: 'flex', gap: 1 }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={isLoading}
          multiline
          maxRows={4}
        />
        <IconButton
          color="primary"
          onClick={handleSend}
          disabled={!input.trim() || isLoading}
        >
          <SendIcon />
        </IconButton>
      </Box>
    </Box>
  );
};

export default AgentChat;