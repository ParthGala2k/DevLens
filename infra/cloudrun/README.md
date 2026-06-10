# Cloud Run deployment

Two services: `devlens-backend` and `devlens-frontend`.

## Deployed URLs

| Service | URL |
|---|---|
| Frontend | https://devlens-frontend-942383800159.us-central1.run.app |
| Backend | https://devlens-backend-942383800159.us-central1.run.app |

GCP project: `dev-blindspot-agent` · Region: `us-central1`

---

## Backend

Built from `backend/Dockerfile` via Cloud Build (`--source`). No build-time variables needed.

```bash
gcloud run deploy devlens-backend \
  --source ./backend \
  --region us-central1 \
  --env-vars-file /tmp/backend-envvars.yaml \
  --allow-unauthenticated \
  --memory 1Gi \
  --quiet
```

Pass environment variables via `--env-vars-file` (YAML). Using a file avoids shell-escaping issues with colons and commas in URLs. The file must contain the **complete** set of env vars each time — `--env-vars-file` replaces all existing vars.

See the root README for a full example YAML.

---

## Frontend

**`NEXT_PUBLIC_API_BASE_URL` is a build-time variable in Next.js.** It is inlined into the client JS bundle during `next build` and cannot be changed at runtime. The frontend image must be built locally with the backend URL passed as a Docker `--build-arg`, then pushed to Artifact Registry and deployed via `--image`.

```bash
BACKEND_URL="https://devlens-backend-942383800159.us-central1.run.app"
IMAGE="us-central1-docker.pkg.dev/dev-blindspot-agent/cloud-run-source-deploy/devlens-frontend:latest"

# Build with backend URL baked in
docker build \
  --build-arg NEXT_PUBLIC_API_BASE_URL="$BACKEND_URL" \
  -t "$IMAGE" \
  ./frontend

# Push
docker push "$IMAGE"

# Deploy from image (not --source)
gcloud run deploy devlens-frontend \
  --image "$IMAGE" \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --quiet
```

If `docker push` fails with a credential helper error, authenticate via access token:

```bash
gcloud auth print-access-token \
  | docker login -u oauth2accesstoken --password-stdin https://us-central1-docker.pkg.dev
```

---

## CORS

The backend's `CORS_ORIGINS` env var must include the frontend URL. After the frontend is deployed:

```bash
# Update CORS_ORIGINS in /tmp/backend-envvars.yaml, then:
gcloud run services update devlens-backend \
  --region us-central1 \
  --env-vars-file /tmp/backend-envvars.yaml \
  --quiet
```

---

## Notes

- The backend root URL (`/`) returns `{"detail": "Not Found"}` — this is expected FastAPI behaviour. Use `/health` to verify the service is up.
- On Cloud Run, `GOOGLE_APPLICATION_CREDENTIALS` must **not** be set. The runtime service account provides Application Default Credentials automatically.
- `FIRESTORE_EMULATOR_HOST` must **not** be set in production — leave it unset to use real Firestore.
- The Artifact Registry repository `cloud-run-source-deploy` was created automatically by the first `gcloud run deploy --source` call.
