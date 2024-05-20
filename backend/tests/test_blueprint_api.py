from flask import url_for


def test_api_players(client, app):
    with app.test_request_context():
        response = client.get(url_for("api.api_players"))
    assert response.status_code == 200


def test_api_player(client, app):
    with app.test_request_context():
        response = client.get(url_for("api.api_player", name="Solevis"))
    assert response.status_code == 200


def test_api_daily(client, app):
    with app.test_request_context():
        response = client.get(url_for("api.api_daily"))
    assert response.status_code == 200


def test_api_changes(client, app):
    with app.test_request_context():
        response = client.get(url_for("api.api_changes"))
    assert response.status_code == 200


def test_api_collections(client, app):
    with app.test_request_context():
        response = client.get(url_for("api.api_collections"))
    assert response.status_code == 200


def test_api_achievements(client, app):
    with app.test_request_context():
        response = client.get(url_for("api.api_achievements"))
    assert response.status_code == 200


def test_api_research(client, app):
    with app.test_request_context():
        response = client.get(url_for("api.api_research"))
    assert response.status_code == 200


def test_api_prestige(client, app):
    with app.test_request_context():
        response = client.get(url_for("api.api_prestige", char_id=196))
    assert response.status_code == 200


def test_api_crew(client, app):
    with app.test_request_context():
        response = client.get(url_for("api.api_crew"))
    assert response.status_code == 200


def test_api_items(client, app):
    with app.test_request_context():
        response = client.get(url_for("api.api_items"))
    assert response.status_code == 200


def test_api_item_prices(client, app):
    with app.test_request_context():
        response = client.get(url_for("api.api_item_prices", item_id=73))
    assert response.status_code == 200


def test_api_item_detail(client, app):
    with app.test_request_context():
        response = client.get(url_for("api.api_item_detail", item_id=73))
    assert response.status_code == 200


def test_api_tournament(client, app):
    with app.test_request_context():
        response = client.get(url_for("api.api_tournament"))
    assert response.status_code == 200


def test_api_rooms(client, app):
    with app.test_request_context():
        response = client.get(url_for("api.api_rooms"))
    assert response.status_code == 200


def test_api_skins(client, app):
    with app.test_request_context():
        response = client.get(url_for("api.api_skins"))
    assert response.status_code == 200


def test_api_ships(client, app):
    with app.test_request_context():
        response = client.get(url_for("api.api_ships"))
    assert response.status_code == 200


def test_api_last_sales(client, app):
    with app.test_request_context():
        response = client.get(url_for("api.api_last_sales", sale_type="item", sale_type_id=106))
        assert response.status_code == 200

        response = client.get(url_for("api.api_last_sales", sale_type="character", sale_type_id=120))
        assert response.status_code == 200


def test_api_last_sales_by_type(client, app):
    with app.test_request_context():
        response = client.get(url_for("api.api_last_sales_by_type", sale_from="blue_cargo"))
        assert response.status_code == 200

        response = client.get(url_for("api.api_last_sales_by_type", sale_from="shop"))
        assert response.status_code == 200

        response = client.get(url_for("api.api_last_sales_by_type", sale_from="daily_rewards"))
        assert response.status_code == 200

        response = client.get(url_for("api.api_last_sales_by_type", sale_from="green_cargo"))
        assert response.status_code == 200

        response = client.get(url_for("api.api_last_sales_by_type", sale_from="promotion_dailydealoffer"))
        assert response.status_code == 200

        response = client.get(url_for("api.api_last_sales_by_type", sale_from="sale"))
        assert response.status_code == 200


def test_api_crafts(client, app):
    with app.test_request_context():
        response = client.get(url_for("api.api_crafts"))
    assert response.status_code == 200


def test_api_missiles(client, app):
    with app.test_request_context():
        response = client.get(url_for("api.api_missiles"))
    assert response.status_code == 200


def test_api_config(client, app):
    with app.test_request_context():
        response = client.get(url_for("api.api_config"))
    assert response.status_code == 200
