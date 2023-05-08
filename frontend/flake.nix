{
  description = "Example JavaScript development environment for Zero to Nix";

  # Flake outputs
  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        # Use a system-specific version of Nixpkgs
        pkgs = nixpkgs.legacyPackages.${system};
      in with pkgs; rec
      {
        # Development environment output
        devShells.default = mkShell {
          shellHook = ''
            export NODE_OPTIONS=--openssl-legacy-provider
          '';

          # The Nix packages provided in the environment
          packages = with pkgs; [
            nodejs-16_x # Node.js 16, plus npm, npx, and corepack
          ];
        };
      }
    );
}
