"""
GenAI Analyzer for ADF Pipeline Failures
"""
import openai
import json
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from config import config
from database import MonitoringAction, db_manager
import uuid

class GenAIAnalyzer:
    """GenAI analyzer for pipeline failure analysis"""
    
    def __init__(self):
        self.config = config.openai
        if self.config.api_key:
            openai.api_key = self.config.api_key
        else:
            print("Warning: OpenAI API key not configured. Using mock analysis.")
    
    def analyze_failure_with_genai(self, pipeline_name: str, error_message: str, run_id: str) -> Dict[str, Any]:
        """
        Analyze pipeline failure using GenAI
        Returns analysis with recommendation
        """
        if not self.config.api_key:
            return self._get_mock_analysis(error_message)
        
        try:
            # Get historical context
            retry_history = db_manager.get_retry_history(pipeline_name)
            
            # Prepare prompt
            prompt = self._create_analysis_prompt(pipeline_name, error_message, retry_history)
            
            # Call OpenAI
            response = openai.ChatCompletion.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "You are an expert Azure Data Factory DevOps engineer analyzing pipeline failures."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            analysis_text = response.choices[0].message.content
            return self._parse_analysis_response(analysis_text, run_id)
            
        except Exception as e:
            print(f"Error in GenAI analysis: {e}")
            return self._get_mock_analysis(error_message)
    
    def _create_analysis_prompt(self, pipeline_name: str, error_message: str, retry_history: list) -> str:
        """Create analysis prompt for GenAI"""
        
        retry_context = ""
        if retry_history:
            retry_context = f"""
Recent retry history for {pipeline_name}:
{json.dumps(retry_history[-5:], indent=2, default=str)}
"""
        
        prompt = f"""
Analyze this Azure Data Factory pipeline failure and provide recommendations:

Pipeline: {pipeline_name}
Error Message: {error_message}

{retry_context}

Please analyze this failure and respond with a JSON object containing:
{{
    "error_type": "transient|persistent|data_quality|configuration|unknown",
    "severity": "low|medium|high|critical",
    "should_retry": true|false,
    "retry_delay_minutes": <number>,
    "confidence_score": <0-100>,
    "analysis_summary": "<brief explanation>",
    "root_cause": "<likely root cause>",
    "recommended_actions": ["<action1>", "<action2>"],
    "manual_intervention_required": true|false
}}

Consider:
- Is this a transient network/timeout issue that often resolves on retry?
- Is this a data quality issue requiring manual intervention?
- Is this a configuration or permissions issue?
- How many recent retries have been attempted?
- What is the pattern of failures for this pipeline?

Focus on actionable recommendations and accurate classification.
"""
        return prompt
    
    def _parse_analysis_response(self, analysis_text: str, run_id: str) -> Dict[str, Any]:
        """Parse GenAI response into structured format"""
        try:
            # Try to extract JSON from response
            json_start = analysis_text.find('{')
            json_end = analysis_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = analysis_text[json_start:json_end]
                parsed = json.loads(json_str)
                
                # Validate required fields
                required_fields = ['error_type', 'should_retry', 'confidence_score', 'analysis_summary']
                if all(field in parsed for field in required_fields):
                    return {
                        "success": True,
                        "analysis": parsed,
                        "raw_response": analysis_text,
                        "run_id": run_id
                    }
            
            # If parsing fails, create structured response from text
            return self._create_fallback_analysis(analysis_text, run_id)
            
        except json.JSONDecodeError:
            return self._create_fallback_analysis(analysis_text, run_id)
    
    def _create_fallback_analysis(self, analysis_text: str, run_id: str) -> Dict[str, Any]:
        """Create fallback analysis when JSON parsing fails"""
        
        # Simple keyword-based analysis
        should_retry = any(keyword in analysis_text.lower() for keyword in [
            'retry', 'transient', 'temporary', 'timeout', 'network'
        ])
        
        error_type = "unknown"
        if any(keyword in analysis_text.lower() for keyword in ['timeout', 'network', 'connection']):
            error_type = "transient"
        elif any(keyword in analysis_text.lower() for keyword in ['data', 'column', 'validation']):
            error_type = "data_quality"
        elif any(keyword in analysis_text.lower() for keyword in ['permission', 'access', 'config']):
            error_type = "configuration"
        
        return {
            "success": True,
            "analysis": {
                "error_type": error_type,
                "severity": "medium",
                "should_retry": should_retry,
                "retry_delay_minutes": 10 if should_retry else 0,
                "confidence_score": 60,
                "analysis_summary": analysis_text[:200] + "..." if len(analysis_text) > 200 else analysis_text,
                "root_cause": "Analysis based on keyword matching",
                "recommended_actions": ["Review detailed logs", "Contact support if issue persists"],
                "manual_intervention_required": not should_retry
            },
            "raw_response": analysis_text,
            "run_id": run_id
        }
    
    def _get_mock_analysis(self, error_message: str) -> Dict[str, Any]:
        """Generate mock analysis for testing"""
        
        # Simple rule-based mock analysis
        error_lower = error_message.lower()
        
        if any(keyword in error_lower for keyword in ['timeout', 'connection', 'network']):
            return {
                "success": True,
                "analysis": {
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
                },
                "raw_response": "Mock analysis: Transient network error",
                "run_id": "mock"
            }
        elif any(keyword in error_lower for keyword in ['column', 'data', 'validation', 'schema']):
            return {
                "success": True,
                "analysis": {
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
                },
                "raw_response": "Mock analysis: Data quality issue",
                "run_id": "mock"
            }
        else:
            return {
                "success": True,
                "analysis": {
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
                },
                "raw_response": "Mock analysis: Unknown error",
                "run_id": "mock"
            }

def should_rerun_pipeline(analysis_result: Dict[str, Any], pipeline_name: str) -> Tuple[bool, str]:
    """
    Determine if pipeline should be rerun based on GenAI analysis
    Returns (should_retry, reason)
    """
    
    if not analysis_result.get("success", False):
        return False, "Analysis failed"
    
    analysis = analysis_result.get("analysis", {})
    
    # Check confidence score
    confidence = analysis.get("confidence_score", 0)
    if confidence < 50:
        return False, f"Low confidence in analysis ({confidence}%)"
    
    # Check explicit recommendation
    should_retry = analysis.get("should_retry", False)
    if not should_retry:
        return False, f"AI recommendation: {analysis.get('analysis_summary', 'No retry recommended')}"
    
    # Check retry history to prevent infinite loops
    recent_retries = db_manager.get_retry_history(pipeline_name, hours=24)
    if len(recent_retries) >= config.monitoring.max_retry_attempts:
        return False, f"Maximum retry attempts ({config.monitoring.max_retry_attempts}) reached in last 24 hours"
    
    # Check error type
    error_type = analysis.get("error_type", "unknown")
    if error_type in ["data_quality", "configuration"]:
        return False, f"Error type '{error_type}' requires manual intervention"
    
    # All checks passed
    return True, f"AI analysis suggests retry for {error_type} error (confidence: {confidence}%)"

def log_decision_and_action(run_id: str, analysis_result: Dict[str, Any], action_taken: str, success: bool) -> str:
    """Log the decision and action taken"""
    
    action_id = str(uuid.uuid4())
    analysis = analysis_result.get("analysis", {})
    
    monitoring_action = MonitoringAction(
        action_id=action_id,
        run_id=run_id,
        action_type=action_taken,
        ai_analysis=json.dumps(analysis),
        decision_reason=analysis.get("analysis_summary", "No analysis available"),
        action_taken=success,
        timestamp=datetime.now()
    )
    
    db_manager.insert_monitoring_action(monitoring_action)
    
    # Update error pattern success rate
    error_type = analysis.get("error_type", "unknown")
    if error_type != "unknown":
        db_manager.update_error_pattern_success_rate(error_type, success)
    
    return action_id
