from datetime import datetime

from analytics_client.client import Metric

version_info = (0, 1, 2)
__version__ = '.'.join(map(str, version_info))


#####################
# Utility functions #
#####################

def save_metric(key, value, timestamp=None):
    """
    Wrapper used to save a metric using a celery task.
    """

    from analytics_client.tasks import store_metric

    # Set a timestamp if it is undefined
    _timestamp = timestamp
    if _timestamp is None:
        _timestamp = datetime.now()

    store_metric.delay(Metric(key=key, value=value, timestamp=_timestamp))
