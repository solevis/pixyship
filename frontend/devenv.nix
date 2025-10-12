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
  packages = [
    pkgs.git
    pkgs.just
  ];

  languages.javascript = {
    enable = true;
    package = nixpkgs-old.nodejs_16;
  };

  dotenv.disableHint = true;
}
