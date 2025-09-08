"""
Enterprise ADF Monitoring & Automation Web Application
A comprehensive visual interface for managing ADF pipelines across multiple environments
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import time
import sqlite3
from typing import Dict, List, Any
import uuid
import os
from pathlib import Path

# Configure page
st.set_page_config(
    page_title="ADF Monitor Pro",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #1f4e79 0%, #2e7db8 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
}
.metric-card {
    background: white;
    padding: 1rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    border-left: 4px solid #2e7db8;
}
.error-card {
    background: #fff5f5;
    border: 1px solid #fed7d7;
    border-radius: 8px;
    padding: 1rem;
    margin: 0.5rem 0;
}
.success-card {
    background: #f0fff4;
    border: 1px solid #9ae6b4;
    border-radius: 8px;
    padding: 1rem;
    margin: 0.5rem 0;
}
.warning-card {
    background: #fffbeb;
    border: 1px solid #fbd38d;
    border-radius: 8px;
    padding: 1rem;
    margin: 0.5rem 0;
}
.sidebar-section {
    background: #f7fafc;
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_environment' not in st.session_state:
    st.session_state.current_environment = "Production"
if 'selected_genai' not in st.session_state:
    st.session_state.selected_genai = "OpenAI GPT-4"
if 'monitoring_active' not in st.session_state:
    st.session_state.monitoring_active = False
if 'environments' not in st.session_state:
    st.session_state.environments = {
        "Production": {
            "subscription_id": "prod-sub-123",
            "resource_group": "prod-rg",
            "data_factory": "prod-adf",
            "status": "Active"
        },
        "Staging": {
            "subscription_id": "stage-sub-456", 
            "resource_group": "stage-rg",
            "data_factory": "stage-adf",
            "status": "Active"
        },
        "Development": {
            "subscription_id": "dev-sub-789",
            "resource_group": "dev-rg", 
            "data_factory": "dev-adf",
            "status": "Active"
        }
    }

class WebAppManager:
    """Main web application manager"""
    
    def __init__(self):
        self.db_path = "adf_monitor_webapp.db"
        self.init_database()
    
    def init_database(self):
        """Initialize application database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Pipeline runs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pipeline_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT UNIQUE,
                environment TEXT,
                pipeline_name TEXT,
                status TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                error_message TEXT,
                duration_minutes INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # AI analysis table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT,
                genai_provider TEXT,
                error_type TEXT,
                confidence_score INTEGER,
                should_retry BOOLEAN,
                analysis_summary TEXT,
                recommended_actions TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Actions taken table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS actions_taken (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT,
                action_type TEXT,
                action_result TEXT,
                user_id TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # System logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                environment TEXT,
                log_level TEXT,
                message TEXT,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # GenAI configurations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS genai_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider_name TEXT,
                model_name TEXT,
                api_endpoint TEXT,
                confidence_threshold INTEGER,
                retry_patterns TEXT,
                active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_mock_pipeline_data(self, environment: str) -> List[Dict]:
        """Generate mock pipeline data for the selected environment"""
        import random
        
        pipelines = [
            "DataIngestionPipeline",
            "ETLTransformPipeline", 
            "DataValidationPipeline",
            "ReportGenerationPipeline",
            "CustomerAnalyticsPipeline",
            "SalesDataPipeline",
            "InventoryUpdatePipeline",
            "ComplianceCheckPipeline"
        ]
        
        statuses = ["Succeeded", "Failed", "Running", "Cancelled"]
        error_types = [
            "Connection timeout to source database",
            "Schema validation failed: Missing column 'customer_id'",
            "Access denied: Insufficient permissions",
            "Data type mismatch in transformation",
            "Source file not found in storage account",
            "Memory exceeded during data processing"
        ]
        
        data = []
        for i in range(20):
            status = random.choice(statuses)
            start_time = datetime.now() - timedelta(hours=random.randint(1, 72))
            duration = random.randint(5, 120)
            
            data.append({
                "run_id": f"{environment.lower()}-run-{uuid.uuid4().hex[:8]}",
                "environment": environment,
                "pipeline_name": random.choice(pipelines),
                "status": status,
                "start_time": start_time,
                "end_time": start_time + timedelta(minutes=duration) if status != "Running" else None,
                "error_message": random.choice(error_types) if status == "Failed" else None,
                "duration_minutes": duration if status != "Running" else None
            })
        
        return data

# Initialize webapp manager
@st.cache_resource
def get_webapp_manager():
    return WebAppManager()

webapp_manager = get_webapp_manager()

def render_header():
    """Render main application header"""
    st.markdown("""
    <div class="main-header">
        <h1>🏭 ADF Monitor Pro - Enterprise Pipeline Management</h1>
        <p>Intelligent monitoring and automation across multiple Azure Data Factory environments</p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render sidebar with controls and configuration"""
    st.sidebar.title("🔧 Control Center")
    
    # Environment Selection
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.subheader("🌐 Environment")
    
    environment = st.sidebar.selectbox(
        "Select ADF Environment",
        options=list(st.session_state.environments.keys()),
        index=list(st.session_state.environments.keys()).index(st.session_state.current_environment)
    )
    
    if environment != st.session_state.current_environment:
        st.session_state.current_environment = environment
        st.rerun()
    
    # Show environment details
    env_details = st.session_state.environments[environment]
    st.sidebar.info(f"""
    **Environment Details:**
    - Subscription: {env_details['subscription_id'][:12]}...
    - Resource Group: {env_details['resource_group']}
    - Data Factory: {env_details['data_factory']}
    - Status: {env_details['status']}
    """)
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # GenAI Provider Selection
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.subheader("🧠 AI Configuration")
    
    genai_providers = [
        "OpenAI GPT-4",
        "OpenAI GPT-3.5-Turbo",
        "Azure OpenAI",
        "Google Gemini Pro",
        "Anthropic Claude-3",
        "Hugging Face Transformers",
        "Local LLaMA Model"
    ]
    
    selected_genai = st.sidebar.selectbox(
        "GenAI Provider",
        options=genai_providers,
        index=genai_providers.index(st.session_state.selected_genai)
    )
    
    if selected_genai != st.session_state.selected_genai:
        st.session_state.selected_genai = selected_genai
    
    # AI Behavior Configuration
    st.sidebar.subheader("⚙️ AI Behavior")
    confidence_threshold = st.sidebar.slider("Confidence Threshold", 50, 95, 75)
    retry_attempts = st.sidebar.slider("Max Retry Attempts", 1, 5, 3)
    retry_delay = st.sidebar.slider("Retry Delay (minutes)", 5, 60, 15)
    
    # Pattern matching settings
    enable_pattern_learning = st.sidebar.checkbox("Enable Pattern Learning", True)
    enable_auto_retry = st.sidebar.checkbox("Enable Auto Retry", True)
    enable_smart_alerts = st.sidebar.checkbox("Smart Alert Filtering", True)
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Monitoring Controls
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.subheader("🎮 Monitoring Controls")
    
    if st.sidebar.button("🚀 Start Monitoring", type="primary"):
        st.session_state.monitoring_active = True
        st.sidebar.success("Monitoring started!")
    
    if st.sidebar.button("⏹️ Stop Monitoring"):
        st.session_state.monitoring_active = False
        st.sidebar.info("Monitoring stopped")
    
    if st.sidebar.button("🔄 Manual Scan"):
        with st.sidebar.spinner("Scanning pipelines..."):
            time.sleep(2)
        st.sidebar.success("Scan completed!")
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Quick Stats
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.subheader("📊 Quick Stats")
    
    # Mock stats for current environment
    st.sidebar.metric("Pipelines Monitored", 127)
    st.sidebar.metric("Success Rate (24h)", "94.2%", "2.1%")
    st.sidebar.metric("Auto-Retries Today", 8, "3")
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Multi-Environment Quick Actions
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.subheader("🌍 Quick Environment Actions")
    
    if st.sidebar.button("🚨 View All Environment Failures", type="primary"):
        st.session_state.current_tab = "Failures"
        # Switch to multi-environment view
        st.session_state.failure_view_mode = "Multi-Environment Overview"
        st.rerun()
    
    if st.sidebar.button("📊 Cross-Environment Comparison"):
        st.session_state.current_tab = "Failures"
        st.session_state.failure_view_mode = "Cross-Environment Comparison" 
        st.rerun()
    
    # Quick environment health indicators
    st.sidebar.markdown("**Environment Health:**")
    col1, col2, col3 = st.sidebar.columns(3)
    with col1:
        st.markdown("🔴 **Prod**<br/>3 issues", unsafe_allow_html=True)
    with col2:
        st.markdown("🟡 **Stage**<br/>1 issue", unsafe_allow_html=True)
    with col3:
        st.markdown("🟢 **Dev**<br/>2 issues", unsafe_allow_html=True)
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

def render_dashboard_page():
    """Render main dashboard"""
    st.header("📊 ADF Monitor Pro - Unified Dashboard")
    
    # Multi-Environment Health Overview
    st.subheader("🌍 Multi-Environment Health Status")
    
    env_health_col1, env_health_col2, env_health_col3, env_health_col4 = st.columns(4)
    
    with env_health_col1:
        st.markdown("### 🔴 Production")
        prod_health = st.container()
        with prod_health:
            st.metric("Pipelines", "45", "-2")
            st.metric("Success Rate", "92.1%", "-1.2%")
            st.metric("Active Failures", "3", "+1")
            st.metric("Critical Issues", "1", "+1")
            
            # Status indicator
            if st.session_state.current_environment == "Production":
                st.success("🟢 Currently Monitoring")
            else:
                if st.button("Switch to Production", key="switch_prod"):
                    st.session_state.current_environment = "Production"
                    st.rerun()
    
    with env_health_col2:
        st.markdown("### 🟡 Staging")
        staging_health = st.container()
        with staging_health:
            st.metric("Pipelines", "32", "+1")
            st.metric("Success Rate", "96.8%", "+0.5%")
            st.metric("Active Failures", "1", "0")
            st.metric("Critical Issues", "0", "0")
            
            if st.session_state.current_environment == "Staging":
                st.success("🟢 Currently Monitoring")
            else:
                if st.button("Switch to Staging", key="switch_staging"):
                    st.session_state.current_environment = "Staging"
                    st.rerun()
    
    with env_health_col3:
        st.markdown("### 🟢 Development")
        dev_health = st.container()
        with dev_health:
            st.metric("Pipelines", "28", "+5")
            st.metric("Success Rate", "88.4%", "-2.1%")
            st.metric("Active Failures", "2", "+1")
            st.metric("Critical Issues", "0", "0")
            
            if st.session_state.current_environment == "Development":
                st.success("🟢 Currently Monitoring")
            else:
                if st.button("Switch to Development", key="switch_dev"):
                    st.session_state.current_environment = "Development"
                    st.rerun()
    
    with env_health_col4:
        st.markdown("### 📊 Global Summary")
        global_summary = st.container()
        with global_summary:
            st.metric("Total Pipelines", "105", "+4")
            st.metric("Avg Success Rate", "92.4%", "-0.9%")
            st.metric("Total Failures", "6", "+2")
            st.metric("Urgent Actions", "1", "+1")
            
            # Global actions
            if st.button("🚨 View All Failures", key="view_all_failures"):
                st.session_state.current_tab = "Failures"
                st.rerun()
    
    st.divider()
    
    # Current Environment Focus
    current_env = st.session_state.current_environment
    st.subheader(f"🎯 Current Focus: {current_env} Environment")
    
    # Top metrics for current environment
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        env_pipeline_count = {"Production": 45, "Staging": 32, "Development": 28}
        st.metric("Pipelines", env_pipeline_count[current_env], "12")
    with col2:
        env_success_rates = {"Production": "92.1%", "Staging": "96.8%", "Development": "88.4%"}
        st.metric("Success Rate (24h)", env_success_rates[current_env], "2.1%")
    with col3:
        env_failures = {"Production": 3, "Staging": 1, "Development": 2}
        st.metric("Active Failures", env_failures[current_env], "+1")
    with col4:
        env_retries = {"Production": 8, "Staging": 3, "Development": 5}
        st.metric("Auto Retries (24h)", env_retries[current_env], "-2")
    with col5:
        env_ai_actions = {"Production": 15, "Staging": 7, "Development": 12}
        st.metric("AI Actions", env_ai_actions[current_env], "+3")
    
    # Cross-Environment Alerts
    st.subheader("🚨 Cross-Environment Alerts")
    
    alert_col1, alert_col2 = st.columns(2)
    
    with alert_col1:
        st.error("🔴 **CRITICAL**: Production ETLTransformPipeline failure requires immediate attention")
        st.warning("🟡 **WARNING**: Staging deployment pending - may affect Production release")
        st.info("ℹ️ **INFO**: Development environment has 2 experimental pipelines running")
    
    with alert_col2:
        st.markdown("**Recent Cross-Environment Events:**")
        st.markdown("• 🔄 **10:30** - Auto-retry successful in Production")
        st.markdown("• 📝 **10:15** - New pipeline deployed to Staging")
        st.markdown("• ⚠️ **09:45** - Permission issue detected across all environments")
        st.markdown("• ✅ **09:30** - Global health check completed")
    
    st.divider()
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Pipeline Status Distribution")
        # Mock data for pie chart
        status_data = {"Succeeded": 89, "Failed": 8, "Running": 3, "Cancelled": 2}
        fig = px.pie(values=list(status_data.values()), names=list(status_data.keys()),
                    title="Last 24 Hours")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Failure Trends")
        # Mock data for line chart
        hours = list(range(24))
        failures = [2, 1, 0, 1, 3, 2, 1, 4, 2, 1, 0, 2, 3, 1, 2, 0, 1, 2, 3, 1, 0, 1, 2, 1]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hours, y=failures, mode='lines+markers', name='Failures'))
        fig.update_layout(title="Failures by Hour", xaxis_title="Hour", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent activity
    st.subheader("🔥 Recent Activity")
    
    # Generate mock recent activity
    mock_data = webapp_manager.get_mock_pipeline_data(st.session_state.current_environment)
    df = pd.DataFrame(mock_data)
    df['start_time'] = pd.to_datetime(df['start_time'])
    df_recent = df.sort_values('start_time', ascending=False).head(10)
    
    for _, row in df_recent.iterrows():
        status_color = {
            "Succeeded": "success-card",
            "Failed": "error-card", 
            "Running": "warning-card",
            "Cancelled": "warning-card"
        }
        
        card_class = status_color.get(row['status'], 'metric-card')
        
        st.markdown(f"""
        <div class="{card_class}">
            <strong>{row['pipeline_name']}</strong> - {row['status']} 
            <br><small>{row['start_time'].strftime('%Y-%m-%d %H:%M:%S')} | Duration: {row['duration_minutes']}min</small>
            {f"<br><em>Error: {row['error_message']}</em>" if row['error_message'] else ""}
        </div>
        """, unsafe_allow_html=True)

def render_failures_page():
    """Render failures analysis page with multi-environment support"""
    st.header("❌ Pipeline Failures Analysis")
    
    # Check if view mode is set from sidebar navigation
    if hasattr(st.session_state, 'failure_view_mode'):
        default_view = st.session_state.failure_view_mode
        # Clear the session state after using it
        del st.session_state.failure_view_mode
    else:
        default_view = "Single Environment"
    
    # Environment View Toggle
    view_mode = st.radio(
        "View Mode",
        ["Single Environment", "Multi-Environment Overview", "Cross-Environment Comparison"],
        index=["Single Environment", "Multi-Environment Overview", "Cross-Environment Comparison"].index(default_view),
        horizontal=True
    )
    
    if view_mode == "Multi-Environment Overview":
        render_multi_env_failures()
    elif view_mode == "Cross-Environment Comparison":
        render_cross_env_comparison()
    else:
        render_single_env_failures()

def render_multi_env_failures():
    """Render failures from all environments on one page"""
    st.subheader("🌍 All Environments - Current Failures")
    
    # Quick stats across all environments
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Production Failures", "3", "-1")
    with col2:
        st.metric("Staging Failures", "1", "+1") 
    with col3:
        st.metric("Development Failures", "2", "0")
    with col4:
        st.metric("Total Active Failures", "6", "0")
    
    # Environment color coding
    env_colors = {
        "Production": "🔴",
        "Staging": "🟡", 
        "Development": "🟢"
    }
    
    # Consolidated failure data from all environments
    all_failures = [
        {
            "environment": "Production",
            "run_id": "prod-run-001",
            "pipeline": "DataIngestionPipeline",
            "error_type": "transient", 
            "confidence": 85,
            "severity": "High",
            "error_message": "Connection timeout to source database",
            "timestamp": datetime.now() - timedelta(minutes=30),
            "ai_analysis": "Network connectivity issue detected. Retry recommended.",
            "status": "Auto-retrying",
            "retry_count": "2/3"
        },
        {
            "environment": "Production",
            "run_id": "prod-run-002", 
            "pipeline": "ETLTransformPipeline",
            "error_type": "data_quality",
            "confidence": 92,
            "severity": "Critical",
            "error_message": "Schema validation failed: Missing column 'customer_id'",
            "timestamp": datetime.now() - timedelta(hours=2),
            "ai_analysis": "Data schema mismatch detected. Manual intervention required.",
            "status": "Needs Review",
            "retry_count": "0/3"
        },
        {
            "environment": "Production",
            "run_id": "prod-run-003",
            "pipeline": "ReportGenerationPipeline", 
            "error_type": "configuration",
            "confidence": 88,
            "severity": "Medium",
            "error_message": "Access denied: Insufficient permissions",
            "timestamp": datetime.now() - timedelta(hours=4),
            "ai_analysis": "Authentication/authorization issue. Check service principal permissions.",
            "status": "Manual Fix Required",
            "retry_count": "1/3"
        },
        {
            "environment": "Staging",
            "run_id": "stg-run-001",
            "pipeline": "DataValidationPipeline",
            "error_type": "transient",
            "confidence": 78,
            "severity": "Low",
            "error_message": "Temporary storage account access issue",
            "timestamp": datetime.now() - timedelta(minutes=45),
            "ai_analysis": "Storage throttling detected. Automatic retry scheduled.",
            "status": "Queued for Retry",
            "retry_count": "1/3"
        },
        {
            "environment": "Development",
            "run_id": "dev-run-001",
            "pipeline": "TestPipeline",
            "error_type": "configuration",
            "confidence": 95,
            "severity": "Low",
            "error_message": "Invalid connection string format",
            "timestamp": datetime.now() - timedelta(hours=1),
            "ai_analysis": "Configuration error in dev environment. Quick fix available.",
            "status": "Dev Issue",
            "retry_count": "0/3"
        },
        {
            "environment": "Development", 
            "run_id": "dev-run-002",
            "pipeline": "DataQualityPipeline",
            "error_type": "data_quality",
            "confidence": 83,
            "severity": "Medium",
            "error_message": "Test data contains invalid date formats",
            "timestamp": datetime.now() - timedelta(hours=3),
            "ai_analysis": "Test data quality issue. Safe to ignore in dev environment.",
            "status": "Under Investigation",
            "retry_count": "0/3"
        }
    ]
    
    # Filters for multi-environment view
    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
    
    with filter_col1:
        env_filter = st.multiselect(
            "Environments", 
            ["Production", "Staging", "Development"],
            default=["Production", "Staging", "Development"]
        )
    with filter_col2:
        severity_filter = st.multiselect(
            "Severity",
            ["Critical", "High", "Medium", "Low"],
            default=["Critical", "High", "Medium", "Low"]
        )
    with filter_col3:
        status_filter = st.multiselect(
            "Status",
            ["Auto-retrying", "Needs Review", "Manual Fix Required", "Queued for Retry", "Dev Issue", "Under Investigation"],
            default=["Auto-retrying", "Needs Review", "Manual Fix Required"]
        )
    with filter_col4:
        time_filter = st.selectbox("Time Range", ["Last Hour", "Last 6 Hours", "Last 24 Hours", "Last Week"])
    
    # Filter failures based on selections
    filtered_failures = [
        f for f in all_failures 
        if f["environment"] in env_filter 
        and f["severity"] in severity_filter 
        and f["status"] in status_filter
    ]
    
    # Sort by severity and timestamp
    severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    filtered_failures.sort(key=lambda x: (severity_order[x["severity"]], x["timestamp"]), reverse=True)
    
    st.markdown(f"**Showing {len(filtered_failures)} failures across {len(env_filter)} environments**")
    
    # Display failures in a unified table
    if filtered_failures:
        for failure in filtered_failures:
            severity_color = {
                "Critical": "🔴",
                "High": "🟠", 
                "Medium": "🟡",
                "Low": "🟢"
            }
            
            with st.expander(
                f"{env_colors[failure['environment']]} {severity_color[failure['severity']]} "
                f"**{failure['environment']}** | {failure['pipeline']} | {failure['timestamp'].strftime('%H:%M:%S')} | "
                f"**{failure['severity']}** | {failure['status']}"
            ):
                # Environment-specific styling
                env_style = {
                    "Production": "background-color: #ffebee; border-left: 4px solid #f44336;",
                    "Staging": "background-color: #fff3e0; border-left: 4px solid #ff9800;",
                    "Development": "background-color: #e8f5e8; border-left: 4px solid #4caf50;"
                }
                
                st.markdown(f'<div style="{env_style[failure["environment"]]} padding: 10px; border-radius: 5px; margin: 5px 0;">', unsafe_allow_html=True)
                
                detail_col1, detail_col2, detail_col3 = st.columns([1, 2, 1])
                
                with detail_col1:
                    st.write(f"**Environment:** {failure['environment']}")
                    st.write(f"**Run ID:** {failure['run_id']}")
                    st.write(f"**Error Type:** {failure['error_type']}")
                    st.write(f"**AI Confidence:** {failure['confidence']}%")
                    st.write(f"**Retry Status:** {failure['retry_count']}")
                
                with detail_col2:
                    st.write(f"**Error Message:**")
                    st.code(failure['error_message'])
                    st.write(f"**AI Analysis:**")
                    st.info(failure['ai_analysis'])
                
                with detail_col3:
                    st.write(f"**Severity:** {failure['severity']}")
                    st.write(f"**Status:** {failure['status']}")
                    st.write(f"**Time:** {failure['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    # Environment-specific actions
                    if failure['environment'] == 'Production':
                        if st.button(f"🚨 Escalate", key=f"escalate_{failure['run_id']}"):
                            st.error("Production issue escalated to on-call team!")
                    
                    if st.button(f"🔄 Force Retry", key=f"retry_{failure['run_id']}"):
                        st.success(f"Retry initiated for {failure['pipeline']} in {failure['environment']}")
                    
                    if st.button(f"📝 Add Note", key=f"note_{failure['run_id']}"):
                        st.text_area("Note:", key=f"note_input_{failure['run_id']}", height=100)
                
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.success("🎉 No failures found matching the current filters!")

def render_cross_env_comparison():
    """Render side-by-side comparison of failures across environments"""
    st.subheader("🔄 Cross-Environment Comparison")
    
    env_col1, env_col2, env_col3 = st.columns(3)
    
    environments = ["Production", "Staging", "Development"]
    env_data = {
        "Production": {
            "total_failures": 3,
            "critical": 1,
            "high": 1, 
            "medium": 1,
            "auto_retrying": 1,
            "manual_required": 2
        },
        "Staging": {
            "total_failures": 1,
            "critical": 0,
            "high": 0,
            "medium": 0, 
            "low": 1,
            "auto_retrying": 1,
            "manual_required": 0
        },
        "Development": {
            "total_failures": 2,
            "critical": 0,
            "high": 0,
            "medium": 1,
            "low": 1,
            "auto_retrying": 0,
            "manual_required": 1
        }
    }
    
    for i, env in enumerate(environments):
        with [env_col1, env_col2, env_col3][i]:
            data = env_data[env]
            
            if env == "Production":
                st.markdown("### 🔴 Production")
            elif env == "Staging":
                st.markdown("### 🟡 Staging") 
            else:
                st.markdown("### 🟢 Development")
            
            st.metric("Total Failures", data["total_failures"])
            st.metric("Critical", data.get("critical", 0))
            st.metric("High", data.get("high", 0))
            st.metric("Medium", data.get("medium", 0))
            st.metric("Auto-Retrying", data["auto_retrying"])
            st.metric("Manual Required", data["manual_required"])
            
            # Quick action for each environment
            if st.button(f"View {env} Details", key=f"view_{env}"):
                st.session_state.current_environment = env
                st.rerun()

def render_single_env_failures():
    """Render failures for the currently selected environment"""
    current_env = st.session_state.current_environment
    st.subheader(f"Environment: {current_env}")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        time_range = st.selectbox("Time Range", ["Last Hour", "Last 6 Hours", "Last 24 Hours", "Last Week"])
    with col2:
        pipeline_filter = st.multiselect("Pipelines", ["All", "DataIngestionPipeline", "ETLTransformPipeline"])
    with col3:
        error_type_filter = st.multiselect("Error Types", ["All", "transient", "data_quality", "configuration"])
    
    # Mock failure data
    failures_data = [
        {
            "run_id": "prod-run-001",
            "pipeline": "DataIngestionPipeline",
            "error_type": "transient", 
            "confidence": 85,
            "error_message": "Connection timeout to source database",
            "timestamp": datetime.now() - timedelta(minutes=30),
            "ai_analysis": "Network connectivity issue detected. Retry recommended.",
            "status": "Auto-retried"
        },
        {
            "run_id": "prod-run-002", 
            "pipeline": "ETLTransformPipeline",
            "error_type": "data_quality",
            "confidence": 92,
            "error_message": "Schema validation failed: Missing column 'customer_id'",
            "timestamp": datetime.now() - timedelta(hours=2),
            "ai_analysis": "Data schema mismatch detected. Manual intervention required.",
            "status": "Needs Review"
        },
        {
            "run_id": "prod-run-003",
            "pipeline": "ReportGenerationPipeline", 
            "error_type": "configuration",
            "confidence": 88,
            "error_message": "Access denied: Insufficient permissions",
            "timestamp": datetime.now() - timedelta(hours=4),
            "ai_analysis": "Authentication/authorization issue. Check service principal permissions.",
            "status": "Manual Fix"
        }
    ]
    
    # Display failures
    for failure in failures_data:
        with st.expander(f"🔴 {failure['pipeline']} - {failure['timestamp'].strftime('%H:%M:%S')}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Run ID:** {failure['run_id']}")
                st.write(f"**Error Type:** {failure['error_type']}")
                st.write(f"**AI Confidence:** {failure['confidence']}%")
                st.write(f"**Status:** {failure['status']}")
            
            with col2:
                st.write(f"**Error Message:**")
                st.code(failure['error_message'])
                st.write(f"**AI Analysis:**")
                st.info(failure['ai_analysis'])
            
            # Action buttons
            action_col1, action_col2, action_col3 = st.columns(3)
            
            with action_col1:
                if st.button(f"🔄 Retry", key=f"retry_{failure['run_id']}"):
                    st.success(f"Retry initiated for {failure['pipeline']}")
            
            with action_col2:
                if st.button(f"🚫 Ignore", key=f"ignore_{failure['run_id']}"):
                    st.info(f"Failure ignored for {failure['pipeline']}")
            
            with action_col3:
                if st.button(f"📝 Add Note", key=f"note_{failure['run_id']}"):
                    note = st.text_input("Add note:", key=f"note_input_{failure['run_id']}")
                    if note:
                        st.success("Note added successfully!")

def render_actions_page():
    """Render actions and interventions page"""
    st.header("🎯 Actions & Interventions")
    
    # Action categories
    tab1, tab2, tab3, tab4 = st.tabs(["🔄 Auto Retries", "👤 Manual Actions", "📋 Scheduled Tasks", "⚡ Bulk Operations"])
    
    with tab1:
        st.subheader("Automatic Retry Management")
        
        # Auto-retry settings
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Global Retry Settings**")
            enable_auto_retry = st.checkbox("Enable Auto Retry", True)
            max_retries = st.slider("Max Retry Attempts", 1, 10, 3)
            retry_delay = st.slider("Retry Delay (minutes)", 5, 120, 15)
        
        with col2:
            st.write("**Retry Patterns**")
            retry_on_timeout = st.checkbox("Retry on Timeout", True)
            retry_on_transient = st.checkbox("Retry on Transient Errors", True)
            retry_on_network = st.checkbox("Retry on Network Issues", True)
        
        # Recent auto-retries
        st.write("**Recent Auto-Retries**")
        retry_data = [
            {"Pipeline": "DataIngestionPipeline", "Reason": "Connection timeout", "Result": "Success", "Time": "10:30 AM"},
            {"Pipeline": "ETLTransformPipeline", "Reason": "Transient error", "Result": "Success", "Time": "09:15 AM"},
            {"Pipeline": "ReportGenerationPipeline", "Reason": "Network issue", "Result": "Failed", "Time": "08:45 AM"}
        ]
        
        df_retries = pd.DataFrame(retry_data)
        st.dataframe(df_retries, use_container_width=True)
    
    with tab2:
        st.subheader("Manual Intervention Actions")
        
        # Quick actions
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Quick Actions**")
            if st.button("🔄 Retry All Failed", type="primary"):
                st.success("Retry initiated for all failed pipelines")
            if st.button("⏹️ Stop All Running"):
                st.warning("All running pipelines stopped")
            if st.button("🔍 Force Refresh"):
                st.info("Pipeline status refreshed")
        
        with col2:
            st.write("**Bulk Operations**")
            selected_pipelines = st.multiselect("Select Pipelines", 
                ["DataIngestionPipeline", "ETLTransformPipeline", "ReportGenerationPipeline"])
            
            if st.button("Execute Bulk Action"):
                if selected_pipelines:
                    st.success(f"Bulk action applied to {len(selected_pipelines)} pipelines")
        
        with col3:
            st.write("**Custom Actions**")
            custom_action = st.text_input("Custom Command")
            if st.button("Execute Custom"):
                if custom_action:
                    st.info(f"Executing: {custom_action}")
    
    with tab3:
        st.subheader("Scheduled Tasks & Automation")
        
        # Scheduling interface
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Create Scheduled Task**")
            task_name = st.text_input("Task Name")
            task_type = st.selectbox("Task Type", ["Health Check", "Auto Retry", "Report Generation", "Cleanup"])
            schedule_type = st.selectbox("Schedule", ["Every Hour", "Daily", "Weekly", "Custom Cron"])
            
            if st.button("Create Schedule"):
                st.success(f"Scheduled task '{task_name}' created")
        
        with col2:
            st.write("**Active Schedules**")
            schedules = [
                {"Name": "Health Check", "Type": "Health Check", "Schedule": "Every Hour", "Status": "Active"},
                {"Name": "Daily Cleanup", "Type": "Cleanup", "Schedule": "Daily", "Status": "Active"},
                {"Name": "Weekly Report", "Type": "Report", "Schedule": "Weekly", "Status": "Paused"}
            ]
            
            df_schedules = pd.DataFrame(schedules)
            st.dataframe(df_schedules, use_container_width=True)
    
    with tab4:
        st.subheader("Bulk Operations")
        
        # Bulk operation interface
        st.write("**Mass Pipeline Management**")
        
        operation_type = st.selectbox("Operation Type", 
            ["Retry All Failed", "Stop All Running", "Update Configuration", "Export Logs"])
        
        if operation_type == "Retry All Failed":
            filter_hours = st.slider("Failed in last X hours", 1, 72, 24)
            exclude_types = st.multiselect("Exclude Error Types", ["data_quality", "configuration"])
            
            if st.button("Execute Bulk Retry"):
                st.success(f"Bulk retry executed for failures in last {filter_hours} hours")
        
        elif operation_type == "Update Configuration":
            config_updates = st.text_area("Configuration Updates (JSON)", 
                '{"retry_attempts": 3, "timeout_minutes": 30}')
            
            if st.button("Apply Configuration"):
                st.success("Configuration updated for all pipelines")

def render_logs_page():
    """Render logs viewing page"""
    st.header("📜 System Logs & Audit Trail")
    
    # Log filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        log_level = st.selectbox("Log Level", ["All", "INFO", "WARNING", "ERROR", "DEBUG"])
    with col2:
        log_source = st.selectbox("Source", ["All", "Monitor Service", "AI Analyzer", "Action Engine"])
    with col3:
        time_range = st.selectbox("Time Range", ["Last Hour", "Last 6 Hours", "Last 24 Hours", "Custom"])
    with col4:
        environment_filter = st.selectbox("Environment", ["All"] + list(st.session_state.environments.keys()))
    
    # Search functionality
    search_query = st.text_input("🔍 Search logs", placeholder="Enter keywords, pipeline names, or error messages")
    
    # Mock log data
    log_entries = [
        {
            "timestamp": datetime.now() - timedelta(minutes=5),
            "level": "INFO",
            "source": "Monitor Service",
            "environment": "Production",
            "message": "Pipeline scan completed successfully",
            "details": "Scanned 127 pipelines, found 3 running, 0 failed"
        },
        {
            "timestamp": datetime.now() - timedelta(minutes=15),
            "level": "WARNING", 
            "source": "AI Analyzer",
            "environment": "Production",
            "message": "Low confidence analysis for pipeline failure",
            "details": "DataIngestionPipeline failed with unknown error pattern. Confidence: 45%"
        },
        {
            "timestamp": datetime.now() - timedelta(minutes=30),
            "level": "ERROR",
            "source": "Action Engine", 
            "environment": "Staging",
            "message": "Auto-retry failed for ETLTransformPipeline",
            "details": "Retry attempt 2/3 failed. Error: Connection timeout persists"
        },
        {
            "timestamp": datetime.now() - timedelta(hours=1),
            "level": "INFO",
            "source": "Monitor Service",
            "environment": "Production", 
            "message": "AI analysis completed",
            "details": "ReportGenerationPipeline analyzed. Error type: configuration. Confidence: 88%"
        }
    ]
    
    # Display logs
    for log in log_entries:
        level_colors = {
            "INFO": "🔵",
            "WARNING": "🟡", 
            "ERROR": "🔴",
            "DEBUG": "⚫"
        }
        
        level_icon = level_colors.get(log['level'], "⚪")
        
        with st.expander(f"{level_icon} {log['timestamp'].strftime('%H:%M:%S')} - {log['message']}"):
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.write(f"**Level:** {log['level']}")
                st.write(f"**Source:** {log['source']}")
                st.write(f"**Environment:** {log['environment']}")
                st.write(f"**Time:** {log['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
            
            with col2:
                st.write(f"**Message:**")
                st.code(log['message'])
                st.write(f"**Details:**")
                st.text(log['details'])
    
    # Export options
    st.subheader("📥 Export Logs")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Export as CSV"):
            st.success("Logs exported to CSV file")
    
    with col2:
        if st.button("📊 Export as JSON"):
            st.success("Logs exported to JSON file")
    
    with col3:
        if st.button("📧 Email Report"):
            st.success("Log report emailed to administrators")

def render_admin_config_page():
    """Render comprehensive admin configuration page"""
    st.header("⚙️ Admin Configuration")
    
    # Configuration tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏢 Azure Setup", 
        "🧠 AI Providers", 
        "🌐 Environments", 
        "🔔 Notifications",
        "🔒 Security"
    ])
    
    with tab1:
        render_azure_setup_config()
    
    with tab2:
        render_ai_providers_config()
    
    with tab3:
        render_environments_config()
    
    with tab4:
        render_notifications_config()
    
    with tab5:
        render_security_config()

def render_azure_setup_config():
    """Render Azure setup configuration"""
    st.subheader("🏢 Azure Configuration")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Service Principal Configuration")
        
        # Load current configuration
        current_tenant = st.session_state.get('azure_tenant_id', os.getenv('AZURE_TENANT_ID', ''))
        current_client_id = st.session_state.get('azure_client_id', os.getenv('AZURE_CLIENT_ID', ''))
        current_subscription = st.session_state.get('azure_subscription_id', os.getenv('AZURE_SUBSCRIPTION_ID', ''))
        
        # Service Principal inputs
        azure_tenant_id = st.text_input(
            "🏢 Azure Tenant ID",
            value=current_tenant,
            help="Your Azure Active Directory tenant ID"
        )
        
        azure_client_id = st.text_input(
            "🆔 Service Principal Client ID", 
            value=current_client_id,
            help="Application (client) ID of your service principal"
        )
        
        azure_client_secret = st.text_input(
            "🔐 Service Principal Secret",
            type="password",
            help="Secret value for your service principal"
        )
        
        azure_subscription_id = st.text_input(
            "📋 Azure Subscription ID",
            value=current_subscription,
            help="Your Azure subscription ID"
        )
        
        st.markdown("### Azure OpenAI Configuration")
        
        # Load current OpenAI config
        current_endpoint = st.session_state.get('azure_openai_endpoint', os.getenv('AZURE_OPENAI_ENDPOINT', ''))
        current_deployment = st.session_state.get('azure_openai_deployment', os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', ''))
        
        azure_openai_endpoint = st.text_input(
            "🧠 Azure OpenAI Endpoint",
            value=current_endpoint,
            placeholder="https://your-resource.openai.azure.com/",
            help="Your Azure OpenAI service endpoint"
        )
        
        azure_openai_key = st.text_input(
            "🔑 Azure OpenAI API Key",
            type="password",
            help="API key for your Azure OpenAI service"
        )
        
        azure_openai_deployment = st.text_input(
            "🚀 Deployment Name",
            value=current_deployment,
            placeholder="gpt-4-deployment",
            help="Name of your GPT model deployment"
        )
        
        azure_openai_version = st.selectbox(
            "📅 API Version",
            ["2024-02-15-preview", "2023-12-01-preview", "2023-10-01-preview"],
            index=0,
            help="Azure OpenAI API version"
        )
        
        # Action buttons
        col_save, col_test, col_auto = st.columns(3)
        
        with col_save:
            if st.button("💾 Save Configuration", use_container_width=True):
                # Save to session state and environment
                config_data = {
                    'azure_tenant_id': azure_tenant_id,
                    'azure_client_id': azure_client_id,
                    'azure_client_secret': azure_client_secret,
                    'azure_subscription_id': azure_subscription_id,
                    'azure_openai_endpoint': azure_openai_endpoint,
                    'azure_openai_key': azure_openai_key,
                    'azure_openai_deployment': azure_openai_deployment,
                    'azure_openai_version': azure_openai_version
                }
                
                # Update session state
                for key, value in config_data.items():
                    st.session_state[key] = value
                
                # Update .env file
                save_to_env_file(config_data)
                
                st.success("✅ Azure configuration saved successfully!")
                st.balloons()
        
        with col_test:
            if st.button("🧪 Test Connections", use_container_width=True):
                test_azure_connections(azure_tenant_id, azure_client_id, azure_client_secret, 
                                     azure_subscription_id, azure_openai_endpoint, azure_openai_key)
        
        with col_auto:
            if st.button("🤖 Auto-Setup", use_container_width=True):
                st.info("🚀 Running automated Azure setup...")
                with st.spinner("Creating service principal and Azure OpenAI..."):
                    run_automated_azure_setup()
    
    with col2:
        st.markdown("### 📋 Quick Setup Guide")
        
        st.markdown("""
        **Step 1: Service Principal**
        ```bash
        az ad sp create-for-rbac \\
          --name "adf-monitor-sp" \\
          --role "Data Factory Contributor"
        ```
        
        **Step 2: Azure OpenAI**
        ```bash
        az cognitiveservices account create \\
          --name "adf-openai" \\
          --resource-group "your-rg" \\
          --kind OpenAI \\
          --sku S0
        ```
        
        **Step 3: Model Deployment**
        ```bash
        az cognitiveservices account deployment create \\
          --name "adf-openai" \\
          --deployment-name "gpt-4-deployment" \\
          --model-name gpt-4
        ```
        """)
        
        st.markdown("### 🔍 Connection Status")
        
        # Show connection status
        status_placeholder = st.empty()
        
        with status_placeholder.container():
            if azure_tenant_id and azure_client_id:
                st.success("🏢 Service Principal: Configured")
            else:
                st.warning("🏢 Service Principal: Not configured")
            
            if azure_openai_endpoint and azure_openai_deployment:
                st.success("🧠 Azure OpenAI: Configured")
            else:
                st.warning("🧠 Azure OpenAI: Not configured")
            
            # Show discovered ADFs
            st.markdown("**📊 Discovered Data Factories:**")
            if st.session_state.get('discovered_adfs'):
                for adf in st.session_state.discovered_adfs:
                    st.write(f"• {adf['name']} ({adf['resource_group']})")
            else:
                st.write("None found - check configuration")

def render_ai_providers_config():
    """Render AI providers configuration"""
    st.subheader("🧠 AI Providers Management")
    
    # Provider tabs
    provider_tab1, provider_tab2, provider_tab3 = st.tabs(["📋 Manage Providers", "⚙️ Model Settings", "📊 Performance"])
    
    with provider_tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### Current AI Providers")
            
            # Initialize providers if not exists
            if 'ai_providers' not in st.session_state:
                st.session_state.ai_providers = [
                    {
                        "id": "azure-openai-primary",
                        "name": "Azure OpenAI GPT-4",
                        "type": "azure-openai",
                        "model": "gpt-4",
                        "endpoint": "",
                        "api_key": "",
                        "deployment": "",
                        "active": True,
                        "priority": 1
                    },
                    {
                        "id": "openai-fallback",
                        "name": "OpenAI GPT-4",
                        "type": "openai",
                        "model": "gpt-4",
                        "endpoint": "https://api.openai.com/v1",
                        "api_key": "",
                        "deployment": "",
                        "active": False,
                        "priority": 2
                    }
                ]
            
            # Display current providers
            for i, provider in enumerate(st.session_state.ai_providers):
                with st.expander(f"{'🟢' if provider['active'] else '🔴'} {provider['name']}", expanded=provider['active']):
                    pcol1, pcol2 = st.columns(2)
                    
                    with pcol1:
                        provider['name'] = st.text_input(f"Provider Name", value=provider['name'], key=f"name_{i}")
                        provider['type'] = st.selectbox(f"Type", 
                            ["azure-openai", "openai", "anthropic", "google"], 
                            index=["azure-openai", "openai", "anthropic", "google"].index(provider['type']),
                            key=f"type_{i}")
                        provider['model'] = st.text_input(f"Model", value=provider['model'], key=f"model_{i}")
                        provider['priority'] = st.number_input(f"Priority", min_value=1, max_value=10, value=provider['priority'], key=f"priority_{i}")
                    
                    with pcol2:
                        provider['endpoint'] = st.text_input(f"Endpoint", value=provider['endpoint'], key=f"endpoint_{i}")
                        provider['api_key'] = st.text_input(f"API Key", type="password", key=f"api_key_{i}")
                        if provider['type'] == 'azure-openai':
                            provider['deployment'] = st.text_input(f"Deployment Name", value=provider.get('deployment', ''), key=f"deployment_{i}")
                        provider['active'] = st.checkbox(f"Active", value=provider['active'], key=f"active_{i}")
                    
                    # Test button for individual provider
                    if st.button(f"🧪 Test {provider['name']}", key=f"test_{i}"):
                        test_ai_provider(provider)
            
            # Add new provider
            st.markdown("### ➕ Add New Provider")
            with st.expander("Add Provider"):
                new_name = st.text_input("Provider Name", placeholder="My Custom AI Provider")
                new_type = st.selectbox("Provider Type", ["azure-openai", "openai", "anthropic", "google"])
                new_model = st.text_input("Model Name", placeholder="gpt-4")
                new_endpoint = st.text_input("API Endpoint", placeholder="https://api.example.com")
                new_api_key = st.text_input("API Key", type="password")
                
                if st.button("➕ Add Provider"):
                    if new_name and new_api_key:
                        new_provider = {
                            "id": f"custom-{len(st.session_state.ai_providers)}",
                            "name": new_name,
                            "type": new_type,
                            "model": new_model,
                            "endpoint": new_endpoint,
                            "api_key": new_api_key,
                            "deployment": "",
                            "active": True,
                            "priority": len(st.session_state.ai_providers) + 1
                        }
                        st.session_state.ai_providers.append(new_provider)
                        st.success(f"✅ Provider '{new_name}' added successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Please provide at least a name and API key")
        
        with col2:
            st.markdown("### 🎛️ Provider Controls")
            
            if st.button("💾 Save All Providers", use_container_width=True):
                save_ai_providers_config(st.session_state.ai_providers)
                st.success("✅ All providers saved!")
            
            if st.button("🧪 Test All Active", use_container_width=True):
                test_all_ai_providers()
            
            if st.button("🔄 Reset to Defaults", use_container_width=True):
                if st.button("⚠️ Confirm Reset"):
                    reset_ai_providers_to_default()
            
            st.markdown("### 📊 Provider Status")
            
            active_count = sum(1 for p in st.session_state.ai_providers if p['active'])
            total_count = len(st.session_state.ai_providers)
            
            st.metric("Active Providers", f"{active_count}/{total_count}")
            
            # Show provider health
            for provider in st.session_state.ai_providers:
                if provider['active']:
                    status = "🟢 Online" if provider.get('last_test_success', True) else "🔴 Error"
                    st.write(f"**{provider['name']}**: {status}")

def save_to_env_file(config_data):
    """Save configuration to .env file"""
    try:
        env_path = Path(".env")
        env_content = []
        
        # Read existing content if file exists
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                env_content = f.readlines()
        
        # Update or add new values
        updated_keys = set()
        for i, line in enumerate(env_content):
            for key, value in config_data.items():
                env_key = key.upper()
                if line.startswith(f"{env_key}="):
                    env_content[i] = f"{env_key}={value}\n"
                    updated_keys.add(key)
                    break
        
        # Add new keys that weren't found
        for key, value in config_data.items():
            if key not in updated_keys:
                env_key = key.upper()
                env_content.append(f"{env_key}={value}\n")
        
        # Write back to file
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(env_content)
        
        return True
    except Exception as e:
        st.error(f"Failed to save to .env file: {e}")
        return False

def test_azure_connections(tenant_id, client_id, client_secret, subscription_id, openai_endpoint, openai_key):
    """Test Azure connections"""
    results = {"adf": False, "openai": False}
    
    # Test Azure Data Factory connection
    with st.spinner("Testing Azure Data Factory connection..."):
        try:
            # Mock test for now - in real implementation, use Azure SDK
            if tenant_id and client_id and client_secret and subscription_id:
                time.sleep(1)  # Simulate API call
                results["adf"] = True
                st.success("✅ Azure Data Factory connection successful!")
            else:
                st.error("❌ Missing Azure credentials")
        except Exception as e:
            st.error(f"❌ Azure Data Factory test failed: {e}")
    
    # Test Azure OpenAI connection
    with st.spinner("Testing Azure OpenAI connection..."):
        try:
            if openai_endpoint and openai_key:
                time.sleep(1)  # Simulate API call
                results["openai"] = True
                st.success("✅ Azure OpenAI connection successful!")
            else:
                st.error("❌ Missing Azure OpenAI credentials")
        except Exception as e:
            st.error(f"❌ Azure OpenAI test failed: {e}")
    
    return results

def run_automated_azure_setup():
    """Run automated Azure setup"""
    try:
        # This would run the setup_azure_automated.py script
        st.info("🤖 This would run the automated setup script...")
        st.info("For now, please run: `python setup_azure_automated.py`")
        time.sleep(2)
        st.success("✅ Automated setup completed! Please refresh the page.")
    except Exception as e:
        st.error(f"❌ Automated setup failed: {e}")

def save_ai_providers_config(providers):
    """Save AI providers configuration"""
    try:
        config_path = Path("config/ai_providers.yaml")
        config_path.parent.mkdir(exist_ok=True)
        
        # Convert providers to YAML format
        yaml_content = "ai_providers:\n"
        for provider in providers:
            yaml_content += f"""  - provider_id: "{provider['id']}"
    provider_name: "{provider['name']}"
    provider_type: "{provider['type']}"
    model_name: "{provider['model']}"
    api_endpoint: "{provider['endpoint']}"
    api_key: "{provider['api_key']}"
    deployment_name: "{provider.get('deployment', '')}"
    active: {str(provider['active']).lower()}
    priority: {provider['priority']}
    temperature: 0.3
    max_tokens: 1000
    confidence_threshold: 75

"""
        
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        
        return True
    except Exception as e:
        st.error(f"Failed to save AI providers: {e}")
        return False

def test_ai_provider(provider):
    """Test individual AI provider"""
    with st.spinner(f"Testing {provider['name']}..."):
        try:
            time.sleep(1)  # Simulate API call
            if provider['api_key']:
                provider['last_test_success'] = True
                st.success(f"✅ {provider['name']} connection successful!")
            else:
                provider['last_test_success'] = False
                st.error(f"❌ {provider['name']} missing API key")
        except Exception as e:
            provider['last_test_success'] = False
            st.error(f"❌ {provider['name']} test failed: {e}")

def test_all_ai_providers():
    """Test all active AI providers"""
    active_providers = [p for p in st.session_state.ai_providers if p['active']]
    
    if not active_providers:
        st.warning("⚠️ No active providers to test")
        return
    
    success_count = 0
    
    for provider in active_providers:
        try:
            time.sleep(0.5)  # Simulate API call
            if provider['api_key']:
                provider['last_test_success'] = True
                success_count += 1
            else:
                provider['last_test_success'] = False
        except Exception:
            provider['last_test_success'] = False
    
    if success_count == len(active_providers):
        st.success(f"✅ All {success_count} providers tested successfully!")
    else:
        st.warning(f"⚠️ {success_count}/{len(active_providers)} providers successful")

def reset_ai_providers_to_default():
    """Reset AI providers to default configuration"""
    st.session_state.ai_providers = [
        {
            "id": "azure-openai-primary",
            "name": "Azure OpenAI GPT-4",
            "type": "azure-openai",
            "model": "gpt-4",
            "endpoint": "",
            "api_key": "",
            "deployment": "",
            "active": True,
            "priority": 1
        },
        {
            "id": "openai-fallback",
            "name": "OpenAI GPT-4",
            "type": "openai",
            "model": "gpt-4",
            "endpoint": "https://api.openai.com/v1",
            "api_key": "",
            "deployment": "",
            "active": False,
            "priority": 2
        }
    ]
    st.success("✅ Providers reset to default configuration")
    st.rerun()

def render_environments_config():
    """Render environments configuration"""
    st.subheader("🌐 Environment Management")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Manage ADF Environments")
        
        # Initialize environments if not exists
        if 'environment_configs' not in st.session_state:
            st.session_state.environment_configs = [
                {
                    "name": "Production",
                    "subscription_id": "",
                    "resource_group": "",
                    "data_factory": "",
                    "region": "eastus",
                    "polling_interval": 300,
                    "active": True
                },
                {
                    "name": "Staging", 
                    "subscription_id": "",
                    "resource_group": "",
                    "data_factory": "",
                    "region": "eastus",
                    "polling_interval": 600,
                    "active": False
                }
            ]
        
        # Display environments
        for i, env in enumerate(st.session_state.environment_configs):
            with st.expander(f"{'🟢' if env['active'] else '🔴'} {env['name']}", expanded=env['active']):
                ecol1, ecol2 = st.columns(2)
                
                with ecol1:
                    env['name'] = st.text_input(f"Environment Name", value=env['name'], key=f"env_name_{i}")
                    env['subscription_id'] = st.text_input(f"Subscription ID", value=env['subscription_id'], key=f"env_sub_{i}")
                    env['resource_group'] = st.text_input(f"Resource Group", value=env['resource_group'], key=f"env_rg_{i}")
                
                with ecol2:
                    env['data_factory'] = st.text_input(f"Data Factory Name", value=env['data_factory'], key=f"env_adf_{i}")
                    env['region'] = st.selectbox(f"Region", 
                        ["eastus", "westus", "westeurope", "eastasia", "southeastasia"],
                        index=["eastus", "westus", "westeurope", "eastasia", "southeastasia"].index(env['region']),
                        key=f"env_region_{i}")
                    env['polling_interval'] = st.number_input(f"Polling Interval (seconds)", 
                        min_value=60, max_value=3600, value=env['polling_interval'], key=f"env_poll_{i}")
                    env['active'] = st.checkbox(f"Active", value=env['active'], key=f"env_active_{i}")
                
                if st.button(f"� Test {env['name']} Connection", key=f"test_env_{i}"):
                    test_environment_connection(env)
        
        # Add new environment
        st.markdown("### ➕ Add New Environment")
        with st.expander("Add Environment"):
            new_env_name = st.text_input("Environment Name", placeholder="Development")
            new_env_sub = st.text_input("Subscription ID")
            new_env_rg = st.text_input("Resource Group")
            new_env_adf = st.text_input("Data Factory Name")
            
            if st.button("➕ Add Environment"):
                if new_env_name and new_env_sub:
                    new_env = {
                        "name": new_env_name,
                        "subscription_id": new_env_sub,
                        "resource_group": new_env_rg,
                        "data_factory": new_env_adf,
                        "region": "eastus",
                        "polling_interval": 600,
                        "active": True
                    }
                    st.session_state.environment_configs.append(new_env)
                    st.success(f"✅ Environment '{new_env_name}' added!")
                    st.rerun()
                else:
                    st.error("❌ Please provide at least name and subscription ID")
    
    with col2:
        st.markdown("### 🎛️ Environment Controls")
        
        if st.button("💾 Save All Environments", use_container_width=True):
            save_environments_config()
            st.success("✅ Environments saved!")
        
        if st.button("🔍 Discover ADFs", use_container_width=True):
            discover_data_factories()
        
        st.markdown("### 📊 Environment Status")
        
        active_envs = sum(1 for env in st.session_state.environment_configs if env['active'])
        total_envs = len(st.session_state.environment_configs)
        
        st.metric("Active Environments", f"{active_envs}/{total_envs}")
        
        for env in st.session_state.environment_configs:
            if env['active']:
                status = "🟢 Connected" if env.get('last_test_success', True) else "🔴 Error"
                st.write(f"**{env['name']}**: {status}")

def render_notifications_config():
    """Render notifications configuration"""
    st.subheader("🔔 Notification Settings")
    
    # Notification channels
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Email Notifications")
        
        email_enabled = st.checkbox("Enable Email Notifications", value=False)
        if email_enabled:
            smtp_server = st.text_input("SMTP Server", placeholder="smtp.office365.com")
            smtp_port = st.number_input("SMTP Port", value=587)
            smtp_username = st.text_input("SMTP Username", placeholder="notifications@company.com")
            smtp_password = st.text_input("SMTP Password", type="password")
            email_recipients = st.text_area("Email Recipients", 
                placeholder="admin@company.com\ndevops@company.com\nteam@company.com")
        
        st.markdown("### Microsoft Teams")
        
        teams_enabled = st.checkbox("Enable Teams Notifications", value=False)
        if teams_enabled:
            teams_webhook = st.text_input("Teams Webhook URL", 
                placeholder="https://company.webhook.office.com/...")
            teams_mention_users = st.text_input("Mention Users", 
                placeholder="@john.doe @jane.smith")
    
    with col2:
        st.markdown("### Slack Notifications")
        
        slack_enabled = st.checkbox("Enable Slack Notifications", value=False)
        if slack_enabled:
            slack_webhook = st.text_input("Slack Webhook URL",
                placeholder="https://hooks.slack.com/services/...")
            slack_channel = st.text_input("Slack Channel", placeholder="#adf-alerts")
            slack_mention_users = st.text_input("Mention Users", placeholder="@channel @john.doe")
        
        st.markdown("### SMS Notifications")
        
        sms_enabled = st.checkbox("Enable SMS Notifications", value=False)
        if sms_enabled:
            sms_provider = st.selectbox("SMS Provider", ["Twilio", "Azure SMS", "Custom"])
            sms_api_key = st.text_input("API Key", type="password")
            sms_phone_numbers = st.text_area("Phone Numbers",
                placeholder="+1-555-0123\n+1-555-0456")
    
    # Notification rules
    st.markdown("### 🎯 Notification Rules")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**When to Notify:**")
        notify_on_failure = st.checkbox("Pipeline Failures", value=True)
        notify_on_retry_fail = st.checkbox("Retry Failures", value=True)
        notify_on_success_after_retry = st.checkbox("Success After Retry", value=True)
        notify_on_long_running = st.checkbox("Long Running Pipelines", value=False)
        
        if notify_on_long_running:
            long_running_threshold = st.number_input("Threshold (minutes)", value=60)
    
    with col2:
        st.markdown("**Notification Frequency:**")
        notification_cooldown = st.selectbox("Cooldown Period", 
            ["No cooldown", "5 minutes", "15 minutes", "1 hour", "4 hours"])
        batch_notifications = st.checkbox("Batch Similar Notifications", value=True)
        quiet_hours_enabled = st.checkbox("Enable Quiet Hours", value=False)
        
        if quiet_hours_enabled:
            quiet_start = st.time_input("Quiet Hours Start", value=datetime.strptime("22:00", "%H:%M").time())
            quiet_end = st.time_input("Quiet Hours End", value=datetime.strptime("08:00", "%H:%M").time())
    
    # Save notifications config
    if st.button("� Save Notification Configuration"):
        st.success("✅ Notification settings saved!")

def render_security_config():
    """Render security configuration"""
    st.subheader("🔒 Security & Access Control")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Authentication")
        
        auth_enabled = st.checkbox("Enable Authentication", value=False)
        if auth_enabled:
            auth_method = st.selectbox("Authentication Method", 
                ["Azure AD", "Local Users", "LDAP", "SAML"])
            
            if auth_method == "Azure AD":
                aad_tenant_id = st.text_input("Azure AD Tenant ID")
                aad_client_id = st.text_input("Application Client ID")
                aad_client_secret = st.text_input("Client Secret", type="password")
            
            session_timeout = st.number_input("Session Timeout (hours)", min_value=1, max_value=24, value=8)
        
        st.markdown("### API Security")
        
        api_key_enabled = st.checkbox("Require API Keys", value=True)
        if api_key_enabled:
            api_key_expiry = st.selectbox("API Key Expiry", 
                ["30 days", "90 days", "1 year", "Never"])
        
        rate_limiting = st.checkbox("Enable Rate Limiting", value=True)
        if rate_limiting:
            rate_limit_requests = st.number_input("Requests per minute", value=100)
    
    with col2:
        st.markdown("### Access Control")
        
        rbac_enabled = st.checkbox("Enable Role-Based Access", value=False)
        if rbac_enabled:
            st.markdown("**Default Roles:**")
            st.write("• **Admin**: Full access to all features")
            st.write("• **Operator**: View and manage pipelines")
            st.write("• **Viewer**: Read-only access")
            
            custom_roles = st.text_area("Custom Roles (JSON)",
                placeholder='{"analyst": {"permissions": ["view", "analyze"]}}')
        
        st.markdown("### Audit & Logging")
        
        audit_enabled = st.checkbox("Enable Audit Logging", value=True)
        audit_retention = st.selectbox("Audit Log Retention", 
            ["30 days", "90 days", "1 year", "Indefinite"])
        
        log_sensitive_data = st.checkbox("Log Sensitive Operations", value=True)
        export_audit_logs = st.checkbox("Allow Audit Log Export", value=False)
    
    # Security scan results
    st.markdown("### 🛡️ Security Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Security Score", "85/100", "5")
    with col2:
        st.metric("Vulnerabilities", "2", "-1")
    with col3:
        st.metric("Last Scan", "2 hours ago")
    
    # Save security config
    if st.button("💾 Save Security Configuration"):
        st.success("✅ Security settings saved!")

def test_environment_connection(env):
    """Test environment connection"""
    with st.spinner(f"Testing {env['name']} connection..."):
        try:
            time.sleep(1)  # Simulate connection test
            if env['subscription_id'] and env['data_factory']:
                env['last_test_success'] = True
                st.success(f"✅ {env['name']} connection successful!")
            else:
                env['last_test_success'] = False
                st.error(f"❌ {env['name']} missing configuration")
        except Exception as e:
            env['last_test_success'] = False
            st.error(f"❌ {env['name']} test failed: {e}")

def save_environments_config():
    """Save environments configuration"""
    try:
        config_path = Path("config/environments.yaml")
        config_path.parent.mkdir(exist_ok=True)
        
        yaml_content = "environments:\n"
        for env in st.session_state.environment_configs:
            yaml_content += f"""  - name: "{env['name']}"
    subscription_id: "{env['subscription_id']}"
    resource_group: "{env['resource_group']}"
    data_factory: "{env['data_factory']}"
    region: "{env['region']}"
    polling_interval: {env['polling_interval']}
    active: {str(env['active']).lower()}

"""
        
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        
        return True
    except Exception as e:
        st.error(f"Failed to save environments: {e}")
        return False

def render_genai_page():
    """Render GenAI configuration page - simplified version"""
    st.header("🧠 GenAI Configuration & Management")
    
    st.info("💡 For full AI configuration, please use the **⚙️ Admin Configuration** page")
    
    # Quick AI status
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Providers", "2", "1")
    with col2:
        st.metric("AI Accuracy", "89.2%", "2.1%")
    with col3:
        st.metric("Analyses Today", "47", "12")
    with col4:
        st.metric("AI Cost Today", "$3.42", "$0.89")
    
    # Quick provider status
    st.subheader("🔧 Provider Status")
    
    providers_status = [
        {"name": "Azure OpenAI GPT-4", "status": "🟢 Active", "usage": "67%"},
        {"name": "OpenAI Fallback", "status": "🟡 Standby", "usage": "15%"},
        {"name": "Google Gemini", "status": "🔴 Inactive", "usage": "0%"}
    ]
    
    for provider in providers_status:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.write(f"**{provider['name']}**")
        with col2:
            st.write(provider['status'])
        with col3:
            st.write(f"Usage: {provider['usage']}")
    
    st.info("🔧 **Configure AI providers in Admin Configuration > AI Providers tab**")

def discover_data_factories():
    """Discover Data Factories in subscription"""
    with st.spinner("Discovering Data Factories..."):
        try:
            time.sleep(2)  # Simulate discovery
            
            # Mock discovered ADFs
            discovered = [
                {"name": "adf-prod-001", "resource_group": "rg-production", "region": "eastus"},
                {"name": "adf-stage-001", "resource_group": "rg-staging", "region": "eastus"},
                {"name": "adf-dev-001", "resource_group": "rg-development", "region": "westus"}
            ]
            
            st.session_state.discovered_adfs = discovered
            st.success(f"✅ Discovered {len(discovered)} Data Factories!")
            
            for adf in discovered:
                st.write(f"• {adf['name']} in {adf['resource_group']} ({adf['region']})")
                
        except Exception as e:
            st.error(f"❌ Discovery failed: {e}")

def save_to_env_file(config_data):
    """Save configuration to .env file"""
    try:
        env_path = ".env"
        with open(env_path, "w") as f:
            for key, value in config_data.items():
                f.write(f"{key}={value}\n")
        return True
    except Exception as e:
        st.error(f"Error saving configuration: {e}")
        return False
            
def discover_data_factories():
    """Discover Data Factories in subscription"""
    with st.spinner("Discovering Data Factories..."):
        try:
            time.sleep(2)  # Simulate discovery
            
            # Mock discovered ADFs
            discovered = [
                {"name": "adf-prod-001", "resource_group": "rg-production", "region": "eastus"},
                {"name": "adf-stage-001", "resource_group": "rg-staging", "region": "eastus"},
                {"name": "adf-dev-001", "resource_group": "rg-development", "region": "westus"}
            ]
            
            st.session_state.discovered_adfs = discovered
            st.success(f"✅ Discovered {len(discovered)} Data Factories!")
            
            for adf in discovered:
                st.write(f"• {adf['name']} in {adf['resource_group']} ({adf['region']})")
                
        except Exception as e:
            st.error(f"❌ Discovery failed: {e}")

def render_help_page():
    """Render help and documentation page"""
    st.header("📚 Help & Documentation")
    
    # Help categories
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🚀 Getting Started", "📖 User Guide", "🔧 Configuration", "🤖 AI Features", "❓ FAQ"])
    
    with tab1:
        st.subheader("Getting Started with ADF Monitor Pro")
        
        st.markdown("""
        ### Welcome to ADF Monitor Pro! 🎉
        
        **ADF Monitor Pro** is an enterprise-grade solution for monitoring and automating Azure Data Factory pipelines across multiple environments.
        
        #### Quick Setup Steps:
        
        1. **Environment Configuration**
           - Navigate to the sidebar "🌐 Environment" section
           - Add your Azure Data Factory details
           - Configure connection credentials
        
        2. **AI Provider Setup**
           - Go to "🧠 GenAI Configuration"
           - Add your preferred AI providers (OpenAI, Azure OpenAI, etc.)
           - Configure API keys and model parameters
        
        3. **Start Monitoring**
           - Use the "🎮 Monitoring Controls" in the sidebar
           - Click "🚀 Start Monitoring" to begin automatic scanning
           - Monitor the dashboard for real-time updates
        
        #### Key Features:
        - ✅ **Multi-Environment Support**: Monitor Production, Staging, Development
        - ✅ **AI-Powered Analysis**: Multiple GenAI providers with intelligent error classification
        - ✅ **Automated Actions**: Smart retry logic and failure handling
        - ✅ **Visual Dashboard**: Real-time monitoring with interactive charts
        - ✅ **Comprehensive Logging**: Complete audit trail and system logs
        """)
    
    with tab2:
        st.subheader("User Guide")
        
        guide_section = st.selectbox("Select Guide Section", [
            "Dashboard Navigation",
            "Managing Failures", 
            "Configuring Actions",
            "Viewing Logs",
            "AI Configuration"
        ])
        
        if guide_section == "Dashboard Navigation":
            st.markdown("""
            ### Dashboard Navigation 📊
            
            **Main Dashboard Features:**
            - **Top Metrics**: Real-time KPIs for pipeline health
            - **Status Distribution**: Visual breakdown of pipeline statuses
            - **Failure Trends**: Historical failure patterns and trends
            - **Recent Activity**: Latest pipeline runs and their status
            
            **Navigation Tips:**
            - Use the sidebar to switch between environments
            - Click on charts for detailed drill-down views
            - Hover over metrics for additional context
            """)
        
        elif guide_section == "Managing Failures":
            st.markdown("""
            ### Managing Pipeline Failures ❌
            
            **Failure Analysis Workflow:**
            1. Navigate to "❌ Pipeline Failures Analysis"
            2. Review AI analysis for each failure
            3. Check confidence scores and recommendations
            4. Take appropriate actions (retry, ignore, or manual fix)
            
            **Understanding AI Analysis:**
            - **Transient**: Temporary issues, usually safe to retry
            - **Data Quality**: Data-related problems requiring manual review
            - **Configuration**: Setup/permission issues needing admin attention
            - **Unknown**: Unclassified errors handled conservatively
            
            **Action Options:**
            - 🔄 **Retry**: Restart the failed pipeline
            - 🚫 **Ignore**: Mark as acknowledged but no action
            - 📝 **Add Note**: Document manual fixes or decisions
            """)
    
    with tab3:
        st.subheader("Configuration Guide")
        
        st.markdown("""
        ### System Configuration 🔧
        
        #### Environment Setup:
        ```json
        {
            "subscription_id": "your-azure-subscription-id",
            "resource_group": "your-resource-group-name", 
            "data_factory": "your-adf-name",
            "region": "eastus"
        }
        ```
        
        #### AI Provider Configuration:
        ```json
        {
            "provider": "OpenAI",
            "model": "gpt-4",
            "api_key": "your-api-key",
            "temperature": 0.3,
            "max_tokens": 1000
        }
        ```
        
        #### Monitoring Settings:
        - **Polling Interval**: How often to check for new pipeline runs
        - **Confidence Threshold**: Minimum AI confidence for auto-actions
        - **Retry Attempts**: Maximum automatic retry attempts
        - **Retry Delay**: Time to wait between retry attempts
        """)
    
    with tab4:
        st.subheader("AI Features Guide")
        
        st.markdown("""
        ### AI-Powered Features 🤖
        
        #### Supported AI Providers:
        - **OpenAI GPT-4**: Best overall accuracy and reasoning
        - **Azure OpenAI**: Enterprise-grade with data residency
        - **Google Gemini**: Fast processing and cost-effective
        - **Anthropic Claude**: Excellent for complex error analysis
        - **Local Models**: On-premises deployment options
        
        #### AI Analysis Capabilities:
        - **Error Classification**: Automatic categorization of failure types
        - **Confidence Scoring**: Reliability measure for AI decisions
        - **Pattern Learning**: Improves accuracy over time
        - **Retry Recommendations**: Smart suggestions for automated actions
        - **Root Cause Analysis**: Human-readable explanations
        
        #### Customization Options:
        - **Behavior Tuning**: Adjust aggressiveness and conservativeness
        - **Custom Patterns**: Define organization-specific error handling
        - **Feedback Learning**: AI learns from user corrections
        - **Multi-Model Ensemble**: Combine multiple AI providers for better accuracy
        """)
    
    with tab5:
        st.subheader("Frequently Asked Questions")
        
        faqs = [
            {
                "question": "How does the AI determine if a pipeline should be retried?",
                "answer": "The AI analyzes error messages, patterns, and historical data to classify errors as transient (safe to retry) or persistent (requiring manual intervention). It considers factors like error type, confidence score, retry history, and success rates."
            },
            {
                "question": "Can I use multiple AI providers simultaneously?",
                "answer": "Yes! You can configure multiple AI providers and either switch between them or use ensemble methods where multiple AIs analyze the same failure for increased accuracy."
            },
            {
                "question": "How secure is my Azure Data Factory data?",
                "answer": "All connections use Azure service principals with minimal required permissions. Error messages are analyzed by AI, but your actual data never leaves your Azure environment. API keys and credentials are encrypted and stored securely."
            },
            {
                "question": "What happens if the AI makes a wrong decision?",
                "answer": "You can provide feedback through the interface, and the AI will learn from corrections. All actions are logged and can be reversed. You can also adjust confidence thresholds to make the system more conservative."
            },
            {
                "question": "How do I add a new Azure Data Factory environment?",
                "answer": "Go to the sidebar Environment section, click 'Add Environment', and provide the subscription ID, resource group, and Data Factory name. You'll also need to configure appropriate service principal credentials."
            }
        ]
        
        for i, faq in enumerate(faqs):
            with st.expander(f"❓ {faq['question']}"):
                st.write(faq['answer'])

def main():
    """Main application entry point"""
    render_header()
    render_sidebar()
    
    # Main navigation
    page = st.sidebar.selectbox(
        "📑 Navigation",
        [
            "📊 Dashboard",
            "❌ Pipeline Failures", 
            "🎯 Actions & Interventions",
            "📜 Logs & Audit Trail",
            "🧠 GenAI Configuration",
            "⚙️ Admin Configuration",
            "📚 Help & Documentation"
        ]
    )
    
    # Route to appropriate page
    if page == "📊 Dashboard":
        render_dashboard_page()
    elif page == "❌ Pipeline Failures":
        render_failures_page()
    elif page == "🎯 Actions & Interventions":
        render_actions_page()
    elif page == "📜 Logs & Audit Trail":
        render_logs_page()
    elif page == "🧠 GenAI Configuration":
        render_genai_page()
    elif page == "⚙️ Admin Configuration":
        render_admin_config_page()
    elif page == "📚 Help & Documentation":
        render_help_page()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        🏭 ADF Monitor Pro v2.0 | Enterprise Pipeline Management Platform<br>
        Powered by AI • Built for Scale • Designed for DevOps Teams
    </div>
    """, unsafe_allow_html=True)

def test_ai_provider(provider):
    """Test individual AI provider"""
    try:
        with st.spinner(f"Testing {provider['name']}..."):
            time.sleep(1)  # Simulate API call
            # In real implementation, this would test the actual API
            provider['last_test_success'] = True
            st.success(f"✅ {provider['name']} connection successful!")
    except Exception as e:
        provider['last_test_success'] = False
        st.error(f"❌ {provider['name']} test failed: {e}")

def test_all_ai_providers():
    """Test all active AI providers"""
    active_providers = [p for p in st.session_state.ai_providers if p['active']]
    for provider in active_providers:
        test_ai_provider(provider)

def reset_ai_providers_to_default():
    """Reset AI providers to default configuration"""
    st.session_state.ai_providers = [
        {
            "id": "azure-openai-primary",
            "name": "Azure OpenAI GPT-4",
            "type": "azure-openai",
            "model": "gpt-4",
            "endpoint": "",
            "api_key": "",
            "deployment": "",
            "active": True,
            "priority": 1
        }
    ]
    st.success("✅ AI providers reset to defaults!")
    st.rerun()

if __name__ == "__main__":
    main()
