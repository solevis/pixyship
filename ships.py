# # Check and maintain verified names
# import base64
#
# from flask import json
#
# from verified import VerifiedShips
#
# SHIP_LIMIT = 10
#
# # TODO: This is defunct, cookies are no longer used to track ships, see local storage instead.
# # DELETE ME
#
#
# class Ships:
#     # The cookie format for ships is ['name': ... other data ...] where name is unique.
#     # The internal format is a dictionary with attributes to ensure uniqueness
#
#     def __init__(self, cookies, session):
#         self.cookies = cookies
#         self.verified = VerifiedShips(session)
#         self.names = self._get_names()
#
#     def _get_names(self):
#         decoded_json = base64.b64decode(bytes(self.cookies.get('ships', ''), 'utf-8')).decode('utf-8') or '[]'
#         ships_list = json.loads(decoded_json)
#         ships_list.sort(key=lambda x: x.get('last', 0), reverse=True)
#         ships_list = ships_list[:SHIP_LIMIT]
#
#         # Backwards compatibility, used to be saved as a list of strings, now list of dicts, always represented
#         #   internally as a set
#         if ships_list and isinstance(ships_list, list):
#             if isinstance(ships_list[0], str):
#                 ships = {s: {} for s in ships_list}  # List of strings
#             else:
#                 ships = {s.pop('name'): s for s in ships_list}   # Expected list of dicts
#         elif ships_list:
#             ships = ships_list
#         else:
#             ships = {}
#
#         # Make sure all verified ships are in
#         v_ships = [n['name'] for n in self.verified.get_ships().values()]
#         # v_ships = {s['name']: {} for s in self.verified.get_ships().values()}
#         for s in v_ships:
#             if s not in ships:
#                 ships[s] = {'verified': True}
#
#         # Mark all ships as verified or not
#         for s in ships:
#             ships[s]['verified'] = s in v_ships
#
#         return ships
#
#     def update(self, new_name, data):
#         if new_name in self.names:
#             self.names[new_name].update(data)
#         else:
#             self.names[new_name] = data
#
#     def cookie_value(self):
#         names = [dict(v, name=k) for k, v in self.names.items()]
#         names = sorted(names, key=lambda x: x['name'])
#         json_data = json.dumps(names)
#         return base64.b64encode(bytes(json_data, 'utf-8')).decode('utf-8')
