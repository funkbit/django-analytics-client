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
from __future__ import print_function

import base64
import json
import re
import string
from datetime import date, datetime
from decimal import Decimal

try:
    # Python 3
    from http import client as http_client
    from urllib.parse import urlencode
    text = str
except ImportError:
    # Python 2
    import httplib as http_client
    from urllib import urlencode
    text = unicode


class AnalyticsObject(object):
    """
    Base object for resources used with analytics.
    """

    def __init__(self, **kwargs):

        for key, value in kwargs.items():
            setattr(self, key, value)


class Metric(AnalyticsObject):

    def __init__(self, **kwargs):

        # Document fields
        self.analytics_site = None
        self.timestamp = None
        self.key = None
        self.value = None

        super(Metric, self).__init__(**kwargs)


class RREntry(AnalyticsObject):

    def __init__(self, **kwargs):

        # Document fields
        self.analytics_site = None
        self.timestamp = None
        self.user_id = None
        self.other_id = None
        self.request_path = None
        self.request_url = None
        self.request_method = None
        self.request_is_api = None
        self.request_bytes = None
        self.response_status = None
        self.response_bytes = None
        self.user_agent = None
        self.referrer = None
        self.client_ip = None
        self.session_id = None
        self.server_socket = None
        self.request_duration = None

        super(RREntry, self).__init__(**kwargs)


class AnalyticsJSONEncoder(json.JSONEncoder):
    """
    Supports serializing datetimes/dates/decimals as JSON.
    """

    def default(self, obj):

        if isinstance(obj, datetime):
            return datetime.strftime(obj, '%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return datetime.strftime(obj, '%Y-%m-%d')
        elif isinstance(obj, AnalyticsObject):
            return obj.__dict__
        elif isinstance(obj, Decimal):
            return text(obj)
        else:
            return json.JSONEncoder.default(self, obj)


def AnalyticsJSONDecoder(d):
    """
    Parses dates/datetimes/decimals in decoded JSON.
    """

    pattern_date = re.compile('\d{4}-\d{2}-\d{2}$')
    pattern_datetime = re.compile('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$')
    pattern_decimal = re.compile('\d+\.\d+$')

    obj = AnalyticsObject()
    for a, b in d.items():

        # Parse datetimes and decimals
        if pattern_datetime.match(text(b)):
            b = datetime.strptime(b, '%Y-%m-%d %H:%M:%S')
        elif pattern_date.match(text(b)):
            b = datetime.strptime(b, '%Y-%m-%d').date()
        elif pattern_decimal.match(text(b)):
            b = Decimal(b)

        if isinstance(b, (list, tuple)):
            setattr(obj, a, [obj(x) if isinstance(x, dict) else x for x in b])
        else:
            setattr(obj, a, obj(b) if isinstance(b, dict) else b)

    return obj


class AnalyticsService(object):
    """
    Analytics client library for accessing Analytics API.
    """

    def __init__(self, username, password, analytics_site, service_url, service_port, debug=False):
        """
        Initializes the client with the specified credentials.
        """

        self.username = username
        self.password = password
        self.analytics_site = analytics_site
        self.SERVICE_URL = service_url
        self.SERVICE_PORT = service_port
        self.DEBUG = debug

    ############
    # REQUESTS #
    ############

    def _request(self, url, method='GET', params={}):
        """
        Performs an HTTP request, with the specified parameters and method.
        """

        # Prepare connection and construct authorization header

        # SSL
        if self.SERVICE_PORT == 443:
            connection = http_client.HTTPSConnection(self.SERVICE_URL, self.SERVICE_PORT)

        # Non-SSL
        else:
            connection = http_client.HTTPConnection(self.SERVICE_URL, self.SERVICE_PORT)

        auth = 'Basic ' + string.strip(base64.encodestring(self.username + ':' + self.password))

        if method == 'GET':

            params = self.url_serialize(params)
            connection.request(method, url + '?' + params, None, {
                'Accept': 'application/json',
                'Authorization': auth,
            })

        else:

            params = self.json_serialize(params)
            connection.request(method, url, params, {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': auth,
            })

        # Fetch and reserialize response
        response = connection.getresponse()
        data = response.read()
        if self.DEBUG:
            print(response.status)
            print(data)

        try:
            obj = json.loads(data, object_hook=AnalyticsJSONDecoder, encoding='utf-8')
        except:
            obj = None

        return response.status, obj

    ###############
    # SERIALIZERS #
    ###############

    def url_serialize(self, obj):
        """
        Returns the specified dictionary as a URL encoded string, suitable for HTTP GET.
        """

        if not obj:
            return ''

        params = []
        for key, value in obj.items():
            params.append((key, value))

        return urlencode(params)

    def json_serialize(self, obj):
        """
        Returns the specified object encoded as JSON, suitable for HTTP POST.
        """

        if not obj:
            return '{}'

        if hasattr(obj, '__dict__'):
            obj = obj.__dict__

        return json.dumps(obj, cls=AnalyticsJSONEncoder)

    ############
    # FEATURES #
    ############

    def store_metric(self, metric=None):
        """
        Stores a new metric object.
        """

        if hasattr(metric, '__dict__'):
            setattr(metric, 'analytics_site', self.analytics_site)

        status, data = self._request('/api/v1/metric/create/', method='POST', params=metric)
        return True if status == 200 else False

    def store_request_response_entry(self, rrentry=None):
        """
        Stores a new request respone entry.
        """

        if hasattr(rrentry, '__dict__'):
            setattr(rrentry, 'analytics_site', self.analytics_site)

        status, data = self._request('/api/v1/rrentry/create/', method='POST', params=rrentry)
        return True if status == 200 else False
