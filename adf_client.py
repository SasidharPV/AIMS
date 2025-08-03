"""
Azure Data Factory REST API Client
"""
import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from azure.identity import ClientSecretCredential
from config import config
from database import PipelineRun, db_manager

class ADFClient:
    """Azure Data Factory REST API client"""
    
    def __init__(self):
        self.config = config.azure
        self.base_url = f"https://management.azure.com/subscriptions/{self.config.subscription_id}/resourceGroups/{self.config.resource_group}/providers/Microsoft.DataFactory/factories/{self.config.data_factory_name}"
        self.credential = None
        self.access_token = None
        self._initialize_auth()
    
    def _initialize_auth(self):
        """Initialize Azure authentication"""
        try:
            if all([self.config.tenant_id, self.config.client_id, self.config.client_secret]):
                self.credential = ClientSecretCredential(
                    tenant_id=self.config.tenant_id,
                    client_id=self.config.client_id,
                    client_secret=self.config.client_secret
                )
                self._get_access_token()
            else:
                print("Warning: Azure authentication not configured. Using mock mode.")
        except Exception as e:
            print(f"Error initializing Azure auth: {e}")
            print("Falling back to mock mode")
    
    def _get_access_token(self):
        """Get access token for Azure API"""
        try:
            if self.credential:
                token = self.credential.get_token("https://management.azure.com/.default")
                self.access_token = token.token
        except Exception as e:
            print(f"Error getting access token: {e}")
    
    def _make_request(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Optional[Dict]:
        """Make authenticated request to ADF API"""
        if not self.access_token:
            print("No access token available, using mock data")
            return self._get_mock_data(endpoint, method)
        
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.base_url}{endpoint}"
            
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return self._get_mock_data(endpoint, method)
    
    def _get_mock_data(self, endpoint: str, method: str) -> Dict[str, Any]:
        """Generate mock data for testing"""
        if "pipelineruns" in endpoint and method == "GET":
            return {
                "value": [
                    {
                        "runId": "mock-run-001",
                        "pipelineName": "DataProcessingPipeline",
                        "status": "Failed",
                        "runStart": (datetime.now() - timedelta(minutes=30)).isoformat(),
                        "runEnd": (datetime.now() - timedelta(minutes=25)).isoformat(),
                        "message": "Activity 'CopyData' failed: The source database connection failed due to timeout. Error code: 40001"
                    },
                    {
                        "runId": "mock-run-002", 
                        "pipelineName": "ETLPipeline",
                        "status": "Succeeded",
                        "runStart": (datetime.now() - timedelta(hours=1)).isoformat(),
                        "runEnd": (datetime.now() - timedelta(minutes=50)).isoformat(),
                        "message": None
                    },
                    {
                        "runId": "mock-run-003",
                        "pipelineName": "DataValidationPipeline", 
                        "status": "Failed",
                        "runStart": (datetime.now() - timedelta(minutes=15)).isoformat(),
                        "runEnd": (datetime.now() - timedelta(minutes=10)).isoformat(),
                        "message": "Validation failed: Missing required column 'customer_id' in source file. This is likely a data quality issue."
                    }
                ]
            }
        elif "pipelineruns" in endpoint and method == "POST":
            return {"status": "Accepted", "message": "Pipeline rerun initiated"}
        
        return {"value": []}
    
    def get_pipeline_runs(self, hours_back: int = 24) -> List[Dict[str, Any]]:
        """Get pipeline runs from the last N hours"""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours_back)
        
        # Format dates for API
        start_str = start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        end_str = end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        
        endpoint = f"/pipelineruns?api-version=2018-06-01&lastUpdatedAfter={start_str}&lastUpdatedBefore={end_str}"
        
        response = self._make_request(endpoint)
        return response.get("value", []) if response else []
    
    def get_pipeline_run_details(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific pipeline run"""
        endpoint = f"/pipelineruns/{run_id}?api-version=2018-06-01"
        return self._make_request(endpoint)
    
    def rerun_pipeline(self, pipeline_name: str, run_id: str = None) -> bool:
        """Rerun a pipeline"""
        try:
            if run_id:
                # Rerun from failed run
                endpoint = f"/pipelineruns/{run_id}/rerun?api-version=2018-06-01"
                response = self._make_request(endpoint, method="POST")
            else:
                # Start new run
                endpoint = f"/pipelines/{pipeline_name}/createRun?api-version=2018-06-01"
                response = self._make_request(endpoint, method="POST", data={})
            
            return response is not None and ("Accepted" in str(response.get("status", "")) or "runId" in response)
            
        except Exception as e:
            print(f"Error rerunning pipeline: {e}")
            return False
    
    def get_pipeline_activities(self, run_id: str) -> List[Dict[str, Any]]:
        """Get activity runs for a pipeline run"""
        endpoint = f"/pipelineruns/{run_id}/activityruns?api-version=2018-06-01"
        response = self._make_request(endpoint)
        return response.get("value", []) if response else []

def get_adf_pipeline_status() -> List[PipelineRun]:
    """Main function to get ADF pipeline status and convert to PipelineRun objects"""
    client = ADFClient()
    
    try:
        # Get pipeline runs from last 2 hours
        runs_data = client.get_pipeline_runs(hours_back=2)
        
        pipeline_runs = []
        for run_data in runs_data:
            try:
                pipeline_run = PipelineRun(
                    run_id=run_data.get("runId", ""),
                    pipeline_name=run_data.get("pipelineName", ""),
                    status=run_data.get("status", ""),
                    start_time=datetime.fromisoformat(run_data.get("runStart", "").replace("Z", "+00:00")),
                    end_time=datetime.fromisoformat(run_data.get("runEnd", "").replace("Z", "+00:00")) if run_data.get("runEnd") else None,
                    error_message=run_data.get("message"),
                    factory_name=config.azure.data_factory_name
                )
                
                # Store in database
                db_manager.insert_pipeline_run(pipeline_run)
                pipeline_runs.append(pipeline_run)
                
            except Exception as e:
                print(f"Error processing pipeline run data: {e}")
                continue
        
        return pipeline_runs
        
    except Exception as e:
        print(f"Error getting pipeline status: {e}")
        return []

def rerun_pipeline(pipeline_name: str, run_id: str = None) -> bool:
    """Rerun a specific pipeline"""
    client = ADFClient()
    return client.rerun_pipeline(pipeline_name, run_id)
