# Build Angular assets
FROM node:20-alpine AS build

WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend ./
RUN npm run build -- --configuration production

# Serve static build via nginx
FROM nginx:1.27-alpine

COPY --from=build /app/dist/angular-frontend/browser /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY frontend/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80

HEALTHCHECK CMD wget --spider -q http://localhost || exit 1

ENTRYPOINT ["/entrypoint.sh"]
