def test_config():
    from config import CONFIG

    assert 'DSN' in CONFIG
    assert 'DEV_MODE' in CONFIG
    assert 'MAINTENANCE' in CONFIG
    assert 'DOMAIN' in CONFIG
    assert 'CSP_REPORT_LOG' in CONFIG
    assert 'SECRET_KEY' in CONFIG
    assert 'SPRITES_DIRECTORY' in CONFIG
