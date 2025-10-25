#!/usr/bin/env python3
"""
🔧 UNIFIED SECRETS MANAGEMENT - SINGLE PAGE REORGANIZATION
Consolidate all secrets management into one comprehensive page with clear sections
"""

from app import app, db
from sqlalchemy import text
from models.secrets_manager import HybridSecretsManager, SecretCategory
import os

def reorganize_secrets_categories():
    """Reorganize secrets into proper sections for single-page view"""
    with app.app_context():
        print("🔧 REORGANIZING SECRETS FOR UNIFIED DASHBOARD:")
        print("=" * 60)
        
        # Define the new organization structure
        reorganization_plan = {
            # External APIs Section - All external service credentials
            'external_apis': {
                'category': 'external_apis',
                'display_name': 'External APIs & Services',
                'description': 'Third-party service credentials and API keys',
                'secrets': [
                    'SMTP_USERNAME', 'SMTP_PASSWORD', 
                    'SERVICENOW_INSTANCE', 'SERVICENOW_USERNAME', 'SERVICENOW_PASSWORD',
                    'GOOGLE_OAUTH_CLIENT_ID', 'GOOGLE_OAUTH_CLIENT_SECRET'
                ]
            },
            
            # Application Configuration Section - Pure app settings
            'application_config': {
                'category': 'application_config', 
                'display_name': 'Application Configuration',
                'description': 'Application-specific settings and configurations',
                'secrets': [
                    'TEAM_EMAIL', 'SERVICENOW_TIMEOUT', 'SERVICENOW_API_VERSION',
                    'SERVICENOW_ASSIGNMENT_GROUPS', 'FLASK_SECRET_KEY', 'SSO_ENCRYPTION_KEY'
                ]
            },
            
            # Feature Controls Section - Feature flags and toggles
            'feature_controls': {
                'category': 'feature_controls',
                'display_name': 'Feature Controls', 
                'description': 'Feature flags and service enablement toggles',
                'secrets': [
                    'SERVICENOW_ENABLED', 'SMTP_ENABLED', 'OAUTH_ENABLED', 'AUDIT_LOGGING_ENABLED'
                ]
            },
            
            # Infrastructure Section - Critical system secrets (Docker secrets)
            'infrastructure': {
                'category': 'infrastructure',
                'display_name': 'Infrastructure & Database',
                'description': 'Critical infrastructure secrets (managed via Docker secrets)',
                'secrets': [
                    'DATABASE_URL', 'SECRETS_MASTER_KEY', 'MYSQL_PASSWORD', 'MYSQL_ROOT_PASSWORD'
                ]
            }
        }
        
        try:
            # Update existing secrets to new categories
            for section_key, section_info in reorganization_plan.items():
                new_category = section_info['category']
                
                for secret_key in section_info['secrets']:
                    query = f"UPDATE secret_store SET category = '{new_category}' WHERE key_name = '{secret_key}'"
                    with db.engine.connect() as connection:
                        result = connection.execute(text(query))
                        connection.commit()
                        if result.rowcount > 0:
                            print(f"✅ Moved {secret_key} → {section_info['display_name']}")
            
            print(f"\n📊 Updated organization:")
            query = "SELECT category, COUNT(*) as count FROM secret_store GROUP BY category ORDER BY category"
            with db.engine.connect() as connection:
                result = connection.execute(text(query))
                categories = result.fetchall()
            
            for category, count in categories:
                display_name = next((info['display_name'] for info in reorganization_plan.values() 
                                   if info['category'] == category), category)
                print(f"- {display_name}: {count} secrets")
                
        except Exception as e:
            print(f"❌ Error reorganizing categories: {e}")
            return False, reorganization_plan
        
        return True, reorganization_plan

def create_unified_dashboard_template():
    """Create new unified dashboard template"""
    print("\n🎨 CREATING UNIFIED DASHBOARD TEMPLATE:")
    print("=" * 60)
    
    template_content = '''{% extends "base.html" %}

{% block title %}Unified Secrets & Configuration Management{% endblock %}

{% block extra_css %}
<style>
    .unified-secrets-container {
        padding: 20px;
        background: #f8f9fa;
    }
    
    .section-card {
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 25px;
        overflow: hidden;
        transition: transform 0.2s ease;
    }
    
    .section-card:hover {
        transform: translateY(-2px);
    }
    
    .section-header {
        padding: 20px 25px;
        border-bottom: 1px solid #e9ecef;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .section-title {
        font-size: 1.2rem;
        font-weight: 600;
        margin: 0;
        color: #2c3e50;
    }
    
    .section-description {
        color: #6c757d;
        font-size: 0.9rem;
        margin: 5px 0 0 0;
    }
    
    .section-badge {
        background: #007bff;
        color: white;
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .section-content {
        padding: 0;
    }
    
    /* Section-specific styling */
    .external-apis .section-header { background: linear-gradient(135deg, #17a2b8 0%, #138496 100%); color: white; }
    .external-apis .section-badge { background: rgba(255,255,255,0.2); }
    
    .application-config .section-header { background: linear-gradient(135deg, #6f42c1 0%, #5a3a9a 100%); color: white; }
    .application-config .section-badge { background: rgba(255,255,255,0.2); }
    
    .feature-controls .section-header { background: linear-gradient(135deg, #20c997 0%, #1a9c7a 100%); color: white; }
    .feature-controls .section-badge { background: rgba(255,255,255,0.2); }
    
    .infrastructure .section-header { background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); color: white; }
    .infrastructure .section-badge { background: rgba(255,255,255,0.2); }
    
    .secret-item {
        padding: 15px 25px;
        border-bottom: 1px solid #f1f3f4;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .secret-item:last-child {
        border-bottom: none;
    }
    
    .secret-info {
        flex-grow: 1;
    }
    
    .secret-name {
        font-family: 'Courier New', monospace;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 4px;
    }
    
    .secret-description {
        color: #6c757d;
        font-size: 0.85rem;
    }
    
    .secret-value {
        font-family: 'Courier New', monospace;
        background: #f8f9fa;
        padding: 8px 12px;
        border-radius: 6px;
        margin: 0 15px;
        min-width: 200px;
        text-align: center;
        color: #495057;
    }
    
    .secret-actions {
        display: flex;
        gap: 8px;
    }
    
    .btn-action {
        padding: 6px 12px;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        font-size: 0.8rem;
        transition: all 0.2s;
    }
    
    .btn-edit { background: #ffc107; color: #212529; }
    .btn-edit:hover { background: #e0a800; }
    
    .btn-delete { background: #dc3545; color: white; }
    .btn-delete:hover { background: #c82333; }
    
    .btn-toggle { background: #6c757d; color: white; }
    .btn-toggle:hover { background: #5a6268; }
    
    .btn-test { background: #17a2b8; color: white; }
    .btn-test:hover { background: #138496; }
    
    .global-actions {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 25px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .page-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #2c3e50;
        margin: 0;
    }
    
    .action-buttons {
        display: flex;
        gap: 10px;
    }
    
    .btn-primary-action {
        background: #007bff;
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 8px;
        font-weight: 500;
        cursor: pointer;
        transition: background 0.2s;
    }
    
    .btn-primary-action:hover {
        background: #0056b3;
    }
    
    .infrastructure-notice {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 15px;
        margin: 15px 25px;
        color: #856404;
    }
    
    .infrastructure-notice strong {
        color: #dc3545;
    }
    
    .empty-section {
        padding: 40px 25px;
        text-align: center;
        color: #6c757d;
    }
    
    .empty-section i {
        font-size: 3rem;
        margin-bottom: 15px;
        opacity: 0.3;
    }
</style>
{% endblock %}

{% block content %}
<div class="unified-secrets-container">
    <!-- Global Actions Header -->
    <div class="global-actions">
        <h1 class="page-title">🔐 Unified Secrets & Configuration Management</h1>
        <div class="action-buttons">
            <button class="btn-primary-action" onclick="addNewSecret()">
                <i class="fas fa-plus"></i> Add New Secret
            </button>
            <button class="btn-primary-action" onclick="refreshAll()">
                <i class="fas fa-sync"></i> Refresh
            </button>
            <button class="btn-primary-action" onclick="exportSecrets()">
                <i class="fas fa-download"></i> Export
            </button>
        </div>
    </div>

    <!-- External APIs & Services Section -->
    <div class="section-card external-apis">
        <div class="section-header">
            <div>
                <h2 class="section-title">🌐 External APIs & Services</h2>
                <p class="section-description">Third-party service credentials and API keys</p>
            </div>
            <span class="section-badge" id="external-apis-count">0</span>
        </div>
        <div class="section-content" id="external-apis-content">
            <!-- Populated by JavaScript -->
        </div>
    </div>

    <!-- Application Configuration Section -->
    <div class="section-card application-config">
        <div class="section-header">
            <div>
                <h2 class="section-title">⚙️ Application Configuration</h2>
                <p class="section-description">Application-specific settings and configurations</p>
            </div>
            <span class="section-badge" id="application-config-count">0</span>
        </div>
        <div class="section-content" id="application-config-content">
            <!-- Populated by JavaScript -->
        </div>
    </div>

    <!-- Feature Controls Section -->
    <div class="section-card feature-controls">
        <div class="section-header">
            <div>
                <h2 class="section-title">🎛️ Feature Controls</h2>
                <p class="section-description">Feature flags and service enablement toggles</p>
            </div>
            <span class="section-badge" id="feature-controls-count">0</span>
        </div>
        <div class="section-content" id="feature-controls-content">
            <!-- Populated by JavaScript -->
        </div>
    </div>

    <!-- Infrastructure & Database Section -->
    <div class="section-card infrastructure">
        <div class="section-header">
            <div>
                <h2 class="section-title">🏗️ Infrastructure & Database</h2>
                <p class="section-description">Critical infrastructure secrets (managed via Docker secrets)</p>
            </div>
            <span class="section-badge" id="infrastructure-count">0</span>
        </div>
        <div class="infrastructure-notice">
            <strong>⚠️ Security Notice:</strong> Infrastructure secrets like database passwords and master keys are managed via Docker secrets or environment variables for maximum security. These are not editable through this interface.
        </div>
        <div class="section-content" id="infrastructure-content">
            <!-- Populated by JavaScript -->
        </div>
    </div>
</div>

<!-- Modals and JavaScript will be added here -->
<script>
document.addEventListener('DOMContentLoaded', function() {
    loadUnifiedSecrets();
});

async function loadUnifiedSecrets() {
    try {
        const response = await fetch('/admin/secrets/api/unified');
        const data = await response.json();
        
        if (data.success) {
            populateSection('external-apis', data.sections.external_apis || []);
            populateSection('application-config', data.sections.application_config || []);
            populateSection('feature-controls', data.sections.feature_controls || []);
            populateSection('infrastructure', data.sections.infrastructure || []);
        }
    } catch (error) {
        console.error('Error loading secrets:', error);
    }
}

function populateSection(sectionId, secrets) {
    const contentElement = document.getElementById(`${sectionId}-content`);
    const countElement = document.getElementById(`${sectionId}-count`);
    
    countElement.textContent = secrets.length;
    
    if (secrets.length === 0) {
        contentElement.innerHTML = `
            <div class="empty-section">
                <i class="fas fa-inbox"></i>
                <p>No secrets configured in this section</p>
            </div>
        `;
        return;
    }
    
    contentElement.innerHTML = secrets.map(secret => `
        <div class="secret-item">
            <div class="secret-info">
                <div class="secret-name">${secret.key_name}</div>
                <div class="secret-description">${secret.description || 'No description provided'}</div>
            </div>
            <div class="secret-value">
                ${secret.value ? '••••••••••••' : 'Not configured'}
            </div>
            <div class="secret-actions">
                ${sectionId !== 'infrastructure' ? `
                    <button class="btn-action btn-edit" onclick="editSecret('${secret.key_name}')">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                    <button class="btn-action btn-test" onclick="testSecret('${secret.key_name}')">
                        <i class="fas fa-vial"></i> Test
                    </button>
                    <button class="btn-action btn-toggle" onclick="toggleSecret('${secret.key_name}')">
                        <i class="fas fa-power-off"></i> ${secret.is_active ? 'Disable' : 'Enable'}
                    </button>
                ` : `
                    <button class="btn-action btn-test" onclick="viewInfraSecret('${secret.key_name}')">
                        <i class="fas fa-eye"></i> View
                    </button>
                `}
            </div>
        </div>
    `).join('');
}

// Placeholder functions - will be implemented
function addNewSecret() { console.log('Add new secret'); }
function refreshAll() { loadUnifiedSecrets(); }
function exportSecrets() { console.log('Export secrets'); }
function editSecret(key) { console.log('Edit secret:', key); }
function testSecret(key) { console.log('Test secret:', key); }
function toggleSecret(key) { console.log('Toggle secret:', key); }
function viewInfraSecret(key) { console.log('View infrastructure secret:', key); }
</script>
{% endblock %}'''
    
    with open('templates/admin/unified_secrets_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print("✅ Created unified dashboard template")

def update_routes_for_unified_dashboard():
    """Add route for unified API"""
    print("\n🔌 ADDING UNIFIED API ROUTE:")
    print("=" * 60)
    
    route_addition = '''
@admin_secrets_bp.route('/api/unified')
@admin_required
def get_unified_secrets():
    """Get all secrets organized by sections for unified dashboard"""
    try:
        secrets_manager = HybridSecretsManager()
        
        # Define section mapping
        section_mapping = {
            'external_apis': ['SMTP_USERNAME', 'SMTP_PASSWORD', 'SERVICENOW_INSTANCE', 
                             'SERVICENOW_USERNAME', 'SERVICENOW_PASSWORD', 'GOOGLE_OAUTH_CLIENT_ID', 
                             'GOOGLE_OAUTH_CLIENT_SECRET'],
            'application_config': ['TEAM_EMAIL', 'SERVICENOW_TIMEOUT', 'SERVICENOW_API_VERSION',
                                  'SERVICENOW_ASSIGNMENT_GROUPS', 'FLASK_SECRET_KEY', 'SSO_ENCRYPTION_KEY'],
            'feature_controls': ['SERVICENOW_ENABLED', 'SMTP_ENABLED', 'OAUTH_ENABLED', 'AUDIT_LOGGING_ENABLED'],
            'infrastructure': ['DATABASE_URL', 'SECRETS_MASTER_KEY', 'MYSQL_PASSWORD', 'MYSQL_ROOT_PASSWORD']
        }
        
        # Get all secrets from database
        with db.engine.connect() as connection:
            result = connection.execute(text("""
                SELECT key_name, category, value_encrypted, is_active, description, 
                       created_at, updated_at 
                FROM secret_store 
                ORDER BY category, key_name
            """))
            all_secrets = result.fetchall()
        
        # Organize secrets by section
        sections = {section: [] for section in section_mapping.keys()}
        
        for secret in all_secrets:
            key_name, category, value_encrypted, is_active, description, created_at, updated_at = secret
            
            # Find which section this secret belongs to
            section_found = None
            for section, keys in section_mapping.items():
                if key_name in keys:
                    section_found = section
                    break
            
            if section_found:
                # Don't include actual values for security
                secret_info = {
                    'key_name': key_name,
                    'category': category,
                    'is_active': is_active,
                    'description': description,
                    'value': '••••••••••••' if value_encrypted else None,
                    'created_at': created_at.isoformat() if created_at else None,
                    'updated_at': updated_at.isoformat() if updated_at else None
                }
                sections[section_found].append(secret_info)
        
        return jsonify({
            'success': True,
            'sections': sections,
            'total_secrets': len(all_secrets),
            'section_counts': {section: len(secrets) for section, secrets in sections.items()}
        })
        
    except Exception as e:
        logging.error(f"Error getting unified secrets: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
'''
    
    print("✅ API route template ready")
    print("   - /api/unified: Get all secrets organized by sections")
    print("   - Security: Actual values masked with ••••••••••••")
    print("   - Organization: 4 clear sections with proper categorization")

def main():
    print("🔧 UNIFIED SECRETS DASHBOARD REORGANIZATION")
    print("=" * 70)
    
    # Reorganize existing secrets
    success, plan = reorganize_secrets_categories()
    if not success:
        print("❌ Failed to reorganize secrets")
        return
    
    # Create unified template
    create_unified_dashboard_template()
    
    # Show route updates needed
    update_routes_for_unified_dashboard()
    
    print(f"\n🎯 REORGANIZATION COMPLETE!")
    print("=" * 70)
    print("✅ Secrets reorganized into 4 clear sections")
    print("✅ Unified dashboard template created")
    print("✅ API route design ready") 
    
    print(f"\n📊 NEW ORGANIZATION:")
    for section_key, section_info in plan.items():
        print(f"- {section_info['display_name']}: {len(section_info['secrets'])} secrets")
    
    print(f"\n🚀 NEXT STEPS:")
    print("1. 🔌 Add the unified API route to admin_secrets.py")
    print("2. 🔄 Update main route to use unified template")
    print("3. 🧪 Test the new organization")
    print("4. 🗑️ Remove old separate tabs if desired")
    
    print(f"\n🎨 BENEFITS:")
    print("- Single page for all secrets management")
    print("- Clear sectional organization")
    print("- No more duplication between tabs")
    print("- Proper separation of concerns")
    print("- Infrastructure secrets clearly marked as read-only")

if __name__ == "__main__":
    main()'''