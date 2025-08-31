# ConfigLake Python Client

Official Python client library for ConfigLake - the centralized configuration and secrets management platform.

## What is ConfigLake?

ConfigLake helps you manage environment variables, API keys, database connections, and other sensitive configuration data across different environments (dev, staging, prod) in one secure dashboard.

## Installation

```bash
pip install configlake
```

## Quick Start

### Basic Usage

```python
from configlake import getConfig, getSecrets, getAllDetails

# Setup connection details
API_URL = "http://localhost:5000"
TOKEN = "your-api-token"
PROJECT_ID = 1
ENVIRONMENT = "production"

# Get only configurations (non-sensitive data)
configs = getConfig(API_URL, TOKEN, PROJECT_ID, ENVIRONMENT)
database_url = configs["DATABASE_URL"]
api_endpoint = configs["API_ENDPOINT"]

# Get only secrets (automatically decrypted)
secrets = getSecrets(API_URL, TOKEN, PROJECT_ID, ENVIRONMENT)  
api_key = secrets["API_KEY"]
jwt_secret = secrets["JWT_SECRET"]

# Get everything together
data = getAllDetails(API_URL, TOKEN, PROJECT_ID, ENVIRONMENT)
print("Configs:", data["configs"])
print("Secrets:", data["secrets"])
```

### Environment-based Configuration

Organize your configuration by environment:

```python
import os
from configlake import getAllDetails

class ConfigManager:
    def __init__(self, api_url, token, project_id):
        self.api_url = api_url
        self.token = token
        self.project_id = project_id
    
    def load_config(self, environment="development"):
        """Load configuration and set environment variables"""
        data = getAllDetails(self.api_url, self.token, self.project_id, environment)
        
        # Set environment variables
        for key, value in data["configs"].items():
            os.environ[key] = value
            
        for key, value in data["secrets"].items():
            os.environ[key] = value
            
        return data

# Usage
config_manager = ConfigManager("http://localhost:5000", "your-token", 1)

# Load development config
dev_config = config_manager.load_config("development")

# Load production config  
prod_config = config_manager.load_config("production")
```

### Django Integration

```python
# settings.py
from configlake import getAllDetails
import os

# Load configuration from ConfigLake
config_data = getAllDetails(
    os.getenv("CONFIGLAKE_URL", "http://localhost:5000"),
    os.getenv("CONFIGLAKE_TOKEN"),
    int(os.getenv("CONFIGLAKE_PROJECT_ID")),
    os.getenv("ENVIRONMENT", "development")
)

configs = config_data["configs"]
secrets = config_data["secrets"]

# Use in Django settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': configs.get('DB_NAME'),
        'USER': secrets.get('DB_USER'),
        'PASSWORD': secrets.get('DB_PASSWORD'),
        'HOST': configs.get('DB_HOST'),
        'PORT': configs.get('DB_PORT'),
    }
}

SECRET_KEY = secrets["DJANGO_SECRET_KEY"]
DEBUG = configs.get("DEBUG", "False").lower() == "true"
```

### Flask Integration

```python
from flask import Flask
from configlake import getAllDetails
import os

app = Flask(__name__)

# Load configuration on startup
config = getAllDetails(
    os.getenv("CONFIGLAKE_URL"),
    os.getenv("CONFIGLAKE_TOKEN"), 
    int(os.getenv("CONFIGLAKE_PROJECT_ID")),
    os.getenv("FLASK_ENV", "development")
)

# Configure Flask
app.config["SECRET_KEY"] = config["secrets"]["FLASK_SECRET_KEY"]
app.config["DATABASE_URL"] = config["configs"]["DATABASE_URL"]

@app.route("/")
def hello():
    return f"Running in {config['environment']} environment"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(config["configs"].get("PORT", 5000)))
```

## Error Handling

The client provides clear error messages for common issues:

```python
from configlake import getConfig

try:
    configs = getConfig(API_URL, TOKEN, PROJECT_ID, ENVIRONMENT)
except Exception as e:
    error_message = str(e)
    
    if "Authentication failed" in error_message:
        print("Invalid API token")
    elif "Access forbidden" in error_message:
        print("Token does not have access to this project")  
    elif "Resource not found" in error_message:
        print("Project or environment does not exist")
    else:
        print(f"Unexpected error: {error_message}")
```

## API Reference

### `getConfig(api_url, token, project_id, environment)`
**Returns**: `dict`  
**Description**: Retrieves plain-text configurations only.

**Example**:
```python
configs = getConfig("http://localhost:5000", "token123", 1, "production")
# Returns: {"DATABASE_URL": "postgresql://...", "API_ENDPOINT": "https://..."}
```

### `getSecrets(api_url, token, project_id, environment)`  
**Returns**: `dict`  
**Description**: Retrieves and automatically decrypts secrets.

**Example**:
```python
secrets = getSecrets("http://localhost:5000", "token123", 1, "production")
# Returns: {"API_KEY": "secret-key-123", "JWT_SECRET": "jwt-secret-456"}
```

### `getAllDetails(api_url, token, project_id, environment)`
**Returns**: `dict`  
**Description**: Retrieves both configurations and secrets in a single call.

**Example**:
```python
data = getAllDetails("http://localhost:5000", "token123", 1, "production")
# Returns: {
#   "configs": {"DATABASE_URL": "postgresql://..."},
#   "secrets": {"API_KEY": "secret-key"},  
#   "project_id": 1,
#   "environment": "production"
# }
```

## Advanced Usage

### Caching Configuration

```python
import time
from configlake import getAllDetails

class CachedConfigManager:
    def __init__(self, api_url, token, project_id, cache_ttl=300):
        self.api_url = api_url
        self.token = token
        self.project_id = project_id
        self.cache_ttl = cache_ttl
        self._cache = {}
        self._cache_time = {}
    
    def get_config(self, environment):
        now = time.time()
        cache_key = environment
        
        # Check if cache is valid
        if (cache_key in self._cache and 
            now - self._cache_time.get(cache_key, 0) < self.cache_ttl):
            return self._cache[cache_key]
        
        # Fetch fresh data
        data = getAllDetails(self.api_url, self.token, self.project_id, environment)
        self._cache[cache_key] = data
        self._cache_time[cache_key] = now
        
        return data

# Usage with 5-minute cache
config_manager = CachedConfigManager("http://localhost:5000", "your-token", 1, cache_ttl=300)
config = config_manager.get_config("production")
```

### Type Hints

```python
from typing import Dict, Any
from configlake import getAllDetails

def load_app_config(environment: str) -> Dict[str, Any]:
    """Load application configuration with proper type hints"""
    return getAllDetails(
        "http://localhost:5000",
        "your-token", 
        1,
        environment
    )

# Usage
config: Dict[str, Any] = load_app_config("production")
database_url: str = config["configs"]["DATABASE_URL"]
api_key: str = config["secrets"]["API_KEY"]
```

## Requirements

- Python >= 3.7
- `requests >= 2.25.0`
- `cryptography >= 3.4.0`

## ConfigLake Setup

To use this client, you need a running ConfigLake instance:

1. **Docker (Easiest)**:
   ```bash
   docker run -d -p 5000:5000 configlake/configlake
   ```

2. **Manual Setup**:
   ```bash
   git clone https://github.com/Govind-Deshmukh/configlake
   cd configlake
   python app.py
   ```

3. **Create API Token**: Login to the ConfigLake dashboard and generate an API token for your project/environment.

## Security Notes

- Store your ConfigLake API token securely (use environment variables, not hardcode)
- Secrets are automatically encrypted in ConfigLake and decrypted by this client
- Use HTTPS in production for the ConfigLake API URL
- Consider IP whitelisting in ConfigLake for additional security

## Links

- **ConfigLake Repository**: https://github.com/Govind-Deshmukh/configlake  
- **Docker Image**: `docker pull configlake/configlake`
- **Node.js Client**: `npm install configlake`

## License

MIT License