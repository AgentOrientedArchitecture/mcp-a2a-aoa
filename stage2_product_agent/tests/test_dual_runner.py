"""Simple test script for dual agent runner."""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

def test_dual_runner_import():
    """Test that dual agent runner can be imported."""
    try:
        from dual_agent_runner import DualAgentRunner
        print("✅ Dual agent runner imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import dual agent runner: {e}")
        return False

def test_dual_runner_initialization():
    """Test that dual agent runner can be initialized."""
    try:
        from dual_agent_runner import DualAgentRunner
        
        # Check if API key is available
        if not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"):
            print("⚠️  No API key found - skipping initialization test")
            print("   Set ANTHROPIC_API_KEY or OPENAI_API_KEY in .env file")
            return True
        
        # Try to initialize
        try:
            runner = DualAgentRunner()
            print("✅ Dual agent runner initialized successfully")
            
            # Check which agents are available
            if runner.smol_agent:
                print("  ✅ SMOL agent available")
            else:
                print("  ❌ SMOL agent not available")
                
            if runner.agno_agent:
                print("  ✅ Agno agent available")
            else:
                print("  ❌ Agno agent not available")
            
            return True
        except Exception as e:
            print(f"❌ Dual agent runner initialization failed: {e}")
            return False
                
    except Exception as e:
        print(f"❌ Dual agent runner test failed: {e}")
        return False

def test_benchmark_import():
    """Test that benchmark script can be imported."""
    try:
        from benchmark import AgentBenchmark
        print("✅ Benchmark script imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import benchmark script: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing Dual Agent Runner Setup")
    print("=" * 40)
    
    tests = [
        test_dual_runner_import,
        test_dual_runner_initialization,
        test_benchmark_import
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 