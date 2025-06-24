#!/bin/bash
set -e

# CONFIG
PROJECT_ID="project-agentd"
REGION="us-central1" # "asia-south1" does not support domain mappings
SERVICE_NAME="agent-flask-app"
IMAGE="gcr.io/$PROJECT_ID/$SERVICE_NAME"

# read .env file and convert to comma-separated KEY=VALUE list
ENV_VARS=$(grep -v '^#' .env | grep -v '^GOOGLE_APPLICATION_CREDENTIALS=' | xargs | sed 's/ /,/g')

cd react-app
echo "[#] Building React app..."
rm -rf flask-app/static
./build.sh
echo "[#] React app build complete! Copying files completed."
cd ..

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
  --set-env-vars $ENV_VARS \
  --update-secrets=GOOGLE_APPLICATION_CREDENTIALS_JSON=projects/1040077044123/secrets/key:latest \
  --service-account agentd-master@$PROJECT_ID.iam.gserviceaccount.com

echo "[#] Testing the deployed service..."

curl -s https://agentd.adityabavadekar.tech/api/db-check | jq