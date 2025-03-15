# Venice Models for Continue

This utility helps you add Venice AI models to your Continue configuration with a simple command.

## What is Venice AI?

Venice AI provides high-quality AI models with a particular emphasis on code-related tasks. These models can be integrated with [Continue](https://continue.dev/), an open-source coding assistant.

## Installation

### Direct Usage

No installation is required beyond having Python 3 and the `requests` library. This script is designed to run with Nix, but can be used directly with Python.

### Using Nix Flake

This project includes a Nix flake that provides:
- A packaged version of the updater
- A NixOS module for running the updater as a systemd service

To use the flake:

```bash
# Run directly using the flake
nix run github:jemilsson/venice-continue-updater

# Install to your profile
nix profile install github:jemilsson/venice-continue-updater
```

## Usage

### Command Line

```bash
# If you have a api-key in your config.json, you can run:
./update.py

# Basic usage
./update.py --api-key your_venice_api_key

# Use environment variable for API key
export VENICE_API_KEY=your_venice_api_key
./update.py

# Dry run to see what changes would be made
./update.py --dry-run

# Specify a custom config path
./update.py --config-path /path/to/config.json
```

### Home Manager Module (Recommended)

The recommended way to use this utility is with Home Manager, which will set up a user-level systemd service:

```nix
{
  inputs.venice-continue-updater.url = "github:jemilsson/venice-continue-updater";
  
  outputs = { self, nixpkgs, home-manager, venice-continue-updater, ... }: {
    homeConfigurations."your-username" = home-manager.lib.homeManagerConfiguration {
      # ...
      modules = [
        # ...
        venice-continue-updater.homeManagerModules.default
        {
          services.veniceUpdater = {
            enable = true;
            apiKey = "your-venice-api-key"; # Optional if in config already
            # Optional settings:
            # configPath = "~/.continue/config.json";
            # startAt = "daily"; # Default is daily, can use systemd calendar format
          };
        }
      ];
    };
  };
}
```

This will set up a systemd user service and timer to automatically update your Continue configuration with Venice AI models daily.

See `example-home-manager-configuration.nix` for a more detailed example.

### NixOS Module

You can also use the NixOS module, which will make the package available system-wide:

```nix
{
  inputs.venice-continue-updater.url = "github:jemilsson/venice-continue-updater";
  
  outputs = { self, nixpkgs, venice-continue-updater, ... }: {
    nixosConfigurations.your-hostname = nixpkgs.lib.nixosSystem {
      # ...
      modules = [
        # ...
        venice-continue-updater.nixosModules.default
        {
          services.veniceUpdater = {
            enable = true;
            apiKey = "your-venice-api-key"; # Optional if in config already
            # Optional settings:
            # configPath = "~/.continue/config.json";
            # startAt = "daily"; # Default is daily, can use systemd calendar format
          };
        }
      ];
    };
  };
}
```

See `example-nixos-configuration.nix` for a more detailed example.

Note: With the NixOS module, you'll still need to set up the Home Manager module for each user that needs to run the updater.

## Development

This repository includes several files to help with development:

- `.envrc` - For direnv integration to automatically set up the development environment
- `shell.nix` - For backward compatibility with non-flake Nix
- `.gitignore` - To exclude Nix build artifacts from version control

To develop locally:

```bash
# If you have direnv installed and allowed
direnv allow

# Or use nix develop
nix develop

# Or traditional nix-shell
nix-shell
```
