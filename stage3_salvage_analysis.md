# Stage 3 Salvage Analysis

## What We Can Keep

### MCP Servers (Fully Functional)
1. **Inventory MCP Server** (`inventory_mcp/server.py`)
   - Complete FastMCP implementation
   - Tools: check_stock, low_stock_alerts, predict_reorder, warehouse_summary, update_stock, transfer_stock
   - Database already populated with realistic data
   - Ready to use as-is

2. **Sales MCP Server** (`sales_mcp/server.py`)
   - Complete FastMCP implementation  
   - Tools: sales_summary, top_products, return_analysis, customer_insights, sales_forecast, revenue_by_category
   - Database with transaction and return data
   - Ready to use as-is

### SMOL Agents (Need Minor Modifications)
1. **Inventory Agent** (`agents/inventory_agent.py`)
   - Remove ACP imports and decorators
   - Keep core SMOL agent functionality
   - Already has intelligent tools: optimize_restocking, predict_stockouts, warehouse_optimization

2. **Sales Analytics Agent** (`agents/sales_agent.py`)
   - Remove ACP imports and decorators
   - Keep core SMOL agent functionality
   - Already has intelligent tools: customer_segmentation, sales_forecasting, return_prediction

### Docker Infrastructure
- Existing Dockerfiles can be adapted
- docker-compose.yml needs updating to remove ACP coordinator

## What We Need to Remove
1. All ACP integration code (`acp_integration/` directory)
2. ACP-specific imports and decorators from agents
3. Coordinator service and related Docker configuration

## What We Need to Add for A2A
1. **Agent Cards** for each agent (Product, Inventory, Sales)
2. **A2A Protocol endpoints** for each agent
3. **Agent communication layer** for direct agent-to-agent interaction
4. **Discovery mechanism** using Agent Cards

## Migration Plan
1. Copy existing MCP servers as-is (they're already functional)
2. Create clean versions of agents without ACP decorators
3. Add A2A protocol implementation to each agent
4. Create Agent Cards following A2A specification
5. Update Docker configuration for A2A deployment