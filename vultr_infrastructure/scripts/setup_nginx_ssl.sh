#!/bin/bash
# Nginx + Let's Encrypt SSL Setup Script
# Configure Nginx reverse proxy with automatic SSL certificates

set -e

echo "=========================================="
echo "Verzek - Nginx + SSL Setup"
echo "=========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
   echo "Please run as root (sudo)"
   exit 1
fi

# Variables
DOMAIN="${1:-verzekhub.yourdomain.com}"
EMAIL="${2:-support@vezekinnovative.com}"

if [ "$DOMAIN" = "verzekhub.yourdomain.com" ]; then
    echo "ERROR: Please provide your actual domain name"
    echo "Usage: ./setup_nginx_ssl.sh yourdomain.com your@email.com"
    exit 1
fi

echo "Domain: $DOMAIN"
echo "Email: $EMAIL"

# Install Nginx and Certbot
echo "Installing Nginx and Certbot..."
apt update -y
apt install -y nginx certbot python3-certbot-nginx

# Create Nginx configuration
echo "Creating Nginx configuration..."
cat > /etc/nginx/sites-available/verzek-hub <<EOF
# Verzek Proxy Hub - Nginx Configuration
# Auto-generated on $(date)

server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Access logs
    access_log /var/log/nginx/verzek-access.log;
    error_log /var/log/nginx/verzek-error.log;

    # Proxy to HAProxy
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeouts for long-running requests
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffer settings
        proxy_buffering off;
        proxy_request_buffering off;
    }

    # Health check endpoint (bypass proxy)
    location /nginx-health {
        access_log off;
        return 200 "OK\n";
        add_header Content-Type text/plain;
    }
}
EOF

# Enable site
echo "Enabling Nginx site..."
ln -sf /etc/nginx/sites-available/verzek-hub /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
echo "Testing Nginx configuration..."
nginx -t

# Reload Nginx
echo "Reloading Nginx..."
systemctl reload nginx

# Request SSL certificate
echo ""
echo "Requesting SSL certificate from Let's Encrypt..."
echo "This may take a few moments..."
certbot --nginx -d "$DOMAIN" --agree-tos -m "$EMAIL" --non-interactive --redirect

# Setup auto-renewal
echo "Setting up automatic SSL renewal..."
(crontab -l 2>/dev/null | grep -v certbot; echo "0 2 * * * certbot renew --quiet --deploy-hook 'systemctl reload nginx'") | crontab -

echo ""
echo "=========================================="
echo "Nginx + SSL installed successfully!"
echo "=========================================="
echo "Domain: https://$DOMAIN"
echo "Certificate: Let's Encrypt"
echo "Auto-renewal: Daily at 2:00 AM"
echo ""
echo "Test endpoints:"
echo "  Health: https://$DOMAIN/health"
echo "  IP Info: https://$DOMAIN/ip"
echo ""
echo "Check certificate:"
echo "  certbot certificates"
echo ""
echo "Manual renewal:"
echo "  certbot renew"
echo ""
echo "Nginx logs:"
echo "  /var/log/nginx/verzek-access.log"
echo "  /var/log/nginx/verzek-error.log"
echo "=========================================="
