#!/bin/sh
set -e

CONFIG_PATH=/usr/share/nginx/html/assets/config.js

cat > "${CONFIG_PATH}" <<EOF
(function () {
  window.__APP_CONFIG__ = {
    apiHost: "${API_HOST:-http://localhost:8000}",
    apiVersion: "${API_VERSION:-vNext}",
    authHost: "${AUTH_HOST:-http://localhost:8080}",
    authRealm: "${AUTH_REALM:-devops-final}",
    authClientId: "${AUTH_CLIENT_ID:-frontend}",
    authClientSecret: "${AUTH_CLIENT_SECRET:-}",
    authUsername: "${AUTH_USERNAME:-}",
    authPassword: "${AUTH_PASSWORD:-}",
  };
})();
EOF

exec nginx -g 'daemon off;'
