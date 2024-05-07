import time

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

    if item_rarity_order < RARITY_MAP.get("Hero"):
        return False

    if item_disp_enhancement is None and item_bonus == 0.0:
        return False

    return True


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


def parse_assets_string(assets_string: str) -> list[dict]:
    """Parse an assets string and return a list of assets."""
    assets = []
    if assets_string:
        # Split the string by "|" to get individual assets
        asset_items = assets_string.split("|")

        for asset_item in asset_items:
            # Check if ":" is in the asset_item
            if ":" in asset_item:
                # Split the reward by ":" to get the type and id/count
                asset_type, asset_id_count = asset_item.split(":")
            else:
                # If ":" is not in the asset_item, the type is None and asset_item is the id/count
                asset_type = None
                asset_id_count = asset_item

            # Check if the id/count contains an "x"
            if "x" in asset_id_count:
                # Split the id/count by "x" to get the id and count
                asset_id, asset_count = asset_id_count.split("x")
            else:
                # If there's no "x", the count is None
                asset_id = asset_id_count
                asset_count = None

            if "[USD/" in assets_string:
                asset_count = None

            # Store the type, id, and count in a dictionary
            asset = {
                "type": asset_type,
                "id": int(asset_id) if asset_id is not None else None,
                "count": int(asset_count) if asset_count is not None else None,
            }

            # Add the asset to the list of assets
            assets.append(asset)

    return assets


def parse_requirement(requirement_string: str) -> dict | None:
    """Parse requirement asset."""
    if not requirement_string:
        return None

    splits = requirement_string.split(":")
    if len(splits) < 2:
        return None

    requirement_type, id_and_amount = splits

    if ">=" in id_and_amount:
        requirement_id, requirement_count = id_and_amount.split(">=")
    else:
        requirement_id, requirement_count = id_and_amount.split(">")

    requirement_type = requirement_type.strip().capitalize()
    requirement_type = get_type_enum_from_string(requirement_type)
    requirement_id = int(requirement_id.strip())
    requirement_count = int(requirement_count.strip())

    # in some case (example: Coal Factory), the amount needed is '> 0' not '>= 1'
    if requirement_count == 0:
        requirement_count = 1

    return {
        "count": requirement_count,
        "type": requirement_type,
        "id": requirement_id,
    }


def parse_price_from_pricestring(pricestring: str) -> tuple[int, str | None]:
    """Split amount and currency."""
    if not pricestring:
        return 0, None

    parts = pricestring.split(":")
    return int(parts[1]), parts[0]
