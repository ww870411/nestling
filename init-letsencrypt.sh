#!/bin/bash
set -e

# Configuration
domains=(platform.smartview.top)
email="locookies12@gmail.com"
staging=0
rsa_key_size=4096
compose_file="docker-compose-server.yml"

# Clean up
echo "### Cleaning up previous Docker environment... ###"
docker-compose -f "$compose_file" down -v

# Ensure TLS parameter files exist before Nginx starts (options-ssl-nginx.conf, ssl-dhparams.pem)
echo "### Ensuring TLS parameter files exist (options-ssl-nginx.conf, ssl-dhparams.pem) ... ###"
docker-compose -f "$compose_file" run --rm --entrypoint "sh -c '
  set -e;
  mkdir -p /etc/letsencrypt;
  if [ ! -f /etc/letsencrypt/options-ssl-nginx.conf ]; then
    if command -v wget >/dev/null 2>&1; then
      wget -q -O /etc/letsencrypt/options-ssl-nginx.conf https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/options-ssl-nginx.conf || true;
    elif command -v curl >/dev/null 2>&1; then
      curl -fsSL -o /etc/letsencrypt/options-ssl-nginx.conf https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/options-ssl-nginx.conf || true;
    fi;
    # Fallback: minimal secure defaults if download failed
    if [ ! -s /etc/letsencrypt/options-ssl-nginx.conf ]; then
      cat > /etc/letsencrypt/options-ssl-nginx.conf <<EOF
ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers off;
add_header Strict-Transport-Security "max-age=63072000" always;
EOF
    fi;
  fi;
  if [ ! -f /etc/letsencrypt/ssl-dhparams.pem ]; then
    if command -v wget >/dev/null 2>&1; then
      wget -q -O /etc/letsencrypt/ssl-dhparams.pem https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem || true;
    elif command -v curl >/dev/null 2>&1; then
      curl -fsSL -o /etc/letsencrypt/ssl-dhparams.pem https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem || true;
    fi;
    # Fallback: generate DH params (may take some time)
    if [ ! -s /etc/letsencrypt/ssl-dhparams.pem ]; then
      openssl dhparam -out /etc/letsencrypt/ssl-dhparams.pem 2048;
    fi;
  fi;
'" certbot

# Create dummy certificate (so Nginx can start with SSL paths present)
echo "### Creating dummy certificate for ${domains[0]} ... ###"
live_path="/etc/letsencrypt/live/${domains[0]}"
docker-compose -f "$compose_file" run --rm --entrypoint "sh -c 'set -e; \
  mkdir -p \"$live_path\" && \
  openssl req -x509 -nodes -newkey rsa:$rsa_key_size -days 1 \
    -keyout \"$live_path/privkey.pem\" \
    -out \"$live_path/fullchain.pem\" \
    -subj \"/CN=localhost\"'" certbot

# Start services
echo "### Starting all services ... ###"
docker-compose -f "$compose_file" up --force-recreate -d

# Request real certificate
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
echo "### Reloading Nginx to apply the new certificate... ###"
docker-compose -f "$compose_file" exec web nginx -s reload

echo "### SETUP COMPLETE! ###"
