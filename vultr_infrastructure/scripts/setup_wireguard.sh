#!/bin/bash
# WireGuard VPN Mesh Setup Script
# Automatically configure WireGuard on Vultr nodes

set -e

echo "=========================================="
echo "Verzek - WireGuard VPN Mesh Setup"
echo "=========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
   echo "Please run as root (sudo)"
   exit 1
fi

# Variables (update these for your setup)
NODE_NAME="${1:-hub}"
NODE_VPN_IP="${2:-10.10.0.1}"
LISTEN_PORT=51820

echo "Configuring node: $NODE_NAME"
echo "VPN IP: $NODE_VPN_IP"

# Install WireGuard
echo "Installing WireGuard..."
apt update -y
apt install -y wireguard wireguard-tools

# Generate keys
echo "Generating WireGuard keys..."
mkdir -p /etc/wireguard
cd /etc/wireguard

if [ ! -f privatekey ]; then
    wg genkey | tee privatekey | wg pubkey > publickey
    chmod 600 privatekey
fi

PRIVATE_KEY=$(cat privatekey)
PUBLIC_KEY=$(cat publickey)

echo "Public Key: $PUBLIC_KEY"
echo "(Save this key - you'll need it for peer configuration)"

# Create base config
echo "Creating WireGuard configuration..."
cat > /etc/wireguard/wg0.conf <<EOF
[Interface]
Address = $NODE_VPN_IP/24
ListenPort = $LISTEN_PORT
PrivateKey = $PRIVATE_KEY
PostUp = sysctl -w net.ipv4.ip_forward=1
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT
PostUp = iptables -A FORWARD -o wg0 -j ACCEPT
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT
PostDown = iptables -D FORWARD -o wg0 -j ACCEPT

# Peers will be added below
# Use: wg set wg0 peer <PUBLIC_KEY> allowed-ips <VPN_IP>/32 endpoint <EXTERNAL_IP>:51820
EOF

chmod 600 /etc/wireguard/wg0.conf

echo ""
echo "=========================================="
echo "WireGuard installed successfully!"
echo "=========================================="
echo "Node: $NODE_NAME"
echo "VPN IP: $NODE_VPN_IP"
echo "Public Key: $PUBLIC_KEY"
echo ""
echo "Next Steps:"
echo "1. Add peers to /etc/wireguard/wg0.conf"
echo "2. Enable WireGuard: systemctl enable wg-quick@wg0"
echo "3. Start WireGuard: systemctl start wg-quick@wg0"
echo "4. Check status: wg show"
echo ""
echo "Example peer configuration:"
echo "[Peer]"
echo "PublicKey = <PEER_PUBLIC_KEY>"
echo "AllowedIPs = <PEER_VPN_IP>/32"
echo "Endpoint = <PEER_EXTERNAL_IP>:51820"
echo "PersistentKeepalive = 25"
echo "=========================================="
