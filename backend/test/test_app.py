def test_config():
    from config import CONFIG

    assert 'DATABASE_URI' in CONFIG
    assert 'DEV_MODE' in CONFIG
    assert 'DOMAIN' in CONFIG
    assert 'SECRET_KEY' in CONFIG
    assert 'SPRITES_DIRECTORY' in CONFIG
    assert 'CHANGES_MAX_ASSETS' in CONFIG
    assert 'EMAIL' in CONFIG
    assert 'MAIN_PIXELSTARSHIPS_API_URL' in CONFIG
    assert 'BACKUP_PIXELSTARSHIPS_API_URL' in CONFIG
    assert 'FORCED_PIXELSTARSHIPS_API_URL' in CONFIG
    assert 'SAVY_PUBLIC_API_TOKEN' in CONFIG
    assert 'SALE_ID_DIFF_WARNING' in CONFIG
