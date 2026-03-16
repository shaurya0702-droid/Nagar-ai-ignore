# ═══════════════════════════════════════════════════════════════════════════
# NagarAI Frontend — Nginx Static Server
# Build context: ./frontend  (set in docker-compose.yml)
# ═══════════════════════════════════════════════════════════════════════════
FROM nginx:1.25-alpine

# Remove default nginx config
RUN rm -f /etc/nginx/conf.d/default.conf /etc/nginx/nginx.conf

# Copy our custom nginx.conf (in same build context as this Dockerfile)
COPY nginx.conf /etc/nginx/nginx.conf

# Copy all frontend static files
COPY . /usr/share/nginx/html

# Remove Dockerfile and nginx.conf from served files
RUN rm -f /usr/share/nginx/html/Dockerfile \
          /usr/share/nginx/html/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
