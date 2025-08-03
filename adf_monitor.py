"""
Main ADF Monitoring & Automation System
"""
import time
import schedule
from datetime import datetime, timedelta
from typing import List
from config import config
from adf_client import get_adf_pipeline_status, rerun_pipeline
from genai_analyzer import analyze_failure_with_genai, should_rerun_pipeline, log_decision_and_action, GenAIAnalyzer
from notification_service import notification_service
from database import PipelineRun, db_manager

class ADFMonitoringSystem:
    """Main ADF monitoring and automation system"""
    
    def __init__(self):
        self.config = config
        self.genai_analyzer = GenAIAnalyzer()
        self.running = False
        
        # Validate configuration
        if not self.config.validate():
            print("❌ Configuration validation failed. Please check your .env file.")
            print("Create a .env file based on .env.example with your actual values.")
    
    def start_monitoring(self, run_once: bool = False):
        """Start the monitoring system"""
        print("🚀 Starting ADF Monitoring & Automation System")
        print(f"📊 Data Factory: {self.config.azure.data_factory_name}")
        print(f"⏱️  Polling interval: {self.config.monitoring.polling_interval_minutes} minutes")
        print(f"🔄 Max retry attempts: {self.config.monitoring.max_retry_attempts}")
        
        if run_once:
            print("\n🔍 Running single monitoring cycle...")
            self.monitor_pipelines()
        else:
            print(f"\n🔄 Starting continuous monitoring...")
            self.running = True
            
            # Schedule monitoring
            schedule.every(self.config.monitoring.polling_interval_minutes).minutes.do(self.monitor_pipelines)
            
            try:
                while self.running:
                    schedule.run_pending()
                    time.sleep(30)  # Check every 30 seconds
            except KeyboardInterrupt:
                print("\n⏹️  Monitoring stopped by user")
                self.running = False
    
    def stop_monitoring(self):
        """Stop the monitoring system"""
        self.running = False
        print("⏹️  Monitoring system stopped")
    
    def monitor_pipelines(self):
        """Main monitoring function"""
        print(f"\n🔍 Monitoring pipelines at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Get current pipeline status
            pipeline_runs = get_adf_pipeline_status()
            
            if not pipeline_runs:
                print("ℹ️  No pipeline runs found")
                return
            
            print(f"📊 Found {len(pipeline_runs)} pipeline runs")
            
            # Process each pipeline run
            failed_runs = [run for run in pipeline_runs if run.status == "Failed"]
            
            if failed_runs:
                print(f"❌ Found {len(failed_runs)} failed runs")
                
                for failed_run in failed_runs:
                    self.process_failed_pipeline(failed_run)
            else:
                print("✅ No failed pipeline runs found")
            
            # Print summary
            self.print_monitoring_summary()
            
        except Exception as e:
            print(f"❌ Error during monitoring: {e}")
            notification_service.send_alert(
                alert_type="warning",
                pipeline_name="System",
                message=f"Monitoring system error: {str(e)}"
            )
    
    def process_failed_pipeline(self, failed_run: PipelineRun):
        """Process a failed pipeline run"""
        print(f"\n🔍 Processing failed pipeline: {failed_run.pipeline_name} (Run ID: {failed_run.run_id})")
        
        try:
            # Check if we've already processed this run
            existing_actions = db_manager.get_retry_history(failed_run.pipeline_name, hours=1)
            if any(action.get('run_id') == failed_run.run_id for action in existing_actions):
                print(f"ℹ️  Run {failed_run.run_id} already processed, skipping")
                return
            
            # Analyze failure with GenAI
            print("🤖 Analyzing failure with AI...")
            analysis_result = self.genai_analyzer.analyze_failure_with_genai(
                failed_run.pipeline_name,
                failed_run.error_message or "No error message available",
                failed_run.run_id
            )
            
            if not analysis_result.get("success", False):
                print("❌ AI analysis failed")
                notification_service.send_failure_alert(
                    failed_run.pipeline_name,
                    failed_run.run_id,
                    failed_run.error_message or "No error message"
                )
                return
            
            analysis = analysis_result.get("analysis", {})
            print(f"🎯 AI Analysis: {analysis.get('analysis_summary', 'No summary')}")
            print(f"🔍 Error Type: {analysis.get('error_type', 'unknown')}")
            print(f"📊 Confidence: {analysis.get('confidence_score', 0)}%")
            
            # Send failure alert with analysis
            notification_service.send_failure_alert(
                failed_run.pipeline_name,
                failed_run.run_id,
                failed_run.error_message or "No error message",
                analysis
            )
            
            # Determine if we should retry
            should_retry, retry_reason = should_rerun_pipeline(analysis_result, failed_run.pipeline_name)
            
            if should_retry:
                print(f"🔄 Attempting auto-retry: {retry_reason}")
                
                # Wait for retry delay
                retry_delay = analysis.get('retry_delay_minutes', config.monitoring.retry_delay_minutes)
                if retry_delay > 0:
                    print(f"⏳ Waiting {retry_delay} minutes before retry...")
                    time.sleep(retry_delay * 60)
                
                # Attempt retry
                retry_success = rerun_pipeline(failed_run.pipeline_name, failed_run.run_id)
                
                if retry_success:
                    print("✅ Pipeline retry initiated successfully")
                    notification_service.send_retry_alert(
                        failed_run.pipeline_name,
                        failed_run.run_id,
                        retry_reason
                    )
                    
                    # Log successful retry action
                    log_decision_and_action(
                        failed_run.run_id,
                        analysis_result,
                        "retry",
                        True
                    )
                else:
                    print("❌ Pipeline retry failed")
                    # Log failed retry action
                    log_decision_and_action(
                        failed_run.run_id,
                        analysis_result,
                        "retry",
                        False
                    )
            else:
                print(f"⏸️  No retry recommended: {retry_reason}")
                
                # Send manual intervention alert
                recommended_actions = analysis.get('recommended_actions', ['Review logs', 'Contact support'])
                notification_service.send_manual_intervention_alert(
                    failed_run.pipeline_name,
                    failed_run.run_id,
                    retry_reason,
                    recommended_actions
                )
                
                # Log manual intervention decision
                log_decision_and_action(
                    failed_run.run_id,
                    analysis_result,
                    "manual_intervention",
                    True
                )
        
        except Exception as e:
            print(f"❌ Error processing failed pipeline: {e}")
            notification_service.send_alert(
                alert_type="warning",
                pipeline_name=failed_run.pipeline_name,
                message=f"Error processing failed pipeline: {str(e)}"
            )
    
    def print_monitoring_summary(self):
        """Print monitoring summary"""
        try:
            stats = db_manager.get_dashboard_stats()
            
            print(f"\n📈 Today's Summary:")
            print(f"   Total Runs: {stats.get('total_runs_today', 0)}")
            print(f"   Failed Runs: {stats.get('failed_runs_today', 0)}")
            print(f"   Success Rate: {stats.get('success_rate_today', 100):.1f}%")
            print(f"   Auto Retries: {stats.get('auto_retries_today', 0)}")
            
        except Exception as e:
            print(f"❌ Error getting summary stats: {e}")
    
    def get_system_status(self) -> dict:
        """Get system status for API/UI"""
        try:
            stats = db_manager.get_dashboard_stats()
            
            return {
                "system_running": self.running,
                "last_check": datetime.now().isoformat(),
                "config_valid": self.config.validate(),
                "stats": stats
            }
        except Exception as e:
            return {
                "system_running": False,
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }

def main():
    """Main entry point"""
    print("🏭 ADF Monitoring & Automation System")
    print("=====================================")
    
    # Create monitoring system
    monitor = ADFMonitoringSystem()
    
    try:
        # Check if running in test mode
        import sys
        if "--test" in sys.argv:
            print("🧪 Running in test mode (single cycle)")
            monitor.start_monitoring(run_once=True)
        else:
            monitor.start_monitoring(run_once=False)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    main()
