#!/usr/bin/env nix-shell
#!nix-shell -i python -p python3 python3Packages.requests

import sys
import argparse
import os
import json
import requests
from pathlib import Path

DEFAULT_CONTINUE_CONFIG_LOCATION = '~/.continue/config.json'
VENICE_API_BASE = 'https://api.venice.ai/api/v1'

def get_api_key(args, config=None):
    """Get API key from command line args, environment, or existing config"""
    # Try command line argument first
    if args.api_key:
        return args.api_key
    
    # Try environment variable
    api_key = os.environ.get('VENICE_API_KEY')
    if api_key:
        return api_key
    
    # Try to extract from config if provided
    if config:
        # Look for Venice models in the config
        for model in config.get('models', []):
            if model.get('apiBase') and 'venice.ai' in model.get('apiBase', ''):
                if model.get('apiKey'):
                    return model.get('apiKey')
    
    return None

def get_continue_config_location(args):
    """Get the Continue config file location from args or environment"""
    # Try command line argument first
    if args.config_path:
        return args.config_path
        
    # Try environment variable
    config_path = os.environ.get('CONTINUE_CONFIG_PATH')
    if config_path:
        return config_path
        
    # Use default location
    return DEFAULT_CONTINUE_CONFIG_LOCATION

def get_venice_models(api_key, filter_for_code=True):
    """Fetch available models from the Venice API and optionally filter for code-optimized ones"""
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    
    try:
        response = requests.get(f'{VENICE_API_BASE}/models', headers=headers)
        response.raise_for_status()
        models = response.json().get('data', [])
        
        # Filter for models optimized for code if requested
        if filter_for_code:
            models = [model for model in models 
                     if model.get('model_spec', {}).get('capabilities', {}).get('optimizedForCode', False)]
            
        return models
    except requests.RequestException as e:
        print(f"Error fetching models from Venice API: {e}")
        return None

def create_continue_model_entry(model_info, api_key):
    """Create a model entry for Continue config"""
    return {
        "title": f"{model_info['id']} (Venice.ai)",
        "provider": "openai",  # Venice uses OpenAI-compatible API
        "model": model_info['id'],
        "apiKey": api_key,
        "apiBase": VENICE_API_BASE
    }

def update_config_with_venice_models(config_path, api_key, dry_run=False):
    """Update Continue config file with Venice API models"""
    # Fetch available models
    venice_models = get_venice_models(api_key)
    if not venice_models:
        print("Failed to fetch models or no models available.")
        return False
    
    # Expand user directory if needed and create Path object
    config_path = Path(os.path.expanduser(config_path))
    
    # Load existing config if it exists
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
    else:
        config = {}
    
    # Initialize models list if it doesn't exist
    if 'models' not in config:
        config['models'] = []
    
    # Create a copy of the config to modify
    updated_config = config.copy()
    
    # Remove any existing Venice models
    updated_config['models'] = [model for model in updated_config['models'] 
                              if not (model.get('apiBase') and 'venice.ai' in model.get('apiBase', ''))]
    
    # Add updated Venice models
    venice_model_entries = [create_continue_model_entry(model, api_key) for model in venice_models]
    updated_config['models'].extend(venice_model_entries)
    
    # If dry run, just print what would change
    if dry_run:
        print("\n=== DRY RUN: The following changes would be made ===")
        print(f"Found {len(venice_models)} Venice models to add:")
        for model in venice_model_entries:
            print(f"  - {model['title']}")
        
        print("\nUpdated configuration would be:")
        print(json.dumps(updated_config, indent=2))
        print("\n=== No changes were made to the configuration file ===")
        return True
    
    # Ensure parent directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write the updated config back to the file
    with open(config_path, 'w') as f:
        json.dump(updated_config, f, indent=2)
    
    print(f"Added {len(venice_model_entries)} Venice models to config at: {config_path}")
    for model in venice_model_entries:
        print(f"  - {model['title']}")
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Update Continue config with Venice API models')
    parser.add_argument('--api-key', help='Venice API key (optional if VENICE_API_KEY environment variable is set)')
    parser.add_argument('--config-path', help='Path to Continue config.json (optional if CONTINUE_CONFIG_PATH environment variable is set)')
    parser.add_argument('--dry-run', action='store_true', help='Print changes without modifying the config file')
    
    args = parser.parse_args()

    # Get config location
    config_path = get_continue_config_location(args)
    print(f"Using Continue config at: {config_path}")
    
    # Load existing config if it exists
    config = {}
    config_path_expanded = Path(os.path.expanduser(config_path))
    if config_path_expanded.exists():
        try:
            with open(config_path_expanded, 'r') as f:
                config = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load config file: {e}")
    
    # Get API key - also check config for existing key
    api_key = get_api_key(args, config)
    if not api_key:
        print("Error: Venice API key not provided. Either:")
        print("  - Pass it as an argument with --api-key")
        print("  - Set the VENICE_API_KEY environment variable")
        print("  - Have an existing Venice model in your Continue config")
        sys.exit(1)
    
    # Update the config with Venice models
    if not update_config_with_venice_models(config_path, api_key, args.dry_run):
        print("Failed to update config with Venice models.")
        sys.exit(1)

if __name__ == "__main__":
    main()