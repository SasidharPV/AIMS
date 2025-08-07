#!/usr/bin/env python3
"""
ADF Monitor Pro - GitHub Deployment Status Checker
Verifies that all deployment components are ready for GitHub
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple

# Colors for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_status(message: str, status: str = "info"):
    """Print colored status messages"""
    colors = {
        "success": f"{Colors.GREEN}✅",
        "error": f"{Colors.RED}❌", 
        "warning": f"{Colors.YELLOW}⚠️",
        "info": f"{Colors.BLUE}ℹ️",
        "check": f"{Colors.CYAN}🔍"
    }
    print(f"{colors.get(status, colors['info'])} {message}{Colors.END}")

def check_file_exists(file_path: str) -> bool:
    """Check if a file exists"""
    return Path(file_path).exists()

def check_git_repository() -> Tuple[bool, str]:
    """Check if we're in a git repository"""
    try:
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            return True, "Git repository detected"
        else:
            return False, "Not a git repository"
    except FileNotFoundError:
        return False, "Git not installed"

def check_requirements_file() -> Tuple[bool, str]:
    """Check if requirements_webapp.txt exists and has required packages"""
    if not check_file_exists("requirements_webapp.txt"):
        return False, "requirements_webapp.txt not found"
    
    required_packages = ["streamlit", "plotly", "pandas", "requests"]
    
    try:
        with open("requirements_webapp.txt", "r") as f:
            content = f.read().lower()
            missing = [pkg for pkg in required_packages if pkg not in content]
            
        if missing:
            return False, f"Missing required packages: {', '.join(missing)}"
        else:
            return True, "All required packages found"
    except Exception as e:
        return False, f"Error reading requirements file: {e}"

def check_webapp_file() -> Tuple[bool, str]:
    """Check if webapp.py exists and has required functions"""
    if not check_file_exists("webapp.py"):
        return False, "webapp.py not found"
    
    try:
        with open("webapp.py", "r") as f:
            content = f.read()
            
        # Check for key Streamlit components
        required_components = ["st.title", "st.sidebar", "main"]
        missing = [comp for comp in required_components if comp not in content]
        
        if missing:
            return False, f"webapp.py missing components: {', '.join(missing)}"
        else:
            return True, "webapp.py contains required Streamlit components"
    except Exception as e:
        return False, f"Error reading webapp.py: {e}"

def check_github_actions() -> Tuple[bool, str]:
    """Check GitHub Actions workflow file"""
    workflow_path = ".github/workflows/deploy-webapp.yml"
    if not check_file_exists(workflow_path):
        return False, "GitHub Actions workflow not found"
    
    try:
        with open(workflow_path, "r") as f:
            content = f.read()
            
        required_jobs = ["test", "deploy-pages"]
        missing_jobs = [job for job in required_jobs if job not in content]
        
        if missing_jobs:
            return False, f"Missing workflow jobs: {', '.join(missing_jobs)}"
        else:
            return True, "GitHub Actions workflow configured correctly"
    except Exception as e:
        return False, f"Error reading workflow file: {e}"

def check_codespaces_config() -> Tuple[bool, str]:
    """Check GitHub Codespaces configuration"""
    config_path = ".devcontainer/devcontainer.json"
    if not check_file_exists(config_path):
        return False, "Codespaces configuration not found"
    
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
            
        required_fields = ["name", "image", "forwardPorts"]
        missing = [field for field in required_fields if field not in config]
        
        if missing:
            return False, f"Missing configuration fields: {', '.join(missing)}"
        
        if 8501 not in config.get("forwardPorts", []):
            return False, "Port 8501 not configured for forwarding"
            
        return True, "Codespaces configuration valid"
    except json.JSONDecodeError:
        return False, "Invalid JSON in devcontainer.json"
    except Exception as e:
        return False, f"Error reading Codespaces config: {e}"

def check_docker_config() -> Tuple[bool, str]:
    """Check Docker configuration"""
    if not check_file_exists("Dockerfile"):
        return False, "Dockerfile not found"
    
    try:
        with open("Dockerfile", "r") as f:
            content = f.read()
            
        required_instructions = ["FROM", "COPY", "RUN", "EXPOSE", "CMD"]
        missing = [inst for inst in required_instructions if inst not in content]
        
        if missing:
            return False, f"Missing Dockerfile instructions: {', '.join(missing)}"
        
        if "8501" not in content:
            return False, "Port 8501 not exposed in Dockerfile"
            
        return True, "Docker configuration valid"
    except Exception as e:
        return False, f"Error reading Dockerfile: {e}"

def check_environment_config() -> Tuple[bool, str]:
    """Check environment configuration"""
    if not check_file_exists(".env.sample"):
        return False, ".env.sample not found"
    
    try:
        with open(".env.sample", "r") as f:
            content = f.read()
            
        required_vars = ["AZURE_TENANT_ID", "AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET"]
        missing = [var for var in required_vars if var not in content]
        
        if missing:
            return False, f"Missing environment variables: {', '.join(missing)}"
            
        return True, "Environment configuration template found"
    except Exception as e:
        return False, f"Error reading .env.sample: {e}"

def run_deployment_check():
    """Run comprehensive deployment readiness check"""
    print(f"{Colors.BOLD}{Colors.CYAN}🏭 ADF Monitor Pro - Deployment Readiness Check{Colors.END}")
    print("=" * 60)
    print()
    
    checks = [
        ("Git Repository", check_git_repository),
        ("Requirements File", check_requirements_file),
        ("Web Application", check_webapp_file),
        ("GitHub Actions", check_github_actions),
        ("Codespaces Config", check_codespaces_config),
        ("Docker Config", check_docker_config),
        ("Environment Config", check_environment_config),
    ]
    
    results = []
    for check_name, check_func in checks:
        print_status(f"Checking {check_name}...", "check")
        success, message = check_func()
        
        if success:
            print_status(f"{check_name}: {message}", "success")
        else:
            print_status(f"{check_name}: {message}", "error")
            
        results.append((check_name, success, message))
    
    print()
    print(f"{Colors.BOLD}📊 Summary{Colors.END}")
    print("-" * 30)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    if passed == total:
        print_status(f"All {total} checks passed! 🎉", "success")
        print()
        print_status("Your repository is ready for GitHub deployment!", "success")
        print()
        print(f"{Colors.BOLD}🚀 Next Steps:{Colors.END}")
        print("1. Push your code to GitHub")
        print("2. Enable GitHub Pages in repository settings")
        print("3. Launch in Codespaces to test")
        print("4. Share your deployment URL!")
        
        return True
    else:
        print_status(f"{passed}/{total} checks passed", "warning")
        print()
        print_status("Please fix the issues above before deploying", "error")
        
        print()
        print(f"{Colors.BOLD}❌ Failed Checks:{Colors.END}")
        for name, success, message in results:
            if not success:
                print(f"   • {name}: {message}")
        
        return False

if __name__ == "__main__":
    success = run_deployment_check()
    sys.exit(0 if success else 1)
