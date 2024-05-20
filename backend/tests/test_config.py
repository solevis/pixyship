def test_default_config(app):
    with app.app_context():
        from app.config import DefaultConfig

        assert DefaultConfig.SQLALCHEMY_DATABASE_URI == "postgresql+psycopg://postgres:postgres@localhost:5432/pixyship"
        assert DefaultConfig.DEV_MODE is True
        assert DefaultConfig.DOMAIN == "localhost:8080"
        assert DefaultConfig.SPRITES_DIRECTORY == "../sprites"
        assert DefaultConfig.FORCED_PIXELSTARSHIPS_API_URL is None
        assert DefaultConfig.USE_STAGING_API is False
        assert DefaultConfig.CHANGES_MAX_ASSETS == 5000
        assert DefaultConfig.SECRET_KEY == "dev"
        assert DefaultConfig.SAVY_PUBLIC_API_TOKEN is None
        assert DefaultConfig.DEVICE_LOGIN_CHECKSUM_KEY is None
        assert DefaultConfig.MIN_DEVICES == 2
        assert DefaultConfig.SESSION_COOKIE_SECURE is True
        assert DefaultConfig.SESSION_COOKIE_HTTPONLY is True
        assert DefaultConfig.SESSION_COOKIE_SAMESITE == "Strict"
        assert DefaultConfig.SENTRY_DSN is None
        assert DefaultConfig.CACHE_TYPE == "SimpleCache"
        assert DefaultConfig.CACHE_DEFAULT_TIMEOUT == 300
        assert DefaultConfig.SPRITE_URL == "//pixelstarships.s3.amazonaws.com/"
        assert DefaultConfig.DISCORD_URL == "https://example.discord/"
        assert DefaultConfig.GITHUB_URL == "https://github.com/solevis/pixyship/"
        assert DefaultConfig.DONATION_URL == "https://example.donate/"
