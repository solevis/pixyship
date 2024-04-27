import datetime
import time

from flask import current_app

from app.constants import RARITY_MAP
from app.enums import RecordTypeEnum


def float_range(values, start_key, end_key):
    start = 0
    if values[start_key]:
        start = float(values[start_key])

    end = 0
    if values[end_key]:
        end = float(values[end_key])

    return start, end


def int_range(values, start_key, end_key):
    start = 0
    if values[start_key]:
        start = int(values[start_key])

    end = 0
    if values[end_key]:
        end = int(values[end_key])

    return start, end


def api_sleep(secs, force_sleep=False):
    if not current_app.config["SAVY_PUBLIC_API_TOKEN"] or current_app.config["USE_STAGING_API"] or force_sleep:
        time.sleep(secs)


def sort_attributes(root):
    for el in root.iter():
        attrib = el.attrib
        if len(attrib) > 1:
            attribs = sorted(attrib.items())
            attrib.clear()
            attrib.update(attribs)


def get_type_enum_from_string(type_string: str) -> RecordTypeEnum | None:
    """Converts a string to a TypeEnum."""

    if type_string == "allrooms":
        type_string = "room"

    try:
        return RecordTypeEnum(type_string.upper())
    except ValueError:
        return None


def format_delta_time(delta_time: datetime.timedelta) -> str:
    """
    Format a timedelta object into a string.

    :param delta_time: The timedelta object to format.
    :return: A string that represents the time difference in weeks, days, hours, and minutes.
    """

    delta_time_seconds = delta_time.days * 24 * 3600 + delta_time.seconds
    delta_time_minutes, delta_time_seconds = divmod(delta_time_seconds, 60)
    delta_time_hours, delta_time_minutes = divmod(delta_time_minutes, 60)
    delta_time_days, delta_time_hours = divmod(delta_time_hours, 24)
    delta_time_weeks, delta_time_days = divmod(delta_time_days, 7)

    delta_time_formatted = ""
    add_space = False

    if delta_time_weeks > 0:
        delta_time_formatted += f"{delta_time_weeks}w"
        add_space = True

    if delta_time_days > 0:
        delta_time_formatted += f"{' ' if add_space else ''}{delta_time_days}d"
        add_space = True

    if delta_time_hours > 0:
        delta_time_formatted += f"{' ' if add_space else ''}{delta_time_hours}h"
        add_space = True

    if delta_time_minutes > 0:
        delta_time_formatted += f"{' ' if add_space else ''}{delta_time_minutes}m"

    return delta_time_formatted


def compute_pvp_ratio(wins, losses, draws):
    """Compute PVP ratio, same formula as Dolores Bot."""

    ratio = 0.0
    battles = wins + losses + draws

    if battles > 0:
        ratio = (wins + 0.5 * draws) / battles
        ratio *= 100

    return round(ratio, 2)


def has_offstat(
    item_type: str, item_slot: str, item_rarity_order: int, item_bonus: float, item_disp_enhancement: str | None
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
