# Revo Backend

A secure NestJS backend application with robust environment and configuration management.

## Secure Environment and Configuration Management

This project implements a secure environment and configuration management system with the following features:

- Secret management using Docker secrets and HashiCorp Vault
- Environment-specific configurations
- Automatic credential rotation
- SSL/TLS configuration
- Security auditing

## Getting Started

### Prerequisites

- Node.js (v18+)
- Docker and Docker Compose
- PowerShell Core (for Windows)

### Setting Up

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd Revo-Backend
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Set up secrets:

   ```bash
   # On Windows
   powershell -ExecutionPolicy Bypass -File config/docker/security/rotate-secrets.ps1

   # On Linux/MacOS
   chmod +x config/docker/security/rotate-secrets.sh
   ./config/docker/security/rotate-secrets.sh
   ```

   Note: The secrets directory is gitignored. Template files are provided in `config/docker/secrets/` for reference.

4. Start the application:

   ```bash
   # Development
   docker-compose -f config/docker/docker-compose.yml up -d

   # Production
   NODE_ENV=prod docker-compose -f config/docker/docker-compose.yml up -d
   ```

### Security Features

- **Secret Management**:
  - Credentials are stored securely using Docker secrets
  - HashiCorp Vault integration for centralized secret management
  - Automatic secret rotation
  - No secrets committed to version control
- **Environment Config**: Different configs for development and production
- **Credential Rotation**: Automatic rotation of credentials
- **TLS/SSL**: Secure communication with SSL/TLS
- **Audit Logging**: Comprehensive audit logging

### Directory Structure

```
config/docker/
├── secrets/           # Docker secrets storage (gitignored)
├── env/              # Environment-specific configurations
│   ├── dev/         # Development environment
│   └── prod/        # Production environment
└── security/        # Security configurations and scripts
```

### Secret Management

The project uses a multi-layered approach to secret management:

1. **Local Development**:

   - Secrets are stored in `config/docker/secrets/` (gitignored)
   - Template files are provided for reference
   - Secrets are generated using secure random values

2. **Production**:
   - Secrets are managed through Docker secrets
   - HashiCorp Vault integration for centralized management
   - Automatic rotation of credentials
   - No secrets stored in version control

### Credential Rotation

To rotate credentials manually:

```bash
# On Windows
powershell -ExecutionPolicy Bypass -File config/docker/security/rotate-secrets.ps1

# On Linux/MacOS
./config/docker/security/rotate-secrets.sh
```

### SSL/TLS Configuration

SSL certificates are automatically generated during setup and can be rotated as needed. Production environments should use proper certificates from a certificate authority.

## Development

For local development without Docker:

1. Create a local .env file:

   ```bash
   cp .env.example .env
   ```

2. Start the development server:
   ```bash
   npm run start:dev
   ```

## Security Best Practices

1. **Secret Management**:

   - Never commit secrets to version control
   - Use Docker secrets for runtime secrets
   - Implement secret rotation
   - Use Vault for centralized secret management

2. **Access Control**:

   - Implement least privilege principle
   - Use strong authentication
   - Enable rate limiting
   - Configure proper CORS policies

3. **SSL/TLS**:

   - Use strong cipher suites
   - Enable certificate rotation
   - Implement certificate validation
   - Use secure protocols

4. **Container Security**:

   - Run containers with minimal privileges
   - Use read-only root filesystem
   - Implement security options
   - Regular security updates

5. **Monitoring and Auditing**:
   - Enable comprehensive logging
   - Implement audit trails
   - Monitor security events
   - Regular security assessments

## Documentation

For more detailed information, see:

- [Security Configuration](config/docker/README.md)
- [API Documentation](http://localhost:3000/docs) (available when server is running)
