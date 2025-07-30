# Project Structure for Customer Data Platform (CDP)

modules/
  ingestion/        # Data ingestion (S3, webhooks, batch, etc.)
  transformation/   # PySpark/ETL jobs
  unification/      # Customer 360 unification logic
  activation/       # Activation pipeline (exports, integrations)
  api/              # API services (enrichment, query)
  analytics/        # Analytics, reporting, dashboards

services/           # Service definitions, Dockerfiles, etc.
scripts/            # Utility scripts, local dev helpers
config/             # Configuration files (YAML, JSON, etc.)
data/               # Local data samples, test data
localstack-data/    # LocalStack state/data

tests/              # Unit/integration tests
README.md           # System design and documentation
docker-compose.yml  # Local dev environment (LocalStack, etc.)
