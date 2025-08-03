"""SMOL Agent tools for A2A discovery and communication."""

import json
import logging
from typing import Any, Dict, List, Optional
import httpx
from smolagents import Tool

logger = logging.getLogger(__name__)


class DiscoverAgentsTool(Tool):
    """Tool for discovering available A2A agents."""
    
    name = "discover_agents"
    description = "Discover available agents in the system that you can communicate with"
    inputs = {}
    output_type = "string"
    
    def __init__(self, agent_ports: List[Dict[str, Any]] = None):
        """Initialize with known agent ports."""
        super().__init__()
        # Default agent configurations
        self.agent_configs = agent_ports or [
            {"name": "product-catalog", "port": 8001, "host": "product-agent"},
            {"name": "inventory-management", "port": 8002, "host": "inventory-agent"},
            {"name": "sales-analytics", "port": 8003, "host": "sales-agent"},
        ]
    
    def forward(self) -> str:
        """Discover available agents."""
        discovered = []
        
        for config in self.agent_configs:
            try:
                # Try to fetch agent card
                url = f"http://{config['host']}:{config['port']}/.well-known/agent-card.json"
                response = httpx.get(url, timeout=5.0)
                
                if response.status_code == 200:
                    card = response.json()
                    discovered.append({
                        "name": config["name"],
                        "description": card.get("description", ""),
                        "capabilities": [skill["name"] for skill in card.get("skills", [])]
                    })
                    logger.info(f"Discovered agent: {config['name']}")
            except Exception as e:
                logger.warning(f"Could not discover agent {config['name']}: {e}")
        
        return json.dumps(discovered, indent=2)


class QueryAgentTool(Tool):
    """Tool for querying other A2A agents."""
    
    name = "query_agent"
    description = "Send a query to another agent and get their response"
    inputs = {
        "agent_name": {
            "type": "string",
            "description": "Name of the agent to query (e.g., 'product-catalog', 'inventory-management', 'sales-analytics')"
        },
        "query": {
            "type": "string", 
            "description": "The question or request to send to the agent"
        }
    }
    output_type = "string"
    
    def __init__(self, agent_ports: List[Dict[str, Any]] = None):
        """Initialize with known agent ports."""
        super().__init__()
        # Default agent configurations
        self.agent_configs = {
            "product-catalog": {"port": 8001, "host": "product-agent"},
            "inventory-management": {"port": 8002, "host": "inventory-agent"},
            "sales-analytics": {"port": 8003, "host": "sales-agent"},
        }
        
        # Override with custom configs if provided
        if agent_ports:
            for config in agent_ports:
                self.agent_configs[config["name"]] = config
    
    def forward(self, agent_name: str, query: str) -> str:
        """Query another agent."""
        if agent_name not in self.agent_configs:
            return f"Unknown agent: {agent_name}. Available agents: {list(self.agent_configs.keys())}"
        
        config = self.agent_configs[agent_name]
        
        try:
            # Prepare A2A protocol message
            payload = {
                "jsonrpc": "2.0",
                "method": "message/send",
                "params": {
                    "message": {
                        "messageId": f"msg-{id(self)}-{hash(query)}",
                        "role": "user",
                        "parts": [{"text": query}],
                    },
                },
                "id": f"req-{id(self)}-{hash(query)}",
            }
            
            # Send to agent
            url = f"http://{config['host']}:{config['port']}/"
            response = httpx.post(url, json=payload, timeout=60.0)
            
            if response.status_code == 200:
                result = response.json()
                # Extract response text
                if result.get("result", {}).get("parts"):
                    return result["result"]["parts"][0].get("text", "No response text")
                else:
                    return json.dumps(result)
            else:
                return f"Error querying {agent_name}: HTTP {response.status_code}"
                
        except Exception as e:
            logger.error(f"Error querying agent {agent_name}: {e}")
            return f"Error querying {agent_name}: {str(e)}"


def get_a2a_tools(agent_ports: List[Dict[str, Any]] = None) -> List[Tool]:
    """Get A2A discovery and communication tools for SMOL agents.
    
    Args:
        agent_ports: Optional list of agent configurations
        
    Returns:
        List of Tool instances
    """
    return [
        DiscoverAgentsTool(agent_ports),
        QueryAgentTool(agent_ports)
    ]