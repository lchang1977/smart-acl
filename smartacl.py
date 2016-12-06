#!/usr/bin/python
# coding: utf-8
import pyjsonrpc
import logging
import time
class SmartACL(object):

    def __init__(self):
        self._controller = self.Controller()
        self._controller.call
	self.switch = 1
	#TODO read from file
	self.whitelist = ["00:00:00:00:00:01", "00:00:00:00:00:02", "00:00:00:00:00:03"]
	#Note this is only for datagathering and graph ploting. It is not required for function. Attacks are automatically detected.
	self.attacklist = []
	#Call REF API for current estimated network throughput
	self.total_speed = 20 #Mbp/s
	self.old_bandwidth = 0
	self.old_flows = None

	#Calculated from previous experiment
	self.whitelist_bandwidth_requirement = 10 #Mbps
	self.detect_and_protect()


    def detect_and_protect(self):
	'''Primary loop for protecting the network'''
	while True:
		#Get flows
		print "Getting flows"
		flows = self._controller.call(method="report_flows", params=[str(self.switch)])
		#Check bandwidth used by whitelisted flows

		print self._controller.call(method="report_port", params=[False, True, str(self.switch), 1])
		#This needs to be calculated over longer time
		if(self.old_flows):
			current_bandwidth = self.calculate_total_bandwidth_used(flows, self.old_flows)
			print "Current bandwidth: " + str(current_bandwidth) + "mbps"
	
		self.old_flows = flows
		print "throughput flows"
		print flows
		time.sleep(2)
	#	print	self._controller.call(method="report_switch_ports", params=[True,True ,str(self.switch)])
#		self._controller.call(method="report_meter_stats", params=[str(self.switch)])
		

#self._controller.call(method="enforce_service", params=[str(switch), src, ip, limit])


    def calculate_total_port_bandwidth(self, ports):
	pass

    def calculate_whitelist_throughput(self):
	pass

    def calculate_other_throughput(self):
	pass

    def get_attack_throughput(self):
	pass

    def calculate_total_bandwidth_used(self, flows, old_flows):
	'''This accuracy depends on the switch implementation'''
	current_bandwidth = 0
	for flow in flows:
		old_timen=0
		old_time=0
		for old_flow in old_flows:
			if(flow["match"] == old_flow["match"]):
				#TODO change when we drop (new flow with the same match field)
				print "Found a match of packets"
				duration = flow["duration"] - old_flow["duration"]
				delta = (self.diff_time(old_flow["duration"], old_flow["nduration"], flow["duration"], flow["nduration"]))
				
		#TODO check if packet in rule. Ignore this rule
				flow_bw = (flow["byte_count"]-old_flow["byte_count"])/delta
				flow["throughtput"] = (flow_bw/1024/1024)*8
				current_bandwidth += flow_bw
		#		diff_time(flow)
		print flow


#	result = current_bandwidth - self.old_bandwidth
#	self.old_bandwidth = current_bandwidth
	result = (current_bandwidth*8)/1024/1024
	return result

    @staticmethod   
    def diff_time (t1_sec, t1_nsec, t2_sec, t2_nsec): 
	def to_float (sec,nsec): 
		return float(sec) + float(nsec)/10E9                                         
	return to_float(t2_sec, t2_nsec) - to_float(t1_sec, t1_nsec)

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
