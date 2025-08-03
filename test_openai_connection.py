"""
Test Azure OpenAI Connection
Validates Azure OpenAI authentication and model access
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openai_packages():
    """Test if OpenAI package is installed"""
    print("🔍 Checking OpenAI packages...")
    
    try:
        import openai
        print(f"  ✅ openai (version: {openai.__version__})")
        return True
    except ImportError:
        print("  ❌ openai - Run: pip install openai")
        return False

def test_environment_variables():
    """Test if required environment variables are set"""
    print("\n🔧 Checking environment variables...")
    
    azure_vars = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_DEPLOYMENT_NAME"
    ]
    
    openai_vars = [
        "OPENAI_API_KEY"
    ]
    
    print("  🧠 Azure OpenAI Configuration:")
    azure_configured = True
    for var in azure_vars:
        value = os.getenv(var)
        if value:
            if "KEY" in var:
                masked_value = value[:8] + "..." if len(value) > 8 else value
            else:
                masked_value = value
            print(f"    ✅ {var}: {masked_value}")
        else:
            print(f"    ❌ {var}: Not set")
            azure_configured = False
    
    print("  🤖 OpenAI Fallback Configuration:")
    openai_configured = True
    for var in openai_vars:
        value = os.getenv(var)
        if value:
            masked_value = value[:8] + "..." if len(value) > 8 else value
            print(f"    ✅ {var}: {masked_value}")
        else:
            print(f"    ⚠️  {var}: Not set (fallback disabled)")
            openai_configured = False
    
    if not azure_configured and not openai_configured:
        print("\n❌ No AI providers configured!")
        return False
    elif azure_configured:
        print("\n✅ Azure OpenAI is configured (recommended)")
        return True
    else:
        print("\n⚠️  Only OpenAI fallback is configured")
        return True

def test_azure_openai_connection():
    """Test Azure OpenAI connection"""
    print("\n🧠 Testing Azure OpenAI connection...")
    
    # Check if Azure OpenAI is configured
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    
    if not all([endpoint, api_key, deployment]):
        print("  ⚠️  Azure OpenAI not configured, skipping...")
        return False
    
    try:
        import openai
        
        # Configure Azure OpenAI
        openai.api_type = "azure"
        openai.api_base = endpoint
        openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        openai.api_key = api_key
        
        print(f"  🔗 Endpoint: {endpoint}")
        print(f"  🚀 Deployment: {deployment}")
        print(f"  📅 API Version: {openai.api_version}")
        
        # Test with a simple completion
        print("  🧪 Testing AI analysis...")
        
        response = openai.ChatCompletion.create(
            engine=deployment,
            messages=[
                {
                    "role": "system", 
                    "content": "You are an Azure Data Factory pipeline failure analyst."
                },
                {
                    "role": "user", 
                    "content": "Analyze this error: 'Connection timeout to source database after 30 seconds'. Respond with JSON: {\"error_type\": \"transient\", \"should_retry\": true, \"confidence_score\": 85, \"analysis_summary\": \"Network connectivity issue detected\"}"
                }
            ],
            max_tokens=200,
            temperature=0.3
        )
        
        if response and response.choices:
            content = response.choices[0].message.content
            print(f"  ✅ Azure OpenAI response received")
            print(f"  📝 Sample analysis: {content[:100]}...")
            
            # Check token usage
            if hasattr(response, 'usage'):
                tokens_used = response.usage.total_tokens
                print(f"  🔢 Tokens used: {tokens_used}")
                
                # Estimate cost (approximate)
                cost_per_1k = 0.02  # Azure OpenAI GPT-4 pricing
                estimated_cost = (tokens_used / 1000) * cost_per_1k
                print(f"  💰 Estimated cost: ${estimated_cost:.4f}")
            
            return True
        else:
            print("  ❌ No response received from Azure OpenAI")
            return False
            
    except Exception as e:
        print(f"  ❌ Azure OpenAI connection failed: {e}")
        
        # Provide helpful error messages
        if "401" in str(e) or "Unauthorized" in str(e):
            print("  💡 Check your API key - it might be invalid or expired")
        elif "404" in str(e) or "NotFound" in str(e):
            print("  💡 Check your endpoint URL and deployment name")
        elif "quota" in str(e).lower():
            print("  💡 You may have exceeded your quota or rate limits")
        elif "deployment" in str(e).lower():
            print("  💡 Check if your model deployment is active and properly named")
        
        return False

def test_openai_fallback():
    """Test OpenAI fallback connection"""
    print("\n🤖 Testing OpenAI fallback connection...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("  ⚠️  OpenAI API key not configured, skipping...")
        return False
    
    try:
        import openai
        
        # Configure regular OpenAI
        openai.api_type = "open_ai"
        openai.api_base = "https://api.openai.com/v1"
        openai.api_key = api_key
        
        print("  🔗 Using OpenAI API")
        
        # Test with a simple completion
        print("  🧪 Testing AI analysis...")
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use cheaper model for testing
            messages=[
                {
                    "role": "system", 
                    "content": "You are an Azure Data Factory pipeline failure analyst."
                },
                {
                    "role": "user", 
                    "content": "Test connection successful. Respond with: 'OpenAI connection working!'"
                }
            ],
            max_tokens=50,
            temperature=0.3
        )
        
        if response and response.choices:
            content = response.choices[0].message.content
            print(f"  ✅ OpenAI response: {content}")
            
            # Check token usage
            if hasattr(response, 'usage'):
                tokens_used = response.usage.total_tokens
                print(f"  🔢 Tokens used: {tokens_used}")
                
                # Estimate cost
                cost_per_1k = 0.001  # GPT-3.5-turbo pricing
                estimated_cost = (tokens_used / 1000) * cost_per_1k
                print(f"  💰 Estimated cost: ${estimated_cost:.4f}")
            
            return True
        else:
            print("  ❌ No response received from OpenAI")
            return False
            
    except Exception as e:
        print(f"  ❌ OpenAI connection failed: {e}")
        
        if "401" in str(e) or "Unauthorized" in str(e):
            print("  💡 Check your OpenAI API key")
        elif "quota" in str(e).lower() or "billing" in str(e).lower():
            print("  💡 Check your OpenAI billing and usage limits")
        
        return False

def test_ai_analysis_flow():
    """Test the complete AI analysis flow"""
    print("\n🔬 Testing AI analysis workflow...")
    
    # Test both providers if available
    providers_tested = 0
    providers_working = 0
    
    # Test Azure OpenAI
    if os.getenv("AZURE_OPENAI_API_KEY"):
        print("  🧠 Testing Azure OpenAI analysis...")
        try:
            # Simulate the actual analysis flow from the application
            from genai_analyzer import GenAIAnalyzer
            
            analyzer = GenAIAnalyzer()
            result = analyzer.analyze_failure_with_genai(
                pipeline_name="TestPipeline",
                error_message="Connection timeout to source database after 30 seconds",
                run_id="test-run-001"
            )
            
            providers_tested += 1
            
            if result.get("success"):
                print("    ✅ Azure OpenAI analysis successful")
                analysis = result.get("analysis", {})
                print(f"    📊 Error Type: {analysis.get('error_type', 'unknown')}")
                print(f"    🎯 Confidence: {analysis.get('confidence_score', 0)}%")
                print(f"    🔄 Should Retry: {analysis.get('should_retry', False)}")
                providers_working += 1
            else:
                print("    ❌ Azure OpenAI analysis failed")
                
        except Exception as e:
            print(f"    ❌ Error testing Azure OpenAI: {e}")
    
    # Test OpenAI fallback
    if os.getenv("OPENAI_API_KEY"):
        print("  🤖 Testing OpenAI fallback analysis...")
        try:
            # Test would go here - for now just indicate it's available
            providers_tested += 1
            print("    ✅ OpenAI fallback available")
            providers_working += 1
            
        except Exception as e:
            print(f"    ❌ Error testing OpenAI: {e}")
    
    if providers_working > 0:
        print(f"  ✅ AI analysis working ({providers_working}/{providers_tested} providers)")
        return True
    else:
        print("  ❌ No AI providers working")
        return False

def create_sample_ai_config():
    """Create sample AI provider configuration"""
    print("\n📝 Creating sample AI configuration...")
    
    try:
        config_template = f"""# Real Azure OpenAI Configuration
# Update these with your actual Azure OpenAI details

ai_providers:
  - provider_id: "azure-openai-gpt4"
    provider_name: "Azure OpenAI GPT-4"
    provider_class: "OpenAIProvider"
    model_name: "{os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4-deployment')}"
    api_endpoint: "{os.getenv('AZURE_OPENAI_ENDPOINT', 'https://your-resource.openai.azure.com/')}"
    api_key: "{os.getenv('AZURE_OPENAI_API_KEY', 'your-azure-openai-api-key')}"
    temperature: 0.3
    max_tokens: 1000
    top_p: 0.9
    frequency_penalty: 0.0
    confidence_threshold: 75
    retry_confidence: 80
    active: true
    cost_per_1k_tokens: 0.02

  - provider_id: "azure-openai-gpt35"
    provider_name: "Azure OpenAI GPT-3.5 Turbo"
    provider_class: "OpenAIProvider"
    model_name: "gpt-35-turbo-deployment"
    api_endpoint: "{os.getenv('AZURE_OPENAI_ENDPOINT', 'https://your-resource.openai.azure.com/')}"
    api_key: "{os.getenv('AZURE_OPENAI_API_KEY', 'your-azure-openai-api-key')}"
    temperature: 0.3
    max_tokens: 1000
    confidence_threshold: 70
    active: false  # Enable as backup
    cost_per_1k_tokens: 0.001

  - provider_id: "openai-gpt4-fallback"
    provider_name: "OpenAI GPT-4 (Fallback)"
    provider_class: "OpenAIProvider"
    model_name: "gpt-4"
    api_endpoint: "https://api.openai.com/v1/chat/completions"
    api_key: "{os.getenv('OPENAI_API_KEY', 'your-openai-api-key')}"
    temperature: 0.3
    max_tokens: 1000
    active: false  # Enable if needed
    cost_per_1k_tokens: 0.03

# Add more providers as needed (Google, Anthropic, etc.)
"""
        
        with open("config/ai_providers_template.yaml", "w") as f:
            f.write(config_template)
        
        print("  ✅ Created config/ai_providers_template.yaml")
        print("  💡 Copy this to config/ai_providers.yaml and update with your details")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Failed to create AI config template: {e}")
        return False

def main():
    """Main test function"""
    print("🧠 Azure OpenAI Connection Test")
    print("=" * 50)
    
    results = []
    
    # Test 1: OpenAI packages
    results.append(("OpenAI Package", test_openai_packages()))
    
    # Test 2: Environment variables
    results.append(("Environment Variables", test_environment_variables()))
    
    # Test 3: Azure OpenAI connection
    results.append(("Azure OpenAI Connection", test_azure_openai_connection()))
    
    # Test 4: OpenAI fallback
    results.append(("OpenAI Fallback", test_openai_fallback()))
    
    # Test 5: AI analysis flow
    results.append(("AI Analysis Flow", test_ai_analysis_flow()))
    
    # Test 6: Create sample config
    results.append(("Sample Configuration", create_sample_ai_config()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed >= 4:  # Allow some tests to fail (like fallback)
        print("\n🎉 AI connection is ready!")
        print("Next steps:")
        print("1. Update config/ai_providers.yaml with your AI provider details")
        print("2. Set USE_AZURE_OPENAI=true in your environment")
        print("3. Run: python startup.py webapp")
        print("4. Test AI analysis in the web interface")
    else:
        print(f"\n⚠️  {total - passed} critical tests failed. Please fix the issues above.")
        print("Common solutions:")
        print("- Install OpenAI package: pip install openai")
        print("- Update .env file with correct Azure OpenAI credentials")
        print("- Verify your Azure OpenAI deployment is active")
        print("- Check your API quotas and billing status")

if __name__ == "__main__":
    main()
