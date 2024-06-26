from xml.etree.ElementTree import Element


def sort_attributes(root: Element) -> None:
    """Sorts the attributes of all elements in the XML tree."""
    for el in root.iter():
        attrib = el.attrib
        if len(attrib) > 1:
            attribs = sorted(attrib.items())
            attrib.clear()
            attrib.update(attribs)
