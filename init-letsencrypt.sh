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

# Create dummy certificate
echo "### Creating dummy certificate for ${domains[0]} ... ###"
path="/etc/letsencrypt/live/${domains[0]}"
docker-compose -f "$compose_file" run --rm -u root --entrypoint " \
  sh -c 'mkdir -p $path && \
  openssl req -x509 -nodes -newkey rsa:$rsa_key_size -days 1 \
    -keyout \"$path/privkey.pem\" \
    -out \"$path/fullchain.pem\" \
    -subj \"/CN=localhost\"'" certbot

# Start services
echo "### Starting all services ... ###"
docker-compose -f "$compose_file" up --force-recreate -d

# --- DEBUGGING PAUSE ---
echo
echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
echo "    PAUSING FOR DEBUGGING. Services are up."
echo "    Please run 'docker-compose ps' and 'sudo ss -tlnp' in another terminal."
echo "    Press Enter to continue and request the real certificate..."
echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
read -p ""
# --- END DEBUGGING PAUSE ---

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