{
  pkgs,
  inputs,
  ...
}:

let
  nixpkgs-old = import inputs.nixpkgs-old {
    system = pkgs.system;
    config.permittedInsecurePackages = [ "nodejs-16.20.2" ];
  };
in
{
  languages.javascript = {
    enable = true;
    package = nixpkgs-old.nodejs_16;
  };

  enterShell = ''
    echo "→ node version: $(node --version)"
    echo "→ npm version: $(npm --version)"
  '';
}
