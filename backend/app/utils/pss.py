import time
from datetime import datetime

from flask import current_app

from app.constants import RARITY_MAP
from app.enums import TypeEnum


def api_sleep(secs: float, force_sleep: bool = False) -> None:
    """Sleep for a certain amount of time if the public API token is not set or if the staging API is used."""
    if not current_app.config["SAVY_PUBLIC_API_TOKEN"] or current_app.config["USE_STAGING_API"] or force_sleep:
        time.sleep(secs)


def has_offstat(
    item_type: str,
    item_slot: str,
    item_rarity_order: int,
    item_bonus: float,
    item_disp_enhancement: str | None,
) -> bool:
    """Check if item have an offstat bonus."""
    if item_type != "Equipment":
        return False

    if item_slot not in ["Accessory", "Head", "Body", "Weapon", "Leg", "Pet"]:
        return False

    if item_rarity_order < RARITY_MAP["Hero"]:
        return False

    return not (item_disp_enhancement is None and item_bonus == 0.0)


def get_offstat_count(
    item_type: str,
    item_slot: str,
    item_rarity_order: int,
    item_bonus: float,
    item_disp_enhancement: str | None,
) -> int:
    """Get the number of offstat bonuses an item can roll: legendary items get a second one."""
    if not has_offstat(item_type, item_slot, item_rarity_order, item_bonus, item_disp_enhancement):
        return 0

    if item_rarity_order >= RARITY_MAP["Legendary"]:
        return 2

    return 1


def get_type_enum_from_string(type_string: str) -> TypeEnum | None:
    """Convert a string to a TypeEnum."""
    if type_string.lower() == "allrooms":
        type_string = "room"

    try:
        return TypeEnum(type_string.upper())
    except ValueError:
        return None


def compute_pvp_ratio(wins: int, losses: int, draws: int) -> float:
    """Compute PVP ratio, same formula as Dolores Bot."""
    ratio = 0.0
    battles = wins + losses + draws

    if battles > 0:
        ratio = (wins + 0.5 * draws) / battles
        ratio *= 100

    return round(ratio, 2)


def parse_assets_string(assets_string: str | None) -> list[dict]:
    """Parse an assets string from API (type:idxcount|type:id|idxcount...), the type and the count are optional.

    Return a list of {"type": str | None, "id": int, "count": int | None}, assets without a numeric id are skipped.
    The count is None when missing or not a number, like the IAP price of a sale reward (item:994x[USD/3]).
    """
    assets = []
    for asset_item in (assets_string or "").split("|"):
        if not asset_item:
            continue

        type_and_id_count = asset_item.split(":")
        if len(type_and_id_count) > 1:
            asset_type: str | None = type_and_id_count[0]
            asset_id_count = type_and_id_count[1]
        else:
            asset_type = None
            asset_id_count = type_and_id_count[0]

        id_and_count = asset_id_count.split("x")
        try:
            asset_id = int(id_and_count[0])
        except ValueError:
            continue

        asset_count = None
        if len(id_and_count) > 1 and id_and_count[1].isdigit():
            asset_count = int(id_and_count[1])

        assets.append({"type": asset_type, "id": asset_id, "count": asset_count})

    return assets


def parse_requirement(requirement_string: str) -> dict | None:
    """Parse requirement asset."""
    if not requirement_string:
        return None

    splits = requirement_string.split(":")
    if len(splits) != 2:
        return None

    requirement_type, id_and_amount = splits

    if ">=" in id_and_amount:
        requirement_id, requirement_count = id_and_amount.split(">=")
    else:
        requirement_id, requirement_count = id_and_amount.split(">")

    requirement_type = requirement_type.strip().capitalize()
    type_ = get_type_enum_from_string(requirement_type)
    if type_ is None:
        return None

    id_ = int(requirement_id.strip())
    count = int(requirement_count.strip())

    # in some case (example: Coal Factory), the amount needed is '> 0' not '>= 1'
    if count == 0:
        count = 1

    return {
        "count": count,
        "type": type_,
        "id": id_,
    }


def parse_price_from_pricestring(pricestring: str) -> tuple[int, str | None]:
    """Split amount and currency."""
    if not pricestring:
        return 0, None

    parts = pricestring.split(":")
    return int(parts[1]), parts[0]


def convert_datetime_to_iso(datetime_str: str) -> str:
    """Convert datetime to ISO format."""
    return datetime.fromisoformat(datetime_str).strftime("%Y-%m-%dT%H:%M:%S")
