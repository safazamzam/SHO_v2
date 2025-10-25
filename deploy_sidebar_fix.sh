#!/bin/bash

# Sidebar Fix Deployment Script
# Run this script from your local project directory

echo "🚀 Deploying Sidebar Fix to Production..."

# Configuration
SERVER_IP="35.200.202.18"
SERVER_USER="sajid"  # Change this to your actual username
SSH_KEY="gcp_ssh_key"
CONTAINER_NAME="my_app_container"

# Check if SSH key exists
if [ ! -f "$SSH_KEY" ]; then
    echo "❌ SSH key not found: $SSH_KEY"
    echo "Please ensure your SSH key is in the current directory"
    exit 1
fi

# Deploy the updated template
echo "📤 Uploading updated base.html template..."
scp -i $SSH_KEY templates/base.html $SERVER_USER@$SERVER_IP:~/shift_handover_app/templates/

if [ $? -eq 0 ]; then
    echo "✅ Template uploaded successfully"
    
    # SSH into server and update container
    echo "🔄 Updating Docker container..."
    ssh -i $SSH_KEY $SERVER_USER@$SERVER_IP << 'EOF'
        cd shift_handover_app
        echo "Copying template to container..."
        sudo docker cp templates/base.html my_app_container:/app/templates/base.html
        sudo docker exec my_app_container chown www-data:www-data /app/templates/base.html
        echo "Restarting web service..."
        sudo docker-compose restart web
        echo "✅ Deployment complete!"
EOF
    
    echo "🎉 Sidebar fix deployed successfully!"
    echo "📱 Test your application at: http://$SERVER_IP"
    echo "🔧 Check sidebar toggle functionality"
    
else
    echo "❌ Failed to upload template"
    echo "Please check your SSH configuration and try again"
    exit 1
fi