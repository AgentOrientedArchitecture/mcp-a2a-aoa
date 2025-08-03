"""A2A Discovery utilities for finding and connecting to other agents."""

import json
import logging
from typing import Any, Dict, List, Optional
import httpx
from urllib.parse import urljoin
import time

logger = logging.getLogger(__name__)


class DiscoveryClient:
    """Client for discovering A2A agents."""
    
    def __init__(self, timeout: int = 10):
        """Initialize discovery client.
        
        Args:
            timeout: HTTP request timeout in seconds
        """
        self.timeout = timeout
        self.discovered_agents = {}
    
    async def discover_agent_at_url(self, base_url: str) -> Optional[Dict[str, Any]]:
        """Discover an agent at a specific URL.
        
        Args:
            base_url: Base URL of the agent (e.g., http://localhost:8001)
            
        Returns:
            Agent card if found, None otherwise
        """
        try:
            # Try to fetch agent card from well-known URL
            card_url = urljoin(base_url, "/.well-known/agent-card.json")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(card_url)
                
                if response.status_code == 200:
                    card = response.json()
                    # Store the base URL with the card
                    card["_discovered_at"] = base_url
                    
                    # Normalize capabilities format
                    # A2A SDK uses 'skills' instead of 'capabilities'
                    if "skills" in card and "capabilities" not in card:
                        card["capabilities"] = card["skills"]
                    
                    # Cache the discovered agent
                    agent_name = card.get("name", "unknown")
                    self.discovered_agents[agent_name] = card
                    
                    logger.info(f"Discovered agent '{agent_name}' at {base_url}")
                    return card
                else:
                    logger.warning(f"No agent card found at {card_url}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error discovering agent at {base_url}: {e}")
            return None
    
    async def discover_agents_on_ports(
        self,
        host: str = "localhost",
        ports: List[int] = None
    ) -> List[Dict[str, Any]]:
        """Discover agents on specific ports.
        
        Args:
            host: Host to check
            ports: List of ports to check (defaults to common ports)
            
        Returns:
            List of discovered agent cards
        """
        if ports is None:
            # Default ports for our demo
            ports = [8001, 8002, 8003]
        
        discovered = []
        
        for port in ports:
            base_url = f"http://{host}:{port}"
            card = await self.discover_agent_at_url(base_url)
            if card:
                discovered.append(card)
        
        return discovered
    
    async def discover_agents_from_env(self) -> List[Dict[str, Any]]:
        """Discover agents from environment variable configuration.
        
        This is useful for Docker environments where agents are
        specified via DISCOVERY_HOSTS environment variable.
        
        Returns:
            List of discovered agent cards
        """
        import os
        
        discovery_hosts = os.getenv("DISCOVERY_HOSTS", "")
        if not discovery_hosts:
            # Fall back to localhost discovery
            return await self.discover_agents_on_ports()
        
        discovered = []
        
        # Parse comma-separated host:port pairs
        for host_port in discovery_hosts.split(","):
            host_port = host_port.strip()
            if ":" in host_port:
                host, port = host_port.split(":", 1)
                base_url = f"http://{host}:{port}"
            else:
                # Assume default port if not specified
                base_url = f"http://{host_port}:8000"
            
            card = await self.discover_agent_at_url(base_url)
            if card:
                discovered.append(card)
        
        return discovered
    
    async def find_agents_with_capability(
        self,
        capability: str,
        search_urls: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Find agents with a specific capability.
        
        Args:
            capability: Capability name to search for
            search_urls: Optional list of URLs to search
            
        Returns:
            List of agent cards with the capability
        """
        agents_with_capability = []
        
        # Search cached agents first
        for agent_name, card in self.discovered_agents.items():
            capabilities = []
            
            # Check skills (A2A SDK format)
            for skill in card.get("skills", []):
                if isinstance(skill, dict):
                    capabilities.append(skill.get("name") or skill.get("id"))
            
            # Check capabilities
            for cap in card.get("capabilities", []):
                if isinstance(cap, dict):
                    capabilities.append(cap.get("name"))
                elif isinstance(cap, str):
                    capabilities.append(cap)
            
            if capability in capabilities:
                agents_with_capability.append(card)
        
        # If search URLs provided, discover those
        if search_urls:
            for url in search_urls:
                card = await self.discover_agent_at_url(url)
                if card:
                    capabilities = []
                    
                    # Check skills (A2A SDK format)
                    for skill in card.get("skills", []):
                        if isinstance(skill, dict):
                            capabilities.append(skill.get("name") or skill.get("id"))
                    
                    # Check capabilities
                    for cap in card.get("capabilities", []):
                        if isinstance(cap, dict):
                            capabilities.append(cap.get("name"))
                        elif isinstance(cap, str):
                            capabilities.append(cap)
                    
                    if capability in capabilities:
                        agents_with_capability.append(card)
        
        return agents_with_capability
    
    def get_discovered_agents(self) -> Dict[str, Dict[str, Any]]:
        """Get all discovered agents.
        
        Returns:
            Dictionary of agent name to agent card
        """
        return self.discovered_agents.copy()
    
    async def query_agent_discovery_endpoint(
        self,
        agent_url: str,
        required_capabilities: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Query an agent's discovery endpoint.
        
        Args:
            agent_url: Base URL of the agent
            required_capabilities: Optional list of required capabilities
            
        Returns:
            List of discovered agents from that endpoint
        """
        try:
            discover_url = urljoin(agent_url, "/agent/discover")
            
            payload = {}
            if required_capabilities:
                payload["capabilities"] = required_capabilities
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(discover_url, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("agents", [])
                else:
                    logger.warning(f"Discovery endpoint returned {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error querying discovery endpoint: {e}")
            return []
    
    def clear_cache(self):
        """Clear the discovered agents cache."""
        self.discovered_agents.clear()
        logger.info("Cleared discovery cache")


class AgentConnection:
    """Helper class for connecting to discovered agents."""
    
    def __init__(self, agent_card: Dict[str, Any]):
        """Initialize connection to an agent.
        
        Args:
            agent_card: The agent's card with endpoint information
        """
        self.agent_card = agent_card
        self.name = agent_card.get("name", "unknown")
        self.base_url = agent_card.get("_discovered_at", "")
        
        # Extract endpoints
        endpoints = agent_card.get("endpoints", {})
        self.http_endpoint = endpoints.get("http", "")
        self.ws_endpoint = endpoints.get("websocket", "")
        
        # If no explicit endpoints, use the URL from the card
        if not self.http_endpoint and agent_card.get("url"):
            self.http_endpoint = agent_card.get("url").rstrip("/")
        elif not self.http_endpoint and self.base_url:
            self.http_endpoint = self.base_url
    
    async def send_task(self, message: str) -> Dict[str, Any]:
        """Send a task to the agent.
        
        Args:
            message: The task message
            
        Returns:
            Task response
        """
        if not self.http_endpoint:
            raise ValueError(f"No HTTP endpoint for agent {self.name}")
        
        # Use root endpoint for JSON-RPC
        task_url = self.http_endpoint.rstrip("/")
        
        # Create JSON-RPC payload for message/send
        payload = {
            "jsonrpc": "2.0",
            "method": "message/send",
            "params": {
                "message": {
                    "messageId": f"msg-{self.name}-{int(time.time())}",
                    "role": "user",
                    "parts": [
                        {
                            "text": message
                        }
                    ]
                }
            },
            "id": f"req-{int(time.time())}"
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(task_url, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    # Handle JSON-RPC response format
                    if "result" in result:
                        return result["result"]
                    elif "error" in result:
                        logger.error(f"JSON-RPC error: {result['error']}")
                        return {"error": result["error"]}
                    else:
                        return result
                else:
                    logger.error(f"Task request failed: {response.status_code}")
                    return {"error": f"Request failed: {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"Error sending task to {self.name}: {e}", exc_info=True)
            return {"error": str(e)}
    
    async def invoke_capability(
        self,
        capability: str,
        args: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Invoke a specific capability on the agent.
        
        Args:
            capability: Capability name
            args: Optional arguments for the capability
            
        Returns:
            Capability response
        """
        # Send as structured message
        message = {
            "capability": capability,
            "args": args or {}
        }
        
        return await self.send_task(json.dumps(message))
    
    def get_capabilities(self) -> List[str]:
        """Get list of agent capabilities.
        
        Returns:
            List of capability names
        """
        capabilities = []
        
        # Check for skills (A2A SDK format)
        skills = self.agent_card.get("skills", [])
        if skills:
            for skill in skills:
                if isinstance(skill, dict):
                    capabilities.append(skill.get("name") or skill.get("id"))
        
        # Also check capabilities array
        for cap in self.agent_card.get("capabilities", []):
            if isinstance(cap, dict) and cap.get("name") not in capabilities:
                capabilities.append(cap.get("name"))
            elif isinstance(cap, str) and cap not in capabilities:
                capabilities.append(cap)
        
        return capabilities