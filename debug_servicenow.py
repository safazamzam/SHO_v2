#!/usr/bin/env python3
"""
Debug ServiceNow configuration and assignment groups
"""
from app import app
from services.servicenow_service import servicenow_service

with app.app_context():
    print("🔍 Debugging ServiceNow Configuration...")
    
    # Check if we can get secrets manager from the app
    try:
        from config import get_secrets_manager
        secrets_manager = get_secrets_manager()
    except ImportError:
        try:
            from models.secrets_manager import secrets_manager
            secrets_manager = secrets_manager
        except:
            print("❌ Could not import secrets manager")
            secrets_manager = None
    if secrets_manager:
        print("✅ Secrets manager available")
        
        # Check ServiceNow secrets
        servicenow_secrets = [
            'SERVICENOW_INSTANCE',
            'SERVICENOW_USERNAME', 
            'SERVICENOW_PASSWORD',
            'SERVICENOW_ENABLED',
            'SERVICENOW_ASSIGNMENT_GROUPS'
        ]
        
        print("\n📋 ServiceNow Secrets Status:")
        for secret_name in servicenow_secrets:
            try:
                value = secrets_manager.get_secret(secret_name)
                if value:
                    # Don't show full password, just indicate it exists
                    if 'PASSWORD' in secret_name:
                        print(f"   ✅ {secret_name}: *** (configured)")
                    elif secret_name == 'SERVICENOW_ASSIGNMENT_GROUPS':
                        print(f"   ✅ {secret_name}: {value}")
                    else:
                        print(f"   ✅ {secret_name}: {value}")
                else:
                    print(f"   ❌ {secret_name}: Not configured")
            except Exception as e:
                print(f"   ❌ {secret_name}: Error - {e}")
    else:
        print("❌ Secrets manager not available")
    
    print("\n🔧 ServiceNow Service Status:")
    
    # Initialize ServiceNow service
    try:
        servicenow_service.initialize(app)
        print("✅ ServiceNow service initialized")
        
        # Check if enabled and configured
        is_enabled = servicenow_service.is_enabled_and_configured()
        print(f"📊 ServiceNow enabled and configured: {is_enabled}")
        
        if is_enabled:
            # Get assignment groups
            assignment_groups = servicenow_service.get_configured_assignment_groups()
            print(f"👥 Assignment groups: {assignment_groups}")
            
            if assignment_groups:
                print("\n🔍 Testing ServiceNow connection...")
                try:
                    # Test connection by fetching change requests
                    change_data = servicenow_service.get_change_requests_for_assignment_group(
                        assignment_groups=assignment_groups,
                        limit=5  # Just test with a few
                    )
                    
                    cr_count = len(change_data.get('change_requests', []))
                    ct_count = len(change_data.get('change_tasks', []))
                    
                    print(f"✅ ServiceNow connection successful!")
                    print(f"📊 Found {cr_count} Change Requests")
                    print(f"📊 Found {ct_count} Change Tasks")
                    
                    # Show sample data
                    if change_data.get('change_requests'):
                        print("\n📋 Sample Change Requests:")
                        for i, cr in enumerate(change_data['change_requests'][:3]):
                            print(f"   {i+1}. {cr.get('number', 'N/A')} - {cr.get('short_description', 'No description')[:50]}...")
                    
                    if change_data.get('change_tasks'):
                        print("\n📋 Sample Change Tasks:")
                        for i, ct in enumerate(change_data['change_tasks'][:3]):
                            print(f"   {i+1}. {ct.get('number', 'N/A')} - {ct.get('short_description', 'No description')[:50]}...")
                            
                except Exception as e:
                    print(f"❌ ServiceNow connection failed: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("❌ No assignment groups configured")
        else:
            print("❌ ServiceNow not properly enabled/configured")
            
    except Exception as e:
        print(f"❌ Error initializing ServiceNow service: {e}")
        import traceback
        traceback.print_exc()