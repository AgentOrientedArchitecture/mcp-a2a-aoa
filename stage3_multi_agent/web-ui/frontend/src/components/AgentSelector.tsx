import React from 'react';
import {
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
  Box,
  Chip,
} from '@mui/material';
import { Agent } from '../types/agent.types';

interface AgentSelectorProps {
  agents: Agent[];
  selectedAgent: string;
  onSelectAgent: (agent: string) => void;
}

const AgentSelector: React.FC<AgentSelectorProps> = ({
  agents,
  selectedAgent,
  onSelectAgent,
}) => {
  // Ensure agents is always an array before using .find()
  const agentsArray = Array.isArray(agents) ? agents : [];
  const selectedAgentData = agentsArray.find((a) => a.name === selectedAgent);

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Select Agent
      </Typography>
      
      <FormControl fullWidth sx={{ mb: 2 }}>
        <InputLabel>Agent</InputLabel>
        <Select
          value={selectedAgent}
          label="Agent"
          onChange={(e) => onSelectAgent(e.target.value)}
        >
          {agentsArray.map((agent) => (
            <MenuItem key={agent.name} value={agent.name}>
              <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                <span style={{ flexGrow: 1 }}>{agent.name}</span>
                <Chip
                  label={agent.status}
                  size="small"
                  color={agent.status === 'online' ? 'success' : 'error'}
                />
              </Box>
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      {selectedAgentData && selectedAgentData.card && (
        <Box>
          <Typography variant="body2" color="text.secondary" paragraph>
            {selectedAgentData.card.description}
          </Typography>
          
          <Typography variant="subtitle2" gutterBottom>
            Skills:
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
            {selectedAgentData.card.skills && selectedAgentData.card.skills.map((skill) => (
              <Chip
                key={skill.id}
                label={skill.name}
                size="small"
                variant="outlined"
              />
            ))}
          </Box>
        </Box>
      )}
    </Box>
  );
};

export default AgentSelector;