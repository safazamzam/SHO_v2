# Solution: Download Agent via Alternative Methods

## Method 1: Direct Browser Download
1. Open your browser and go to: https://github.com/Microsoft/azure-pipelines-agent/releases
2. Download: vsts-agent-linux-x64-3.232.0.tar.gz (or latest version)
3. Upload to your GCP VM using one of these methods:

### Upload via GCP Console:
1. Go to: https://console.cloud.google.com/storage
2. Create a bucket or use existing one
3. Upload the tar.gz file
4. On GCP VM: `gsutil cp gs://your-bucket/vsts-agent-linux-x64-3.232.0.tar.gz ~/azuredevops-agent/`

### Upload via SCP (if SSH works):
```bash
scp -i ~/.ssh/my-gcp-key vsts-agent-linux-x64-3.232.0.tar.gz shifthandoversajid@35.200.202.18:~/azuredevops-agent/
```

## Method 2: Pre-built Script Solution
Create this script on your GCP VM:

```bash
#!/bin/bash
# Alternative agent setup script

cd ~
mkdir -p azuredevops-agent
cd azuredevops-agent

# Try multiple download sources
echo "Attempting download from multiple sources..."

# Source 1: Microsoft CDN
wget -q --timeout=30 https://vstsagentpackage.azureedge.net/agent/3.232.0/vsts-agent-linux-x64-3.232.0.tar.gz && echo "Downloaded from Microsoft CDN" && SUCCESS=1

# Source 2: GitHub if CDN fails
if [ -z "$SUCCESS" ]; then
    wget -q --timeout=30 https://github.com/Microsoft/azure-pipelines-agent/releases/download/v3.232.0/vsts-agent-linux-x64-3.232.0.tar.gz && echo "Downloaded from GitHub" && SUCCESS=1
fi

# Source 3: Alternative GitHub URL
if [ -z "$SUCCESS" ]; then
    curl -L -o vsts-agent-linux-x64-3.232.0.tar.gz https://api.github.com/repos/Microsoft/azure-pipelines-agent/releases/assets/123456789 && echo "Downloaded via GitHub API" && SUCCESS=1
fi

if [ -n "$SUCCESS" ]; then
    echo "✅ Download successful!"
    tar -zxf vsts-agent-linux-x64-3.232.0.tar.gz
    rm vsts-agent-linux-x64-3.232.0.tar.gz
    echo "🎉 Agent extracted! Run: ./config.sh"
else
    echo "❌ All download methods failed. Manual upload required."
fi
```

## Method 3: Manual Installation Script
If downloads keep failing, run this on your GCP VM:

```bash
# Install Azure CLI (has agent functionality)
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Alternative: Install using apt (if available)
sudo apt update
sudo apt install azure-cli

# Then use Azure CLI to download agent
az extension add --name azure-devops
```

## Method 4: Verify Network Issues
Run these commands on your GCP VM to diagnose:

```bash
# Check DNS
dig google.com
nslookup github.com

# Check HTTP connectivity
curl -v https://google.com
telnet github.com 443

# Check GCP VM network settings
ip route show
cat /etc/resolv.conf
```

## Quick Test Command
Try this on your GCP VM:
```bash
curl -s https://httpbin.org/ip
```

If this works, the issue is specific to the Microsoft domains.