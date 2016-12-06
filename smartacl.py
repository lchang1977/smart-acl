#!/usr/bin/python
# coding: utf-8
import pyjsonrpc
import logging
import time
import json
import csv
class SmartACL(object):

    def __init__(self):
        self._controller = self.Controller()
	logging.basicConfig(level=logging.DEBUG, format='%(asctime)-15s %(message)s')
        self._controller.call
	self.switch = 1
	self.IP_SRC_INDEX = 4
	#TODO read from file
	self.whitelist = ["10.0.0.1", "10.0.0.2", "10.0.0.3"]
	#Note this is only for datagathering and graph ploting. It is not required for function. Attacks are automatically detected.
	self.attacklist = ["10.0.0.4"]
	self.test_server = ['10.0.0.6']
	#Call REF API for current estimated network throughput
	self.total_bandwidth = 120 #Mbps
	self.old_bandwidth = 0
	self.old_flows = None

	#Use false when only wanting to report network stats
	self.APP_ACTIVE = True

	self.csv_file = open('log-'+str(time.time())+'.csv', 'w')
	self.file_writer = csv.writer(self.csv_file)
	#Calculated from previous experiment
	self.whitelist_bandwidth_requirement = 60 #Mbp
	self.detect_and_protect()

    def detect_and_protect(self):
	'''Primary loop for protecting the network'''
	enforced = False
	while True:
		#Get flows
		print "--------------------------------"
		flows = self._controller.call(method="report_flows", params=[str(self.switch)])
		#Check bandwidth used by whitelisted flows

		#print self._controller.call(method="report_port", params=[False, True, str(self.switch), 1])
		#This needs to be calculated over longer time
		if(self.old_flows):
			current_bandwidth = self.calculate_total_bandwidth_used(flows, self.old_flows)
			logging.debug("Total throughput: %smbps", str(current_bandwidth))
			
			#TODO calculate bandwidth of whitelist, other traffic, and attack traffic.
			whitelist_throughput = self.calculate_whitelist_throughput(flows)
	
			logging.debug("Whitelist throughput: %smbps", str(whitelist_throughput))

			other_throughput = self.calculate_other_throughput(flows)

			logging.debug("Other throughput: %smbps", str(other_throughput))

			attack_throughput = self.get_attack_throughput(flows)
	
			logging.debug("Attack throughput: %smbps", str(attack_throughput))
			#need to be careful to only call this once
			
			#If other traffic > total_bw-whitelist_req then install meters.
			available_bandwidth = self.total_bandwidth - self.whitelist_bandwidth_requirement

			logging.debug("Available bandwidth %s", str(available_bandwidth-other_throughput))

			self.file_writer.writerow([whitelist_throughput, other_throughput, attack_throughput, available_bandwidth])


			if(self.APP_ACTIVE):
				if(other_throughput > self.total_bandwidth - self.whitelist_bandwidth_requirement):
					logging.debug("Warning. Using too much bandwidth!")
				
					if(not enforced):
						self._controller.call(method="enforce_service", params=[str(self.switch), "10.0.0.4", ["10.0.0.6"], 30000])
						enforced=True
			#print flows	


	
		self.old_flows = flows
		time.sleep(2)
	#	print	self._controller.call(method="report_switch_ports", params=[True,True ,str(self.switch)])
#		self._controller.call(method="report_meter_stats", params=[str(self.switch)])
		

#self._controller.call(method="enforce_service", params=[str(switch), src, ip, limit])


    def calculate_total_port_bandwidth(self, ports):
	pass

    def calculate_whitelist_throughput(self, flows):
	throughput = 0
	for flow in flows:
		for aloud_match in self.whitelist:
			match_fields = flow['match']['OFPMatch']['oxm_fields'] 
			if(len(match_fields)>=self.IP_SRC_INDEX):
				#print match_fields[self.IP_SRC_INDEX]
				if(aloud_match in str(match_fields[self.IP_SRC_INDEX]["OXMTlv"]["value"])):
					#TODO if no throughput field calculate it
					if('throughput' in flow):
#						logging.debug("Found match in whitelist")
						throughput += flow['throughput']
					else:
						pass
				#		logging.debug('Warning: no throughput field. Assuming missmatch between old and new flows')
	return throughput

    def calculate_other_throughput(self, flows):
	throughput = 0
	for flow in flows:
		match_fields = flow['match']['OFPMatch']['oxm_fields'] 
		#print "OTHER MATCH FIELDS"
		#print match_fields
		if(len(match_fields)>=self.IP_SRC_INDEX):
			#Check if this not in whitelist
			#print str(match_fields[2]["OXMTlv"]["value"])
			if(str(match_fields[self.IP_SRC_INDEX]["OXMTlv"]["value"]) not in self.whitelist):
				if('throughput' in flow):
#					logging.debug("Found match not in whitelist")
					throughput += flow['throughput']
				else:
					pass
				#	logging.debug('Warning: no throughput field. Assuming missmatch between old and new flows')
					
					
	return throughput

    def get_attack_throughput(self, flows):
	throughput = 0
	for flow in flows:
		for aloud_match in self.attacklist:
			match_fields = flow['match']['OFPMatch']['oxm_fields'] 
			#print "ATTACK MATCH FIELDS"
			#print match_fields
			if(len(match_fields)>=self.IP_SRC_INDEX):
				if(aloud_match in str(match_fields[self.IP_SRC_INDEX ])):
					#print "Attack Flow detected"
					if('throughput' in flow):
						logging.debug("Found match in attack")
						throughput += flow['throughput']
						#print throughput
					else:
						logging.debug('Warning: no throughput field. Assuming missmatch between old and new flows')
				else:
					pass
					#print "WARNING:" + aloud_match + " not in " + str(match_fields[self.IP_SRC_INDEX]) 
			elif('throughput' in flow):
				throughput += flow['throughput']
				#print str(flow)	
	return throughput

    def calculate_total_bandwidth_used(self, flows, old_flows):
	'''This accuracy depends on the switch implementation'''
	current_bandwidth = 0
	for flow in flows:
		old_timen=0
		old_time=0
		for old_flow in old_flows:
			if(flow["match"] == old_flow["match"]):
				#print "CALC :" + str(flow['match'])
				#TODO change when we drop (new flow with the same match field)
				#print "Found a match of packets"
				duration = flow["duration"] - old_flow["duration"]
				delta = (self.diff_time(old_flow["duration"], old_flow["nduration"], flow["duration"], flow["nduration"]))
				
				#TODO check if packet in rule. Ignore this rule
				if(not delta==0):
					flow_bw = (flow["byte_count"]-old_flow["byte_count"])/delta
					flow["throughput"] = (flow_bw/1024/1024)*8
					current_bandwidth += flow_bw
		#		diff_time(flow)


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
