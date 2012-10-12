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

import datetime
import logging
import uuid
import socket
import time

from analytics_client.client import RREntry
from analytics_client.tasks import store_request_response_entry

logger = logging.getLogger(__name__)
socket_name = socket.gethostname()


class AnalyticsClientMiddleware(object):
    """
    Collect request-response data, send it to celery for processing.
    """

    def process_request(self, request):

        try:

            # Assign UUID used to match the response, and record the start time for the request.
            self._uid = uuid.uuid4()
            self._start_time = time.time()
            request._uid = self._uid

        except:
            logger.exception('Analytics middleware failed to process request.')

        finally:
            return None

    def process_response(self, request, response):

        try:
            # Match the request and response UUIDs
            uid1 = getattr(self, '_uid', None)
            uid2 = getattr(request, '_uid', None)
            if uid1 is not None and uid2 is not None:
                if uid1 == uid2:

                    # Collect data
                    user_id = 0
                    if request.user.is_authenticated():
                        user_id = request.user.pk

                    method = getattr(request, 'method', None)
                    path = getattr(request, 'path_info', None)
                    full_path = request.get_full_path()
                    is_api = getattr(request, 'is_api', None)
                    status = getattr(response, 'status_code', None)
                    request_bytes = len(getattr(request, 'body', ''))
                    response_bytes = len(getattr(response, 'content', ''))

                    user_agent = 'none'
                    if 'HTTP_USER_AGENT' in request.META.keys():
                        user_agent = request.META['HTTP_USER_AGENT']

                    referrer = 'none'
                    if 'HTTP_REFERER' in request.META.keys():
                        referrer = request.META['HTTP_REFERER']

                    # TODO: We may need to use HTTP_X_FORWARDED_FOR
                    client_ip = 'none'
                    if 'REMOTE_ADDR' in request.META.keys():
                        client_ip = request.META['REMOTE_ADDR']

                    session_id = 'none'
                    if hasattr(request, 'session'):
                        session_id = request.session.session_key
                        if session_id is None:
                            session_id = 'none'

                    # Calculate the request processing duration
                    duration = 0
                    request_start = getattr(self, '_start_time', None)
                    if request_start is not None:
                        duration = (time.time() - request_start)

                    # Create a request response entry object
                    entry = RREntry()
                    entry.user_id = user_id
                    entry.other_id = 0
                    entry.timestamp = datetime.datetime.now()
                    entry.request_path = path
                    entry.request_url = full_path
                    entry.request_method = method
                    entry.request_is_api = is_api
                    entry.request_bytes = request_bytes
                    entry.response_status = status
                    entry.response_bytes = response_bytes
                    entry.user_agent = user_agent
                    entry.referrer = referrer
                    entry.client_ip = client_ip
                    entry.session_id = session_id
                    entry.server_socket = socket_name
                    entry.request_duration = int(duration * 1000)

                    # Send the collected data to a celery task
                    store_request_response_entry.delay(entry)

                else:
                    logger.warning('Analytics middleware failed match request UUID to response UUID.')
        except:
            logger.exception('Analytics middleware failed to process response.')

        finally:
            return response
