import getpass
import logging
import socket
from logging.handlers import SMTPHandler

from api_errors import EXPIRED_TOKEN_RESP2
from config import CONFIG
from pixelstarshipsapi import PixelStarshipsApi
from run import push_context

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

mail_handler = SMTPHandler(
    mailhost=("localhost", 25),
    fromaddr='{}@{}'.format(getpass.getuser(), socket.gethostname()),
    toaddrs=[CONFIG['EMAIL']],
    subject="Error on PixyShip!"
)

mail_handler.setLevel(logging.ERROR)
logger.addHandler(mail_handler)


def check_savy_token():
    """Check if the token given by Savy has expired."""

    # no need to check if token not defined
    if not CONFIG['SAVY_PUBLIC_API_TOKEN']:
        return

    # avoid Flask RuntimeError: No application found
    push_context()

    # get the top user
    params = {
        'from': 1,
        'to': 1
    }

    # retrieve data as XML from Pixel Starships API
    pss_api = PixelStarshipsApi()
    endpoint = f'https://{pss_api.server}/LadderService/ListUsersByRanking'
    logger.info('Checking {}...'.format(endpoint))
    response = pss_api.call(endpoint, params=params, need_token=True)

    if response.text == EXPIRED_TOKEN_RESP2:
        logger.error('Savy Token has expired: {}'.format(response.text))


if __name__ == '__main__':
    check_savy_token()
