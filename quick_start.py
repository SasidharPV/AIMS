"""
Quick Start Script for ADF Monitoring System
"""
import os
import sys
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'requests',
        'openai', 
        'python-dotenv',
        'schedule'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install with: pip install " + " ".join(missing_packages))
        return False
    
    return True

def setup_environment():
    """Setup environment configuration"""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("📝 Creating .env file...")
        
        # Copy from example
        example_file = Path(".env.example")
        if example_file.exists():
            with open(example_file, 'r') as f:
                content = f.read()
            
            with open(env_file, 'w') as f:
                f.write(content)
            
            print("✅ .env file created from template")
            print("⚠️  Please edit .env file with your actual values before running")
            return False
        else:
            print("❌ .env.example file not found")
            return False
    
    return True

def run_tests():
    """Run system tests"""
    print("🧪 Running system tests...")
    
    try:
        from test_system import run_tests
        return run_tests()
    except ImportError as e:
        print(f"❌ Could not import test module: {e}")
        return False

def generate_mock_data():
    """Generate mock data for testing"""
    print("🎭 Generating mock data...")
    
    try:
        from mock_data import MockDataGenerator
        generator = MockDataGenerator()
        generator.save_mock_data_to_file("mock_data.json")
        print("✅ Mock data generated successfully")
        return True
    except Exception as e:
        print(f"❌ Error generating mock data: {e}")
        return False

def start_monitoring():
    """Start the monitoring system"""
    print("🚀 Starting ADF monitoring system...")
    
    try:
        from adf_monitor import main
        main()
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped by user")
    except Exception as e:
        print(f"❌ Error starting monitoring: {e}")

def start_dashboard():
    """Start the Streamlit dashboard"""
    print("📊 Starting dashboard...")
    
    try:
        import subprocess
        subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard.py"])
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        print("💡 Make sure Streamlit is installed: pip install streamlit")

def main_menu():
    """Main menu for quick start"""
    print("🏭 ADF Monitoring & Automation System - Quick Start")
    print("===================================================")
    
    while True:
        print("\nChoose an option:")
        print("1. 🔧 Check dependencies")
        print("2. ⚙️  Setup environment (.env)")
        print("3. 🧪 Run tests")
        print("4. 🎭 Generate mock data")
        print("5. 🚀 Start monitoring (console)")
        print("6. 📊 Start dashboard (Streamlit)")
        print("7. 🔍 Run single monitoring cycle")
        print("8. ❌ Exit")
        
        choice = input("\nEnter your choice (1-8): ").strip()
        
        if choice == "1":
            if check_dependencies():
                print("✅ All dependencies are installed")
            
        elif choice == "2":
            if setup_environment():
                print("✅ Environment already configured")
            
        elif choice == "3":
            run_tests()
            
        elif choice == "4":
            generate_mock_data()
            
        elif choice == "5":
            if not check_dependencies():
                continue
            if not setup_environment():
                print("⚠️  Please configure .env file first")
                continue
            start_monitoring()
            
        elif choice == "6":
            if not check_dependencies():
                continue
            start_dashboard()
            
        elif choice == "7":
            if not check_dependencies():
                continue
            if not setup_environment():
                print("⚠️  Please configure .env file first")
                continue
            print("🔍 Running single monitoring cycle...")
            try:
                from adf_monitor import ADFMonitoringSystem
                monitor = ADFMonitoringSystem()
                monitor.start_monitoring(run_once=True)
            except Exception as e:
                print(f"❌ Error: {e}")
            
        elif choice == "8":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()
