FROM node:20-alpine AS base

# SECURITY: Install security updates
RUN apk update && apk upgrade --no-cache

WORKDIR /app

# ---- Dependencies Stage ----
FROM base AS deps

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies (use npm install if no lock file, npm ci if lock file exists)
RUN if [ -f package-lock.json ]; then npm ci --only=production; else npm install --only=production; fi

# ---- Build Stage ----
FROM base AS builder

COPY package.json package-lock.json* ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

# Copy application code
COPY . .

# Build the application
RUN npm run build

# ---- Production Stage ----
FROM base AS runner

# SECURITY: Set environment variables
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1

# SECURITY: Create non-root user
RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 nextjs

# Copy built application
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# SECURITY: Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

# SECURITY: Production mode
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]

