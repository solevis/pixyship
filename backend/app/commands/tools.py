import datetime
import json

import click
from flask import current_app
from flask.cli import AppGroup, with_appcontext
from sqlalchemy.dialects.postgresql import insert

from app.ext import db
from app.models import DailySale

tools_cli = AppGroup("tools", help="Tools for the app.")


def translate_limitedcatalogtype(limitedcatalogtype):
    return limitedcatalogtype.lower()


def translate_limitedcatalogcurrencytype(limitedcatalogcurrencytype):
    return limitedcatalogcurrencytype.lower()


def save_daily_sale(daily_sale):
    try:
        insert_command = (
            insert(DailySale.__table__)
            .values(
                type=daily_sale.type,
                type_id=daily_sale.type_id,
                sale_at=daily_sale.sale_at,
                sale_from=daily_sale.sale_from,
                currency=daily_sale.currency,
                price=daily_sale.price,
            )
            .on_conflict_do_nothing()
        )

        db.session.execute(insert_command)
        db.session.commit()
    except Exception as e:
        current_app.logger.exception(f"Error when saving Daily Sale in database: {e}")
        db.session.rollback()


@tools_cli.command("import-dolores-sales-history")
@click.argument("json_input", type=click.File("rb"))
@with_appcontext
def import_dolores_sales_history(json_input):
    """Import sales history from Dolores."""

    sales = json.load(json_input)
    json_input.close()

    for sale in sales:
        expiry_date_as_string = sale["limitedcatalogexpirydate"]["__value__"]
        expiry_date = datetime.datetime.strptime(expiry_date_as_string, "%Y-%m-%d").astimezone(datetime.UTC)
        sale_at = expiry_date - datetime.timedelta(1)

        daily_sale = DailySale(
            type=translate_limitedcatalogtype(sale["limitedcatalogtype"]),
            type_id=int(sale["limitedcatalogargument"]),
            sale_at=sale_at,
            sale_from="shop",
            currency=translate_limitedcatalogcurrencytype(sale["limitedcatalogcurrencytype"]),
            price=sale["limitedcatalogcurrencyamount"],
        )

        save_daily_sale(daily_sale)
