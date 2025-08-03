# Multi-stage build for optimized production image
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY backend/package*.json ./backend/
COPY frontend/package*.json ./frontend/

# Install dependencies
RUN cd backend && npm install
RUN cd frontend && npm install

# Copy source code
COPY backend ./backend
COPY frontend ./frontend

# Build backend
RUN cd backend && npm run build

# Build frontend
RUN cd frontend && npm run build

# Production stage
FROM node:18-alpine

WORKDIR /app

# Install serve for frontend
RUN npm install -g serve

# Copy backend build and dependencies
COPY --from=builder /app/backend/dist ./backend/dist
COPY --from=builder /app/backend/node_modules ./backend/node_modules
COPY --from=builder /app/backend/package.json ./backend/

# Copy frontend build
COPY --from=builder /app/frontend/dist ./frontend/dist

# Create startup script
RUN echo '#!/bin/sh' > /app/start.sh && \
    echo 'cd /app/backend && node dist/index.js &' >> /app/start.sh && \
    echo 'cd /app && serve -s frontend/dist -l 3000 &' >> /app/start.sh && \
    echo 'wait' >> /app/start.sh && \
    chmod +x /app/start.sh

# Expose ports
EXPOSE 3000 3001

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3001/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"

# Start both services
CMD ["/app/start.sh"]