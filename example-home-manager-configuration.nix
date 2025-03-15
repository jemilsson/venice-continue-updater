# Example Home Manager configuration for using the Venice Continue Updater
# This file is meant as a reference and should be adapted to your specific setup

{ config, pkgs, ... }:

{
  # Import the flake's Home Manager module
  imports = [
    # Example of how to reference the flake in your configuration
    # inputs.venice-continue-updater.homeManagerModules.default
  ];

  # Enable and configure the Venice Continue Updater service
  services.veniceUpdater = {
    enable = true;
    
    # Venice API key (optional if already in your Continue config)
    apiKey = "your-venice-api-key";
    
    # Path to Continue config.json (optional, defaults to ~/.continue/config.json)
    # configPath = "~/.continue/config.json";
    
    # When to run the service (optional, defaults to "daily")
    # Uses systemd calendar format: https://www.freedesktop.org/software/systemd/man/systemd.time.html
    # startAt = "daily";
    # startAt = "weekly";
    # startAt = "*-*-* 04:00:00";  # Every day at 4 AM
  };

  # The Home Manager module will:
  # 1. Install the venice-continue-updater package
  # 2. Set up a systemd user service
  # 3. Configure a timer to run the service at the specified interval
}