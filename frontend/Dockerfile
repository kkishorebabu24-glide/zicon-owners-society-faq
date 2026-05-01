# Frontend Dockerfile - React PWA with Docker Hardened Images
# Multi-stage build: Node builder + Nginx runtime

# Stage 1: Builder
FROM dhi.io/node:20-debian13-dev AS builder

WORKDIR /app

# Copy package files first for layer caching
COPY frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy source
COPY frontend .

# Build production bundle (disable eslint for line ending issues)
RUN DISABLE_ESLINT_PLUGIN=true npm run build

# Stage 2: Runtime (using -dev for shell access)
FROM dhi.io/nginx:1.30-debian13-dev

# Copy nginx configuration
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Copy built app from builder
COPY --from=builder /app/build /usr/share/nginx/html

# Ensure proper permissions for nginx
RUN chown -R nginx:nginx /usr/share/nginx/html /var/cache/nginx /var/log/nginx
USER nginx

EXPOSE 3000

HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
