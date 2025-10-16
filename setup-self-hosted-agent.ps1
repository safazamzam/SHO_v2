# Self-Hosted Azure DevOps Agent Setup Script
# Run this script to set up a self-hosted agent for your pipeline

param(
    [string]$AgentName = "SelfHostedAgent",
    [string]$PoolName = "Default",
    [string]$WorkDirectory = "C:\agent\_work"
)

Write-Host "🚀 Setting up Azure DevOps Self-Hosted Agent..." -ForegroundColor Green

# Download and extract agent
$agentUrl = "https://vstsagentpackage.azureedge.net/agent/3.243.1/vsts-agent-win-x64-3.243.1.zip"
$agentZip = "vsts-agent-win-x64-3.243.1.zip"
$agentDir = "C:\agent"

Write-Host "📦 Creating agent directory..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path $agentDir -Force

Write-Host "⬬ Downloading Azure DevOps agent..." -ForegroundColor Yellow
Invoke-WebRequest -Uri $agentUrl -OutFile $agentZip

Write-Host "📂 Extracting agent..." -ForegroundColor Yellow
Expand-Archive -Path $agentZip -DestinationPath $agentDir -Force

Write-Host "🧹 Cleaning up..." -ForegroundColor Yellow
Remove-Item $agentZip

Write-Host "⚙️ Configuration Instructions:" -ForegroundColor Cyan
Write-Host "1. Open PowerShell as Administrator" -ForegroundColor White
Write-Host "2. Navigate to: cd $agentDir" -ForegroundColor White
Write-Host "3. Run: .\config.cmd" -ForegroundColor White
Write-Host "4. Follow the prompts with these values:" -ForegroundColor White
Write-Host "   - Server URL: https://dev.azure.com/mdsajid020" -ForegroundColor Gray
Write-Host "   - Authentication type: PAT" -ForegroundColor Gray
Write-Host "   - Personal Access Token: [Your PAT from Azure DevOps]" -ForegroundColor Gray
Write-Host "   - Agent pool: $PoolName" -ForegroundColor Gray
Write-Host "   - Agent name: $AgentName" -ForegroundColor Gray
Write-Host "   - Work folder: $WorkDirectory" -ForegroundColor Gray
Write-Host "5. Run: .\run.cmd" -ForegroundColor White

Write-Host ""
Write-Host "📋 To create a Personal Access Token (PAT):" -ForegroundColor Cyan
Write-Host "1. Go to: https://dev.azure.com/mdsajid020/_usersSettings/tokens" -ForegroundColor White
Write-Host "2. Click 'New Token'" -ForegroundColor White
Write-Host "3. Name: 'SelfHostedAgent'" -ForegroundColor White
Write-Host "4. Scopes: Agent Pools (read, manage)" -ForegroundColor White
Write-Host "5. Copy the token for configuration" -ForegroundColor White

Write-Host ""
Write-Host "✅ Agent download completed! Follow the configuration steps above." -ForegroundColor Green