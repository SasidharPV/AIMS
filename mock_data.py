"""
Mock Data Generator for Testing ADF Monitoring System
"""
import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random

class MockDataGenerator:
    """Generate mock data for testing the ADF monitoring system"""
    
    def __init__(self):
        self.pipeline_names = [
            "DataProcessingPipeline",
            "ETLPipeline", 
            "DataValidationPipeline",
            "ReportGenerationPipeline",
            "CustomerDataPipeline",
            "SalesAnalyticsPipeline"
        ]
        
        self.error_templates = [
            {
                "type": "transient",
                "messages": [
                    "Activity 'CopyData' failed: The source database connection failed due to timeout. Error code: 40001",
                    "Pipeline execution failed due to temporary network connectivity issues",
                    "Service temporarily unavailable. Please retry after some time",
                    "Request timeout occurred while connecting to the data source"
                ]
            },
            {
                "type": "data_quality",
                "messages": [
                    "Validation failed: Missing required column 'customer_id' in source file",
                    "Data type mismatch: Expected INTEGER but found STRING in column 'amount'",
                    "Duplicate key violation: Primary key constraint failed",
                    "Schema validation failed: Column 'created_date' not found in source"
                ]
            },
            {
                "type": "configuration",
                "messages": [
                    "Access denied: Insufficient permissions to read from storage account",
                    "Authentication failed: Invalid credentials for data source connection",
                    "Configuration error: Invalid connection string format",
                    "Resource not found: Storage container 'data-input' does not exist"
                ]
            }
        ]
    
    def generate_pipeline_runs(self, count: int = 10, failed_percentage: float = 0.3) -> List[Dict[str, Any]]:
        """Generate mock pipeline run data"""
        runs = []
        
        for i in range(count):
            run_id = f"mock-run-{uuid.uuid4().hex[:8]}"
            pipeline_name = random.choice(self.pipeline_names)
            
            # Determine if this run should be failed
            is_failed = random.random() < failed_percentage
            
            start_time = datetime.now() - timedelta(
                minutes=random.randint(5, 120),
                seconds=random.randint(0, 59)
            )
            
            if is_failed:
                end_time = start_time + timedelta(minutes=random.randint(1, 30))
                status = "Failed"
                error_category = random.choice(self.error_templates)
                error_message = random.choice(error_category["messages"])
            else:
                end_time = start_time + timedelta(minutes=random.randint(5, 60))
                status = "Succeeded"
                error_message = None
            
            run = {
                "runId": run_id,
                "pipelineName": pipeline_name,
                "status": status,
                "runStart": start_time.isoformat() + "Z",
                "runEnd": end_time.isoformat() + "Z",
                "message": error_message
            }
            
            runs.append(run)
        
        return runs
    
    def generate_mock_genai_responses(self) -> Dict[str, Dict[str, Any]]:
        """Generate mock GenAI analysis responses for different error types"""
        
        return {
            "transient_network": {
                "error_type": "transient",
                "severity": "medium",
                "should_retry": True,
                "retry_delay_minutes": 10,
                "confidence_score": 85,
                "analysis_summary": "Network timeout detected. This is a transient connectivity issue that typically resolves on retry.",
                "root_cause": "Temporary network connectivity or service availability issue",
                "recommended_actions": [
                    "Retry the pipeline execution",
                    "Monitor network connectivity",
                    "Check Azure service health status",
                    "Consider increasing timeout values if pattern persists"
                ],
                "manual_intervention_required": False
            },
            "data_quality_schema": {
                "error_type": "data_quality",
                "severity": "high", 
                "should_retry": False,
                "retry_delay_minutes": 0,
                "confidence_score": 92,
                "analysis_summary": "Schema validation failure detected. Source data structure has changed and requires manual review.",
                "root_cause": "Data schema mismatch or missing required columns",
                "recommended_actions": [
                    "Review source data schema changes",
                    "Update pipeline to handle new schema",
                    "Contact data provider about schema changes",
                    "Implement schema evolution handling",
                    "Add data validation steps"
                ],
                "manual_intervention_required": True
            },
            "configuration_access": {
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
                    "Validate storage account access rights",
                    "Update authentication settings"
                ],
                "manual_intervention_required": True
            },
            "unknown_error": {
                "error_type": "unknown",
                "severity": "medium",
                "should_retry": True,
                "retry_delay_minutes": 15,
                "confidence_score": 65,
                "analysis_summary": "Unable to classify error definitively. Recommending cautious retry with monitoring.",
                "root_cause": "Error pattern not recognized in training data",
                "recommended_actions": [
                    "Attempt one retry with careful monitoring",
                    "Review detailed activity logs",
                    "Check for similar patterns in history",
                    "Escalate to support if retry fails",
                    "Consider adding to error pattern training"
                ],
                "manual_intervention_required": False
            }
        }
    
    def save_mock_data_to_file(self, filename: str = "mock_data.json"):
        """Save mock data to JSON file for testing"""
        
        mock_data = {
            "pipeline_runs": self.generate_pipeline_runs(20, 0.4),
            "genai_responses": self.generate_mock_genai_responses(),
            "generated_at": datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(mock_data, f, indent=2)
        
        print(f"Mock data saved to {filename}")
        return mock_data

def create_test_scenario():
    """Create a specific test scenario with various failure types"""
    
    generator = MockDataGenerator()
    
    # Create specific test cases
    test_scenarios = [
        {
            "runId": "test-transient-001",
            "pipelineName": "DataProcessingPipeline",
            "status": "Failed",
            "runStart": (datetime.now() - timedelta(minutes=10)).isoformat() + "Z",
            "runEnd": (datetime.now() - timedelta(minutes=5)).isoformat() + "Z",
            "message": "Activity 'CopyData' failed: The source database connection failed due to timeout. Error code: 40001"
        },
        {
            "runId": "test-data-quality-001", 
            "pipelineName": "ETLPipeline",
            "status": "Failed",
            "runStart": (datetime.now() - timedelta(minutes=20)).isoformat() + "Z",
            "runEnd": (datetime.now() - timedelta(minutes=15)).isoformat() + "Z",
            "message": "Validation failed: Missing required column 'customer_id' in source file. This is likely a data quality issue."
        },
        {
            "runId": "test-config-001",
            "pipelineName": "CustomerDataPipeline", 
            "status": "Failed",
            "runStart": (datetime.now() - timedelta(minutes=30)).isoformat() + "Z",
            "runEnd": (datetime.now() - timedelta(minutes=25)).isoformat() + "Z",
            "message": "Access denied: Insufficient permissions to read from storage account 'customerdata'"
        }
    ]
    
    return test_scenarios

if __name__ == "__main__":
    generator = MockDataGenerator()
    
    # Generate and save mock data
    mock_data = generator.save_mock_data_to_file("mock_data.json")
    
    # Create test scenarios
    test_data = create_test_scenario()
    with open("test_scenarios.json", 'w') as f:
        json.dump(test_data, f, indent=2)
    
    print(f"Generated {len(mock_data['pipeline_runs'])} mock pipeline runs")
    print(f"Generated {len(test_data)} test scenarios")
    print("Files created: mock_data.json, test_scenarios.json")
