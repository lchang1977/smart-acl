#!/usr/bin/python
# coding: utf-8

class SmartACL(object):

    def __init__(self, host, port):
        self._controller = self.Controller()
        self._controller.call

	while true:
		#Get flows
				
		self._controller.call(method="report_flow_stats", params=[str(switch)])
		self._controller.call(method="report_meter_stats", params=[str(switch)])
		

#self._controller.call(method="enforce_service", params=[str(switch), src, ip, limit])


    class Controller(object):
        '''Represents all communication with the controller.'''

        def __init__(self):
            '''Connect to the controller.'''
            self._testing = testing
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
