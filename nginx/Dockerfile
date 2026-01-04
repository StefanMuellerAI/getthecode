FROM nginx:1.25-alpine

# SECURITY: Install security updates
RUN apk update && apk upgrade --no-cache

# Remove default config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom config as main nginx.conf (replaces the default)
COPY nginx.conf /etc/nginx/nginx.conf

# Copy htpasswd for Basic Auth (stats page protection)
COPY .htpasswd /etc/nginx/.htpasswd

# Create directory for SSL certificates
RUN mkdir -p /etc/nginx/ssl

# Create directory for Let's Encrypt challenges
RUN mkdir -p /var/www/certbot

# SECURITY: Create non-root user (nginx already runs as nginx user internally)
# But we set proper permissions
RUN chown -R nginx:nginx /var/cache/nginx \
    && chown -R nginx:nginx /var/log/nginx \
    && chown -R nginx:nginx /etc/nginx/conf.d

# Expose ports
EXPOSE 80 443

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
    CMD wget --no-verbose --tries=1 --spider http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]







