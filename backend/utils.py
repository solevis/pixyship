from collections import defaultdict


def dict_get(data, *args):
    value = data or {}

    for arg in args:
        value = value.get(arg) or {}

    return value


def etree_to_dict(tree):
    d = {tree.tag: {} if tree.attrib else None}
    children = list(tree)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {tree.tag: {k: v[0] if len(v) == 1 else v
                        for k, v in dd.items()}}
    if tree.attrib:
        d[tree.tag].update(('@' + k, v)
                           for k, v in tree.attrib.items())
    if tree.text:
        text = tree.text.strip()
        if children or tree.attrib:
            if text:
                d[tree.tag]['#text'] = text
        else:
            d[tree.tag] = text
    return d


def float_range(values, start_key, end_key):
    start = float(values.get(start_key, 0))
    end = float(values.get(end_key, 0))

    return start, end


def int_range(values, start_key, end_key):
    start = int(values[start_key])
    end = int(values[end_key])

    return start, end
