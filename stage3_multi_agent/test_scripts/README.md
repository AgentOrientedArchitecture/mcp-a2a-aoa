# Stage 3 Test Scripts

This directory contains test scripts for validating the Stage 3 multi-agent system functionality.

## Available Tests

### 1. test_product_search.py
Tests the Product Agent's search functionality directly.

**Usage:**
```bash
python3 test_product_search.py
```

**What it tests:**
- Product search with various parameter combinations
- Verifies MCP server integration
- Checks if all 3 laptops are correctly identified

### 2. test_ui_response.py
Tests the Web UI backend API to ensure proper agent responses.

**Usage:**
```bash
python3 test_ui_response.py
```

**What it tests:**
- Web UI backend API connectivity
- Verifies agents return actual results (not async task IDs)
- Measures response time
- Validates product data in responses

### 3. test_agent_discovery.py
Tests the A2A agent discovery mechanism.

**Usage:**
```bash
python3 test_agent_discovery.py
```

**What it tests:**
- Agent discovery on network ports
- Agent card retrieval
- Capability parsing
- Connection establishment

### 4. test_complete_fixes.py
Comprehensive test suite for all implemented fixes.

**Usage:**
```bash
python3 test_complete_fixes.py
```

**What it tests:**
- Agent discovery (capability parsing fix)
- Simple queries (message parsing and timeout fixes)
- Complex queries (multi-agent coordination)
- All critical bug fixes

## Running All Tests

```bash
cd stage3_multi_agent/test_scripts
python3 test_product_search.py && python3 test_ui_response.py
```

## Prerequisites

- All Stage 3 services must be running:
  ```bash
  cd stage3_multi_agent
  ./deploy_with_telemetry.sh deploy
  ```

- Python packages required:
  - requests
  - json (built-in)
  - time (built-in)

## Expected Results

✅ **Success Indicators:**
- Product Agent correctly identifies 3 laptops
- Response times under 60 seconds
- Actual product data returned (not task IDs)
- All agents accessible via their endpoints

❌ **Common Issues:**
- "Async task started with ID" - Async tasks not properly disabled
- Timeout errors - Agents taking too long to respond
- Connection refused - Services not running
- Empty results - Database or MCP server issues

## Test Coverage

These scripts provide basic functional testing for:
- Agent API endpoints
- Web UI backend integration
- Product search functionality
- Response format validation

For comprehensive testing including telemetry, use the Phoenix UI at http://localhost:6006 to monitor test execution.