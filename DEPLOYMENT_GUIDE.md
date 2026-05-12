# Deployment Guide

This project now includes a minimal container-based deployment stack for the backend.

## What Is Included

- `Dockerfile` for the Flask API backend
- `docker-compose.yml` for the app + Ollama runtime
- `wsgi.py` entrypoint for Gunicorn
- `.dockerignore` to keep builds clean

## Local Container Run

1. Build and start the stack:

```bash
docker compose up --build
```

2. Pull the Ollama model inside the Ollama container if needed:

```bash
docker exec -it virtualgirlfriend-ollama ollama pull mistral
```

3. Open the API:

```bash
curl http://localhost:5000/api/status
```

## Environment Notes

- `OLLAMA_BASE_URL` defaults to `http://localhost:11434` in local mode.
- In Docker Compose it is set to `http://ollama:11434`.
- `FLASK_DEBUG` should be `False` in containers.
- `PORT` defaults to `5000`.
- The compose stack uses PostgreSQL for conversation storage via `DATABASE_URL`.

## Production Considerations

- Replace SQLite with PostgreSQL for multi-user production deployments.
- Add a reverse proxy such as Nginx or Caddy in front of Gunicorn.
- Configure backups, logging, and health checks before exposing publicly.
- If you want GPU-backed Ollama inference, run Ollama on the host or a GPU-enabled container host and point `OLLAMA_BASE_URL` at it.
- See [PRODUCTION_HARDENING.md](PRODUCTION_HARDENING.md) for the remaining operational work.
