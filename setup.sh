#!/bin/bash

# =====================================================================================
#                               All-in-One Setup Script
# =====================================================================================
# This script performs a full, one-time setup for the Nestling application, including:
# 1. Configuring the system firewall (iptables) correctly for Docker.
# 2. Persisting the firewall rules.
# 3. Running the Let's Encrypt SSL certificate generation process.
# =====================================================================================

set -e # Exit immediately if a command exits with a non-zero status.

# --- PART 1: CONFIGURE FIREWALL (IPTABLES) ---

echo "### Configuring system firewall (iptables)... ###"

# Flush all existing rules to start from a clean slate
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X
iptables -t mangle -F
iptables -t mangle -X

# Set default policies to ACCEPT. Docker manages its own rules.
# The primary security layer will be the Oracle Cloud Security List.
iptables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT

# Install persistence tool if not present
if ! dpkg -s iptables-persistent >/dev/null 2>&1; then
  echo "iptables-persistent not found. Installing..."
  apt-get update
  # Pre-seed answers for the interactive prompts
  echo "iptables-persistent iptables-persistent/autosave_v4 boolean true" | debconf-set-selections
  echo "iptables-persistent iptables-persistent/autosave_v6 boolean true" | debconf-set-selections
  apt-get install -y iptables-persistent
fi

# Save the new, open iptables configuration
netfilter-persistent save

echo "### Firewall configured to an open state. Docker will manage its own rules. ###"


# --- PART 2: RESTART DOCKER & RUN DEPLOYMENT ---

echo
echo "### Restarting Docker service to apply network settings... ###"
systemctl restart docker
sleep 5 # Give docker some time to settle

# Navigate to script's directory to find docker-compose.yml
cd "$(dirname "$0")"

# Now, run the logic from the old init-letsencrypt.sh script

# Configuration
domains=(platform.smartview.top)
email="locookies12@gmail.com"
staging=0
rsa_key_size=4096
compose_file="docker-compose-server.yml"

# Clean up previous Docker environment
echo
echo "### Cleaning up previous Docker environment... ###"
docker-compose -f "$compose_file" down -v

# Create dummy certificate
echo
echo "### Creating dummy certificate for ${domains[0]} ... ###"
path="/etc/letsencrypt/live/${domains[0]}"
docker-compose -f "$compose_file" run --rm -u root --entrypoint " \
  sh -c 'mkdir -p $path && \
  openssl req -x509 -nodes -newkey rsa:$rsa_key_size -days 1 \
    -keyout \"$path/privkey.pem\" \
    -out \"$path/fullchain.pem\" \
    -subj \"/CN=localhost\"'" certbot

# Start services
echo
echo "### Starting all services ... ###"
docker-compose -f "$compose_file" up --force-recreate -d

# Request real certificate
echo
echo "### Deleting dummy certificate and requesting real certificate for ${domains[0]} ... ###"
staging_arg=""
if [ "$staging" != "0" ]; then staging_arg="--staging"; fi

docker-compose -f "$compose_file" run --rm -u root --entrypoint "rm -Rf /etc/letsencrypt/live/${domains[0]} /etc/letsencrypt/archive/${domains[0]} /etc/letsencrypt/renewal/${domains[0]}.conf" certbot

docker-compose -f "$compose_file" run --rm --entrypoint " \
  certbot certonly --webroot -w /var/www/certbot \
    $staging_arg \
    -d ${domains[0]} \
    --email $email \
    --rsa-key-size $rsa_key_size \
    --agree-tos \
    --force-renewal" certbot

# Reload Nginx
echo
echo "### Reloading Nginx to apply the new certificate... ###"
docker-compose -f "$compose_file" exec web nginx -s reload

echo
echo "================================================================="
echo "    SETUP COMPLETE! SSL certificate should be configured."
echo "================================================================="
echo 
