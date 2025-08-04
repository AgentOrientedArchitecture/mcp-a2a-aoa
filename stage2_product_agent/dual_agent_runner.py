"""Dual Agent Runner - Stage 2 Comparison Tool.

This module provides a way to run both SMOL and Agno agents side by side
for comparison of capabilities, reasoning, and explainability.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

# Add parent directory to path to import from stage1
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables only if not in Docker
if not os.getenv("DOCKER_CONTAINER", False):
    load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DualAgentRunner:
    """Runner for comparing SMOL and Agno agents side by side."""

    def __init__(self):
        """Initialize the dual agent runner."""
        self.agent_framework = os.getenv("AGENT_FRAMEWORK", "both")
        
        # Initialize agents based on configuration
        self.smol_agent = None
        self.agno_agent = None
        
        if self.agent_framework in ["smol", "both"]:
            try:
                from agent import ProductCatalogAgent
                self.smol_agent = ProductCatalogAgent()
                logger.info("✅ SMOL agent initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize SMOL agent: {e}")
        
        if self.agent_framework in ["agno", "both"]:
            try:
                from agno_agent import ProductCatalogAgnoAgent
                self.agno_agent = ProductCatalogAgnoAgent()
                logger.info("✅ Agno agent initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Agno agent: {e}")

    def compare_query(self, user_input: str) -> Dict[str, Any]:
        """Run the same query through both agents and compare results."""
        results = {}
        
        if self.smol_agent:
            try:
                logger.info("Running query through SMOL agent...")
                smol_response = self.smol_agent.run(user_input)
                results["smol"] = {
                    "response": smol_response,
                    "status": "success"
                }
            except Exception as e:
                logger.error(f"SMOL agent error: {e}")
                results["smol"] = {
                    "response": f"Error: {str(e)}",
                    "status": "error"
                }
        
        if self.agno_agent:
            try:
                logger.info("Running query through Agno agent...")
                agno_response = self.agno_agent.query(user_input)
                results["agno"] = {
                    "response": agno_response,
                    "status": "success"
                }
            except Exception as e:
                logger.error(f"Agno agent error: {e}")
                results["agno"] = {
                    "response": f"Error: {str(e)}",
                    "status": "error"
                }
        
        return results

    def run_comparison_mode(self):
        """Run the agents in comparison mode."""
        print("=" * 80)
        print("Product Catalog Agent - Stage 2 Comparison Mode")
        print("Comparing SMOL vs Agno Agent Frameworks")
        print("=" * 80)
        print()
        
        # Show available agents
        if self.smol_agent:
            print("✅ SMOL Agent: Available")
        else:
            print("❌ SMOL Agent: Not available")
            
        if self.agno_agent:
            print("✅ Agno Agent: Available")
        else:
            print("❌ Agno Agent: Not available")
        
        print()
        print("Commands:")
        print("- Type your query to compare both agents")
        print("- Type 'smol <query>' to use only SMOL agent")
        print("- Type 'agno <query>' to use only Agno agent")
        print("- Type 'quit' to exit")
        print()
        
        while True:
            try:
                user_input = input("Query: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                # Check for specific agent commands
                if user_input.lower().startswith("smol "):
                    query = user_input[5:].strip()
                    if self.smol_agent:
                        print("\n🤖 SMOL Agent Response:")
                        print("-" * 40)
                        response = self.smol_agent.run(query)
                        print(response)
                        print()
                    else:
                        print("❌ SMOL agent not available")
                    continue
                
                if user_input.lower().startswith("agno "):
                    query = user_input[6:].strip()
                    if self.agno_agent:
                        print("\n🧠 Agno Agent Response:")
                        print("-" * 40)
                        response = self.agno_agent.query(query)
                        print(response)
                        print()
                    else:
                        print("❌ Agno agent not available")
                    continue
                
                # Run comparison
                print("\n🔄 Running comparison...")
                results = self.compare_query(user_input)
                
                # Display results
                if "smol" in results:
                    print("\n🤖 SMOL Agent Response:")
                    print("-" * 40)
                    print(results["smol"]["response"])
                    print()
                
                if "agno" in results:
                    print("\n🧠 Agno Agent Response:")
                    print("-" * 40)
                    print(results["agno"]["response"])
                    print()
                
                # Show comparison summary
                if len(results) > 1:
                    print("📊 Comparison Summary:")
                    print("-" * 40)
                    for agent, result in results.items():
                        status = "✅" if result["status"] == "success" else "❌"
                        print(f"{status} {agent.upper()}: {result['status']}")
                    print()
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}\n")

    def run_benchmark(self, test_queries: List[str]) -> Dict[str, Any]:
        """Run a benchmark comparison with predefined test queries."""
        print("=" * 80)
        print("Running Benchmark Comparison")
        print("=" * 80)
        print()
        
        benchmark_results = {
            "smol": {"success": 0, "errors": 0, "responses": []},
            "agno": {"success": 0, "errors": 0, "responses": []}
        }
        
        for i, query in enumerate(test_queries, 1):
            print(f"Test {i}/{len(test_queries)}: {query}")
            
            results = self.compare_query(query)
            
            for agent, result in results.items():
                if result["status"] == "success":
                    benchmark_results[agent]["success"] += 1
                else:
                    benchmark_results[agent]["errors"] += 1
                
                benchmark_results[agent]["responses"].append({
                    "query": query,
                    "response": result["response"],
                    "status": result["status"]
                })
            
            print(f"  SMOL: {'✅' if results.get('smol', {}).get('status') == 'success' else '❌'}")
            print(f"  Agno: {'✅' if results.get('agno', {}).get('status') == 'success' else '❌'}")
            print()
        
        # Print summary
        print("📊 Benchmark Summary:")
        print("-" * 40)
        for agent, stats in benchmark_results.items():
            total = stats["success"] + stats["errors"]
            success_rate = (stats["success"] / total * 100) if total > 0 else 0
            print(f"{agent.upper()}: {stats['success']}/{total} successful ({success_rate:.1f}%)")
        
        return benchmark_results


def main():
    """Main entry point for the dual agent runner."""
    try:
        runner = DualAgentRunner()
        
        # Check if we have any agents available
        if not runner.smol_agent and not runner.agno_agent:
            print("❌ No agents available. Check your configuration.")
            sys.exit(1)
        
        # Run in comparison mode
        runner.run_comparison_mode()
        
    except Exception as e:
        logger.error(f"Failed to start dual agent runner: {e}")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 