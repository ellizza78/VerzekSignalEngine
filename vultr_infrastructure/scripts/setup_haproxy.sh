#!/bin/bash
# HAProxy Load Balancer Setup Script
# Configure HAProxy on the hub node for load balancing across mesh nodes

set -e

echo "=========================================="
echo "Verzek - HAProxy Load Balancer Setup"
echo "=========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
   echo "Please run as root (sudo)"
   exit 1
fi

# Variables
NODE1_VPN_IP="${1:-10.10.0.2}"
NODE2_VPN_IP="${2:-10.10.0.3}"
HUB_VPN_IP="${3:-10.10.0.1}"

echo "Configuring HAProxy load balancer..."
echo "Hub: $HUB_VPN_IP"
echo "Node1: $NODE1_VPN_IP"
echo "Node2: $NODE2_VPN_IP"

# Install HAProxy
echo "Installing HAProxy..."
apt update -y
apt install -y haproxy

# Backup original config
if [ -f /etc/haproxy/haproxy.cfg ]; then
    cp /etc/haproxy/haproxy.cfg /etc/haproxy/haproxy.cfg.backup
fi

# Create HAProxy configuration
echo "Creating HAProxy configuration..."
cat > /etc/haproxy/haproxy.cfg <<EOF
global
    log /dev/log local0
    log /dev/log local1 notice
    chroot /var/lib/haproxy
    stats socket /run/haproxy/admin.sock mode 660 level admin expose-fd listeners
    stats timeout 30s
    user haproxy
    group haproxy
    daemon

    # Default SSL material locations
    ca-base /etc/ssl/certs
    crt-base /etc/ssl/private

    # Security
    ssl-default-bind-ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256
    ssl-default-bind-options ssl-min-ver TLSv1.2 no-tls-tickets

defaults
    log global
    mode http
    option httplog
    option dontlognull
    timeout connect 10s
    timeout client 30s
    timeout server 30s
    errorfile 400 /etc/haproxy/errors/400.http
    errorfile 403 /etc/haproxy/errors/403.http
    errorfile 408 /etc/haproxy/errors/408.http
    errorfile 500 /etc/haproxy/errors/500.http
    errorfile 502 /etc/haproxy/errors/502.http
    errorfile 503 /etc/haproxy/errors/503.http
    errorfile 504 /etc/haproxy/errors/504.http

# Statistics page
listen stats
    bind 127.0.0.1:8404
    stats enable
    stats uri /stats
    stats refresh 30s
    stats admin if TRUE

# Frontend - accepts connections from Nginx
frontend verzek_proxy
    bind 127.0.0.1:5000
    default_backend mesh_nodes

# Backend - distributes to mesh nodes
backend mesh_nodes
    balance roundrobin
    option httpchk GET /health
    http-check expect status 200
    
    # Hub node (local)
    server hub $HUB_VPN_IP:5000 check inter 5s fall 3 rise 2
    
    # Worker nodes
    server node1 $NODE1_VPN_IP:5000 check inter 5s fall 3 rise 2
    server node2 $NODE2_VPN_IP:5000 check inter 5s fall 3 rise 2
EOF

# Create stats authentication (optional)
# echo "admin:$(openssl passwd -1 yourpassword)" > /etc/haproxy/haproxy.passwd

# Test configuration
echo "Testing HAProxy configuration..."
haproxy -c -f /etc/haproxy/haproxy.cfg

# Enable and restart HAProxy
echo "Enabling and starting HAProxy..."
systemctl enable haproxy
systemctl restart haproxy

echo ""
echo "=========================================="
echo "HAProxy installed successfully!"
echo "=========================================="
echo "Listening on: 127.0.0.1:5000"
echo "Load balancing to:"
echo "  - Hub: $HUB_VPN_IP:5000"
echo "  - Node1: $NODE1_VPN_IP:5000"
echo "  - Node2: $NODE2_VPN_IP:5000"
echo ""
echo "HAProxy Stats: http://127.0.0.1:8404/stats"
echo ""
echo "Check status: systemctl status haproxy"
echo "View logs: journalctl -u haproxy -f"
echo "=========================================="
