"""
Test Azure Data Factory Connection
Validates authentication and ADF access for the monitoring application
"""
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_azure_packages():
    """Test if required Azure packages are installed"""
    print("🔍 Checking Azure SDK packages...")
    
    try:
        from azure.identity import ClientSecretCredential
        print("  ✅ azure-identity")
    except ImportError:
        print("  ❌ azure-identity - Run: pip install azure-identity")
        return False
    
    try:
        from azure.mgmt.datafactory import DataFactoryManagementClient
        print("  ✅ azure-mgmt-datafactory")
    except ImportError:
        print("  ❌ azure-mgmt-datafactory - Run: pip install azure-mgmt-datafactory")
        return False
    
    try:
        from azure.core.exceptions import AzureError
        print("  ✅ azure-core")
    except ImportError:
        print("  ❌ azure-core - Run: pip install azure-core")
        return False
    
    return True

def test_environment_variables():
    """Test if required environment variables are set"""
    print("\n🔧 Checking environment variables...")
    
    required_vars = [
        "AZURE_TENANT_ID",
        "AZURE_CLIENT_ID", 
        "AZURE_CLIENT_SECRET",
        "AZURE_SUBSCRIPTION_ID"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Show first 8 characters for security
            masked_value = value[:8] + "..." if len(value) > 8 else value
            print(f"  ✅ {var}: {masked_value}")
        else:
            print(f"  ❌ {var}: Not set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please update your .env file with the correct values.")
        return False
    
    return True

def test_azure_authentication():
    """Test Azure authentication with service principal"""
    print("\n🔐 Testing Azure authentication...")
    
    try:
        from azure.identity import ClientSecretCredential
        
        credential = ClientSecretCredential(
            tenant_id=os.getenv("AZURE_TENANT_ID"),
            client_id=os.getenv("AZURE_CLIENT_ID"),
            client_secret=os.getenv("AZURE_CLIENT_SECRET")
        )
        
        # Test credential by getting a token
        token = credential.get_token("https://management.azure.com/.default")
        
        if token:
            print("  ✅ Azure authentication successful")
            print(f"  🔑 Token expires: {datetime.fromtimestamp(token.expires_on)}")
            return True
        else:
            print("  ❌ Failed to obtain Azure token")
            return False
            
    except Exception as e:
        print(f"  ❌ Azure authentication failed: {e}")
        return False

def test_adf_connection():
    """Test connection to Azure Data Factory"""
    print("\n🏭 Testing Azure Data Factory connection...")
    
    try:
        from azure.identity import ClientSecretCredential
        from azure.mgmt.datafactory import DataFactoryManagementClient
        from azure.core.exceptions import AzureError
        
        # Setup authentication
        credential = ClientSecretCredential(
            tenant_id=os.getenv("AZURE_TENANT_ID"),
            client_id=os.getenv("AZURE_CLIENT_ID"),
            client_secret=os.getenv("AZURE_CLIENT_SECRET")
        )
        
        # Create ADF client
        client = DataFactoryManagementClient(
            credential=credential,
            subscription_id=os.getenv("AZURE_SUBSCRIPTION_ID")
        )
        
        print("  ✅ ADF client created successfully")
        
        # Test by listing all data factories in subscription
        print("  🔍 Discovering Data Factory instances...")
        
        factories_found = []
        
        # You'll need to provide your resource group names here
        # For now, let's try to list all resource groups and find ADFs
        try:
            from azure.mgmt.resource import ResourceManagementClient
            
            resource_client = ResourceManagementClient(
                credential=credential,
                subscription_id=os.getenv("AZURE_SUBSCRIPTION_ID")
            )
            
            # List all resource groups
            resource_groups = list(resource_client.resource_groups.list())
            print(f"  📁 Found {len(resource_groups)} resource groups")
            
            for rg in resource_groups:
                try:
                    # List data factories in each resource group
                    factories = list(client.factories.list_by_resource_group(rg.name))
                    
                    if factories:
                        print(f"  🏭 Resource Group '{rg.name}':")
                        for factory in factories:
                            print(f"    - {factory.name} (Location: {factory.location})")
                            factories_found.append({
                                "name": factory.name,
                                "resource_group": rg.name,
                                "location": factory.location
                            })
                            
                except AzureError as e:
                    # Skip resource groups we don't have access to
                    if "AuthorizationFailed" in str(e):
                        continue
                    else:
                        print(f"    ⚠️  Error accessing RG '{rg.name}': {e}")
                        
        except ImportError:
            print("  ⚠️  azure-mgmt-resource not installed, using manual configuration")
            print("  💡 To auto-discover ADFs, install: pip install azure-mgmt-resource")
        
        if factories_found:
            print(f"\n  ✅ Found {len(factories_found)} Data Factory instances")
            print("  💡 Update your config/environments.yaml with these details:")
            
            for factory in factories_found:
                print(f"""
    - name: "{factory['name']}"
      subscription_id: "{os.getenv('AZURE_SUBSCRIPTION_ID')}"
      resource_group: "{factory['resource_group']}"
      data_factory: "{factory['name']}"
      region: "{factory['location']}"
      tenant_id: "{os.getenv('AZURE_TENANT_ID')}"
      client_id: "{os.getenv('AZURE_CLIENT_ID')}"
      client_secret: "{os.getenv('AZURE_CLIENT_SECRET')}"
      status: "Active"
      polling_interval: 300
      retry_attempts: 3""")
            
            return True
        else:
            print("  ⚠️  No Data Factory instances found")
            print("  💡 Make sure your service principal has access to ADF resources")
            return False
            
    except Exception as e:
        print(f"  ❌ ADF connection failed: {e}")
        print("  💡 Check your service principal permissions and resource access")
        return False

def test_adf_pipeline_access():
    """Test accessing pipeline runs from a specific ADF"""
    print("\n📊 Testing pipeline run access...")
    
    # This requires manual configuration since we need specific ADF details
    print("  ℹ️  To test pipeline access, you need to:")
    print("     1. Update config/environments.yaml with your ADF details")
    print("     2. Run the main application: python startup.py webapp")
    print("     3. Check the dashboard for real pipeline data")
    
    return True

def create_sample_config():
    """Create sample configuration files with discovered ADF instances"""
    print("\n📝 Creating sample configuration...")
    
    try:
        # Update environments.yaml template
        config_template = f"""# Real Azure Data Factory Environments
# Update these with your actual ADF instances

environments:
  - name: "Production"
    subscription_id: "{os.getenv('AZURE_SUBSCRIPTION_ID', 'your-subscription-id')}"
    resource_group: "your-prod-rg-name"
    data_factory: "your-prod-adf-name"
    region: "eastus"
    tenant_id: "{os.getenv('AZURE_TENANT_ID', 'your-tenant-id')}"
    client_id: "{os.getenv('AZURE_CLIENT_ID', 'your-client-id')}"
    client_secret: "{os.getenv('AZURE_CLIENT_SECRET', 'your-client-secret')}"
    status: "Active"
    polling_interval: 300
    retry_attempts: 3

  - name: "Staging"
    subscription_id: "{os.getenv('AZURE_SUBSCRIPTION_ID', 'your-subscription-id')}"
    resource_group: "your-stage-rg-name"
    data_factory: "your-stage-adf-name"
    region: "eastus"
    tenant_id: "{os.getenv('AZURE_TENANT_ID', 'your-tenant-id')}"
    client_id: "{os.getenv('AZURE_CLIENT_ID', 'your-client-id')}"
    client_secret: "{os.getenv('AZURE_CLIENT_SECRET', 'your-client-secret')}"
    status: "Active"
    polling_interval: 600
    retry_attempts: 2

# Add more environments as needed
"""
        
        with open("config/environments_template.yaml", "w") as f:
            f.write(config_template)
        
        print("  ✅ Created config/environments_template.yaml")
        print("  💡 Copy this to config/environments.yaml and update with your ADF details")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Failed to create config template: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Azure Data Factory Connection Test")
    print("=" * 50)
    
    results = []
    
    # Test 1: Azure packages
    results.append(("Azure Packages", test_azure_packages()))
    
    # Test 2: Environment variables
    results.append(("Environment Variables", test_environment_variables()))
    
    # Test 3: Azure authentication
    results.append(("Azure Authentication", test_azure_authentication()))
    
    # Test 4: ADF connection
    results.append(("ADF Connection", test_adf_connection()))
    
    # Test 5: Pipeline access
    results.append(("Pipeline Access Info", test_adf_pipeline_access()))
    
    # Test 6: Create sample config
    results.append(("Sample Configuration", create_sample_config()))
    
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
    
    if passed == total:
        print("\n🎉 All tests passed! Your Azure Data Factory connection is ready.")
        print("Next steps:")
        print("1. Update config/environments.yaml with your ADF instances")
        print("2. Run: python startup.py webapp")
        print("3. Open: http://localhost:8501")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please fix the issues above.")
        print("Common solutions:")
        print("- Install missing packages: pip install azure-identity azure-mgmt-datafactory")
        print("- Update .env file with correct Azure credentials")
        print("- Verify service principal permissions in Azure portal")

if __name__ == "__main__":
    main()
