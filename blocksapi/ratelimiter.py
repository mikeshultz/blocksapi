import redis
from datetime import datetime
from .config import LOGGER, REDIS, RATE_LIMITER_EXPIRY, RATE_LIMIT

log = LOGGER.getChild('ratelimiter')


class IPLimiter(object):
    """ A class for handling IP limiting """
    def __init__(self):
        self.store = redis.Redis(host=REDIS.get('host'), port=REDIS.get('port'))

    def request(self, ip):
        """ Signal a request and return True if they're allowed """
        store_key = "{}_{}".format(ip, datetime.now().strftime('%Y%m%d'))
        
        # Get the count
        count = self.store.get(store_key)
        ttl = self.store.pttl(store_key)
        
        # Must be a number
        if count is None:
            count = 1
        else:
            count = int(count) + 1
            
        """ TTL LIMITATIONS
            ===============
            This TTL usage does have some limitations.  If 30 requests are made
            in less than a second between each, the TTL will less than it should
            by approximately as long as it takes to process this request since 
            the TTL is being set with the ttl value we got when we started.
        """
        self.store.psetex(store_key, ttl or (RATE_LIMITER_EXPIRY * 1000), count)

        # Is the request still allowed and under limit?
        if count <= RATE_LIMIT:
            log.debug('Rate limiter passed. Count: {}:{}'.format(count, ttl))
            return True
        else:
            log.warning('Request has been rate limited')
            return False