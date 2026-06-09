"""
test_evaluation.py - Comprehensive Evaluation Tests for the System
"""

import sys
import os
import time
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from orchestrator import ResearchWritingOrchestrator
from agents import ResearchWritingAgents
from tools import SourceCredibilityAnalyzer
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('evaluation_results.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SystemEvaluator:
    """Evaluation test suite for the multi-agent system"""
    
    def __init__(self):
        self.results = {
            "test_timestamp": datetime.now().isoformat(),
            "tests": []
        }
        self.orchestrator = ResearchWritingOrchestrator()
    
    def test_1_basic_functionality(self):
        """Test 1: Basic System Functionality - Can it complete a simple task?"""
        print("\n" + "="*60)
        print("TEST 1: BASIC FUNCTIONALITY TEST")
        print("="*60)
        
        test_result = {
            "test_name": "Basic Functionality Test",
            "test_id": "TEST_001",
            "description": "Verify system can complete a simple research and writing task",
            "status": "PENDING",
            "metrics": {}
        }
        
        try:
            # Test parameters
            topic = "Benefits of Green Tea"
            audience = "general"
            
            print(f"Testing with topic: '{topic}'")
            print(f"Target audience: {audience}")
            
            # Start timing
            start_time = time.time()
            
            # Execute workflow
            result = self.orchestrator.execute_workflow(
                topic=topic,
                audience=audience,
                mode="sequential"
            )
            
            # End timing
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Verify output exists
            output_exists = result is not None
            output_length = len(str(result)) if result else 0
            
            # Check if output files were created
            outputs_dir = Path("outputs")
            output_files = list(outputs_dir.glob("*Green_Tea*"))
            files_created = len(output_files) > 0
            
            # Collect metrics
            test_result["metrics"] = {
                "execution_time_seconds": round(execution_time, 2),
                "output_generated": output_exists,
                "output_length_chars": output_length,
                "files_created": files_created,
                "number_of_files": len(output_files)
            }
            
            # Determine pass/fail
            if output_exists and output_length > 500 and files_created:
                test_result["status"] = "PASSED"
                print(f"✅ TEST PASSED - Execution time: {execution_time:.2f}s")
            else:
                test_result["status"] = "FAILED"
                print(f"❌ TEST FAILED - Missing output or files")
            
        except Exception as e:
            test_result["status"] = "ERROR"
            test_result["error"] = str(e)
            print(f"❌ TEST ERROR: {str(e)}")
            logger.error(f"Test 1 failed with error: {str(e)}", exc_info=True)
        
        self.results["tests"].append(test_result)
        return test_result
    
    def test_2_error_handling(self):
        """Test 2: Error Handling - Can it handle invalid inputs gracefully?"""
        print("\n" + "="*60)
        print("TEST 2: ERROR HANDLING TEST")
        print("="*60)
        
        test_result = {
            "test_name": "Error Handling Test",
            "test_id": "TEST_002",
            "description": "Verify system handles edge cases and errors gracefully",
            "status": "PENDING",
            "metrics": {}
        }
        
        try:
            # Test with very long topic (edge case)
            topic = "x" * 500  # Very long topic
            
            print(f"Testing with edge case: 500 character topic")
            
            start_time = time.time()
            
            # This should handle gracefully
            try:
                result = self.orchestrator.execute_workflow(
                    topic=topic,
                    audience="general",
                    mode="sequential"
                )
                handled_long_topic = True
                error_message = None
            except Exception as e:
                handled_long_topic = False
                error_message = str(e)
            
            end_time = time.time()
            
            # Test with empty topic
            print("Testing with empty topic...")
            empty_topic_handled = False
            try:
                result = self.orchestrator.execute_workflow(
                    topic="",
                    audience="general",
                    mode="sequential"
                )
                empty_topic_handled = False  # Should have failed
            except:
                empty_topic_handled = True  # Good - it caught the error
            
            # Collect metrics
            test_result["metrics"] = {
                "long_topic_handled": handled_long_topic,
                "empty_topic_handled": empty_topic_handled,
                "execution_time": round(end_time - start_time, 2),
                "error_message": error_message
            }
            
            # Determine pass/fail
            if handled_long_topic or empty_topic_handled:
                test_result["status"] = "PASSED"
                print(f"✅ TEST PASSED - Error handling works")
            else:
                test_result["status"] = "FAILED"
                print(f"❌ TEST FAILED - Poor error handling")
                
        except Exception as e:
            test_result["status"] = "ERROR"
            test_result["error"] = str(e)
            print(f"❌ TEST ERROR: {str(e)}")
            logger.error(f"Test 2 failed with error: {str(e)}", exc_info=True)
        
        self.results["tests"].append(test_result)
        return test_result
    
    def test_3_custom_tool_functionality(self):
        """Test 3: Custom Tool - Does the credibility analyzer work correctly?"""
        print("\n" + "="*60)
        print("TEST 3: CUSTOM TOOL FUNCTIONALITY TEST")
        print("="*60)
        
        test_result = {
            "test_name": "Custom Tool Test",
            "test_id": "TEST_003",
            "description": "Verify Source Credibility Analyzer functions correctly",
            "status": "PENDING",
            "metrics": {}
        }
        
        try:
            # Initialize the custom tool
            analyzer = SourceCredibilityAnalyzer()
            
            # Test cases for different URLs
            test_urls = [
                ("https://www.nature.com/articles/test", "high", 80),  # Trusted domain
                ("http://suspicious-site.com/article", "low", 60),     # HTTP, unknown
                ("https://stanford.edu/research/paper", "high", 85),   # Educational
            ]
            
            results = []
            all_passed = True
            
            for url, expected_level, min_score in test_urls:
                print(f"Testing URL: {url}")
                
                # Analyze the URL
                analysis = analyzer._run(url)
                
                # Check if analysis returned expected structure
                has_score = "credibility_score" in analysis
                has_factors = "factors" in analysis
                has_recommendations = "recommendations" in analysis
                
                # Check if score is reasonable
                score = analysis.get("credibility_score", 0)
                score_reasonable = 0 <= score <= 100
                
                # Store result
                url_result = {
                    "url": url,
                    "score": score,
                    "has_required_fields": has_score and has_factors and has_recommendations,
                    "score_reasonable": score_reasonable,
                    "expected_level": expected_level,
                    "meets_expectation": score >= min_score if expected_level == "high" else score < min_score
                }
                
                results.append(url_result)
                
                if not url_result["meets_expectation"]:
                    all_passed = False
                
                print(f"  Score: {score}, Expected: {expected_level}")
            
            # Collect metrics
            test_result["metrics"] = {
                "urls_tested": len(test_urls),
                "all_passed": all_passed,
                "detailed_results": results
            }
            
            # Determine pass/fail
            if all_passed:
                test_result["status"] = "PASSED"
                print(f"✅ TEST PASSED - Custom tool works correctly")
            else:
                test_result["status"] = "FAILED"
                print(f"❌ TEST FAILED - Some URLs not analyzed correctly")
                
        except Exception as e:
            test_result["status"] = "ERROR"
            test_result["error"] = str(e)
            print(f"❌ TEST ERROR: {str(e)}")
            logger.error(f"Test 3 failed with error: {str(e)}", exc_info=True)
        
        self.results["tests"].append(test_result)
        return test_result
    
    def test_4_performance_metrics(self):
        """Test 4: Performance - Is the system efficient?"""
        print("\n" + "="*60)
        print("TEST 4: PERFORMANCE METRICS TEST")
        print("="*60)
        
        test_result = {
            "test_name": "Performance Test",
            "test_id": "TEST_004",
            "description": "Measure system performance and resource usage",
            "status": "PENDING",
            "metrics": {}
        }
        
        try:
            # Run multiple tests to get average
            execution_times = []
            topics = ["Artificial Intelligence", "Climate Change", "Space Exploration"]
            
            for topic in topics:
                print(f"Performance test with topic: '{topic}'")
                
                start_time = time.time()
                
                try:
                    result = self.orchestrator.execute_workflow(
                        topic=topic,
                        audience="general",
                        mode="sequential"
                    )
                    
                    end_time = time.time()
                    execution_time = end_time - start_time
                    execution_times.append(execution_time)
                    
                    print(f"  Completed in {execution_time:.2f} seconds")
                    
                except Exception as e:
                    print(f"  Failed: {str(e)}")
            
            # Calculate metrics
            if execution_times:
                avg_time = sum(execution_times) / len(execution_times)
                min_time = min(execution_times)
                max_time = max(execution_times)
                
                # Performance thresholds
                performance_good = avg_time < 300  # Less than 5 minutes average
                
                test_result["metrics"] = {
                    "average_execution_time": round(avg_time, 2),
                    "min_execution_time": round(min_time, 2),
                    "max_execution_time": round(max_time, 2),
                    "successful_runs": len(execution_times),
                    "total_runs": len(topics),
                    "success_rate": f"{(len(execution_times)/len(topics))*100:.1f}%"
                }
                
                if performance_good and len(execution_times) == len(topics):
                    test_result["status"] = "PASSED"
                    print(f"✅ TEST PASSED - Good performance: avg {avg_time:.2f}s")
                else:
                    test_result["status"] = "PARTIAL"
                    print(f"⚠️ TEST PARTIAL - Some issues with performance")
            else:
                test_result["status"] = "FAILED"
                print(f"❌ TEST FAILED - No successful executions")
                
        except Exception as e:
            test_result["status"] = "ERROR"
            test_result["error"] = str(e)
            print(f"❌ TEST ERROR: {str(e)}")
            logger.error(f"Test 4 failed with error: {str(e)}", exc_info=True)
        
        self.results["tests"].append(test_result)
        return test_result
    
    def generate_evaluation_report(self):
        """Generate a comprehensive evaluation report"""
        print("\n" + "="*60)
        print("GENERATING EVALUATION REPORT")
        print("="*60)
        
        # Calculate summary statistics
        total_tests = len(self.results["tests"])
        passed_tests = sum(1 for t in self.results["tests"] if t["status"] == "PASSED")
        failed_tests = sum(1 for t in self.results["tests"] if t["status"] == "FAILED")
        error_tests = sum(1 for t in self.results["tests"] if t["status"] == "ERROR")
        
        # Add summary
        self.results["summary"] = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "errors": error_tests,
            "success_rate": f"{(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "0%"
        }
        
        # Save JSON report
        report_dir = Path("evaluation_reports")
        report_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = report_dir / f"evaluation_report_{timestamp}.json"
        
        with open(json_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"✅ JSON report saved to: {json_file}")
        
        # Generate markdown report
        md_file = report_dir / f"evaluation_report_{timestamp}.md"
        
        with open(md_file, 'w') as f:
            f.write("# System Evaluation Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- **Total Tests**: {total_tests}\n")
            f.write(f"- **Passed**: {passed_tests} ✅\n")
            f.write(f"- **Failed**: {failed_tests} ❌\n")
            f.write(f"- **Errors**: {error_tests} ⚠️\n")
            f.write(f"- **Success Rate**: {self.results['summary']['success_rate']}\n\n")
            
            f.write("## Detailed Test Results\n\n")
            
            for test in self.results["tests"]:
                f.write(f"### {test['test_name']}\n")
                f.write(f"- **Test ID**: {test['test_id']}\n")
                f.write(f"- **Status**: {test['status']}\n")
                f.write(f"- **Description**: {test['description']}\n")
                
                if test.get("metrics"):
                    f.write("- **Metrics**:\n")
                    for key, value in test["metrics"].items():
                        if isinstance(value, list):
                            f.write(f"  - {key}: [details in JSON]\n")
                        else:
                            f.write(f"  - {key}: {value}\n")
                
                if test.get("error"):
                    f.write(f"- **Error**: {test['error']}\n")
                
                f.write("\n")
            
            f.write("## Conclusions\n\n")
            
            if passed_tests == total_tests:
                f.write("✅ **All tests passed!** The system is functioning excellently.\n")
            elif passed_tests >= total_tests * 0.75:
                f.write("✅ **System performing well** with most tests passing.\n")
            elif passed_tests >= total_tests * 0.5:
                f.write("⚠️ **System needs attention** - several tests failing.\n")
            else:
                f.write("❌ **System has issues** - majority of tests failing.\n")
        
        print(f"✅ Markdown report saved to: {md_file}")
        
        # Print summary to console
        print("\n" + "="*60)
        print("EVALUATION SUMMARY")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Errors: {error_tests} ⚠️")
        print(f"Success Rate: {self.results['summary']['success_rate']}")
        print("="*60)
        
        return self.results


def run_evaluation():
    """Main function to run all evaluation tests"""
    from dotenv import load_dotenv
    load_dotenv()
    
    print("\n" + "="*60)
    print("STARTING SYSTEM EVALUATION")
    print("="*60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create evaluator
    evaluator = SystemEvaluator()
    
    # Run all tests
    evaluator.test_1_basic_functionality()
    evaluator.test_2_error_handling()
    evaluator.test_3_custom_tool_functionality()
    evaluator.test_4_performance_metrics()
    
    # Generate report
    report = evaluator.generate_evaluation_report()
    
    return report


if __name__ == "__main__":
    # Run the evaluation
    run_evaluation()