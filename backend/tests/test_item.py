from app.services.item import ItemService


def test_parse_module_extra_enhancement_short_disp_is_a_string():
    item = {"ModuleType": "Turret", "ItemSubType": "Module", "ModuleArgument": "250"}

    result = ItemService.parse_module_extra_enhancement(item)

    assert result["enhancement"] == "Hp"
    assert isinstance(result["short_disp_enhancement"], str)
    assert result["bonus"] == 250.0


def test_parse_module_extra_enhancement_without_module():
    item = {"ModuleType": "None", "ItemSubType": "Module", "ModuleArgument": "0"}

    result = ItemService.parse_module_extra_enhancement(item)

    assert result["enhancement"] is None
    assert result["short_disp_enhancement"] is None
