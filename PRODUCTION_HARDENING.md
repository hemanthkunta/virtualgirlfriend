# Production Hardening Guide

This document covers the remaining work needed to turn the container stack into a production deployment.

## Already Implemented

- Flask API runs behind Gunicorn in a container
- Ollama runs as a separate service in Docker Compose
- PostgreSQL is used for conversation storage in the compose stack
- SQLite remains available for local development

## Recommended Next Steps

### Reverse Proxy

Put Nginx or Caddy in front of the app container.

Suggested responsibilities:
- Terminate TLS
- Handle request timeouts
- Serve static assets or cache video responses if needed
- Add rate limiting and request size limits

### SSL / HTTPS

- Use Let's Encrypt or your hosting provider's managed certificates
- Redirect HTTP to HTTPS
- Set secure cookie and CORS headers if you add auth later

### Monitoring

Track at least the following:
- API uptime
- Ollama health
- PostgreSQL health
- Disk usage for audio/video outputs
- Container restarts

### Backups

- Back up PostgreSQL volumes regularly
- Back up generated media if you need conversation replay or audit history
- Store backups off-host or in object storage

### Security Review

- Remove any unused environment variables
- Avoid exposing Ollama publicly unless needed
- Lock down database credentials
- Review file upload limits and media handling paths

### Health Checks

Suggested endpoints:
- `/api/health`
- `/api/status`

## Deployment Order

1. Build and test the Docker Compose stack locally
2. Add reverse proxy and TLS
3. Set up backups
4. Add monitoring and alerts
5. Run load tests before public launch
