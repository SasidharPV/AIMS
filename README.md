# ADF Monitoring & Automation System

A comprehensive GenAI-supported monitoring and automation solution for Azure Data Factory (ADF) that automatically detects pipeline failures, analyzes errors using AI, and executes appropriate remediation actions.

## 🎯 Features

- **Real-time Pipeline Monitoring**: Continuously monitors ADF pipelines for failures
- **AI-Powered Error Analysis**: Uses GenAI to classify and analyze error messages
- **Automated Retry Logic**: Intelligently determines when to retry failed pipelines
- **Multi-Channel Notifications**: Sends alerts via console, Microsoft Teams, and email
- **Comprehensive Dashboard**: Streamlit-based dashboard for monitoring and analytics
- **Historical Tracking**: SQLite database for logging decisions and tracking patterns
- **Mock Testing Environment**: Complete mock data system for testing without Azure resources

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   ADF Pipelines │────│  Monitor Service │────│  GenAI Analyzer │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │                          │
                              ▼                          ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Notification   │────│  Decision Engine │────│   Log Storage   │
│    Service      │    │                  │    │   (SQLite)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                      ┌──────────────────┐
                      │  Auto-Retry      │
                      │    Service       │
                      └──────────────────┘
```

## 📁 Project Structure

```
AIMS/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── .env.example             # Environment configuration template
├── config.py                # Configuration management
├── database.py              # SQLite database manager
├── adf_client.py            # Azure Data Factory REST API client
├── genai_analyzer.py        # GenAI analysis engine
├── notification_service.py  # Multi-channel notifications
├── adf_monitor.py           # Main monitoring system
├── dashboard.py             # Streamlit dashboard
├── mock_data.py             # Mock data generator for testing
├── test_system.py           # Comprehensive test suite
└── quick_start.py           # Interactive setup and launch
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:
- Azure Data Factory credentials
- OpenAI API key
- Notification settings (Teams, email)

### 3. Run the System

#### Option A: Interactive Setup
```bash
python quick_start.py
```

#### Option B: Direct Launch
```bash
# Run monitoring system
python adf_monitor.py

# Or run dashboard
streamlit run dashboard.py

# Or run single test cycle
python adf_monitor.py --test
```

## 🔧 Configuration

### Required Configuration

```env
# Azure Data Factory
AZURE_SUBSCRIPTION_ID=your_subscription_id
AZURE_RESOURCE_GROUP=your_resource_group
AZURE_DATA_FACTORY_NAME=your_adf_name
AZURE_TENANT_ID=your_tenant_id
AZURE_CLIENT_ID=your_client_id
AZURE_CLIENT_SECRET=your_client_secret

# OpenAI
OPENAI_API_KEY=your_openai_api_key
```

### Optional Configuration

```env
# Monitoring Settings
POLLING_INTERVAL_MINUTES=5
MAX_RETRY_ATTEMPTS=3
RETRY_DELAY_MINUTES=10

# Notifications
TEAMS_WEBHOOK_URL=your_teams_webhook
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_FROM=alerts@company.com
EMAIL_TO=team@company.com
```

## 🧠 AI Analysis Features

The GenAI analyzer provides:

- **Error Classification**: Categorizes errors as transient, data quality, configuration, or unknown
- **Retry Recommendations**: Determines if and when to retry failed pipelines
- **Root Cause Analysis**: Provides human-readable explanations of failures
- **Confidence Scoring**: Measures confidence in analysis and recommendations
- **Pattern Learning**: Tracks success rates of different error patterns over time

### Example AI Analysis Output

```json
{
  "error_type": "transient",
  "severity": "medium",
  "should_retry": true,
  "retry_delay_minutes": 10,
  "confidence_score": 85,
  "analysis_summary": "Network timeout detected. This is typically a transient issue that resolves on retry.",
  "root_cause": "Network connectivity or service timeout",
  "recommended_actions": [
    "Retry the pipeline",
    "Monitor for pattern of network issues",
    "Check service health status"
  ],
  "manual_intervention_required": false
}
```

## 📊 Dashboard Features

The Streamlit dashboard provides:

- **Real-time Overview**: Current system status and KPIs
- **Failed Runs Analysis**: Detailed view of recent failures
- **AI Analysis Results**: Review of AI decisions and recommendations
- **Trends & Analytics**: Historical patterns and insights
- **Manual Controls**: Ability to trigger manual checks and actions

## 🧪 Testing

### Run Tests
```bash
python test_system.py
```

### Generate Mock Data
```bash
python mock_data.py
```

### Test with Mock Data
```bash
python adf_monitor.py --test
```

The system includes comprehensive mock data generation for testing without Azure resources.

## 📡 API Functions

### Core Functions

```python
# Monitor pipelines
def get_adf_pipeline_status() -> List[PipelineRun]

# Analyze failures with AI  
def analyze_failure_with_genai(pipeline_name: str, error_message: str, run_id: str) -> Dict[str, Any]

# Determine retry action
def should_rerun_pipeline(analysis_result: Dict[str, Any], pipeline_name: str) -> Tuple[bool, str]

# Execute pipeline retry
def rerun_pipeline(pipeline_name: str, run_id: str = None) -> bool

# Log decisions and actions
def log_decision_and_action(run_id: str, analysis_result: Dict[str, Any], action_taken: str, success: bool) -> str
```

## 🔔 Notification Channels

### Console Alerts
- Real-time console output with formatted alerts
- Color-coded severity levels
- Detailed error information

### Microsoft Teams
- Rich card notifications with pipeline details
- Color-coded by alert type (failure, retry, success)
- Actionable information for quick response

### Email Alerts
- Formatted email notifications
- Complete error details and recommended actions
- Configurable SMTP settings

## 📈 Monitoring Capabilities

- **Pipeline Status Tracking**: Success/failure rates by pipeline
- **Error Pattern Analysis**: Common failure types and trends
- **Retry Success Rates**: Effectiveness of automated retries
- **Time-based Analytics**: Failure patterns by time of day/week
- **Performance Metrics**: System response times and effectiveness

## 🔧 Production Deployment

### Scaling Considerations

1. **Database**: Consider PostgreSQL for production scale
2. **Message Queue**: Add Redis/RabbitMQ for high-volume processing
3. **Container Deployment**: Docker containers for easy deployment
4. **Monitoring**: Add application performance monitoring
5. **Security**: Implement proper secret management

### Recommended Architecture

```
Azure Container Instance
├── ADF Monitor (Main Service)
├── Dashboard (Streamlit)
├── PostgreSQL (Database)
└── Redis (Message Queue)
```

## 🔐 Security

- Store sensitive credentials in Azure Key Vault
- Use Managed Identity for Azure authentication
- Implement proper RBAC for ADF access
- Encrypt database connections
- Regular security audits of dependencies

## 📚 Dependencies

- **Core**: requests, openai, python-dotenv, schedule
- **Azure**: azure-identity, azure-mgmt-datafactory  
- **Database**: sqlite3 (built-in)
- **Dashboard**: streamlit, plotly, pandas
- **Testing**: pytest, unittest.mock
- **Notifications**: pymsteams, smtplib

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the test suite with `python test_system.py`
2. Run in debug mode with mock data
3. Review logs in the dashboard
4. Check configuration in `.env` file

## 🎯 Roadmap

- [ ] Integration with Azure Monitor Logs
- [ ] Machine Learning model for failure prediction
- [ ] Slack notification support
- [ ] REST API for external integrations
- [ ] Advanced retry strategies (exponential backoff)
- [ ] Pipeline dependency analysis
- [ ] Custom notification templates
- [ ] Multi-tenant support
