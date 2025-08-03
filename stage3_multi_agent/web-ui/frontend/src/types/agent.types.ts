export interface Agent {
  name: string;
  status: 'online' | 'offline';
  card?: AgentCard;
  error?: string;
}

export interface AgentCard {
  name: string;
  description: string;
  version: string;
  url: string;
  protocolVersion: string;
  preferredTransport: string;
  capabilities: {
    pushNotifications: boolean;
    streaming: boolean;
  };
  defaultInputModes: string[];
  defaultOutputModes: string[];
  skills: Skill[];
}

export interface Skill {
  id: string;
  name: string;
  description: string;
  examples: string[];
  tags: string[];
}

export interface Capability {
  name: string;
  description: string;
}

export interface Message {
  id: string;
  role: 'user' | 'agent';
  content: string;
  agent?: string;
  timestamp: Date;
  responseTime?: number;
}

export interface CommunicationEvent {
  type: 'query_start' | 'query_complete' | 'query_error' | 'agent_communication';
  agent: string;
  targetAgent?: string;
  query?: string;
  response?: string;
  error?: string;
  messageId: string;
  timestamp: string;
  responseTime?: number;
}