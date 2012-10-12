# encoding=utf-8
"""
Copyright (c) 2012, Funkbit AS.

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the Analytics service nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY FUNKBIT AS ''AS IS''
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL FUNKBIT AS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import logging

from celery.task import task
from django.conf import settings
from django.utils import translation

from analytics_client.client import AnalyticsService
from analytics_client.settings import _ANALYTICS_USERNAME, _ANALYTICS_PASSWORD, _ANALYTICS_SITE_ID, _ANALYTICS_HOST, _ANALYTICS_PORT

logger = logging.getLogger(__name__)

service = AnalyticsService(
            username=_ANALYTICS_USERNAME,
            password=_ANALYTICS_PASSWORD,
            analytics_site=_ANALYTICS_SITE_ID,
            service_url=_ANALYTICS_HOST,
            service_port=_ANALYTICS_PORT,
            debug=settings.DEBUG
        )


@task(max_retries=10, default_retry_delay=10, ignore_result=False)
def store_request_response_entry(entry):

    # en-us is the default language in management commands
    # http://code.djangoproject.com/ticket/10078
    translation.activate(settings.LANGUAGE_CODE)

    try:

        # Store the data in the analytics service
        if entry is not None:
            if not service.store_request_response_entry(entry):
                logger.warning('Task failed to store request response entry')
        else:
            logger.warning('Task got invalid request response entry')

    except Exception as exc:
        logger.exception('Task failed to store analytics entry')

        # Retry
        store_request_response_entry.retry(args=[entry, ], exc=exc)

    # en-us is the default language in management commands
    # http://code.djangoproject.com/ticket/10078
    translation.deactivate()


@task(max_retries=10, default_retry_delay=10, ignore_result=False)
def store_metric(metric):

    # en-us is the default language in management commands
    # http://code.djangoproject.com/ticket/10078
    translation.activate(settings.LANGUAGE_CODE)

    try:

        # Store the data in the analytics service
        if metric is not None:
            if not service.store_metric(metric):
                logger.warning('Task failed to store metric')
        else:
            logger.warning('Task got invalid metric')

    except Exception as exc:
        logger.exception('Task failed to store metric')

        # Retry
        store_metric.retry(args=[metric, ], exc=exc)

    # en-us is the default language in management commands
    # http://code.djangoproject.com/ticket/10078
    translation.deactivate()
