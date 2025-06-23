#!/bin/bash
set -e

# CONFIG
PROJECT_ID="project-agentd"
REGION="asia-south1"
SERVICE_NAME="agent-flask-app"
IMAGE="gcr.io/$PROJECT_ID/$SERVICE_NAME"

# read .env file and convert to comma-separated KEY=VALUE list
ENV_VARS=$(grep -v '^#' .env | grep -v '^GOOGLE_APPLICATION_CREDENTIALS=' | xargs | sed 's/ /,/g')

echo "Building Docker image..."
docker build -t $IMAGE .

echo "Pushing image to GCR..."
docker push $IMAGE

echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars $ENV_VARS

echo "[#] Deployment complete!"
