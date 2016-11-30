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
# 'AS IS' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
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
''' System Tests for Client
'''
import unittest

from ServiceNowRac.snow_client import SnowClient

from test.system.config import CONFIG


DATA = {
    'category'           : 'Request',
    'comments'           : 'This Incident was generated by'
                           ' ServiceNowRac system test',
    'description'        : 'Test generate Incident',
    'priority'           : '3',
    'impact'             : '3',
    'short_description'  : 'Test generate Incident',
    'reason'             : 'Network Requirements',
    'type'               : 'Routine',
    'state'              : 'New',
}


class TestSnowClient(unittest.TestCase):
    ''' Tests the ServiceNow Client using the common 'incident' table
    '''
    def setUp(self):
        self.client = SnowClient(CONFIG['host'],
                                 CONFIG['user'],
                                 CONFIG['passwd'])

    def test_00_post_get(self):
        ''' Test and verify 'post' and 'get' operation.

            Create incident, verify, delete, and verify deletion
        '''
        resp = self.client.post('incident', 'sysparm_action=insert', DATA)
        self.assertNotEqual(resp, None)
        self.assertIsInstance(resp, list)
        self.assertEqual(len(resp), 1)
        sys_id = resp[0]['sys_id']
        resp = self.client.post('incident', 'sysparm_action=deleteRecord',
                                {'sysparm_sys_id' : sys_id})
        self.assertNotEqual(resp, None)
        self.assertIsInstance(resp, list)
        self.assertEqual(resp[0]['sys_id'], sys_id)
        resp = self.client.get('incident', 'sysparm_sys_id=%s' % sys_id)
        self.assertIsInstance(resp, list)
        self.assertEqual(len(resp), 0)

    def test_01_get_302(self):
        ''' Verify 'get' error handling of HTTP status 302
        '''
        client = SnowClient(CONFIG['host'],
                            CONFIG['user'],
                            CONFIG['passwd'],
                            api='')

        resp = client.get('incident', 'sysparm_sys_id='
                          '9c573169c611228700193229fff72400')
        self.assertEqual(resp, None)

    def test_02_get_json_ret_error(self):
        ''' Verify 'get' handling of json error status
        '''
        data = self.client.get('incident', 'sysparm_action=dummy')
        self.assertEqual(data, None)

    def test_03_get_json_no_record(self):
        ''' Verify 'get' handling of no record in json
        '''
        data = self.client.get('incident', 'sysparm_action=get')
        self.assertEqual(data, None)

    def test_04_post_no_payload(self):
        ''' Verify 'post' error handling when no payload provided
        '''
        payload = None
        resp = self.client.post('incident', 'sysparm_action=insert',
                                payload)
        self.assertEqual(resp, None)

    def test_05_post_302(self):
        ''' Verify 'post' error handling of HTTP status 302
        '''
        client = SnowClient(CONFIG['host'],
                            CONFIG['user'],
                            CONFIG['passwd'],
                            api='')

        resp = client.post('incident', 'sysparm_action=insert', DATA)
        self.assertEqual(resp, None)

    def test_06_post_json_ret_error(self):
        ''' Verify 'post' error handling of json return status
        '''
        payload = {}
        resp = self.client.post('incident', 'sysparm_action=dummy',
                                payload)
        self.assertEqual(resp, None)

if __name__ == '__main__':
    unittest.main()
