"""
Complete Demo Script for ADF Monitoring & Automation System
Demonstrates the full workflow with mock data
"""
import time
import json
from datetime import datetime
from mock_data import MockDataGenerator, create_test_scenario
from database import PipelineRun, db_manager
from genai_analyzer import GenAIAnalyzer, should_rerun_pipeline, log_decision_and_action
from notification_service import notification_service
from adf_client import rerun_pipeline

def demo_full_workflow():
    """Demonstrate the complete monitoring and automation workflow"""
    
    print("🎬 ADF Monitoring & Automation System - Complete Demo")
    print("=" * 60)
    
    # Initialize components
    analyzer = GenAIAnalyzer()
    generator = MockDataGenerator()
    
    print("\n1️⃣  Generating mock pipeline failures...")
    test_scenarios = create_test_scenario()
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🔍 Processing Scenario {i}: {scenario['pipelineName']}")
        print("=" * 40)
        
        # Create PipelineRun object
        pipeline_run = PipelineRun(
            run_id=scenario['runId'],
            pipeline_name=scenario['pipelineName'],
            status=scenario['status'],
            start_time=datetime.fromisoformat(scenario['runStart'].replace('Z', '+00:00')),
            end_time=datetime.fromisoformat(scenario['runEnd'].replace('Z', '+00:00')),
            error_message=scenario['message'],
            factory_name="DemoDataFactory"
        )
        
        # Store in database
        print(f"💾 Storing pipeline run in database...")
        db_manager.insert_pipeline_run(pipeline_run)
        
        # Analyze with GenAI
        print(f"🤖 Analyzing failure with AI...")
        analysis_result = analyzer.analyze_failure_with_genai(
            pipeline_run.pipeline_name,
            pipeline_run.error_message,
            pipeline_run.run_id
        )
        
        if analysis_result.get('success'):
            analysis = analysis_result['analysis']
            print(f"   📊 Error Type: {analysis.get('error_type', 'unknown')}")
            print(f"   📈 Confidence: {analysis.get('confidence_score', 0)}%")
            print(f"   💬 Summary: {analysis.get('analysis_summary', 'No summary')}")
            
            # Send failure notification
            notification_service.send_failure_alert(
                pipeline_run.pipeline_name,
                pipeline_run.run_id,
                pipeline_run.error_message,
                analysis
            )
            
            # Determine retry action
            should_retry, retry_reason = should_rerun_pipeline(analysis_result, pipeline_run.pipeline_name)
            
            if should_retry:
                print(f"   🔄 Decision: RETRY - {retry_reason}")
                
                # Send retry notification
                notification_service.send_retry_alert(
                    pipeline_run.pipeline_name,
                    pipeline_run.run_id,
                    retry_reason
                )
                
                # Simulate retry attempt
                print(f"   ⏳ Simulating pipeline retry...")
                time.sleep(2)  # Simulate processing time
                
                # Mock retry result (80% success rate)
                import random
                retry_success = random.random() < 0.8
                
                if retry_success:
                    print(f"   ✅ Retry successful!")
                    notification_service.send_success_alert(
                        pipeline_run.pipeline_name,
                        pipeline_run.run_id,
                        "retry"
                    )
                else:
                    print(f"   ❌ Retry failed")
                
                # Log the action
                log_decision_and_action(
                    pipeline_run.run_id,
                    analysis_result,
                    "retry",
                    retry_success
                )
                
            else:
                print(f"   ⏸️  Decision: NO RETRY - {retry_reason}")
                
                # Send manual intervention alert
                recommended_actions = analysis.get('recommended_actions', ['Review logs', 'Contact support'])
                notification_service.send_manual_intervention_alert(
                    pipeline_run.pipeline_name,
                    pipeline_run.run_id,
                    retry_reason,
                    recommended_actions
                )
                
                # Log manual intervention decision
                log_decision_and_action(
                    pipeline_run.run_id,
                    analysis_result,
                    "manual_intervention",
                    True
                )
        
        else:
            print(f"   ❌ AI analysis failed")
        
        print(f"   ⏱️  Waiting before next scenario...")
        time.sleep(3)
    
    print("\n📊 Demo Summary")
    print("=" * 30)
    
    # Get dashboard stats
    stats = db_manager.get_dashboard_stats()
    print(f"Total Runs Today: {stats.get('total_runs_today', 0)}")
    print(f"Failed Runs Today: {stats.get('failed_runs_today', 0)}")
    print(f"Success Rate: {stats.get('success_rate_today', 100):.1f}%")
    print(f"Auto Retries Today: {stats.get('auto_retries_today', 0)}")
    
    # Show recent failed runs
    print(f"\n📋 Recent Failed Runs:")
    failed_runs = db_manager.get_failed_runs_last_hours(1)
    for run in failed_runs[-3:]:  # Show last 3
        print(f"   - {run['pipeline_name']}: {run['error_message'][:50]}...")
    
    print(f"\n🎉 Demo completed successfully!")
    print(f"💡 Next steps:")
    print(f"   - Run 'streamlit run dashboard.py' to view the dashboard")
    print(f"   - Check 'adf_monitoring.db' for stored data")
    print(f"   - Review logs and notifications above")

def demo_ai_analysis_variations():
    """Demonstrate different AI analysis scenarios"""
    
    print("\n🧠 AI Analysis Variations Demo")
    print("=" * 40)
    
    analyzer = GenAIAnalyzer()
    
    # Test different error types
    test_errors = [
        {
            "type": "Network Timeout",
            "message": "Connection timeout to source database after 30 seconds",
            "expected": "transient"
        },
        {
            "type": "Data Quality",
            "message": "Schema validation failed: Column 'customer_id' not found in source table",
            "expected": "data_quality"
        },
        {
            "type": "Access Denied", 
            "message": "Access denied: Insufficient permissions to read from storage account",
            "expected": "configuration"
        },
        {
            "type": "Unknown Error",
            "message": "Unexpected error occurred during pipeline execution: Code 500",
            "expected": "unknown"
        }
    ]
    
    for i, error_test in enumerate(test_errors, 1):
        print(f"\n{i}. Testing {error_test['type']}:")
        print(f"   Error: {error_test['message']}")
        
        # Analyze with AI
        result = analyzer.analyze_failure_with_genai(
            "TestPipeline",
            error_test['message'],
            f"test-run-{i}"
        )
        
        if result.get('success'):
            analysis = result['analysis']
            print(f"   🎯 Detected Type: {analysis.get('error_type', 'unknown')}")
            print(f"   🔄 Should Retry: {analysis.get('should_retry', False)}")
            print(f"   📊 Confidence: {analysis.get('confidence_score', 0)}%")
            print(f"   ✅ Expected: {error_test['expected']}")
            
            # Check if classification matches expectation
            if analysis.get('error_type') == error_test['expected']:
                print(f"   ✅ Classification correct!")
            else:
                print(f"   ⚠️  Classification mismatch")
        else:
            print(f"   ❌ Analysis failed")

def demo_notification_system():
    """Demonstrate notification system"""
    
    print("\n📢 Notification System Demo")
    print("=" * 35)
    
    # Test different notification types
    
    print("\n1. Failure Alert:")
    notification_service.send_failure_alert(
        "DemoDataPipeline",
        "demo-run-001",
        "Connection timeout to source database",
        {
            "error_type": "transient",
            "severity": "medium",
            "ai_recommendation": "Retry recommended - network timeout detected"
        }
    )
    
    print("\n2. Retry Alert:")
    notification_service.send_retry_alert(
        "DemoDataPipeline",
        "demo-run-001",
        "AI analysis suggests retry for transient error"
    )
    
    print("\n3. Success Alert:")
    notification_service.send_success_alert(
        "DemoDataPipeline", 
        "demo-run-001",
        "retry"
    )
    
    print("\n4. Manual Intervention Alert:")
    notification_service.send_manual_intervention_alert(
        "DemoDataPipeline",
        "demo-run-002",
        "Data quality issue requires manual review",
        [
            "Review source data schema",
            "Contact data provider",
            "Update pipeline configuration"
        ]
    )

def main():
    """Main demo function"""
    
    print("🎭 Choose Demo Type:")
    print("1. Complete Workflow Demo")
    print("2. AI Analysis Variations")
    print("3. Notification System Demo")
    print("4. All Demos")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        demo_full_workflow()
    elif choice == "2":
        demo_ai_analysis_variations()
    elif choice == "3":
        demo_notification_system()
    elif choice == "4":
        demo_full_workflow()
        demo_ai_analysis_variations()
        demo_notification_system()
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
