#!/bin/bash

# =====================================================================================
#                       SSL Certificate Initialization Script
# =====================================================================================
# This script automates the process of obtaining an initial SSL certificate from
# Let's Encrypt using Certbot in a Docker environment. It handles the initial
# "chicken-and-egg" problem where Nginx needs a certificate to start, but Certbot
# needs Nginx to be running to obtain a certificate.
#
# You only need to run this script ONCE for the initial setup.
# =====================================================================================

# --- Configuration ---
# Set your domain and email here.
domains=(platform.smartview.top)
email="locookies12@gmail.com"

# Set to 1 to use Let's Encrypt's staging server for testing, 0 for production.
staging=0

# --- Advanced Configuration ---
rsa_key_size=4096
compose_file="docker-compose-server.yml"

# --- Script Logic ---

# Helper function to check if a command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Check for required commands
if ! command_exists docker-compose; then echo "Error: docker-compose is not installed." >&2; exit 1; fi
if ! command_exists docker; then echo "Error: docker is not installed." >&2; exit 1; fi

# Clean up previous attempts to ensure a fresh start
echo "### Cleaning up previous Docker environment... ###"
docker-compose -f "$compose_file" down -v

# Check if real certificates already exist
if docker-compose -f "$compose_file" run --rm --entrypoint "[ -d /etc/letsencrypt/live/${domains[0]} ]" certbot;
then
  echo
  echo "### Found existing certificates for ${domains[0]}. Skipping creation. ###"
  echo "### To force renewal, run: docker-compose -f $compose_file run --rm --entrypoint \"certbot renew --force-renewal\" certbot ###"
  echo
  exit
fi

# Create dummy certificate so Nginx can start
echo "### Creating dummy certificate for ${domains[0]} ... ###"
path="/etc/letsencrypt/live/${domains[0]}"

# IMPORTANT FIX: Run the command as root user (-u root) to ensure permissions
docker-compose -f "$compose_file" run --rm -u root --entrypoint " \
  sh -c 'mkdir -p $path && \
  openssl req -x509 -nodes -newkey rsa:$rsa_key_size -days 1 \
    -keyout \"$path/privkey.pem\" \
    -out \"$path/fullchain.pem\" \
    -subj \"/CN=localhost\"'" certbot

if [ $? -ne 0 ]; then echo "Error: Dummy certificate creation failed." >&2; exit 1; fi

# Start all services (Nginx will start using the dummy cert)
echo
echo "### Starting all services ... ###"
docker-compose -f "$compose_file" up --force-recreate -d

# Request the real certificate from Let's Encrypt
echo
echo "### Deleting dummy certificate and requesting real certificate for ${domains[0]} ... ###"

# Select appropriate staging flag
staging_arg=""
if [ "$staging" != "0" ]; then staging_arg="--staging"; fi

# Command to remove the dummy certificate files
docker-compose -f "$compose_file" run --rm -u root --entrypoint " \
  rm -Rf /etc/letsencrypt/live/${domains[0]} && \
  rm -Rf /etc/letsencrypt/archive/${domains[0]} && \
  rm -Rf /etc/letsencrypt/renewal/${domains[0]}.conf" certbot

# Command to request the certificate
docker-compose -f "$compose_file" run --rm --entrypoint " \
  certbot certonly --webroot -w /var/www/certbot \
    $staging_arg \
    -d ${domains[0]} \
    --email $email \
    --rsa-key-size $rsa_key_size \
    --agree-tos \
    --force-renewal" certbot

if [ $? -ne 0 ]; then
    echo "Error: Let's Encrypt certificate request failed." >&2
    exit 1
fi

# Reload Nginx to apply the new certificate
echo
echo "### Reloading Nginx to apply the new certificate... ###"
docker-compose -f "$compose_file" exec web nginx -s reload

echo
echo "================================================================="
echo "    SSL certificate has been successfully configured!"
echo "================================================================="
echo
