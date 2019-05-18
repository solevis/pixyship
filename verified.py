# Check and maintain verified names
import time

EXPIRE_SECS = 60 * 60 * 24 * 14  # secs * mins * hours * days


class VerifiedShips:

    def __init__(self, session):
        self.session = session

    def check(self, name):
        return False
        v, now = self._expire()
        self.session['verified'] = v
        if self.session.get('ok') == 'ok':
            return True
        if name.lower() in v:
            return v[name.lower()]['expire_at'] > now
        return False

    def update(self, name):
        v, now = self._expire()
        v[name.lower()] = {
            'expire_at': now + EXPIRE_SECS,
            'name': name,
        }
        self.session['verified'] = v
        return v

    def _expire(self):
        v = self.session.get('verified', {})
        now = int(time.time())
        try:
            return {n: e for n, e in v.items() if e['expire_at'] >= now}, now
        except TypeError:
            # Reset cause we probably changed formats
            return {}, now

    def get_ships(self):
        try:
            v = self.session.get('verified') or {}
            # Check that the latest values are in the dict, or start over.
            if v and 'name' not in next(iter(v.values())):
                return {}
            return v
        except Exception:
            return {}
