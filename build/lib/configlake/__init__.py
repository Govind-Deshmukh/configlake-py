"""
Config Lake - Python Client
Simple Python client for Config Lake - fetch and decrypt configurations and secrets
"""

import base64
import requests
from cryptography.fernet import Fernet
from typing import Dict, Any

__version__ = "1.0.5"


class ConfigLakeError(Exception):
    """Custom exception for Config Lake operations"""
    pass


def _make_request(base_url: str, token: str, endpoint: str) -> Dict[str, Any]:
    """Make HTTP request to Config Lake API"""
    url = f"{base_url.rstrip('/')}{endpoint}"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers, timeout=30)
    
    if response.status_code == 401:
        raise ConfigLakeError("Authentication failed - invalid API token")
    elif response.status_code == 403:
        raise ConfigLakeError("Access forbidden - token not valid for this project")
    elif response.status_code == 404:
        raise ConfigLakeError("Resource not found - check project ID and environment name")
    elif response.status_code != 200:
        raise ConfigLakeError(f"API request failed: {response.status_code} {response.text}")
    
    return response.json()


def _decrypt_secret(encrypted_value: str, environment_key: str) -> str:
    """Decrypt a secret using the environment key"""
    try:
        fernet = Fernet(environment_key.encode())
        decoded_value = base64.b64decode(encrypted_value.encode())
        decrypted_value = fernet.decrypt(decoded_value)
        return decrypted_value.decode('utf-8')
    except Exception as e:
        raise ConfigLakeError(f"Decryption failed: {str(e)}")


def get_config(base_url: str, token: str, project_id: int, environment: str) -> Dict[str, str]:
    """Get plain-text configurations"""
    endpoint = f"/api/config/{project_id}/{environment}"
    data = _make_request(base_url, token, endpoint)
    return data.get("configs", {})


def get_secrets(base_url: str, token: str, project_id: int, environment: str) -> Dict[str, str]:
    """Get decrypted secrets"""
    endpoint = f"/api/secrets/{project_id}/{environment}"
    data = _make_request(base_url, token, endpoint)
    
    environment_key = data.get("environment_key")
    encrypted_secrets = data.get("secrets", {})
    
    if not environment_key:
        raise ConfigLakeError("Environment key not found in API response")
    
    # Decrypt all secrets
    decrypted_secrets = {}
    for key, encrypted_value in encrypted_secrets.items():
        decrypted_secrets[key] = _decrypt_secret(encrypted_value, environment_key)
    
    return decrypted_secrets


def get_all_details(base_url: str, token: str, project_id: int, environment: str) -> Dict[str, Any]:
    """Get both configurations and decrypted secrets"""
    endpoint = f"/api/all/{project_id}/{environment}"
    data = _make_request(base_url, token, endpoint)
    
    configs = data.get("configs", {})
    secrets = data.get("secrets", {})  # Already decrypted by server
    
    return {
        "configs": configs,
        "secrets": secrets,
        "project_id": data.get("project_id"),
        "environment": data.get("environment")
    }


# Backwards compatible function names
getConfig = get_config
getSecrets = get_secrets
getAllDetails = get_all_details


__all__ = ['get_config', 'get_secrets', 'get_all_details', 'getConfig', 'getSecrets', 'getAllDetails', 'ConfigLakeError']