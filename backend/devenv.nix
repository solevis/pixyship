{
  pkgs,
  ...
}:

{
  packages = [
    pkgs.git
    pkgs.just
  ];

  languages.python = {
    enable = true;
    package = pkgs.python311;
    uv.enable = true;
    uv.sync.enable = true;
  };

  services.postgres = {
    enable = true;
    package = pkgs.postgresql_15;
    listen_addresses = "127.0.0.1";
    initialScript = "CREATE USER pixyship SUPERUSER;";
    initialDatabases = [
      {
        name = "pixyship";
      }
    ];
  };

  services.redis = {
    enable = true;
    package = pkgs.redis;
    port = 6379;
  };

  enterShell = ''
    echo "→ uv version: $(uv --version)"
    echo "→ python version: $(python --version)"
    echo "→ postgres version: $(psql --version)"
    echo "→ redis version: $(redis-server --version)"
    echo "→ venv path: $UV_PROJECT_ENVIRONMENT"
  '';

  dotenv.disableHint = true;
}
