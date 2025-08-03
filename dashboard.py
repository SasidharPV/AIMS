"""
Streamlit Dashboard for ADF Monitoring System
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import time
from database import db_manager
from adf_monitor import ADFMonitoringSystem
from config import config

# Page configuration
st.set_page_config(
    page_title="ADF Monitoring Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize monitoring system
@st.cache_resource
def get_monitoring_system():
    return ADFMonitoringSystem()

def main():
    """Main dashboard function"""
    
    st.title("🏭 ADF Monitoring & Automation Dashboard")
    st.markdown("Real-time monitoring and automated failure handling for Azure Data Factory pipelines")
    
    # Sidebar
    st.sidebar.title("🔧 Control Panel")
    
    # System status
    monitor = get_monitoring_system()
    system_status = monitor.get_system_status()
    
    # Status indicator
    if system_status.get("system_running", False):
        st.sidebar.success("✅ System Running")
    else:
        st.sidebar.error("❌ System Stopped")
    
    if system_status.get("config_valid", False):
        st.sidebar.success("✅ Configuration Valid")
    else:
        st.sidebar.warning("⚠️ Configuration Issues")
    
    # Manual controls
    st.sidebar.subheader("Manual Controls")
    if st.sidebar.button("🔍 Run Manual Check"):
        with st.spinner("Running pipeline check..."):
            monitor.monitor_pipelines()
        st.sidebar.success("Check completed!")
    
    if st.sidebar.button("🔄 Refresh Data"):
        st.rerun()
    
    # Configuration display
    with st.sidebar.expander("📊 Configuration"):
        st.text(f"Data Factory: {config.azure.data_factory_name}")
        st.text(f"Polling Interval: {config.monitoring.polling_interval_minutes} min")
        st.text(f"Max Retries: {config.monitoring.max_retry_attempts}")
    
    # Main dashboard content
    col1, col2, col3, col4 = st.columns(4)
    
    # Get dashboard stats
    stats = system_status.get("stats", {})
    
    # KPI Cards
    with col1:
        st.metric(
            label="Total Runs Today",
            value=stats.get("total_runs_today", 0),
            delta=None
        )
    
    with col2:
        st.metric(
            label="Failed Runs Today", 
            value=stats.get("failed_runs_today", 0),
            delta=None
        )
    
    with col3:
        st.metric(
            label="Success Rate",
            value=f"{stats.get('success_rate_today', 100):.1f}%",
            delta=None
        )
    
    with col4:
        st.metric(
            label="Auto Retries Today",
            value=stats.get("auto_retries_today", 0),
            delta=None
        )
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "❌ Failed Runs", "🤖 AI Analysis", "📈 Trends"])
    
    with tab1:
        show_overview_tab()
    
    with tab2:
        show_failed_runs_tab()
    
    with tab3:
        show_ai_analysis_tab()
    
    with tab4:
        show_trends_tab()

def show_overview_tab():
    """Show overview tab content"""
    st.subheader("📊 Pipeline Overview")
    
    try:
        # Get recent pipeline runs
        failed_runs = db_manager.get_failed_runs_last_hours(24)
        
        if failed_runs:
            df = pd.DataFrame(failed_runs)
            df['start_time'] = pd.to_datetime(df['start_time'])
            
            # Pipeline status chart
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Pipeline Status Distribution")
                status_counts = df['status'].value_counts()
                fig = px.pie(values=status_counts.values, names=status_counts.index, 
                           title="Pipeline Run Status")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("Failures by Pipeline")
                pipeline_failures = df['pipeline_name'].value_counts()
                fig = px.bar(x=pipeline_failures.index, y=pipeline_failures.values,
                           title="Failed Runs by Pipeline")
                fig.update_xaxis(title="Pipeline Name")
                fig.update_yaxis(title="Failed Runs")
                st.plotly_chart(fig, use_container_width=True)
            
            # Recent activity timeline
            st.subheader("Recent Activity Timeline")
            df_sorted = df.sort_values('start_time', ascending=False).head(10)
            
            for _, row in df_sorted.iterrows():
                with st.expander(f"🔴 {row['pipeline_name']} - {row['start_time'].strftime('%H:%M:%S')}"):
                    st.text(f"Run ID: {row['run_id']}")
                    st.text(f"Status: {row['status']}")
                    st.text(f"Start Time: {row['start_time']}")
                    if row['error_message']:
                        st.text(f"Error: {row['error_message'][:200]}...")
        else:
            st.info("No failed pipeline runs in the last 24 hours")
            
    except Exception as e:
        st.error(f"Error loading overview data: {e}")

def show_failed_runs_tab():
    """Show failed runs tab content"""
    st.subheader("❌ Failed Pipeline Runs")
    
    try:
        # Time range selector
        hours_back = st.selectbox("Time Range", [1, 6, 12, 24, 48, 168], index=3)
        
        failed_runs = db_manager.get_failed_runs_last_hours(hours_back)
        
        if failed_runs:
            df = pd.DataFrame(failed_runs)
            df['start_time'] = pd.to_datetime(df['start_time'])
            df = df.sort_values('start_time', ascending=False)
            
            # Display as expandable cards
            for _, run in df.iterrows():
                with st.expander(f"🔴 {run['pipeline_name']} - {run['start_time'].strftime('%Y-%m-%d %H:%M:%S')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.text(f"Run ID: {run['run_id']}")
                        st.text(f"Pipeline: {run['pipeline_name']}")
                        st.text(f"Status: {run['status']}")
                        st.text(f"Start Time: {run['start_time']}")
                        
                    with col2:
                        if run['error_message']:
                            st.text_area("Error Message", run['error_message'], height=100, disabled=True)
                        
                        # Check for monitoring actions
                        actions = db_manager.get_retry_history(run['pipeline_name'], hours=1)
                        run_actions = [a for a in actions if a.get('run_id') == run['run_id']]
                        
                        if run_actions:
                            st.text(f"Actions Taken: {len(run_actions)}")
                            for action in run_actions:
                                st.text(f"- {action.get('action_type', 'unknown')}: {action.get('decision_reason', 'No reason')}")
        else:
            st.info(f"No failed runs found in the last {hours_back} hours")
            
    except Exception as e:
        st.error(f"Error loading failed runs: {e}")

def show_ai_analysis_tab():
    """Show AI analysis tab content"""
    st.subheader("🤖 AI Analysis Results")
    
    try:
        # Get monitoring actions with AI analysis
        with db_manager.db_path:
            import sqlite3
            conn = sqlite3.connect(db_manager.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT ma.*, pr.pipeline_name, pr.error_message 
                FROM monitoring_actions ma
                JOIN pipeline_runs pr ON ma.run_id = pr.run_id
                WHERE ma.ai_analysis IS NOT NULL
                ORDER BY ma.timestamp DESC
                LIMIT 20
            ''')
            
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            conn.close()
        
        if results:
            for result in results:
                with st.expander(f"🤖 {result['pipeline_name']} - {result['timestamp']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.text(f"Action Type: {result['action_type']}")
                        st.text(f"Decision: {result['decision_reason']}")
                        st.text(f"Action Taken: {'Yes' if result['action_taken'] else 'No'}")
                    
                    with col2:
                        if result['ai_analysis']:
                            try:
                                ai_data = json.loads(result['ai_analysis'])
                                st.json(ai_data)
                            except json.JSONDecodeError:
                                st.text(result['ai_analysis'])
        else:
            st.info("No AI analysis results found")
            
    except Exception as e:
        st.error(f"Error loading AI analysis: {e}")

def show_trends_tab():
    """Show trends tab content"""
    st.subheader("📈 Trends and Analytics")
    
    try:
        # Get data for trends
        failed_runs = db_manager.get_failed_runs_last_hours(168)  # Last week
        
        if failed_runs:
            df = pd.DataFrame(failed_runs)
            df['start_time'] = pd.to_datetime(df['start_time'])
            df['date'] = df['start_time'].dt.date
            df['hour'] = df['start_time'].dt.hour
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Failures by day
                st.subheader("Failures by Day")
                daily_failures = df.groupby('date').size()
                fig = px.line(x=daily_failures.index, y=daily_failures.values,
                             title="Daily Failure Count")
                fig.update_xaxis(title="Date")
                fig.update_yaxis(title="Failed Runs")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Failures by hour of day
                st.subheader("Failures by Hour")
                hourly_failures = df.groupby('hour').size()
                fig = px.bar(x=hourly_failures.index, y=hourly_failures.values,
                           title="Failure Count by Hour of Day")
                fig.update_xaxis(title="Hour of Day")
                fig.update_yaxis(title="Failed Runs")
                st.plotly_chart(fig, use_container_width=True)
            
            # Error pattern analysis
            st.subheader("Common Error Patterns")
            
            # Simple error categorization
            error_keywords = {
                'Network/Timeout': ['timeout', 'network', 'connection'],
                'Data Quality': ['column', 'validation', 'schema', 'data'],
                'Access/Auth': ['access', 'permission', 'authentication', 'denied'],
                'Configuration': ['config', 'setting', 'parameter']
            }
            
            error_categories = []
            for _, row in df.iterrows():
                if row['error_message']:
                    error_msg = row['error_message'].lower()
                    category = 'Other'
                    for cat, keywords in error_keywords.items():
                        if any(keyword in error_msg for keyword in keywords):
                            category = cat
                            break
                    error_categories.append(category)
                else:
                    error_categories.append('Unknown')
            
            df['error_category'] = error_categories
            category_counts = df['error_category'].value_counts()
            
            fig = px.pie(values=category_counts.values, names=category_counts.index,
                        title="Error Categories")
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.info("No data available for trends analysis")
            
    except Exception as e:
        st.error(f"Error loading trends: {e}")

if __name__ == "__main__":
    main()
