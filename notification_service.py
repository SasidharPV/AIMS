"""
Notification Service for ADF Monitoring System
"""
import smtplib
import requests
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any, Optional
from config import config

class NotificationService:
    """Handles notifications via console, Teams, and email"""
    
    def __init__(self):
        self.config = config.notification
    
    def send_alert(self, alert_type: str, pipeline_name: str, message: str, details: Optional[Dict[str, Any]] = None):
        """Send alert via all configured channels"""
        
        alert_data = {
            "timestamp": datetime.now().isoformat(),
            "type": alert_type,
            "pipeline": pipeline_name,
            "message": message,
            "details": details or {}
        }
        
        # Always send to console
        self._send_console_alert(alert_data)
        
        # Send to Teams if configured
        if self.config.teams_webhook_url:
            self._send_teams_alert(alert_data)
        
        # Send email if configured
        if all([self.config.email_smtp_server, self.config.email_from, self.config.email_to]):
            self._send_email_alert(alert_data)
    
    def _send_console_alert(self, alert_data: Dict[str, Any]):
        """Send alert to console"""
        print("\n" + "="*80)
        print(f"🚨 ADF ALERT: {alert_data['type'].upper()}")
        print("="*80)
        print(f"⏰ Time: {alert_data['timestamp']}")
        print(f"📊 Pipeline: {alert_data['pipeline']}")
        print(f"💬 Message: {alert_data['message']}")
        
        if alert_data['details']:
            print("\n📋 Details:")
            for key, value in alert_data['details'].items():
                if isinstance(value, dict):
                    print(f"  {key}:")
                    for sub_key, sub_value in value.items():
                        print(f"    {sub_key}: {sub_value}")
                else:
                    print(f"  {key}: {value}")
        
        print("="*80 + "\n")
    
    def _send_teams_alert(self, alert_data: Dict[str, Any]):
        """Send alert to Microsoft Teams"""
        try:
            # Determine alert color
            color_map = {
                "failure": "FF0000",  # Red
                "retry": "FFA500",    # Orange  
                "success": "00FF00",  # Green
                "warning": "FFFF00"   # Yellow
            }
            
            color = color_map.get(alert_data['type'], "0078D4")  # Default blue
            
            # Create Teams message
            teams_message = {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "themeColor": color,
                "summary": f"ADF Alert: {alert_data['pipeline']}",
                "sections": [
                    {
                        "activityTitle": f"🚨 ADF {alert_data['type'].title()} Alert",
                        "activitySubtitle": alert_data['pipeline'],
                        "facts": [
                            {"name": "Time", "value": alert_data['timestamp']},
                            {"name": "Pipeline", "value": alert_data['pipeline']},
                            {"name": "Message", "value": alert_data['message']}
                        ]
                    }
                ]
            }
            
            # Add details if available
            if alert_data['details']:
                detail_facts = []
                for key, value in alert_data['details'].items():
                    if not isinstance(value, dict):
                        detail_facts.append({"name": key, "value": str(value)})
                
                if detail_facts:
                    teams_message['sections'].append({
                        "activityTitle": "Additional Details",
                        "facts": detail_facts
                    })
            
            # Send to Teams
            response = requests.post(
                self.config.teams_webhook_url,
                json=teams_message,
                timeout=30
            )
            response.raise_for_status()
            print(f"✅ Teams notification sent successfully")
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to send Teams notification: {e}")
        except Exception as e:
            print(f"❌ Error sending Teams notification: {e}")
    
    def _send_email_alert(self, alert_data: Dict[str, Any]):
        """Send alert via email"""
        try:
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.config.email_from
            msg['To'] = self.config.email_to
            msg['Subject'] = f"ADF Alert: {alert_data['type'].title()} - {alert_data['pipeline']}"
            
            # Create email body
            body = f"""
ADF Monitoring Alert

Type: {alert_data['type'].title()}
Pipeline: {alert_data['pipeline']}
Time: {alert_data['timestamp']}

Message:
{alert_data['message']}
"""
            
            if alert_data['details']:
                body += "\n\nDetails:\n"
                for key, value in alert_data['details'].items():
                    if isinstance(value, dict):
                        body += f"\n{key}:\n"
                        for sub_key, sub_value in value.items():
                            body += f"  {sub_key}: {sub_value}\n"
                    else:
                        body += f"{key}: {value}\n"
            
            body += "\n\n---\nGenerated by ADF Monitoring & Automation System"
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.config.email_smtp_server, self.config.email_smtp_port) as server:
                server.starttls()
                if self.config.email_password:
                    server.login(self.config.email_from, self.config.email_password)
                server.send_message(msg)
            
            print(f"✅ Email notification sent successfully")
            
        except smtplib.SMTPException as e:
            print(f"❌ Failed to send email notification: {e}")
        except Exception as e:
            print(f"❌ Error sending email notification: {e}")
    
    def send_failure_alert(self, pipeline_name: str, run_id: str, error_message: str, analysis: Optional[Dict] = None):
        """Send pipeline failure alert"""
        details = {
            "run_id": run_id,
            "error_message": error_message[:500] + "..." if len(error_message) > 500 else error_message
        }
        
        if analysis:
            details.update({
                "error_type": analysis.get("error_type", "unknown"),
                "severity": analysis.get("severity", "unknown"),
                "ai_recommendation": analysis.get("analysis_summary", "No analysis available")
            })
        
        self.send_alert(
            alert_type="failure",
            pipeline_name=pipeline_name,
            message=f"Pipeline {pipeline_name} failed",
            details=details
        )
    
    def send_retry_alert(self, pipeline_name: str, run_id: str, retry_reason: str):
        """Send pipeline retry alert"""
        details = {
            "run_id": run_id,
            "retry_reason": retry_reason
        }
        
        self.send_alert(
            alert_type="retry", 
            pipeline_name=pipeline_name,
            message=f"Auto-retrying pipeline {pipeline_name}",
            details=details
        )
    
    def send_success_alert(self, pipeline_name: str, run_id: str, action: str):
        """Send success alert"""
        details = {
            "run_id": run_id,
            "action": action
        }
        
        self.send_alert(
            alert_type="success",
            pipeline_name=pipeline_name, 
            message=f"Pipeline {pipeline_name} {action} successful",
            details=details
        )
    
    def send_manual_intervention_alert(self, pipeline_name: str, run_id: str, reason: str, recommended_actions: list):
        """Send manual intervention required alert"""
        details = {
            "run_id": run_id,
            "reason": reason,
            "recommended_actions": recommended_actions
        }
        
        self.send_alert(
            alert_type="warning",
            pipeline_name=pipeline_name,
            message=f"Manual intervention required for pipeline {pipeline_name}",
            details=details
        )

# Global notification service instance
notification_service = NotificationService()
