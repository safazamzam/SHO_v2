# 🚀 Azure DevOps Self-Hosted Agent - Quick Setup Commands

## Step 1: Connect to your GCP VM
Use one of these methods:

### Method A: GCP Console (Recommended)
1. Go to: https://console.cloud.google.com/compute/instances
2. Find your VM and click "SSH" button
3. This opens a web-based terminal

### Method B: gcloud CLI (if you have it installed)
```bash
gcloud compute ssh shifthandoversajid@your-vm-name --zone=your-zone
```

### Method C: Fix local SSH (if needed)
```powershell
# Check if SSH key exists
Get-Content ~/.ssh/my-gcp-key
# If key format issues, convert line endings:
(Get-Content ~/.ssh/my-gcp-key -Raw) -replace "`r`n", "`n" | Set-Content ~/.ssh/my-gcp-key-fixed -NoNewline
ssh -i ~/.ssh/my-gcp-key-fixed -o ConnectTimeout=30 shifthandoversajid@35.200.202.18
```

## Step 2: Run Setup Command (Copy this entire block)
Once connected to your GCP VM, run this single command:

```bash
curl -fsSL https://raw.githubusercontent.com/microsoft/azure-pipelines-agent/master/src/Misc/layoutbin/installdependencies.sh | bash && \
mkdir -p ~/azuredevops-agent && cd ~/azuredevops-agent && \
wget -q https://vstsagentpackage.azureedge.net/agent/3.232.0/vsts-agent-linux-x64-3.232.0.tar.gz && \
tar zxf vsts-agent-linux-x64-3.232.0.tar.gz && \
rm vsts-agent-linux-x64-3.232.0.tar.gz && \
echo "✅ Agent downloaded! Now run: ./config.sh"
```

## Step 3: Configure Agent
After the download completes, run:
```bash
cd ~/azuredevops-agent
./config.sh
```

When prompted, enter:
- **Server URL:** `https://dev.azure.com/mdsajid020`
- **Authentication:** `PAT`
- **Personal Access Token:** [Create at https://dev.azure.com/mdsajid020/_usersSettings/tokens]
- **Agent pool:** `Default`
- **Agent name:** `GCP-SelfHostedAgent`
- **Work folder:** `_work`
- **Run as service:** `Y`

## Step 4: Install and Start Service
```bash
cd ~/azuredevops-agent
sudo ./svc.sh install
sudo ./svc.sh start
sudo ./svc.sh status
```

## Step 5: Verify Agent
Check that your agent appears online at:
https://dev.azure.com/mdsajid020/_settings/agentpools

## 🔑 Create Personal Access Token
Before configuring, create a PAT token:
1. Go to: https://dev.azure.com/mdsajid020/_usersSettings/tokens
2. Click "New Token"
3. Name: `GCP-SelfHostedAgent`
4. Expiration: 90 days
5. Scopes: **Agent Pools** (Read & manage)
6. Click "Create" and copy the token

## ✅ Success Verification
- Agent shows as "Online" in Azure DevOps
- Pipeline runs without parallelism errors
- Deployment happens directly on the same VM

## 🐞 Troubleshooting
If agent fails to start:
```bash
# Check logs
cd ~/azuredevops-agent
cat _diag/*.log | tail -50

# Restart service
sudo ./svc.sh stop
sudo ./svc.sh start
```