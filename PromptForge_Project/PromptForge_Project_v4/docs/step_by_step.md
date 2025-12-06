
# PromptForge — Step-by-step End-to-End Setup & Run Guide

This guide walks through completing the PromptForge v2 project from zero to a running stack, verifying functionality, and extending it for production. Follow each step in order.

---
## 0. Prerequisites (local machine)
- Docker & Docker Compose installed (recommended Docker Desktop).
- Git installed.
- Python 3.8+ (for running scripts / tests locally if not using Docker).
- (Optional) Node.js & npm/yarn for frontend development.
- Sufficient disk space if using Hugging Face models locally (models can be multiple GBs).

---
## 1. Get the project files
1. Download `PromptForge_Project_v2.zip` and unzip, or clone your GitHub repo if you pushed it.
   ```bash
   unzip PromptForge_Project_v2.zip -d PromptForge_Project
   cd PromptForge_Project_v2
   ```
2. Inspect files: `backend/`, `docker-compose.yml`, `docs/`, `infra/`, `tests/`.

---
## 2. Configure environment variables (secrets)
1. Copy the example env file:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env`:
   - Set `MODEL_PROVIDER` to `mock`, `hf`, or `openai`.
   - If `openai`, set `OPENAI_API_KEY` and optionally `OPENAI_ENGINE`.
   - If `hf` and you prefer HF Inference API instead of local model, you may need a HF token and code changes (see notes below).
   - `DATABASE_URL` defaults to a Postgres service in docker-compose; leave it as-is for local Docker usage.

**Security note:** Never commit `.env` or keys to source control. Use your CI/CD secrets manager.

---
## 3. Run the full stack with Docker Compose (recommended)
1. Build and run:
   ```bash
   docker-compose up --build
   ```
2. Services started:
   - Backend API: `http://localhost:8000/docs`
   - Postgres: `localhost:5432` (DB: `promptforge`, user: `promptforge_user`, password: `promptforge_pass`)
   - Grafana: `http://localhost:3000` (admin/admin)

3. Verify backend:
   - Open `http://localhost:8000/docs` (Swagger UI) and try `GET /templates` and `POST /generate` (use a JSON body matching the `PromptRequest` model).

---
## 4. Run tests locally (without Docker)
1. Create a virtual environment and install backend deps:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r backend/requirements.txt
   ```
2. Initialize DB for local sqlite (if using default):
   ```bash
   bash scripts/init_db.sh
   ```
3. Run pytest:
   ```bash
   pytest -q
   ```

---
## 5. Using real inference providers
### OpenAI
1. Set in `.env`: `MODEL_PROVIDER=openai` and `OPENAI_API_KEY=your_key_here`.
2. Restart the backend (Docker Compose will pick up env if using `.env` in same folder).
3. Use `POST /generate` to send prompt requests. Monitor Postgres to confirm rows in `prompt_metrics`.

**Notes:** OpenAI API usage may incur cost and rate limits. Use small `max_tokens` in testing.

### Hugging Face (local model)
1. Set in `.env`: `MODEL_PROVIDER=hf` and `HF_MODEL=your_model_id`.
2. Local HF models can be large — ensure sufficient RAM/disk. The backend uses `transformers` pipeline for summarization by default.
3. Restart backend. The first inference will download model weights and may take time.

### Hugging Face (Inference API alternative)
- To avoid heavy local downloads, modify `backend/main.py` to call the HF Inference API (requires HF token) instead of using `transformers` locally. Store HF token in `.env` and implement a simple HTTP adapter that posts to the HF inference endpoint.

---
## 6. Grafana: connect to Postgres and build dashboards
1. Open Grafana at `http://localhost:3000` (admin/admin).
2. Add Data Source -> PostgreSQL:
   - Host: `postgres:5432`
   - Database: `promptforge`
   - User: `promptforge_user`
   - Password: `promptforge_pass`
   - Note: When Grafana runs in Docker Compose, use hostname `postgres`.
3. Create a dashboard with panels using queries against `prompt_metrics`. Example query:
   ```sql
   SELECT id, template_id, (metrics->>'relevance')::float as relevance, timestamp
   FROM prompt_metrics
   ORDER BY timestamp DESC
   LIMIT 100;
   ```
4. Visualize `relevance` and `clarity` across `experiment_group` with time-series or bar charts.

---
## 7. Running A/B experiments with `experiment_group`
1. Assign `experiment_group` when calling `/generate`, e.g. `"A"` or `"B"`.
2. Collect a statistically meaningful number of samples per group (depends on expected effect size).
3. Export metrics from Postgres or run statistical tests in Python (e.g., SciPy or Bayesian tests) using columns `(metrics->>'relevance')::float` and `(metrics->>'clarity')::float` to compare groups.
4. Optional: implement a backend endpoint to compute p-values or Bayesian credible intervals automatically and show them in Grafana or frontend.

---
## 8. CI / GitHub Actions notes
1. Store `OPENAI_API_KEY` and DB credentials as GitHub Secrets.
2. The included `.github/workflows/ci.yml` runs `pytest`. For tests requiring real APIs, mock external calls or run them behind feature flags in CI.

---
## 9. Deploying to a cloud provider (high-level)
1. Containerize services (already done). Push images to a registry (Docker Hub, GHCR, ECR).
2. Use Kubernetes, ECS, or Fargate to orchestrate services. Use managed Postgres (RDS) in prod and a managed secrets store.
3. Use Prometheus + Grafana or a hosted observability platform for production metrics. Postgres is OK for small-scale experiments but use a time-series DB for heavy telemetry.
4. Add authentication, rate limiting, request logging, and monitoring for production readiness.

---
## 10. Suggested extensions (prioritized)
1. Replace local HF with HF Inference API adapter to avoid heavy downloads.
2. Implement a lightweight frontend that assigns `experiment_group` and shows live metric charts.
3. Add Postgres migrations via Alembic and a proper release/migration strategy.
4. Add A/B statistical endpoints and automated experiment analysis.
5. Add Prometheus exporter to emit metrics to Prometheus, then use Grafana for dashboards and alerts.

---
## 11. Troubleshooting tips
- If the backend fails to connect to Postgres in Docker, ensure `DATABASE_URL` matches service name: `postgresql://promptforge_user:promptforge_pass@postgres:5432/promptforge`.
- For HF local models, ensure `transformers` is installed and you have sufficient memory; consider switching to `MODEL_PROVIDER=mock` for quick iterations.
- If Docker Compose fails to build due to missing system dependencies, ensure apt packages are installed in Dockerfile (the provided Dockerfile includes common build deps).

---
## 12. Where the step-by-step file is located
This exact guide is located at: `docs/step_by_step.md` in the project root.
