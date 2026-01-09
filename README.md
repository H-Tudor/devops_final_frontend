# DevOps Final Frontend - LLM Compose Generator

Transform a loose list of services into a full docker-compose file with the power of AI.

## About

The frontend is now an Angular single-page application. It mirrors the previous Streamlit UI while running entirely in the browser and communicating with the `devops-final-backend` and Keycloak.

Runtime configuration (API host, Keycloak realm, and client credentials) is injected via `assets/config.js`. When running in a container, these values are generated from environment variables so you can point the UI to any backend without rebuilding.

## Prerequisites

- Node.js 18+ and npm
- Backend API and Keycloak instances reachable by the browser

## Local development

```bash
cd frontend
npm install
npm start
```

The app runs on `http://localhost:4200`. Update `src/assets/config.js` if you need to change backend endpoints locally.

## Production build

```bash
cd frontend
npm run build
```

The production build is emitted to `frontend/dist/angular-frontend/browser`.

## Container

The Dockerfile builds the Angular app and serves it through Nginx. At runtime you can configure the backend by setting environment variables:

- `API_HOST` (default: `http://localhost:8000`)
- `API_VERSION` (default: `vNext`)
- `AUTH_HOST` (default: `http://localhost:8080`)
- `AUTH_REALM` (default: `devops-final`)
- `AUTH_CLIENT_ID`
- `AUTH_CLIENT_SECRET`
- `AUTH_USERNAME`
- `AUTH_PASSWORD`

Example:

```bash
docker build -t devops-final-frontend .
docker run -p 8080:80 \
  -e API_HOST=http://devops_final_backend:8000 \
  -e AUTH_HOST=http://keycloak:8080 \
  -e AUTH_REALM=devops \
  -e AUTH_CLIENT_ID=frontend \
  devops-final-frontend
```

## Testing

Run a production build to ensure the application compiles successfully:

```bash
cd frontend
npm run build
```
