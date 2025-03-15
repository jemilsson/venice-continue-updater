# shell.nix - For backward compatibility with non-flake nix
(import (fetchTarball "https://github.com/edolstra/flake-compat/archive/master.tar.gz") {
  src = ./.;
}).shellNix