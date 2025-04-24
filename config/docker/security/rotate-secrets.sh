#!/bin/bash

# Exit on error
set -e

# Configuration
# Make path relative to script location
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SECRETS_DIR="$SCRIPT_DIR/../../secrets"
VAULT_ADDR="https://localhost:8200"
VAULT_TOKEN="${VAULT_TOKEN}"

# Function to generate random string
generate_random_string() {
    local length=$1
    openssl rand -base64 $((length * 3/4)) | tr -d '/+=' | head -c $length
}

# Function to save secret without newline
save_secret() {
    local file="$1"
    local content="$2"
    echo -n "$content" > "$file"
}
# Function to rotate database password
    rotate_db_password() {
   # Use a subshell to avoid leaking password in error traces
     local new_password
     new_password=$(set -o pipefail; generate_random_string 32)
     
     # Set trap to clear password variable on exit
     trap 'new_password="REDACTED"; unset new_password' RETURN
    
    save_secret "$SECRETS_DIR/db_password.txt" "$new_password"
    
    # Update Vault if available
    if [ -n "$VAULT_TOKEN" ] && [ -n "$VAULT_ADDR" ]; then
       # Send request to Vault and check for successful response
        response=$(curl -s -w "\n%{http_code}" -X POST \
            -H "X-Vault-Token: $VAULT_TOKEN" \
            -H "Content-Type: application/json" \
            -d "{\"value\": \"$new_password\"}" \
            "$VAULT_ADDR/v1/secret/database/password")
        
        status_code=$(echo "$response" | tail -n1)
        response_body=$(echo "$response" | sed '$d')
        
        if [ "$status_code" -ne 200 ] && [ "$status_code" -ne 204 ]; then
            echo "Error updating Vault with database password: $response_body"
            return 1
        fi
    fi 
}

# Function to rotate JWT secret
rotate_jwt_secret() {
     local new_secret
     new_secret=$(generate_random_string 64)
    save_secret "$SECRETS_DIR/jwt_secret.txt" "$new_secret"
    
    # Update Vault if available
    if [ -n "$VAULT_TOKEN" ] && [ -n "$VAULT_ADDR" ]; then
        # Send request to Vault and check for successful response
         response=$(curl -s -w "\n%{http_code}" -X POST \
             -H "X-Vault-Token: $VAULT_TOKEN" \
             -H "Content-Type: application/json" \
             -d "{\"value\": \"$new_secret\"}" \
             "$VAULT_ADDR/v1/secret/jwt/secret")
         
         status_code=$(echo "$response" | tail -n1)
         response_body=$(echo "$response" | sed '$d')
        
         if [ "$status_code" -ne 200 ] && [ "$status_code" -ne 204 ]; then
             echo "Error updating Vault with JWT secret: $response_body"
             return 1
         fi
    fi
}

# Function to rotate SSL certificates
rotate_ssl_certificates() {
     # Check if openssl is available
     if ! command -v openssl >/dev/null 2>&1; then
         echo "Error: OpenSSL is not installed or not in PATH. Cannot generate SSL certificates."
         return 1
     fi

    # Generate new private key
    openssl genrsa -out "$SECRETS_DIR/ssl_key.pem" 4096
    chmod 600 "$SECRETS_DIR/ssl_key.pem"
    
    # Generate new certificate
    openssl req -x509 -new -nodes \
        -key "$SECRETS_DIR/ssl_key.pem" \
        -sha256 -days 365 \
        -out "$SECRETS_DIR/ssl_cert.pem" \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
    
    # Update Vault if available
    if [ -n "$VAULT_TOKEN" ] && [ -n "$VAULT_ADDR" ]; then
    # Create temporary file for JSON payload
       tmp_json=$(mktemp)
        key_b64=$(base64 -w 0 < "$SECRETS_DIR/ssl_key.pem")
        cert_b64=$(base64 -w 0 < "$SECRETS_DIR/ssl_cert.pem")
        
        cat > "$tmp_json" << EOF
{
    "key": "$key_b64",
    "cert": "$cert_b64"
}
EOF
        
        # Send request to Vault and check for successful response
        response=$(curl -s -w "\n%{http_code}" -X POST \
            -H "X-Vault-Token: $VAULT_TOKEN" \
            -H "Content-Type: application/json" \
            -d @"$tmp_json" \
            "$VAULT_ADDR/v1/secret/ssl/cert")
        
        status_code=$(echo "$response" | tail -n1)
        response_body=$(echo "$response" | sed '$d')
        
        if [ "$status_code" -ne 200 ] && [ "$status_code" -ne 204 ]; then
            echo "Error updating Vault with SSL certificate: $response_body"
            return 1
        fi
    fi
           
        # Clean up temporary file
        rm "$tmp_json"
}
  # Function to rotate Vault token
   rotate_vault_token() {
     local new_token
     new_token=$(generate_random_string 64)
     save_secret "$SECRETS_DIR/vault_token.txt" "$new_token"
     
     # Update environment variables
    ENV_DIR="$(dirname "$(dirname "$(dirname "$SCRIPT_DIR")")")/env"
     if [ -d "$ENV_DIR" ]; then
         find "$ENV_DIR" -type f -name ".env" -exec sed -i "s/VAULT_TOKEN=.*/VAULT_TOKEN=$new_token/" {} \;
     fi
}

# Main rotation function
rotate_secrets() {
    echo "Starting secret rotation..."
    
    # Create secrets directory if it doesn't exist
    mkdir -p "$SECRETS_DIR"
    chmod 700 "$SECRETS_DIR"
   
    # Verify directory ownership is correct
    current_user=$(id -u -n)
    current_group=$(id -g -n)
    directory_owner=$(stat -c '%U' "$SECRETS_DIR")
    directory_group=$(stat -c '%G' "$SECRETS_DIR")
    
    if [ "$directory_owner" != "$current_user" ] || [ "$directory_group" != "$current_group" ]; then
        echo "Warning: Secrets directory has incorrect ownership. Expected $current_user:$current_group, got $directory_owner:$directory_group"
        if [ "$(id -u)" -eq 0 ]; then
            echo "Fixing ownership..."
            chown "$current_user:$current_group" "$SECRETS_DIR"
        else
            echo "Cannot fix ownership without root privileges. Please run: sudo chown $current_user:$current_group $SECRETS_DIR"
        fi
    fi

    # Backup existing secrets
     BACKUP_DIR=$(mktemp -d)
     if [ -d "$SECRETS_DIR" ]; then
         cp -r "$SECRETS_DIR"/* "$BACKUP_DIR"/ 2>/dev/null || true
         echo "Created backup of existing secrets"
     fi
     
     # Set trap to restore from backup on failure
     trap 'echo "Error occurred, restoring from backup..."; rm -rf "$SECRETS_DIR"; mkdir -p "$SECRETS_DIR"; cp -r "$BACKUP_DIR"/* "$SECRETS_DIR"/ 2>/dev/null || true; rm -rf "$BACKUP_DIR"; echo "Restored from backup"; exit 1' ERR
     

    # Rotate all secrets
    rotate_db_password
    rotate_jwt_secret
    rotate_ssl_certificates
    rotate_vault_token


    # Clean up backup on success
    rm -rf "$BACKUP_DIR"
    echo "Secret rotation completed successfully!"

    # Remove trap
    trap - ERR
}

# Execute rotation
rotate_secrets 