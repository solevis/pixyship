{ pkgs, ... }:

{
  packages = [
    pkgs.git
    pkgs.just
  ];

  dotenv.disableHint = true;
}
