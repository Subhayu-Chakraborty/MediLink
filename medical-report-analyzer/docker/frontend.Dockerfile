# ─────────────────────────────────────────────────────────────────────────────
# Frontend Dockerfile — Vite + React + TypeScript (Node 18)
# Location: docker/frontend.Dockerfile
# Build context: ./frontend
# ─────────────────────────────────────────────────────────────────────────────

FROM node:18-alpine

# Set working directory
WORKDIR /app

# Install dependencies first (layer caching optimization)
COPY package.json package-lock.json* ./
RUN npm ci

# Copy application source code
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Run Vite dev server, binding to all interfaces (required inside Docker)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
