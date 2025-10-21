# SSH Key Setup for Azure DevOps Secure Files

## 📋 **Steps to Complete the Setup**

### **1. Upload SSH Key as Secure File**
1. Go to: https://dev.azure.com/mdsajid020/shift_handover_v2/_library?itemType=SecureFiles
2. Click **"+ Secure file"**
3. Upload file: `gcp_ssh_key` (the private key file in this directory)
4. Name it exactly: `gcp_ssh_key`
5. Check **"Authorize for use in all pipelines"**

### **2. Run the Pipeline**
1. Go to: https://dev.azure.com/mdsajid020/shift_handover_v2/_build
2. Click **"Run pipeline"** on "Shift-Handover-ACR-Pipeline"
3. The pipeline will now:
   - ✅ Build Docker image from Dockerfile
   - ✅ Push image to Azure Container Registry
   - ✅ Deploy container to GCP VM
   - ✅ Run health check

### **3. Access Your Application**
After successful deployment, your Flask app will be accessible at:
- **Internal:** http://35.200.202.18:5000
- **External:** http://35.200.202.18:5000 (if firewall allows)

### **4. Open Firewall (If Needed)**
If you can't access the app externally, run this GCP command:
```bash
gcloud compute firewall-rules create allow-flask-5000 \
    --allow tcp:5000 \
    --description "Allow Flask app on port 5000"
```

### **5. Monitor Deployment**
Check container status:
```bash
ssh -i gcp_ssh_key shifthandoversajid@35.200.202.18 "sudo docker ps"
```

Check application logs:
```bash
ssh -i gcp_ssh_key shifthandoversajid@35.200.202.18 "sudo docker logs shift-handover-app"
```

## 🎯 **What the Pipeline Does Now**

### **Build Stage:**
- Builds Docker image using your Dockerfile
- Pushes to Azure Container Registry (shifthandoveracr.azurecr.io)
- Tags with build number and 'latest'

### **Deploy Stage:**
- Downloads SSH key securely
- Stops any existing container
- Pulls latest image from ACR
- Runs new container on port 5000
- Performs health check

### **Container Configuration:**
- **Name:** shift-handover-app
- **Port:** 5000 (mapped to host port 5000)
- **Restart Policy:** unless-stopped
- **Health Check:** curl to localhost:5000

Your Flask application will now be properly containerized and deployed automatically! 🚀