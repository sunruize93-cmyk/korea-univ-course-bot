import ntplib
import time
from loguru import logger

class TimeSynchronizer:
    def __init__(self, server='pool.ntp.org'):
        self.server = server
        self.offset = 0.0
        self.synced = False

    def sync(self):
        """Syncs local time with NTP server to calculate offset."""
        client = ntplib.NTPClient()
        try:
            response = client.request(self.server, version=3)
            self.offset = response.offset
            self.synced = True
            logger.info(f"NTP sync successful. Local time offset: {self.offset:.6f} seconds")
        except Exception as e:
            logger.error(f"Failed to sync with NTP server: {e}")
            self.offset = 0.0
            self.synced = False

    def get_time(self):
        """Returns the current accurate time (Local + Offset)."""
        if not self.synced:
            self.sync()
        return time.time() + self.offset

    def sleep_until(self, target_timestamp):
        """Precise sleep until a specific timestamp."""
        current = self.get_time()
        delta = target_timestamp - current
        if delta > 0:
            time.sleep(delta)
