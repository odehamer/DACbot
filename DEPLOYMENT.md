# Azure Container Instances Deployment Guide

This guide explains how to deploy the DACbot to Azure Container Instances.

## Prerequisites

- Azure CLI installed and configured
- Docker installed locally (for building the image)
- An Azure Container Registry (ACR) or Docker Hub account
- Discord bot token and channel ID

## Quick Start

### 1. Build and Push Docker Image

#### Option A: Using Azure Container Registry (Recommended)

```bash
# Login to Azure
az login

# Create a resource group (if you don't have one)
az group create --name dacbot-rg --location eastus

# Create Azure Container Registry
az acr create --resource-group dacbot-rg --name <YOUR_ACR_NAME> --sku Basic

# Login to ACR
az acr login --name <YOUR_ACR_NAME>

# Build and push the image
docker build -t <YOUR_ACR_NAME>.azurecr.io/dacbot:latest .
docker push <YOUR_ACR_NAME>.azurecr.io/dacbot:latest
```

#### Option B: Using Docker Hub

```bash
# Login to Docker Hub
docker login

# Build and push the image
docker build -t <YOUR_DOCKERHUB_USERNAME>/dacbot:latest .
docker push <YOUR_DOCKERHUB_USERNAME>/dacbot:latest
```

### 2. Configure Azure Container Instance YAML

Edit `azure-container-instance.yaml` and replace the following placeholders:

- `<YOUR_ACR_NAME>` - Your Azure Container Registry name (or use Docker Hub image)
- `<YOUR_DISCORD_TOKEN>` - Your Discord bot token
- `<YOUR_DISCORD_CHANNEL_ID>` - Your Discord channel ID

### 3. Deploy to Azure Container Instances

```bash
# Deploy using the YAML configuration
az container create --resource-group dacbot-rg --file azure-container-instance.yaml

# Check deployment status
az container show --resource-group dacbot-rg --name dacbot-container --output table

# View logs
az container logs --resource-group dacbot-rg --name dacbot-container
```

## Alternative: Deploy Using Azure CLI Command

If you prefer not to use a YAML file, you can deploy directly with CLI:

```bash
az container create \
  --resource-group dacbot-rg \
  --name dacbot-container \
  --image <YOUR_ACR_NAME>.azurecr.io/dacbot:latest \
  --cpu 1 \
  --memory 1.5 \
  --environment-variables DISCORD_CHANNEL_ID=<YOUR_CHANNEL_ID> \
  --secure-environment-variables DISCORD_TOKEN=<YOUR_TOKEN> \
  --restart-policy Always \
  --os-type Linux
```

## Monitoring and Management

### View Logs
```bash
az container logs --resource-group dacbot-rg --name dacbot-container --follow
```

### Restart Container
```bash
az container restart --resource-group dacbot-rg --name dacbot-container
```

### Stop Container
```bash
az container stop --resource-group dacbot-rg --name dacbot-container
```

### Delete Container
```bash
az container delete --resource-group dacbot-rg --name dacbot-container
```

## Environment Variables

The container requires the following environment variables:

- `DISCORD_TOKEN` - Your Discord bot token (required, should be kept secret)
- `DISCORD_CHANNEL_ID` - The Discord channel ID where notifications will be sent (required)

## Testing Locally

Before deploying to Azure, you can test the container locally:

```bash
# Build the image
docker build -t dacbot:local .

# Run the container
docker run -e DISCORD_TOKEN=<YOUR_TOKEN> \
           -e DISCORD_CHANNEL_ID=<YOUR_CHANNEL_ID> \
           dacbot:local
```

## Troubleshooting

### Container fails to start
- Check logs: `az container logs --resource-group dacbot-rg --name dacbot-container`
- Verify environment variables are set correctly
- Ensure the Discord token is valid

### Cannot pull image from ACR
- Enable admin user on ACR: `az acr update --name <YOUR_ACR_NAME> --admin-enabled true`
- Get credentials: `az acr credential show --name <YOUR_ACR_NAME>`
- Update the deployment to include registry credentials

### Audio not working
- Note: Audio playback won't work in containers as there's no audio output device
- The TTS functionality in `tiktoklive.py` may need modification for containerized environments

## Cost Considerations

Azure Container Instances charges based on:
- vCPU time (1 vCPU in this configuration)
- Memory (1.5 GB in this configuration)
- Runtime duration

Estimated cost: ~$30-40/month for continuous operation

## Security Best Practices

1. **Never commit secrets** - Keep your `.env` file in `.gitignore`
2. **Use Azure Key Vault** - For production, integrate with Azure Key Vault for secrets
3. **Use managed identities** - Enable managed identity for ACR access
4. **Regular updates** - Keep base images and dependencies updated

## Advanced Configuration

### Using Azure Key Vault for Secrets

```bash
# Create Key Vault
az keyvault create --name <YOUR_KEYVAULT_NAME> --resource-group dacbot-rg --location eastus

# Store secrets
az keyvault secret set --vault-name <YOUR_KEYVAULT_NAME> --name discord-token --value <YOUR_TOKEN>

# Reference in container (requires managed identity setup)
```

### Auto-restart on Failure

The current configuration uses `restartPolicy: Always`, which automatically restarts the container if it fails.

## Support

For issues with:
- Discord.py: https://discordpy.readthedocs.io/
- TikTokLive: https://github.com/isaackogan/TikTokLive
- Azure Container Instances: https://docs.microsoft.com/en-us/azure/container-instances/
