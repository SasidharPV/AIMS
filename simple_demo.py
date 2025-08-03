"""
Simplified Demo for ADF Monitoring System (No Azure Dependencies Required)
"""
import time
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

def create_demo_database():
    """Create demo database and populate with sample data"""
    db_path = "demo_adf_monitoring.db"
    
    # Remove existing demo database
    if Path(db_path).exists():
        Path(db_path).unlink()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE pipeline_runs (
            run_id TEXT PRIMARY KEY,
            pipeline_name TEXT NOT NULL,
            status TEXT NOT NULL,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP,
            error_message TEXT,
            factory_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE monitoring_actions (
            action_id TEXT PRIMARY KEY,
            run_id TEXT NOT NULL,
            action_type TEXT NOT NULL,
            ai_analysis TEXT,
            decision_reason TEXT NOT NULL,
            action_taken BOOLEAN NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert sample failed pipeline runs
    sample_runs = [
        {
            "run_id": "demo-run-001",
            "pipeline_name": "DataProcessingPipeline", 
            "status": "Failed",
            "start_time": datetime.now() - timedelta(minutes=30),
            "end_time": datetime.now() - timedelta(minutes=25),
            "error_message": "Connection timeout to source database after 30 seconds. Error code: 40001",
            "factory_name": "DemoDataFactory"
        },
        {
            "run_id": "demo-run-002",
            "pipeline_name": "ETLPipeline",
            "status": "Failed", 
            "start_time": datetime.now() - timedelta(minutes=45),
            "end_time": datetime.now() - timedelta(minutes=40),
            "error_message": "Schema validation failed: Missing required column 'customer_id' in source file",
            "factory_name": "DemoDataFactory"
        },
        {
            "run_id": "demo-run-003",
            "pipeline_name": "ReportGenerationPipeline",
            "status": "Failed",
            "start_time": datetime.now() - timedelta(minutes=15),
            "end_time": datetime.now() - timedelta(minutes=10),
            "error_message": "Access denied: Insufficient permissions to read from storage account 'reports'",
            "factory_name": "DemoDataFactory"
        }
    ]
    
    for run in sample_runs:
        cursor.execute('''
            INSERT INTO pipeline_runs 
            (run_id, pipeline_name, status, start_time, end_time, error_message, factory_name)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            run["run_id"], run["pipeline_name"], run["status"],
            run["start_time"], run["end_time"], run["error_message"], run["factory_name"]
        ))
    
    conn.commit()
    conn.close()
    return db_path

def analyze_error_with_mock_ai(error_message):
    """Mock AI analysis based on error message patterns"""
    error_lower = error_message.lower()
    
    if any(keyword in error_lower for keyword in ['timeout', 'connection', 'network']):
        return {
            "error_type": "transient",
            "severity": "medium",
            "should_retry": True,
            "retry_delay_minutes": 10,
            "confidence_score": 85,
            "analysis_summary": "Network/timeout error detected. This is typically a transient issue that resolves on retry.",
            "root_cause": "Network connectivity or service timeout",
            "recommended_actions": [
                "Retry the pipeline",
                "Monitor for pattern of network issues", 
                "Check service health status"
            ],
            "manual_intervention_required": False
        }
    elif any(keyword in error_lower for keyword in ['column', 'schema', 'validation', 'data']):
        return {
            "error_type": "data_quality",
            "severity": "high",
            "should_retry": False,
            "retry_delay_minutes": 0,
            "confidence_score": 90,
            "analysis_summary": "Data quality issue detected. Manual intervention required to fix data source.",
            "root_cause": "Data schema or content validation failure",
            "recommended_actions": [
                "Review source data quality",
                "Check data schema changes",
                "Contact data provider",
                "Update pipeline to handle schema changes"
            ],
            "manual_intervention_required": True
        }
    elif any(keyword in error_lower for keyword in ['access', 'permission', 'denied', 'authentication']):
        return {
            "error_type": "configuration",
            "severity": "high", 
            "should_retry": False,
            "retry_delay_minutes": 0,
            "confidence_score": 88,
            "analysis_summary": "Access denied error indicates authentication or authorization configuration issue.",
            "root_cause": "Invalid credentials or insufficient permissions",
            "recommended_actions": [
                "Verify service principal credentials",
                "Check resource access permissions",
                "Review connection string configuration",
                "Update authentication settings"
            ],
            "manual_intervention_required": True
        }
    else:
        return {
            "error_type": "unknown",
            "severity": "medium",
            "should_retry": True,
            "retry_delay_minutes": 15,
            "confidence_score": 70,
            "analysis_summary": "Unknown error type. Attempting retry with caution.",
            "root_cause": "Unclear from error message",
            "recommended_actions": [
                "Retry once with monitoring",
                "Review detailed activity logs",
                "Escalate if retry fails"
            ],
            "manual_intervention_required": False
        }

def send_console_notification(alert_type, pipeline_name, message, details=None):
    """Send formatted console notification"""
    print("\n" + "="*80)
    print(f"🚨 ADF ALERT: {alert_type.upper()}")
    print("="*80)
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Pipeline: {pipeline_name}")
    print(f"💬 Message: {message}")
    
    if details:
        print("\n📋 Details:")
        for key, value in details.items():
            if isinstance(value, list):
                print(f"  {key}:")
                for item in value:
                    print(f"    - {item}")
            else:
                print(f"  {key}: {value}")
    
    print("="*80 + "\n")

def demo_monitoring_workflow():
    """Demonstrate the complete monitoring workflow"""
    
    print("🎬 ADF Monitoring & Automation System - Live Demo")
    print("=" * 60)
    print("This demo shows the complete workflow without requiring Azure or OpenAI credentials")
    
    # Create demo database
    print("\n1️⃣  Setting up demo database...")
    db_path = create_demo_database()
    print(f"✅ Demo database created: {db_path}")
    
    # Connect to database and get failed runs
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM pipeline_runs WHERE status = 'Failed'")
    failed_runs = cursor.fetchall()
    
    print(f"\n2️⃣  Found {len(failed_runs)} failed pipeline runs to process")
    
    # Process each failed run
    for i, run in enumerate(failed_runs, 1):
        run_id, pipeline_name, status, start_time, end_time, error_message, factory_name, created_at = run
        
        print(f"\n🔍 Processing Run {i}: {pipeline_name}")
        print("=" * 50)
        print(f"   Run ID: {run_id}")
        print(f"   Error: {error_message}")
        
        # Send failure notification
        send_console_notification(
            "FAILURE",
            pipeline_name,
            f"Pipeline {pipeline_name} failed",
            {
                "run_id": run_id,
                "error_message": error_message[:100] + "..." if len(error_message) > 100 else error_message,
                "start_time": start_time
            }
        )
        
        # Analyze with mock AI
        print("🤖 Analyzing failure with AI...")
        analysis = analyze_error_with_mock_ai(error_message)
        
        print(f"   📊 Error Type: {analysis['error_type']}")
        print(f"   📈 Confidence: {analysis['confidence_score']}%")
        print(f"   💬 Summary: {analysis['analysis_summary']}")
        
        # Determine action
        should_retry = analysis['should_retry']
        
        if should_retry:
            print(f"   🔄 Decision: RETRY RECOMMENDED")
            
            # Send retry notification
            send_console_notification(
                "RETRY",
                pipeline_name, 
                f"Auto-retrying pipeline {pipeline_name}",
                {
                    "run_id": run_id,
                    "retry_reason": analysis['analysis_summary'],
                    "retry_delay": f"{analysis['retry_delay_minutes']} minutes"
                }
            )
            
            # Simulate retry
            print(f"   ⏳ Simulating pipeline retry (waiting {analysis['retry_delay_minutes']} seconds)...")
            time.sleep(3)  # Shortened for demo
            
            # Mock retry result (75% success rate) 
            import random
            retry_success = random.random() < 0.75
            
            if retry_success:
                print(f"   ✅ Retry SUCCESSFUL!")
                send_console_notification(
                    "SUCCESS",
                    pipeline_name,
                    f"Pipeline {pipeline_name} retry successful",
                    {"run_id": run_id, "action": "retry"}
                )
            else:
                print(f"   ❌ Retry FAILED - escalating to manual intervention")
                send_console_notification(
                    "WARNING", 
                    pipeline_name,
                    f"Manual intervention required for pipeline {pipeline_name}",
                    {
                        "run_id": run_id,
                        "reason": "Retry failed - requires manual review",
                        "recommended_actions": analysis['recommended_actions']
                    }
                )
            
            # Log action in database
            action_id = f"action-{run_id}-retry"
            cursor.execute('''
                INSERT INTO monitoring_actions 
                (action_id, run_id, action_type, ai_analysis, decision_reason, action_taken, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                action_id, run_id, "retry", json.dumps(analysis),
                analysis['analysis_summary'], retry_success, datetime.now()
            ))
            
        else:
            print(f"   ⏸️  Decision: MANUAL INTERVENTION REQUIRED")
            print(f"   📝 Reason: {analysis['analysis_summary']}")
            
            # Send manual intervention notification
            send_console_notification(
                "WARNING",
                pipeline_name,
                f"Manual intervention required for pipeline {pipeline_name}",
                {
                    "run_id": run_id,
                    "reason": analysis['analysis_summary'],
                    "recommended_actions": analysis['recommended_actions']
                }
            )
            
            # Log manual intervention
            action_id = f"action-{run_id}-manual"
            cursor.execute('''
                INSERT INTO monitoring_actions 
                (action_id, run_id, action_type, ai_analysis, decision_reason, action_taken, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                action_id, run_id, "manual_intervention", json.dumps(analysis),
                analysis['analysis_summary'], True, datetime.now()
            ))
        
        print(f"   💾 Action logged to database")
        time.sleep(2)  # Brief pause between runs
    
    conn.commit()
    
    # Show summary statistics
    print(f"\n📊 DEMO SUMMARY")
    print("=" * 30)
    
    # Get stats from database
    cursor.execute("SELECT COUNT(*) FROM pipeline_runs WHERE DATE(start_time) = DATE('now')")
    total_runs = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM pipeline_runs WHERE status = 'Failed' AND DATE(start_time) = DATE('now')")
    failed_runs_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM monitoring_actions WHERE action_type = 'retry'")
    retry_attempts = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM monitoring_actions WHERE action_type = 'manual_intervention'")  
    manual_interventions = cursor.fetchone()[0]
    
    success_rate = ((total_runs - failed_runs_count) / total_runs * 100) if total_runs > 0 else 100
    
    print(f"📈 Total Pipeline Runs: {total_runs}")
    print(f"❌ Failed Runs: {failed_runs_count}")
    print(f"✅ Success Rate: {success_rate:.1f}%")
    print(f"🔄 Auto Retries Attempted: {retry_attempts}")
    print(f"👤 Manual Interventions: {manual_interventions}")
    
    # Show recent actions
    print(f"\n📋 Recent AI Decisions:")
    cursor.execute('''
        SELECT ma.action_type, ma.decision_reason, pr.pipeline_name, ma.timestamp
        FROM monitoring_actions ma
        JOIN pipeline_runs pr ON ma.run_id = pr.run_id
        ORDER BY ma.timestamp DESC
        LIMIT 5
    ''')
    
    actions = cursor.fetchall()
    for action in actions:
        action_type, reason, pipeline_name, timestamp = action
        print(f"   - {pipeline_name}: {action_type} - {reason[:60]}...")
    
    conn.close()
    
    print(f"\n🎉 Demo completed successfully!")
    print(f"\n💡 Key Features Demonstrated:")
    print(f"   ✅ Automatic pipeline failure detection")
    print(f"   ✅ AI-powered error analysis and classification")
    print(f"   ✅ Intelligent retry vs manual intervention decisions")
    print(f"   ✅ Multi-channel notification system")
    print(f"   ✅ Complete audit trail and logging")
    print(f"   ✅ Real-time dashboard-ready statistics")
    
    print(f"\n📁 Files created:")
    print(f"   - {db_path} (SQLite database with demo data)")
    print(f"   - Check the database to see logged actions and decisions")

if __name__ == "__main__":
    demo_monitoring_workflow()
