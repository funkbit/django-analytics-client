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

from datetime import datetime
from analytics_client.client import AnalyticsService, Metric, RREntry

# Replace username, password and analytics site id with your proper credentials
service = AnalyticsService(
        username='username',
        password='password',
        analytics_site=1,
        service_url='analytics.service.com',
        service_port=443,
        debug=False
    )


# Creates a new metric entry for key 'test_key'
metric = Metric(
        timestamp=datetime.now(),
        key='test_key',
        value='test metric value',
    )

# Store the metric in the analytics service
service.store_metric(metric)

# Create a new request response entry
rrentry = RREntry(
        timestamp=datetime.now(),
        user_id=0,
        other_id=0,
        request_path='/',
        request_url='/',
        request_method='GET',
        request_is_api=False,
        request_bytes=300,
        response_status=200,
        response_bytes=600,
        user_agent='Firefox',
        referrer='none',
        client_ip='127.0.0.1',
        session_id='none',
        server_socket='localhost',
        request_duration=2,
    )

# Store the rrentry in the analytics service
service.store_request_response_entry(rrentry)
