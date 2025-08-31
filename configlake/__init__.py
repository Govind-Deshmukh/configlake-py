"""
Config Lake - Python Client
Simple functions to fetch and decrypt configurations and secrets
"""

import os
import base64
import requests
from cryptography.fernet import Fernet

__version__ = "1.0.0"

def _decrypt_secret(encrypted_value, environment_key):
    """Decrypt a secret using the environment key"""
    try:
        fernet = Fernet(environment_key.encode())
        decoded_value = base64.b64decode(encrypted_value.encode())
        decrypted_value = fernet.decrypt(decoded_value)
        return decrypted_value.decode('utf-8')
    except Exception as e:
        raise Exception(f"Decryption failed: {str(e)}")

def _make_request(api_url, token, endpoint):
    """Make API request"""
    url = f"{api_url.rstrip('/')}{endpoint}"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers, timeout=30)
    
    if response.status_code == 401:
        raise Exception("Authentication failed - invalid API token")
    elif response.status_code == 403:
        raise Exception("Access forbidden - token not valid for this project")
    elif response.status_code == 404:
        raise Exception("Resource not found - check project ID and environment name")
    elif response.status_code != 200:
        raise Exception(f"API request failed: {response.status_code} {response.text}")
    
    return response.json()

def getConfig(api_url, token, project_id, environment):
    """Get plain-text configurations"""
    endpoint = f"/api/config/{project_id}/{environment}"
    data = _make_request(api_url, token, endpoint)
    return data.get("configs", {})

def getSecrets(api_url, token, project_id, environment):
    """Get decrypted secrets"""
    endpoint = f"/api/secrets/{project_id}/{environment}"
    data = _make_request(api_url, token, endpoint)
    
    environment_key = data.get("environment_key")
    encrypted_secrets = data.get("secrets", {})
    
    if not environment_key:
        raise Exception("Environment key not found in API response")
    
    # Decrypt all secrets
    decrypted_secrets = {}
    for key, encrypted_value in encrypted_secrets.items():
        decrypted_secrets[key] = _decrypt_secret(encrypted_value, environment_key)
    
    return decrypted_secrets

def getAllDetails(api_url, token, project_id, environment):
    """Get both configurations and decrypted secrets"""
    endpoint = f"/api/all/{project_id}/{environment}"
    data = _make_request(api_url, token, endpoint)
    
    configs = data.get("configs", {})
    environment_key = data.get("environment_key")
    encrypted_secrets = data.get("secrets", {})
    
    if not environment_key:
        raise Exception("Environment key not found in API response")
    
    # Decrypt all secrets
    decrypted_secrets = {}
    for key, encrypted_value in encrypted_secrets.items():
        decrypted_secrets[key] = _decrypt_secret(encrypted_value, environment_key)
    
    return {
        "configs": configs,
        "secrets": decrypted_secrets,
        "project_id": data.get("project_id"),
        "environment": data.get("environment")
    }