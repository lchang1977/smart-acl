#!/usr/bin/python
# coding: utf-8
import pyjsonrpc
import logging
class SmartACL(object):

    def __init__(self):
        self._controller = self.Controller()
        self._controller.call
	self.switch = 1

	while True:
		#Get flows
		print "Getting flows"
		self._controller.call(method="report_flow_stats", params=[str(self.switch)])
		self._controller.call(method="report_meter_stats", params=[str(self.switch)])
		

#self._controller.call(method="enforce_service", params=[str(switch), src, ip, limit])


    class Controller(object):
        '''Represents all communication with the controller.'''

        def __init__(self):
            '''Connect to the controller.'''
            self._client = pyjsonrpc.HttpClient(url = "http://localhost:4000/jsonrpc")

        def call(self, **kwargs):
            '''Make a call to the controller.'''
            result = None
            logging.debug('[controller][call]: %s', kwargs)
            try:
                result = self._client.call(kwargs['method'], *kwargs['params'])
            except pyjsonrpc.rpcerror.InternalError as e:
                print e, kwargs
                logging.debug('[controller][result]: %s', result)
            return result

SmartACL()
