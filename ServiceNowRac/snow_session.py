#
# Copyright (c) 2016, Arista Networks, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#   Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
#   Neither the name of Arista Networks nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ARISTA NETWORKS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
''' ServiceNow Session

SNOW Session extends requests.Session to add functionality for connection
retry in the case of the following errors:
    o HTTP Errors
        - 502
        - 503
        - 504
    o requests Exceptions
        - Timeout
        - ConnectionError
'''

import time
import logging

from requests import Session
from requests.exceptions import ConnectionError, HTTPError, Timeout
from logging.handlers import SysLogHandler

class SnowSession(Session):
    ''' TODO
    '''
    MAX_RETRIES = 3
    MAX_RETRY_DELAY = 3
    RETRY_BACKOFF = 2

    def __init__(self):
        super(SnowSession, self).__init__()
        self.headers.update({
            'content-type': 'application/json',
            'accept': 'application/json'
        })

        # Define class level logger
        self.log = logging.getLogger(__name__)

    def _make_request(self, req_type, url, **kwargs):
        ''' XXX
        '''
        method = getattr(super(SnowSession, self), req_type.lower())

        max_retries, max_delay = self.MAX_RETRIES, self.MAX_RETRY_DELAY
        retry_num = 0
        while retry_num < max_retries:
            try:
                response = method(url, **kwargs)
                response.raise_for_status()
                if response.status_code == 200:
                    return response
            except HTTPError as error:
                if error.response.status_code in [502, 503, 504]:
                    self.log.error('%s: Request Error: %s...retry %d',
                                   req_type, error, retry_num)
                    exeception = error
                else:
                    raise error
            except (Timeout, ConnectionError) as error:
                self.log.error('%s: Request Error: %s...retry %d', req_type,
                               error, retry_num)
                exeception = error


            retry_num += 1
            self.log.error('%s: Request %d - backoff for %d sec', req_type,
                           retry_num, max_delay)
            time.sleep(max_delay)
            max_delay *= self.RETRY_BACKOFF

        if exeception is not None:
            raise exeception
        return response

    def head(self, url, **kwargs):
        ''' Over-ride the head() method
        '''
        return self._make_request('HEAD', url, **kwargs)

    def get(self, url, **kwargs):
        ''' Over-ride the get() method
        '''
        return self._make_request('GET', url, **kwargs)

    def post(self, url, **kwargs):
        ''' Over-ride the post() method
        '''
        return self._make_request('POST', url, **kwargs)

    def put(self, url, **kwargs):
        ''' Over-ride the put() method
        '''
        return self._make_request('PUT', url, **kwargs)

    def patch(self, url, **kwargs):
        ''' Over-ride the patch() method
        '''
        return self._make_request('PATCH', url, **kwargs)

    def delete(self, url, **kwargs):
        ''' Over-ride the delete() method
        '''
        return self._make_request('DELETE', url, **kwargs)
