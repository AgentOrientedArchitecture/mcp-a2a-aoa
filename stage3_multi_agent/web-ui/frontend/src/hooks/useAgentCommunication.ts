import { useState } from 'react';
import { useQuery, useMutation } from 'react-query';
import axios from 'axios';
import { Agent } from '../types/agent.types';

const API_BASE = 'http://localhost:3001/api';

export function useAgentCommunication() {
  const [agents, setAgents] = useState<Agent[]>([]);

  // Fetch agent status
  const { refetch } = useQuery(
    'agentStatus',
    async () => {
      const response = await axios.get(`${API_BASE}/agents/status`);
      return response.data;
    },
    {
      enabled: true, // Ensure query runs on mount
      refetchInterval: 30000, // Refetch every 30 seconds
      onSuccess: (data) => {
        // Ensure data is an array before setting agents
        if (Array.isArray(data)) {
          setAgents(data);
        } else {
          console.error('Invalid agents data received:', data);
          setAgents([]);
        }
      },
      onError: (error) => {
        console.error('Failed to fetch agents:', error);
        setAgents([]);
      },
    }
  );

  // Send query mutation
  const sendQueryMutation = useMutation(
    async ({ agent, query }: { agent: string; query: string }) => {
      const response = await axios.post(`${API_BASE}/agent/${agent}/query`, {
        query,
      });
      return response.data;
    }
  );

  const sendQuery = async (agent: string, query: string) => {
    return sendQueryMutation.mutateAsync({ agent, query });
  };

  return {
    agents,
    sendQuery,
    isLoading: sendQueryMutation.isLoading,
    error: sendQueryMutation.error,
    refetchAgents: refetch,
  };
}