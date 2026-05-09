# Frontend Dockerfile - React PWA with Docker Hardened Images
# Multi-stage build: Node builder + Nginx runtime
# DHI hardened base for production security

# Stage 1: Builder
FROM dhi.io/node:20-debian13-dev AS builder

WORKDIR /app

ARG REACT_APP_API_URL=http://localhost:8000
ENV REACT_APP_API_URL=${REACT_APP_API_URL}

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy source and build production bundle
COPY . .
RUN DISABLE_ESLINT_PLUGIN=true npm run build

# Stage 2: Runtime
FROM dhi.io/nginx:1.30-debian13-dev

WORKDIR /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built app from builder
COPY --from=builder /app/build /usr/share/nginx/html

# Ensure proper permissions for nginx
RUN chown -R nginx:nginx /usr/share/nginx/html /var/cache/nginx /var/log/nginx
USER nginx

EXPOSE 3000

HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
