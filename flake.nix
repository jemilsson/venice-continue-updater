{
  description = "Venice Continue Updater - Automatically update Continue with Venice AI models";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    home-manager = {
      url = "github:nix-community/home-manager";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, home-manager, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        
        veniceUpdater = pkgs.python3Packages.buildPythonApplication {
          pname = "venice-continue-updater";
          version = "0.1.0";
          
          src = ./.;
          
          propagatedBuildInputs = with pkgs.python3Packages; [
            requests
          ];
          
          # No build phase needed, just install the script
          format = "other";
          
          installPhase = ''
            mkdir -p $out/bin
            cp update.py $out/bin/venice-continue-updater
            chmod +x $out/bin/venice-continue-updater
          '';
        };
      in
      {
        packages = {
          default = veniceUpdater;
          veniceUpdater = veniceUpdater;
        };
        
        apps.default = flake-utils.lib.mkApp {
          drv = veniceUpdater;
          name = "venice-continue-updater";
        };
      }
    ) // {
      # NixOS module
      nixosModules.default = { config, lib, pkgs, ... }:
        let
          cfg = config.services.veniceUpdater;
        in
        {
          options.services.veniceUpdater = {
            enable = lib.mkEnableOption "Venice Continue Updater service";
            
            apiKey = lib.mkOption {
              type = lib.types.str;
              default = "";
              description = "Venice API key";
              example = "your-venice-api-key";
            };
            
            configPath = lib.mkOption {
              type = lib.types.str;
              default = "~/.continue/config.json";
              description = "Path to Continue config.json";
              example = "/home/user/.continue/config.json";
            };
            
            startAt = lib.mkOption {
              type = lib.types.str;
              default = "daily";
              description = "When to run the service, in systemd calendar format";
              example = "daily";
            };
          };
          
          config = lib.mkIf cfg.enable {
            # Make the package available
            environment.systemPackages = [ self.packages.${pkgs.system}.veniceUpdater ];
          };
        };
      
      # Home Manager module
      homeManagerModules.default = { config, lib, pkgs, ... }:
        let
          cfg = config.services.veniceUpdater;
        in
        {
          options.services.veniceUpdater = {
            enable = lib.mkEnableOption "Venice Continue Updater service";
            
            apiKey = lib.mkOption {
              type = lib.types.str;
              default = "";
              description = "Venice API key";
              example = "your-venice-api-key";
            };
            
            configPath = lib.mkOption {
              type = lib.types.str;
              default = "~/.continue/config.json";
              description = "Path to Continue config.json";
              example = "~/.continue/config.json";
            };
            
            startAt = lib.mkOption {
              type = lib.types.str;
              default = "daily";
              description = "When to run the service, in systemd calendar format";
              example = "daily";
            };
          };
          
          config = lib.mkIf cfg.enable {
            # Install the package
            home.packages = [ self.packages.${pkgs.system}.veniceUpdater ];
            
            # Set up the user service
            systemd.user.services.venice-continue-updater = {
              Unit = {
                Description = "Venice Continue Updater Service";
              };
              
              Service = {
                Type = "oneshot";
                ExecStart = "${self.packages.${pkgs.system}.veniceUpdater}/bin/venice-continue-updater ${lib.optionalString (cfg.apiKey != "") "--api-key ${cfg.apiKey}"} --config-path ${cfg.configPath}";
                Environment = lib.optional (cfg.apiKey != "") "VENICE_API_KEY=${cfg.apiKey}";
              };
            };
            
            # Set up the timer
            systemd.user.timers.venice-continue-updater = {
              Unit = {
                Description = "Timer for Venice Continue Updater";
              };
              
              Timer = {
                OnCalendar = cfg.startAt;
                Persistent = true;
              };
              
              Install = {
                WantedBy = [ "timers.target" ];
              };
            };
          };
        };
    };
}