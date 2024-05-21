def test_crews(app, service_factory):
    with app.app_context():
        crews = service_factory.character_service.get_characters_from_records()

        assert len(crews) > 0
        assert crews[392]["id"] == 392
        assert crews[392]["name"] == "Polaran Pilgrim"


def test_items(app, service_factory):
    with app.app_context():
        items = service_factory.item_service.get_items_from_records()

        assert len(items) > 0
        assert items[600]["id"] == 600
    assert items[600]["name"] == "Federation Officer Armor"


def test_rooms(app, service_factory):
    with app.app_context():
        rooms, _, = service_factory.room_service.get_rooms_from_records()

        assert len(rooms) > 0
        assert rooms[10]["id"] == 10
        assert rooms[10]["name"] == "Bedroom Lv2"
        assert rooms[10]["level"] == 2


def test_crafts(app, service_factory):
    with app.app_context():
        crafts = service_factory.craft_service.get_crafts_from_records()

        assert len(crafts) > 0
        assert crafts[10]["id"] == 10
        assert crafts[10]["name"] == "Interceptor Lv7"
        assert crafts[10]["hp"] == 5


def test_missiles(app, service_factory):
    with app.app_context():
        missiles = service_factory.missile_service.get_missiles_from_records()

        assert len(missiles) > 0
        assert missiles[40]["id"] == 40
        assert missiles[40]["name"] == "Penetrator Lv5"
        assert missiles[40]["volley"] == 1.0


def test_ships(app, service_factory):
    with app.app_context():
        ships = service_factory.ship_service.get_ships_from_records()

        assert len(ships) > 0
        assert ships[129]["id"] == 129
        assert ships[129]["name"] == "Oumaumau Invader"
        assert ships[129]["level"] == 11


def test_collections(app, service_factory):
    with app.app_context():
        collections = service_factory.collection_service.get_collections_from_records()

        assert len(collections) > 0
        assert collections[7]["id"] == 7
        assert collections[7]["name"] == "Federation"


def test_researches(app, service_factory):
    with app.app_context():
        researches = service_factory.research_service.get_researches_from_records()

        assert len(researches) > 0
        assert researches[42]["ResearchDesignId"] == "42"
        assert researches[42]["ResearchName"] == "Advanced Training Lv5"


def test_prices(app, service_factory):
    with app.app_context():
        prices = service_factory.market_service.get_prices_from_db()

        assert len(prices) > 0


def test_sprites(app, service_factory):
    with app.app_context():
        sprites = service_factory.sprite_service.get_sprites_from_records()

        assert len(sprites) > 0


def test_search_player(app, service_factory):
    with app.app_context():
        players = service_factory.player_service.get_player_data("Solevis")

        assert len(players) == 1
        assert players[0]["name"] == "Solevis"


def test_changes(app, service_factory):
    with app.app_context():
        changes = service_factory.changes_service.get_changes_from_db()

        assert len(changes) > 0


def test_user_id(app, service_factory):
    with app.app_context():
        user_id = service_factory.player_service.find_user_id("Solevis")

        assert user_id == 6635604
