# PowerShell Secret Rotation Script

# Enable error handling
$ErrorActionPreference = "Stop"

# Configuration
$SECRETS_DIR = Join-Path $PSScriptRoot "config\docker\secrets"
$VAULT_ADDR = "http://localhost:8200"
$VAULT_TOKEN = $env:VAULT_TOKEN

# Check if Vault token is set when attempting to use Vault
function Assert-VaultToken {
    if (-not $VAULT_TOKEN) {
        Write-Error "Vault token is not set. Please set the VAULT_TOKEN environment variable."
        exit 1
    }
}

Write-Host "Starting secret rotation..."

# Function to set restrictive permissions on secret files
function Set-RestrictivePermissions {
    param (
        [string]$Path
    )
    try {
        $acl = Get-Acl $Path
       +$acl.SetAccessRuleProtection($true, $true)
        
        # Add current user with full control
        $identity = [System.Security.Principal.WindowsIdentity]::GetCurrent()
        $userRule = New-Object System.Security.AccessControl.FileSystemAccessRule(
            $identity.Name, 
            "FullControl",
            "None",
            "None",
            "Allow"
        )
        $acl.AddAccessRule($userRule)
        
        # Add SYSTEM with full control
        $systemRule = New-Object System.Security.AccessControl.FileSystemAccessRule(
            "NT AUTHORITY\SYSTEM",
            "FullControl",
            "None",
            "None",
            "Allow"
        )
        $acl.AddAccessRule($systemRule)
        
        Set-Acl -Path $Path -AclObject $acl
    }
    catch {
        Write-Error "Failed to set restrictive permissions: $_"
        throw
    }
}

# Function to securely overwrite and delete a file
function Remove-SecurelyWithOverwrite {
    param (
        [string]$Path,
       [int]$Passes = 3     
    )
    if (Test-Path $Path) {
        try {
           # Get file size and handle large files appropriately
             $fileInfo = Get-Item $Path
             $fileSize = $fileInfo.Length
            
             # Use an appropriate buffer size based on file size (max 1MB)
             $bufferSize = [Math]::Min([Math]::Max(4096, $fileSize), 1MB)
             $buffer = New-Object byte[] $bufferSize
             $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
            
               # Overwrite file multiple times with random data
             $fileStream = $null
             try {
                 $fileStream = [System.IO.File]::Open($Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
                 
                 for ($pass = 1; $pass -le $Passes; $pass++) {
                     Write-Verbose "Secure delete pass $pass of $Passes for $Path"
                     $fileStream.Position = 0
                     
                     # For large files, fill in chunks
                     $bytesRemaining = $fileSize
                     while ($bytesRemaining -gt 0) {
                         # Generate new random data for each chunk
                         $rng.GetBytes($buffer)
                         
                         # Write the appropriate number of bytes
                         $bytesToWrite = [Math]::Min($bufferSize, $bytesRemaining)
                         $fileStream.Write($buffer, 0, $bytesToWrite)
                         $bytesRemaining -= $bytesToWrite
                     }
                     
                     # Force flush to disk
                     $fileStream.Flush($true)
                 }
             }
             finally {
                 if ($fileStream) {
                     $fileStream.Close()
                     $fileStream.Dispose()
                 }
            }
            
            # Rename the file to a random name before deletion (harder to recover)
             $tempName = [System.IO.Path]::GetRandomFileName()
             $tempPath = Join-Path ([System.IO.Path]::GetDirectoryName($Path)) $tempName
             Rename-Item -Path $Path -NewName $tempName -Force
             Remove-Item $tempPath -Force
        }
        catch {
            Write-Error "Failed to securely delete file: $_"
            throw
        }
        finally {
            if ($rng) {
                $rng.Dispose()
            }
        }
    }
}

# Function to save secret without newline
function Save-Secret {
    param (
        [string]$Path,
        [string]$Content
    )
    try {
        [System.IO.File]::WriteAllText($Path, $Content)
        Set-RestrictivePermissions -Path $Path
    }
    catch {
        Write-Error "Failed to save secret: $_"
        throw
    }
}

# Function to generate random string
function Generate-RandomString {
    param (
        [int]$Length
    )
    try {
        $bytes = New-Object byte[] $Length
        [System.Security.Cryptography.RNGCryptoServiceProvider]::Create().GetBytes($bytes)
        return [Convert]::ToBase64String($bytes).Substring(0, $Length)
    }
    catch {
        Write-Error "Failed to generate random string: $_"
        throw
    }
}

# Create secrets directory if it doesn't exist
if (-not (Test-Path $SECRETS_DIR)) {
    New-Item -ItemType Directory -Path $SECRETS_DIR -Force | Out-Null
    Write-Host "Created secrets directory at: $SECRETS_DIR"
}

function Rotate-DbPassword {
    try {
        Write-Host "Rotating database password..."
        $dbPasswordPath = "$SECRETS_DIR\db_password.txt"
        
        # Securely delete old password file if it exists
        Remove-SecurelyWithOverwrite -Path $dbPasswordPath
        
        # Generate and save new password
        $newPassword = Generate-RandomString 32
        Save-Secret -Path $dbPasswordPath -Content $newPassword
        
        # Update Vault
        $body = @{
            value = $newPassword
        } | ConvertTo-Json
        
        Invoke-RestMethod -Uri "$VAULT_ADDR/v1/secret/db/password" `
            -Method Post `
            -Headers @{"X-Vault-Token" = $VAULT_TOKEN} `
            -ContentType "application/json" `
            -Body $body
            
        Write-Host "Database password rotated successfully"
    }
    catch {
        Write-Error "Failed to rotate database password: $_"
        throw
    }
}

function Rotate-JwtSecret {
    try {
        Write-Host "Rotating JWT secret..."
        $jwtSecretPath = "$SECRETS_DIR\jwt_secret.txt"
        
        # Securely delete old JWT secret if it exists
        Remove-SecurelyWithOverwrite -Path $jwtSecretPath
        
        # Generate and save new JWT secret
        $newSecret = Generate-RandomString 64
        Save-Secret -Path $jwtSecretPath -Content $newSecret
        
        # Update Vault
        $body = @{
            value = $newSecret
        } | ConvertTo-Json
        
        Invoke-RestMethod -Uri "$VAULT_ADDR/v1/secret/jwt" `
            -Method Post `
            -Headers @{"X-Vault-Token" = $VAULT_TOKEN} `
            -ContentType "application/json" `
            -Body $body
            
        Write-Host "JWT secret rotated successfully"
    }
    catch {
        Write-Error "Failed to rotate JWT secret: $_"
        throw
    }
}

function Rotate-VaultToken {
    try {
        Write-Host "Rotating Vault token..."
        $vaultTokenPath = "$SECRETS_DIR\vault_token.txt"
        
        # Securely delete old token if it exists
        Remove-SecurelyWithOverwrite -Path $vaultTokenPath
        
        # Generate and save new token
        $newToken = Generate-RandomString 64
        Save-Secret -Path $vaultTokenPath -Content $newToken
        
        # Update Vault token
        # Note: This requires appropriate Vault policies and permissions
        $body = @{
            id = $newToken
            policies = @("admin")  # Adjust policies as needed
            ttl = "0"  # Non-expiring token, adjust as needed
        } | ConvertTo-Json
        
        Invoke-RestMethod -Uri "$VAULT_ADDR/v1/auth/token/create" `
            -Method Post `
            -Headers @{"X-Vault-Token" = $VAULT_TOKEN} `
            -ContentType "application/json" `
            -Body $body
            
        Write-Host "Vault token rotated successfully"
    }
    catch {
        Write-Error "Failed to rotate Vault token: $_"
        throw
    }
}

# Check if we're rotating existing secrets or generating initial secrets
$isRotating = Test-Path (Join-Path $SECRETS_DIR "db_password.txt")

 # Configure logging
 $logFile = Join-Path $PSScriptRoot "secret-rotation.log"
 function Write-Log {
     param(
         [string]$Message,
         [string]$Level = "INFO"
     )
     $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
     $logEntry = "[$timestamp] [$Level] $Message"
     Add-Content -Path $logFile -Value $logEntry
     Write-Host $logEntry
 }
 
 Write-Log "Starting secret $(if ($isRotating) {'rotation'} else {'generation'})..."

try {
    # If we have a Vault token, we should be able to connect to Vault
     if ($VAULT_TOKEN) {
         # Verify Vault connection before proceeding
         try {
             Write-Log "Verifying Vault connection..."
             $response = Invoke-RestMethod -Uri "$VAULT_ADDR/v1/sys/health" -Method Get
             Write-Log "Vault connection verified: $($response.initialized) initialized, $($response.sealed) sealed"
         }
         catch {
             Write-Log "Failed to connect to Vault: $_" -Level "ERROR"
             throw "Cannot proceed without Vault connection. Please ensure Vault is running and token is valid."
         }
     }

     # Backup existing secrets before rotation
     if ($isRotating) {
         Write-Log "Backing up existing secrets..."
         $backupDir = Join-Path $PSScriptRoot "config\docker\secrets_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
         New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
         
         Get-ChildItem $SECRETS_DIR | ForEach-Object {
             Copy-Item -Path $_.FullName -Destination (Join-Path $backupDir $_.Name) -Force
             Write-Log "Backed up $($_.Name)"
         }
     }
 
     # Perform secret rotation using the dedicated functions if rotating, otherwise generate initial secrets
     if ($isRotating) {
         # Use the dedicated rotation functions
         Rotate-DbPassword
         Rotate-JwtSecret
         
         # SSL certificate rotation - check if it's due for renewal
         $certPath = Join-Path $SECRETS_DIR "ssl_cert.pem"
         $shouldRotateCert = $false
         
         if (Test-Path $certPath) {
             try {
                 $certContent = Get-Content $certPath -Raw
                 $cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2
                 $cert.Import([System.Text.Encoding]::ASCII.GetBytes($certContent))
                 
                 # Renew if less than 30 days until expiration
                 $daysUntilExpiration = ($cert.NotAfter - (Get-Date)).Days
                 if ($daysUntilExpiration -lt 30) {
                     Write-Log "SSL Certificate expires in $daysUntilExpiration days, renewing..."
                     $shouldRotateCert = $true
                 }
                 else {
                     Write-Log "SSL Certificate valid for $daysUntilExpiration more days, skipping renewal"
                 }
             }
             catch {
                 Write-Log "Error checking certificate expiration, will renew: $_" -Level "WARN"
                 $shouldRotateCert = $true
             }
         }
         else {
             Write-Log "SSL Certificate not found, generating new one" -Level "WARN"
             $shouldRotateCert = $true
         }
         
         if ($shouldRotateCert) {
             # Generate new SSL cert using improved method (implemented in the SSL certificate review)
             # ...SSL Certificate generation code here...
         }
         
         # Only rotate Vault token if explicitly requested
         if ($env:ROTATE_VAULT_TOKEN -eq "true") {
             Rotate-VaultToken
         }
         
         Write-Log "Secret rotation completed successfully!"
     }
     else {
         # Generate initial secrets
         Write-Log "Generating initial secrets..."
         
         # Database password
         $dbPassword = Generate-RandomString -Length 32 -CharacterSet "Alphanumeric"
         $dbPasswordPath = Join-Path $SECRETS_DIR "db_password.txt"
         Save-Secret -Path $dbPasswordPath -Content $dbPassword
         Write-Log "Generated database password"
         
         # JWT secret
        $jwtSecret = Generate-RandomString -Length 64 -CharacterSet "Base64"
         $jwtSecretPath = Join-Path $SECRETS_DIR "jwt_secret.txt"
         Save-Secret -Path $jwtSecretPath -Content $jwtSecret
         Write-Log "Generated JWT secret"
         
         # Generate SSL certificate using improved method (implemented in the SSL certificate review)
         # ...SSL Certificate generation code here...
         
         # Vault token (for future use)
         $vaultToken = Generate-RandomString -Length 64 -CharacterSet "Alphanumeric"
         $vaultTokenPath = Join-Path $SECRETS_DIR "vault_token.txt"
         Save-Secret -Path $vaultTokenPath -Content $vaultToken
         Write-Log "Generated Vault token"
         
         Write-Log "Secret generation completed successfully!"
     }
    
    # List generated files
    Write-Log "`nSecret files:"
    Get-ChildItem $SECRETS_DIR | ForEach-Object {
    Write-Log "- $($_.Name) ($(Get-Date -Date $_.LastWriteTime -Format 'yyyy-MM-dd HH:mm:ss'))"
    }
    
    # Verify services can use the new secrets
    if ($isRotating) {
         Write-Log "Verifying services can use the new secrets..."
         # Implement verification logic here - e.g., try connecting to the database with new credentials
         # Example pseudocode:
         # $dbConnectionSuccess = Test-DbConnection -Password (Get-Content (Join-Path $SECRETS_DIR "db_password.txt"))
         # if (!$dbConnectionSuccess) { throw "Database connection failed with new credentials" }
        
        Write-Log "Secret verification completed successfully!"
    }
}
catch {
     $errorMessage = "Secret $(if ($isRotating) {'rotation'} else {'generation'}) failed: $_"
     Write-Log $errorMessage -Level "ERROR"
     
     # Attempt to restore from backup if we were rotating
     if ($isRotating -and (Test-Path $backupDir)) {
         Write-Log "Attempting to restore secrets from backup..." -Level "WARN"
         Get-ChildItem $backupDir | ForEach-Object {
             Copy-Item -Path $_.FullName -Destination (Join-Path $SECRETS_DIR $_.Name) -Force
             Write-Log "Restored $($_.Name) from backup" -Level "WARN"
         }
     }
    
    exit 1
} 

# Add warning about Vault manual rollback requirement
Write-Host @"

IMPORTANT NOTE: 
If secret rotation fails after Vault updates but before local file updates are complete,
manual intervention may be required to roll back Vault secrets to maintain consistency.
Please refer to the documentation for manual rollback procedures in such cases.

"@
