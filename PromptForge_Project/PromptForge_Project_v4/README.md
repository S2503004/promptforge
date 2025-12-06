
# PromptForge — End-to-end Prompt Engineering Toolkit (GitHub-ready)

**PromptForge** demonstrates a production-style prompt engineering project with:
- FastAPI backend supporting mock/OpenAI/Hugging Face inference adapters
- Simple React TypeScript frontend playground (minimal, ready to `npm install`)
- Postgres for metrics persistence, Grafana for dashboards (docker-compose)
- Dockerized services, GitHub Actions CI, tests, and full documentation

## Quick GitHub-ready checklist
1. Download and unzip this repository.
2. Inspect `.env.example` and create `.env` with required secrets.
3. To run locally with Docker: `docker-compose up --build` (services: backend, postgres, grafana).
4. To run frontend locally:
   - `cd frontend`
   - `npm install`
   - `npm run dev` (or `npm start` if using CRA)
5. Backend API docs: `http://localhost:8000/docs`
6. Grafana: `http://localhost:3000` (admin/admin)

## Repo structure
- `backend/` — FastAPI app, requirements, Docker entry
- `frontend/` — React TypeScript app (basic playground)
- `infra/` — Dockerfiles and infra scripts
- `docker-compose.yml` — local stack (backend, postgres, grafana)
- `docs/` — report, step by step, secrets, resume blurb
- `.github/workflows/ci.yml` — test CI

## License
MIT — see LICENSE file.
