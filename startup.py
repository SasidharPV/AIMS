"""
Enterprise ADF Monitor Pro - Startup and Launcher Script
Handles initialization, dependency checking, and app launching
"""
import os
import sys
import subprocess
import json
import time
from pathlib import Path
from typing import List, Dict, Any

def check_python_version() -> bool:
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False

def check_dependencies() -> Dict[str, bool]:
    """Check if required dependencies are installed"""
    required_packages = [
        "streamlit",
        "plotly", 
        "pandas",
        "yaml",  # PyYAML imports as 'yaml'
        "requests",
        "dotenv"  # python-dotenv imports as 'dotenv'
    ]
    
    optional_packages = [
        "openai",
        "anthropic", 
        "google-generativeai",
        "azure-identity",
        "azure-mgmt-datafactory"
    ]
    
    results = {"required": {}, "optional": {}}
    
    print("\n🔍 Checking required dependencies...")
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"  ✅ {package}")
            results["required"][package] = True
        except ImportError:
            print(f"  ❌ {package} - Missing")
            results["required"][package] = False
    
    print("\n🔍 Checking optional dependencies...")
    for package in optional_packages:
        try:
            if package == "google-generativeai":
                __import__("google.generativeai")
            else:
                __import__(package.replace("-", "_"))
            print(f"  ✅ {package}")
            results["optional"][package] = True
        except ImportError:
            print(f"  ⚠️  {package} - Optional (features limited)")
            results["optional"][package] = False
    
    return results

def install_dependencies(missing_packages: List[str]) -> bool:
    """Install missing dependencies"""
    if not missing_packages:
        return True
    
    print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
    
    try:
        # Create requirements for missing packages
        requirements_content = "\n".join(missing_packages)
        
        with open("temp_requirements.txt", "w") as f:
            f.write(requirements_content)
        
        # Install packages
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "temp_requirements.txt"
        ], capture_output=True, text=True)
        
        # Clean up temp file
        os.remove("temp_requirements.txt")
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully!")
            return True
        else:
            print(f"❌ Failed to install dependencies: {result.stderr}")
            return False
    
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def initialize_configuration():
    """Initialize configuration files"""
    print("\n⚙️ Initializing configuration...")
    
    try:
        # Import and initialize config manager
        from enterprise_config import get_config_manager
        config_manager = get_config_manager()
        
        print("✅ Configuration files initialized")
        return True
    
    except Exception as e:
        print(f"❌ Error initializing configuration: {e}")
        return False

def create_sample_env_file():
    """Create sample environment file"""
    env_content = """# ADF Monitor Pro - Environment Configuration
# Copy this file to .env and update with your actual values

# Azure Configuration
AZURE_TENANT_ID=your-tenant-id-here
AZURE_CLIENT_ID=your-client-id-here
AZURE_CLIENT_SECRET=your-client-secret-here
AZURE_SUBSCRIPTION_ID=your-subscription-id-here

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.3

# Azure OpenAI Configuration (alternative)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-azure-openai-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name

# Google AI Configuration
GOOGLE_AI_API_KEY=your-google-api-key-here

# Anthropic Configuration
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Notification Configuration
TEAMS_WEBHOOK_URL=https://your-company.webhook.office.com/...
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@company.com
SMTP_PASSWORD=your-app-password
EMAIL_RECIPIENTS=admin@company.com,devops@company.com

# Application Configuration
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///adf_monitor_enterprise.db
ENABLE_AUTHENTICATION=false
SESSION_TIMEOUT_HOURS=8
"""
    
    env_file = Path(".env.sample")
    if not env_file.exists():
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✅ Sample environment file created (.env.sample)")
    else:
        print("⚠️  Sample environment file already exists")

def setup_database():
    """Setup application database"""
    print("\n🗄️ Setting up database...")
    
    try:
        from webapp import WebAppManager
        webapp_manager = WebAppManager()
        print("✅ Database initialized successfully")
        return True
    
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False

def check_port_availability(port: int = 8501) -> bool:
    """Check if the default Streamlit port is available"""
    import socket
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def launch_application(mode: str = "webapp", port: int = 8501):
    """Launch the application"""
    print(f"\n🚀 Launching ADF Monitor Pro...")
    
    if mode == "webapp":
        # Check port availability
        if not check_port_availability(port):
            print(f"⚠️  Port {port} is busy, trying port {port + 1}")
            port += 1
            if not check_port_availability(port):
                print(f"❌ Port {port} is also busy. Please specify a different port.")
                return False
        
        print(f"🌐 Starting web application on http://localhost:{port}")
        print("📖 Access the application in your browser")
        print("⏹️  Press Ctrl+C to stop the application")
        
        try:
            # Launch Streamlit app
            result = subprocess.run([
                sys.executable, "-m", "streamlit", "run", "webapp.py", 
                "--server.port", str(port),
                "--server.headless", "true",
                "--browser.gatherUsageStats", "false"
            ])
            
            return result.returncode == 0
        
        except KeyboardInterrupt:
            print("\n🛑 Application stopped by user")
            return True
        except Exception as e:
            print(f"❌ Error launching webapp: {e}")
            return False
    
    elif mode == "demo":
        print("🎬 Running demonstration...")
        try:
            from simple_demo import main as demo_main
            demo_main()
            return True
        except Exception as e:
            print(f"❌ Error running demo: {e}")
            return False
    
    elif mode == "test":
        print("🧪 Running tests...")
        try:
            result = subprocess.run([sys.executable, "test_system.py"])
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Error running tests: {e}")
            return False

def print_banner():
    """Print application banner"""
    banner = """
███████╗██████╗░███████╗  ███╗░░░███╗░█████╗░███╗░░██╗██╗████████╗░█████╗░██████╗░
██║░░██║██╔══██╗██╔════╝  ████╗░████║██╔══██╗████╗░██║██║╚══██╔══╝██╔══██╗██╔══██╗
███████║██║░░██║█████╗░░  ██╔████╔██║██║░░██║██╔██╗██║██║░░░██║░░░██║░░██║██████╔╝
██╔══██║██║░░██║██╔══╝░░  ██║╚██╔╝██║██║░░██║██║╚████║██║░░░██║░░░██║░░██║██╔══██╗
██║░░██║██████╔╝██║░░░░░  ██║░╚═╝░██║╚█████╔╝██║░╚███║██║░░░██║░░░╚█████╔╝██║░░██║
╚═╝░░╚═╝╚═════╝░╚═╝░░░░░  ╚═╝░░░░░╚═╝░╚════╝░╚═╝░░╚══╝╚═╝░░░╚═╝░░░░╚════╝░╚═╝░░╚═╝

                    ██████╗░██████╗░░█████╗░
                    ██╔══██╗██╔══██╗██╔══██╗
                    ██████╔╝██████╔╝██║░░██║
                    ██╔═══╝░██╔══██╗██║░░██║
                    ██║░░░░░██║░░██║╚█████╔╝
                    ╚═╝░░░░░╚═╝░░╚═╝░╚════╝░

           🏭 Enterprise Azure Data Factory Monitoring & Automation
           🤖 AI-Powered Pipeline Management • Multi-Environment Support
           📊 Real-time Dashboards • Intelligent Error Analysis
    """
    
    print(banner)
    print("=" * 80)

def show_help():
    """Show help information"""
    help_text = """
🆘 ADF Monitor Pro - Help

USAGE:
  python startup.py [COMMAND] [OPTIONS]

COMMANDS:
  webapp      Launch the web application (default)
  demo        Run a demonstration of the system
  test        Run system tests
  setup       Initial setup and configuration
  help        Show this help message

OPTIONS:
  --port PORT     Specify port for webapp (default: 8501)
  --install-deps  Auto-install missing dependencies
  --skip-checks   Skip dependency checks

EXAMPLES:
  python startup.py                    # Launch webapp on default port
  python startup.py webapp --port 8080 # Launch webapp on port 8080
  python startup.py demo               # Run demonstration
  python startup.py setup             # Initial setup
  python startup.py --install-deps    # Install dependencies and launch

CONFIGURATION:
  1. Copy .env.sample to .env
  2. Update .env with your Azure and AI provider credentials
  3. Modify config/environments.yaml for your ADF environments
  4. Configure AI providers in config/ai_providers.yaml

SUPPORT:
  - Documentation: See README.md
  - Configuration Guide: config/README.md
  - Troubleshooting: Check logs/ directory
"""
    print(help_text)

def main():
    """Main startup function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ADF Monitor Pro Startup")
    parser.add_argument("command", nargs="?", default="webapp", 
                       choices=["webapp", "demo", "test", "setup", "help"],
                       help="Command to execute")
    parser.add_argument("--port", type=int, default=8501,
                       help="Port for webapp (default: 8501)")
    parser.add_argument("--install-deps", action="store_true",
                       help="Auto-install missing dependencies")
    parser.add_argument("--skip-checks", action="store_true",
                       help="Skip dependency checks")
    
    args = parser.parse_args()
    
    # Show help
    if args.command == "help":
        show_help()
        return
    
    # Print banner
    print_banner()
    
    # Check Python version
    if not check_python_version():
        print("\n❌ Incompatible Python version. Please upgrade to Python 3.8+")
        sys.exit(1)
    
    # Check dependencies
    if not args.skip_checks:
        deps = check_dependencies()
        
        # Check for missing required dependencies
        missing_required = [pkg for pkg, installed in deps["required"].items() if not installed]
        
        if missing_required:
            if args.install_deps:
                if not install_dependencies(missing_required):
                    print("\n❌ Failed to install required dependencies")
                    sys.exit(1)
            else:
                print(f"\n❌ Missing required dependencies: {', '.join(missing_required)}")
                print("Run with --install-deps to auto-install or install manually:")
                print(f"  pip install {' '.join(missing_required)}")
                sys.exit(1)
    
    # Setup and initialization
    if args.command == "setup" or not Path("config").exists():
        print("\n🔧 Running initial setup...")
        
        # Create sample environment file
        create_sample_env_file()
        
        # Initialize configuration
        if not initialize_configuration():
            print("❌ Setup failed")
            sys.exit(1)
        
        # Setup database
        if not setup_database():
            print("❌ Database setup failed")
            sys.exit(1)
        
        print("\n✅ Setup completed successfully!")
        
        if args.command == "setup":
            print("\n📝 Next steps:")
            print("1. Copy .env.sample to .env and update with your credentials")
            print("2. Review configuration files in config/ directory")
            print("3. Run 'python startup.py webapp' to start the application")
            return
    
    # Launch application
    print("\n🚀 Starting ADF Monitor Pro...")
    success = launch_application(args.command, args.port)
    
    if success:
        print("\n✅ Application completed successfully!")
    else:
        print("\n❌ Application failed to start")
        sys.exit(1)

if __name__ == "__main__":
    main()
