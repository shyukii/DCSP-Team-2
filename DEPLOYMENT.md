# Cloud Run Deployment Guide

## Prerequisites
- `gcloud` CLI installed
- Docker installed

## Step 1: Authentication
```bash
gcloud auth login
gcloud config set project nimble-equator-460013-a6
```

## Step 2: Enable APIs
```bash
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

## Step 3: Build and Push Container
```bash
docker build -t gcr.io/nimble-equator-460013-a6/nutribot-app .
gcloud auth configure-docker
docker push gcr.io/nimble-equator-460013-a6/nutribot-app
```

## Step 4: Create Secrets
Replace `YOUR_*` with actual values:

```bash
echo "YOUR_BOT_TOKEN" | gcloud secrets create bot-token --data-file=-
echo "YOUR_OPENAI_KEY" | gcloud secrets create openai-api-key --data-file=-
echo "YOUR_REPLICATE_TOKEN" | gcloud secrets create replicate-api-token --data-file=-
echo "YOUR_SUPABASE_URL" | gcloud secrets create supabase-url --data-file=-
echo "YOUR_SUPABASE_KEY" | gcloud secrets create supabase-anon-key --data-file=-
echo "YOUR_CLARIFAI_TANK_PAT" | gcloud secrets create clarifai-tank-pat --data-file=-
echo "YOUR_CLARIFAI_PLANT_PAT" | gcloud secrets create clarifai-plant-pat --data-file=-
```

## Step 5: Create Service Account
```bash
gcloud iam service-accounts create nutribot-service-account
gcloud projects add-iam-policy-binding nimble-equator-460013-a6 --member="serviceAccount:nutribot-service-account@nimble-equator-460013-a6.iam.gserviceaccount.com" --role="roles/secretmanager.secretAccessor"
```

## Step 6: Update and Deploy
**Bash/Linux/macOS:**
```bash
sed 's/PROJECT_ID/nimble-equator-460013-a6/g' cloudrun.yaml > cloudrun-deploy.yaml
gcloud run services replace cloudrun-deploy.yaml --region=asia-southeast1
```

**PowerShell/Windows:**
```powershell
(Get-Content cloudrun.yaml) -replace 'PROJECT_ID', 'nimble-equator-460013-a6' | Set-Content cloudrun-deploy.yaml
gcloud run services replace cloudrun-deploy.yaml --region=asia-southeast1
```

## Step 7: Get Service URL
```bash
gcloud run services describe nutribot-app --region=asia-southeast1 --format="value(status.url)"
```

## Step 8: Set Telegram Webhook
Replace `BOT_TOKEN` with your actual token and `SERVICE_URL` with URL from step 7:

```bash
curl -X POST "https://api.telegram.org/bot7787023282:AAGcLCvCiiT94hVKfWzSzMtz5WNtnJE1Axo/setWebhook" -H "Content-Type: application/json" -d '{"url": "https://nutribot-app-7ksso7ovsa-as.a.run.app/webhook"}'
```
```powershell
Invoke-WebRequest -Uri "https://api.telegram.org/bot7787023282:AAGcLCvCiiT94hVKfWzSzMtz5WNtnJE1Axo/setWebhook" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"url":"https://nutribot-app-7ksso7ovsa-as.a.run.app/webhook"}'
Invoke-WebRequest -Uri "https://api.telegram.org/bot7787023282:AAGcLCvCiiT94hVKfWzSzMtz5WNtnJE1Axo/setWebhook" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"url":"https://nutribot-app-340554908049.asia-southeast1.run.app/webhook"}'

```
## Updates
When you make changes to the code and want to deploy a new version:

```bash
docker build -t gcr.io/nimble-equator-460013-a6/nutribot-app .
docker push gcr.io/nimble-equator-460013-a6/nutribot-app
gcloud run deploy nutribot-app --image gcr.io/nimble-equator-460013-a6/nutribot-app --region=asia-southeast1
```

## Troubleshooting
Check logs:
```bash
gcloud logs tail /projects/nimble-equator-460013-a6/logs/run.googleapis.com%2Fstdout --region=asia-southeast1
```