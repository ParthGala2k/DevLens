#!/usr/bin/env bash
# Enable the GCP APIs and create the datasets DevLens needs. Run once per project.
# TODO: parameterize from .env; this is a checklist scaffold.
set -euo pipefail

: "${GOOGLE_CLOUD_PROJECT:?set GOOGLE_CLOUD_PROJECT}"

gcloud config set project "$GOOGLE_CLOUD_PROJECT"

gcloud services enable \
  aiplatform.googleapis.com \
  bigquery.googleapis.com \
  firestore.googleapis.com \
  run.googleapis.com

# Metrics dataset for derived views
bq --location="${GOOGLE_CLOUD_LOCATION:-US}" mk -d "${BIGQUERY_DATASET_METRICS:-devlens_metrics}" || true

echo "Done. Next: configure Fivetran connectors (github/jira/slack/calendar/pagerduty) -> BigQuery,"
echo "      set GitHub MCP vars in .env, then 'make bq-views'."
