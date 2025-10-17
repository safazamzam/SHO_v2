# 🚀 Self-Hosted Azure DevOps Agent Setup Guide

## Step 1: Create Personal Access Token (PAT)

1. **Open your browser and go to:** 
   https://dev.azure.com/mdsajid020/_usersSettings/tokens

2. **Click "New Token"**

3. **Configure the token:**
   - **Name:** `SelfHostedAgent`
   - **Expiration:** 90 days (or custom)
   - **Scopes:** Select "Agent Pools" → Check "Read & manage"

4. **Click "Create"**

5. **IMPORTANT:** Copy the token immediately - you won't see it again!

## Step 2: Download and Setup Agent

### Option A: PowerShell Download (try first)
```powershell
# Create agent directory
New-Item -ItemType Directory -Path "C:\agent" -Force

# Navigate to agent directory
Set-Location "C:\agent"

# Download latest agent (alternative URL)
Invoke-WebRequest -Uri "https://github.com/Microsoft/azure-pipelines-agent/releases/download/v3.243.1/vsts-agent-win-x64-3.243.1.zip" -OutFile "agent.zip"

# Extract agent
Expand-Archive -Path "agent.zip" -DestinationPath "." -Force

# Clean up
Remove-Item "agent.zip"
```

### Option B: Manual Download (if PowerShell fails)
1. **Go to:** https://github.com/Microsoft/azure-pipelines-agent/releases
2. **Download:** `vsts-agent-win-x64-3.243.1.zip` (latest Windows x64 version)
3. **Create folder:** `C:\agent`
4. **Extract the zip file** to `C:\agent`

## Step 3: Configure Agent

1. **Open PowerShell as Administrator**

2. **Navigate to agent directory:**
   ```powershell
   Set-Location "C:\agent"
   ```

3. **Run configuration:**
   ```powershell
   .\config.cmd
   ```

4. **Answer the prompts:**
   - **Server URL:** `https://dev.azure.com/mdsajid020`
   - **Authentication type:** `PAT`
   - **Personal access token:** [Paste your PAT from Step 1]
   - **Agent pool:** `Default` (press Enter)
   - **Agent name:** `SelfHostedAgent` (or press Enter for default)
   - **Work folder:** `_work` (press Enter for default)
   - **Run as service:** `Y` (recommended)
   - **User account:** Press Enter (use default)

## Step 4: Start Agent

If you configured it as a service:
```powershell
# The agent will start automatically
# Check status with:
Get-Service -Name "*azure*"
```

If not configured as service:
```powershell
.\run.cmd
```

## Step 5: Verify Agent in Azure DevOps

1. **Go to:** https://dev.azure.com/mdsajid020/_settings/agentpools
2. **Click on "Default" pool**
3. **Verify your agent appears in the "Agents" tab with status "Online"**

## Step 6: Run Your Pipeline

Once the agent is online, your pipeline will use the self-hosted agent and bypass the parallelism limitation!

## Troubleshooting

### If agent shows offline:
- Check Windows Services for "Azure DevOps Agent"
- Restart the service: `Restart-Service -Name "*azure*"`

### If configuration fails:
- Verify your PAT token has correct permissions
- Check network connectivity to dev.azure.com

### If agent doesn't appear:
- Wait 1-2 minutes for registration
- Refresh the agent pools page
- Check the agent configuration logs in `C:\agent\_diag\`

## Success Verification

✅ Agent appears as "Online" in Azure DevOps  
✅ Pipeline runs without parallelism errors  
✅ Your application deploys successfully  

**Once this is working, your pipeline will run immediately without waiting for Microsoft's hosted agents!**