import argparse
import json
import logging
import sys
from datetime import datetime, timedelta

from sqlalchemy.dialects.postgresql import insert

from db import db
from models import DailySale
from run import push_context

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def translate_limitedcatalogtype(limitedcatalogtype):
    return limitedcatalogtype.lower()


def translate_limitedcatalogcurrencytype(limitedcatalogcurrencytype):
    return limitedcatalogcurrencytype.lower()


def _save_daily_sale(daily_sale):
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
        logger.exception("Error when saving Daily Sale in database: {}".format(e))
        db.session.rollback()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        help="JSON file to import",
        type=argparse.FileType("r", encoding="UTF-8"),
        required=True,
    )
    args = parser.parse_args()

    sales = json.load(args.input)
    args.input.close()

    for sale in sales:
        expiry_date_as_string = sale["limitedcatalogexpirydate"]["__value__"]
        expiry_date = datetime.strptime(expiry_date_as_string, "%Y-%m-%d")
        sale_at = expiry_date - timedelta(1)

        daily_sale = DailySale(
            type=translate_limitedcatalogtype(sale["limitedcatalogtype"]),
            type_id=int(sale["limitedcatalogargument"]),
            sale_at=sale_at,
            sale_from="shop",
            currency=translate_limitedcatalogcurrencytype(sale["limitedcatalogcurrencytype"]),
            price=sale["limitedcatalogcurrencyamount"],
        )

        _save_daily_sale(daily_sale)


if __name__ == "__main__":
    # avoid Flask RuntimeError: No application found
    push_context()

    main()
