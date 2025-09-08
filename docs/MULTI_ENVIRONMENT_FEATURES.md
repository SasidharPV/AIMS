# Multi-Environment Monitoring Features

## Overview

ADF Monitor Pro now provides comprehensive multi-environment failure monitoring capabilities, allowing you to view and manage failures across Production, Staging, and Development environments from a single unified interface.

## Key Features

### 🌍 Multi-Environment Dashboard
- **Unified Health Overview**: View health status of all environments at a glance
- **Environment Switching**: Quick toggle between environments with one-click access
- **Global Summary Metrics**: Consolidated statistics across all environments
- **Cross-Environment Alerts**: Real-time notifications for critical issues

### 🚨 Enhanced Failure Monitoring

#### Three Viewing Modes:

1. **Single Environment View** (Traditional)
   - Focus on one environment at a time
   - Detailed failure analysis for selected environment
   - Environment-specific actions and remediation

2. **Multi-Environment Overview** 🌟 *NEW*
   - All environment failures on one page
   - Color-coded environment indicators (🔴 Production, 🟡 Staging, 🟢 Development)
   - Priority-based sorting (Critical → High → Medium → Low)
   - Environment-specific actions:
     - 🚨 **Escalate** (Production only)
     - 🔄 **Force Retry** (All environments)
     - 📝 **Add Notes** (All environments)

3. **Cross-Environment Comparison** 🌟 *NEW*
   - Side-by-side comparison of environment health
   - Quick environment switching from comparison view
   - Comparative metrics and trends

### 🎯 Smart Filtering & Organization

#### Multi-Environment Filters:
- **Environment Selection**: Filter by specific environments
- **Severity Levels**: Critical, High, Medium, Low
- **Status Types**: Auto-retrying, Needs Review, Manual Fix Required, etc.
- **Time Ranges**: Last Hour, 6 Hours, 24 Hours, Week

#### Visual Indicators:
- **Environment Colors**: 
  - 🔴 Production (Red border/background)
  - 🟡 Staging (Orange border/background)  
  - 🟢 Development (Green border/background)
- **Severity Icons**: 🔴 Critical, 🟠 High, 🟡 Medium, 🟢 Low
- **Status Badges**: Auto-retrying, Queued, Under Investigation

### ⚡ Quick Actions & Navigation

#### Sidebar Quick Access:
- **🚨 View All Environment Failures**: Direct access to multi-environment view
- **📊 Cross-Environment Comparison**: Jump to comparison mode
- **Environment Health Indicators**: Live status of all environments

#### Smart Routing:
- Sidebar buttons automatically switch to Failures page with appropriate view mode
- Session state preservation for seamless navigation
- Context-aware default selections

## Usage Examples

### Scenario 1: Production Crisis Management
When a critical issue occurs in production:
1. Click **🚨 View All Environment Failures** in sidebar
2. Automatically opens multi-environment view
3. Production failures appear at top (sorted by severity)
4. Use **🚨 Escalate** button for immediate on-call notification
5. Compare with staging to identify if issue will propagate

### Scenario 2: Cross-Environment Issue Analysis
To investigate issues affecting multiple environments:
1. Navigate to **Cross-Environment Comparison** mode
2. Compare failure counts and patterns across environments
3. Identify common root causes or environment-specific issues
4. Plan coordinated remediation strategy

### Scenario 3: Daily Operations Review
For regular monitoring activities:
1. Start with **Multi-Environment Overview**
2. Use filters to focus on specific severity levels
3. Review cross-environment patterns and trends
4. Switch to single environment view for detailed investigation

## Technical Implementation

### Data Structure
```python
failure_data = {
    "environment": "Production|Staging|Development",
    "run_id": "unique_identifier",
    "pipeline": "pipeline_name",
    "error_type": "transient|data_quality|configuration",
    "confidence": 0-100,
    "severity": "Critical|High|Medium|Low",
    "error_message": "detailed_error_description",
    "timestamp": datetime_object,
    "ai_analysis": "ai_generated_insights",
    "status": "current_status",
    "retry_count": "current/max_retries"
}
```

### Session State Management
- `st.session_state.current_environment`: Active environment
- `st.session_state.failure_view_mode`: Selected view mode
- `st.session_state.current_tab`: Active page/tab

### Environment Configuration
Each environment maintains its own configuration:
```python
environments = {
    "Production": {
        "subscription_id": "...",
        "resource_group": "...", 
        "data_factory": "...",
        "status": "Active|Maintenance|Offline"
    }
    # ... similar for Staging and Development
}
```

## Benefits

1. **Faster Issue Resolution**: See all critical issues across environments immediately
2. **Better Context**: Understand how failures relate across the deployment pipeline
3. **Improved Prioritization**: Environment-aware severity and action recommendations
4. **Streamlined Workflow**: Fewer clicks to get comprehensive failure overview
5. **Enhanced Collaboration**: Teams can quickly understand multi-environment impact

## Future Enhancements

- **Environment Dependency Mapping**: Show how staging issues may affect production
- **Automated Cross-Environment Correlation**: AI-powered relationship detection
- **Multi-Environment Dashboards**: Custom views for specific teams/roles
- **Environment Promotion Tracking**: Monitor code/config movement through environments
- **Cross-Environment Alerting**: Smart notifications based on environment relationships

## Getting Started

1. Navigate to the **❌ Pipeline Failures** page
2. Select **Multi-Environment Overview** from the radio buttons
3. Explore the consolidated view with environment-specific filters
4. Use quick access buttons in the sidebar for faster navigation
5. Try **Cross-Environment Comparison** for side-by-side analysis

The multi-environment features are designed to provide maximum visibility with minimal complexity, enabling faster and more informed decision-making across your Azure Data Factory ecosystem.
