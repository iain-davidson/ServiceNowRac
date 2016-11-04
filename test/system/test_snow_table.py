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

''' Test Table
'''
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../lib'))
import unittest

from ServiceNowRac.snow_client import SnowClient
from ServiceNowRac.snow_table import SnowTable

CONFIG = {
    'host': 'ven01082',
    'user': 'admin',
    'passwd': 'AristaInnovates'
}

# pylint: disable=invalid-name
sys_id = None

class TestSnowTable(unittest.TestCase):
    ''' Tests the ServiceNow table API

        NOTE: Tests are named test_XX_* where XX is a number in
        sequence. This is to keep the order of execution since later
        tests are dependent on the insertion of a record.
    '''
    def setUp(self):
        client = SnowClient(CONFIG['host'],
                            CONFIG['user'],
                            CONFIG['passwd'])
        self.table = SnowTable('incident', client)

    def test_00_insert(self):
        ''' Test insert functionality
            Note: Global sysid is kept for testing 'get' later.
                  Also used to delete later.
        '''
        # pylint: disable=global-statement
        global sys_id

        data = {
            'category'           : 'Request',
            'comments'           : 'This Incident was generated by'
                                   ' ServiceNowRac system test',
            'description'        : 'Test generate Incident',
            'impact'             : '3',
            'priority'           : '3',
            'reason'             : 'Network Requirements',
            'short_description'  : 'Test generate Incident',
            'state'              : 'New',
            'type'               : 'Routine',
        }

        resp = self.table.insert(data)[0]
        self.assertEquals(resp['short_description'], 'Test generate Incident')
        sys_id = resp['sys_id']

    def test_01_get(self):
        ''' Test 'get'' functionality using sysid of previous insert
        '''
        resp = self.table.get(sys_id)
        self.assertEquals(resp['sys_id'], sys_id)

    def test_02_get_bad_return(self):
        ''' Verify NoneType returned on 'get' using invalid sysid
        '''
        sysid = '00112233445566778899abcdefdeadfe'
        data = self.table.get(sysid)
        self.assertEquals(data, None)

    def test_03_get_keys(self):
        ''' Verify 'get_keys' functionality.
        '''
        data = self.table.get_keys('short_description=Test generate Incident')
        self.assertGreater(len(data), 0)

    def test_04_get_records(self):
        ''' Verify 'get_records' functionality
        '''
        data = self.table.get_records('short_description='
                                      'Test generate Incident')
        self.assertGreater(len(data), 0)

    def test_05_update(self):
        ''' Verify 'update' functionality
        '''
        description = 'Test Incident CHANGED'
        data = {
            'short_description'  : description,
        }

        query = 'sys_id=%s' % sys_id
        resp = self.table.update(data, query)[0]
        self.assertEquals(resp['short_description'], description)

    def test_06_delete(self):
        ''' Verify 'delete' functionality using sysid from previous insert
        '''
        data = self.table.delete(sys_id)[0]
        self.assertEquals(data['sys_id'], sys_id)
        resp = self.table.get(sys_id)
        self.assertEquals(resp, None)

    def test_07_insert_multiple(self):
        ''' Verify 'insert_multiple' functionality
        '''
        # { "records" : [ { ... }, { ... } ] }
        #       data = self.table.insert_multiple(data)

    def test_08_delete_multiple(self):
        ''' Verify 'delete_multiple' functionality
        '''
        # data = self.table.delete_multiple('name=Arista Networks')
        # self.assertEquals(len(data), 52)

if __name__ == '__main__':
    unittest.main()
