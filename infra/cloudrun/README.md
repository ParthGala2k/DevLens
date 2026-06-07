# Cloud Run deployment

Two services: `devlens-backend` and `devlens-frontend`, each built from its Dockerfile.

```bash
# Backend
gcloud run deploy devlens-backend \
  --source ./backend \
  --region "$GOOGLE_CLOUD_LOCATION" \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,..." \
  --allow-unauthenticated

# Frontend (point NEXT_PUBLIC_API_BASE_URL at the backend URL from above)
gcloud run deploy devlens-frontend \
  --source ./frontend \
  --region "$GOOGLE_CLOUD_LOCATION" \
  --set-env-vars "NEXT_PUBLIC_API_BASE_URL=<backend-url>" \
  --allow-unauthenticated
```

TODO: move secrets to Secret Manager; grant the backend runtime SA BigQuery + Firestore +
Vertex AI roles. `make deploy` will wrap these commands.
