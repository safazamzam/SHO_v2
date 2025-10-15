# Shift Handover Application v2 - Azure DevOps Repository

This is an enhanced Flask-based Shift Handover Application with comprehensive SSO (Single Sign-On) integration, automated ServiceNow CTask assignment, and modern dashboard features.

## ✨ Key Features

### 🔐 SSO Authentication
- **Multi-Provider Support**: Google OAuth, Azure AD, SAML 2.0, Generic OAuth, LDAP
- **Admin Configuration**: Visual dashboard for managing SSO providers  
- **Secure Storage**: Encrypted configuration storage using Fernet encryption
- **Role-Based Access**: Admin-only access to SSO configuration
- **Seamless Integration**: Built-in authentication flows with user provisioning

### 📊 Core Application Features
- **Shift Handover Management**: Create, edit, and track shift handovers
- **ServiceNow Integration**: Automated CTask assignment and incident tracking
- **Team Management**: Roster management with role-based permissions
- **Dashboard Analytics**: Real-time metrics and shift status monitoring
- **Audit Logging**: Comprehensive activity tracking and reporting
- **Email Notifications**: Automated notifications on handover submission
- **Export Features**: Export incidents/key points to PDF/CSV

### 🛠 Technical Stack
- **Backend**: Flask, SQLAlchemy, PostgreSQL/SQLite
- **Frontend**: Modern HTML5, CSS3, JavaScript with responsive design
- **Authentication**: Flask-Login with SSO integration
- **Security**: Encrypted configurations, CSRF protection, secure sessions
- **API Integration**: ServiceNow REST API, OAuth 2.0 providers

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Virtual environment
- Database (SQLite for development, PostgreSQL for production)

### Local Development Setup
```bash
# Clone from Azure DevOps
git clone https://dev.azure.com/mdsajid020/shift_handover_v2/_git/shift_handover_v2
cd shift_handover_v2

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
copy .env.example .env
# Edit .env with your configuration

# Initialize database
python init_database.py

# Run the application
python app.py
```

### Access the Application
- **Main Application**: http://127.0.0.1:5000
- **SSO Configuration**: http://127.0.0.1:5000/admin/sso/ (Admin only)
- **Admin Dashboard**: http://127.0.0.1:5000/admin/configuration

## 🔧 SSO Configuration

### Google OAuth Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Set authorized redirect URI: `http://your-domain/auth/sso/callback/google_oauth`
6. Copy Client ID and Client Secret to SSO configuration

### Azure AD Setup
1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to Azure Active Directory > App registrations
3. Create new registration
4. Configure redirect URI: `http://your-domain/auth/sso/callback/azure_ad`
5. Generate client secret
6. Copy Application (client) ID and client secret

## 🚢 Docker Deployment

### Quick Start with Docker
```bash
# Build and start the containers
docker-compose up --build

# Access the application at http://localhost:5000

# Initialize the database (in a new terminal)
docker-compose exec web flask shell
>>> from app import db
>>> db.create_all()
>>> exit()
```

### Production Docker Setup
```bash
# Use production configuration
docker-compose -f docker-compose.prod.yml up --build
```

## 🔒 Security Features
- **Encrypted Storage**: All SSO configurations encrypted using Fernet
- **Environment Variables**: Sensitive data stored in environment variables
- **CSRF Protection**: Built-in cross-site request forgery protection
- **Session Security**: Secure session management with proper timeouts
- **Role-Based Access**: Admin-only access to sensitive configurations

## 🌐 Azure DevOps Integration
- **Repository**: https://dev.azure.com/mdsajid020/shift_handover_v2
- **CI/CD Pipelines**: Automated build and deployment
- **Branch Policies**: Protected main branch with pull request requirements
- **Work Items**: Integration with Azure Boards for project management

## 📊 Monitoring & Logging
- **Application Logs**: Comprehensive logging with rotating file handlers
- **Audit Trail**: User activity tracking and security auditing
- **Health Checks**: Built-in health monitoring endpoints
- **Performance Metrics**: Response time and usage analytics

---

**Repository**: https://dev.azure.com/mdsajid020/shift_handover_v2
**Last Updated**: October 15, 2025
**Version**: 2.0 with SSO Integration

## Notes
- For proof-of-concept, authentication uses static credentials.
- Replace SMTP and DB credentials in `.env` for production use.
