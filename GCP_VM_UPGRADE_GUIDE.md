# GCP VM Upgrade Commands

## 📋 **Upgrade Steps Using gcloud CLI**

### **1. Stop the VM**
```bash
gcloud compute instances stop [VM_NAME] --zone=[ZONE]
```

### **2. Change Machine Type**
```bash
gcloud compute instances set-machine-type [VM_NAME] --machine-type=e2-medium --zone=[ZONE]
```

### **3. Start the VM**
```bash
gcloud compute instances start [VM_NAME] --zone=[ZONE]
```

## 🔍 **Find Your VM Details**

If you need to find your VM name and zone:
```bash
gcloud compute instances list --filter="externalIP:35.200.202.18"
```

## 📊 **Machine Type Comparison**

| Type | vCPUs | Memory | Monthly Cost* |
|------|-------|--------|---------------|
| e2-small | 1 | 2 GB | ~$13 |
| e2-medium | 1 | 4 GB | ~$27 |

*Approximate costs for us-central1 region

## 🎯 **Benefits of e2-medium**

- **Double Memory:** 4GB vs 2GB (better for Docker builds)
- **Better Performance:** Same CPU but more memory for caching
- **Stable Agent:** Less likely to have memory issues during builds
- **Docker Efficiency:** Better container performance

## ⚠️ **Important Notes**

1. **VM will be temporarily down** during the upgrade (2-3 minutes)
2. **Azure DevOps agent will restart** automatically after VM boots
3. **All data preserved** - this only changes compute resources
4. **IP address stays the same** (35.200.202.18)

## 🔄 **After Upgrade**

Once upgraded, restart the Azure DevOps agent service:
```bash
ssh -i gcp_ssh_key shifthandoversajid@35.200.202.18 "cd ~/myagent && sudo ./svc.sh restart"
```