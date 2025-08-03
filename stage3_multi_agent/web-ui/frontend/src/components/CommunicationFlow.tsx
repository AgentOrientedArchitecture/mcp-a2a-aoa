import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Chip,
} from '@mui/material';
import {
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  TimelineOppositeContent,
} from '@mui/lab';
import {
  Send as SendIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  SwapHoriz as SwapHorizIcon,
} from '@mui/icons-material';
import { CommunicationEvent } from '../types/agent.types';

interface CommunicationFlowProps {
  events: CommunicationEvent[];
}

const CommunicationFlow: React.FC<CommunicationFlowProps> = ({ events }) => {
  const getEventIcon = (type: string) => {
    switch (type) {
      case 'query_start':
        return <SendIcon />;
      case 'query_complete':
        return <CheckCircleIcon />;
      case 'query_error':
        return <ErrorIcon />;
      case 'agent_communication':
        return <SwapHorizIcon />;
      default:
        return <SendIcon />;
    }
  };

  const getEventColor = (type: string): any => {
    switch (type) {
      case 'query_start':
        return 'primary';
      case 'query_complete':
        return 'success';
      case 'query_error':
        return 'error';
      case 'agent_communication':
        return 'secondary';
      default:
        return 'grey';
    }
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Communication Flow
      </Typography>

      {events.length === 0 ? (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
          No communication events yet. Start a conversation to see the flow.
        </Typography>
      ) : (
        <Timeline position="right">
          {events.map((event, index) => (
            <TimelineItem key={`${event.messageId}-${index}`}>
              <TimelineOppositeContent
                sx={{ m: 'auto 0' }}
                variant="body2"
                color="text.secondary"
              >
                {formatTime(event.timestamp)}
              </TimelineOppositeContent>
              
              <TimelineSeparator>
                <TimelineConnector sx={{ bgcolor: 'grey.300' }} />
                <TimelineDot color={getEventColor(event.type)}>
                  {getEventIcon(event.type)}
                </TimelineDot>
                <TimelineConnector sx={{ bgcolor: 'grey.300' }} />
              </TimelineSeparator>
              
              <TimelineContent sx={{ py: '12px', px: 2 }}>
                <Paper elevation={1} sx={{ p: 1.5 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                    <Typography variant="subtitle2" component="span">
                      {event.agent}
                    </Typography>
                    {event.responseTime && (
                      <Chip
                        label={`${event.responseTime}ms`}
                        size="small"
                        variant="outlined"
                      />
                    )}
                  </Box>
                  
                  {event.type === 'query_start' && (
                    <Typography variant="body2" color="text.secondary">
                      Received: "{event.query?.substring(0, 50)}..."
                    </Typography>
                  )}
                  
                  {event.type === 'query_complete' && (
                    <Typography variant="body2" color="success.main">
                      Completed successfully
                    </Typography>
                  )}
                  
                  {event.type === 'query_error' && (
                    <Typography variant="body2" color="error.main">
                      Error: {event.error}
                    </Typography>
                  )}
                  
                  {event.type === 'agent_communication' && event.targetAgent && (
                    <Typography variant="body2">
                      → {event.targetAgent}
                    </Typography>
                  )}
                </Paper>
              </TimelineContent>
            </TimelineItem>
          ))}
        </Timeline>
      )}
    </Box>
  );
};

export default CommunicationFlow;