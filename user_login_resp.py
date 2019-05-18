import re

TOKEN_EXPIRED_RE = re.compile('errorMessage[^>]*ccess token')
INSPECT_SHIP_ERROR = 'InspectShip errorMessage='
EXPIRED_TOKEN_RESP = '<InspectShip errorMessage="Access token expired." />'
EXPIRED_TOKEN_RESP1 = '<InspectShip errorMessage="Access token expired." />'
FAILED_AUTH = '<InspectShip errorMessage="GetShip: Failed to authorize access token." />'
EXPIRED_TOKEN_RESP2 = '<ListUsersByRanking errorMessage="Failed to authorize access token." />'
