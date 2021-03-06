# -*- coding: utf-8 -*-

import unittest
from time import sleep
from multiprocessing import Process

from bottle import Bottle, run, response, request


def nicupdate():
    arg_hostname = request.query.hostname
    arg_myip = request.query.myip
    assert len(arg_hostname) > 0
    assert len(arg_myip) > 0
    response.content_type = 'text/plain; charset=utf-8'
    return str("good %s" % arg_myip)


class DyndnsV2App(Bottle):
    '''
    A minimal http server that resembles an actual dyndns service
    '''
    def __init__(self, host='localhost', port=8000):
        super(DyndnsV2App, self).__init__()
        self.host = host
        self.port = port
        self.process = None
        self.route(path='/nic/update', callback=nicupdate)

    def run(self):
        run(self, host=self.host, port=self.port, debug=False, quiet=True)

    def start(self):
        self.process = Process(target=self.run)
        self.process.start()
        # even though I have a super fast quad core cpu, this is not working
        # consistently if we don't sleep here!
        sleep(3.5)

    def stop(self):
        self.process.terminate()
        self.process = None
        #sleep(1)

    @property
    def url(self):
        return 'http://%s:%s' % (self.host, str(self.port))


class DummyUpdaterTests(unittest.TestCase):
    def test_dummy(self):
        import dyndnsc.updater.dummy
        NAME = "dummy"
        theip = "127.0.0.1"
        self.assertEqual(NAME, dyndnsc.updater.dummy.UpdateProtocolDummy.configuration_key())
        updater = dyndnsc.updater.dummy.UpdateProtocolDummy()
        self.assertEqual(str, type(updater.updateUrl()))
        self.assertEqual(theip, updater.update(theip))


class DyndnsV2BottleServerTests(unittest.TestCase):
    def setUp(self):
        """
        Start local server
        """
        import random
        portnumber = random.randint(8000, 8900)
        self.server = DyndnsV2App('127.0.0.1', portnumber)
        self.url = "http://127.0.0.1:%i/nic/update" % portnumber
        self.server.start()
        unittest.TestCase.setUp(self)

    def tearDown(self):
        """
        Stop local server.
        """
        self.server.stop()
        self.server = None
        unittest.TestCase.tearDown(self)

    def test_noip(self):
        import dyndnsc.updater.noip
        NAME = "noip"
        theip = "127.0.0.1"
        options = {"hostname": "no-ip.example.com", "userid": "dummy", "password": "1234"}
        self.assertEqual(NAME, dyndnsc.updater.noip.UpdateProtocolNoip.configuration_key())
        updater = dyndnsc.updater.noip.UpdateProtocolNoip(options)
        updater.updateurl = self.url
        self.assertEqual(str, type(updater.updateUrl()))
        self.assertEqual(self.url, updater.updateUrl())
        res = updater.update(theip)
        self.assertEqual(theip, res)

    def test_dyndns(self):
        import dyndnsc.updater.dyndns
        NAME = "dyndns"
        theip = "127.0.0.1"
        options = {"hostname": "dyndns.example.com", "userid": "dummy", "password": "1234"}
        self.assertEqual(NAME, dyndnsc.updater.dyndns.UpdateProtocolDyndns.configuration_key())
        updater = dyndnsc.updater.dyndns.UpdateProtocolDyndns(options)
        updater.updateurl = self.url
        self.assertEqual(str, type(updater.updateUrl()))
        self.assertEqual(self.url, updater.updateUrl())
        res = updater.update(theip)
        self.assertEqual(theip, res)

    def test_nsupdate_info(self):
        import dyndnsc.updater.nsupdate_info
        NAME = "nsupdate"
        theip = "127.0.0.1"
        options = {"hostname": "nsupdate_info.example.com", "userid": "dummy", "password": "1234"}
        self.assertEqual(NAME, dyndnsc.updater.nsupdate_info.UpdateProtocolNsUpdate.configuration_key())
        updater = dyndnsc.updater.nsupdate_info.UpdateProtocolNsUpdate(options)
        updater.updateurl = self.url
        self.assertEqual(str, type(updater.updateUrl()))
        self.assertEqual(self.url, updater.updateUrl())
        res = updater.update(theip)
        self.assertEqual(theip, res)


if __name__ == '__main__':
    DyndnsV2App('localhost', 8000).run()
