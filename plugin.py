########################################################################################
# 	Domoticz Tuya Smart Plug Python Plugin                                       	   #
#                                                                                      #
# 	MIT License                                                                        #
#                                                                                      #
#	Copyright (c) 2018 tixi                                                            #
#                                                                                      #
#	Permission is hereby granted, free of charge, to any person obtaining a copy       #
#	of this software and associated documentation files (the "Software"), to deal      #
#	in the Software without restriction, including without limitation the rights       #
#	to use, copy, modify, merge, publish, distribute, sublicense, and/or sell          #
#	copies of the Software, and to permit persons to whom the Software is              #
#	furnished to do so, subject to the following conditions:                           #
#                                                                                      #
#	The above copyright notice and this permission notice shall be included in all     #
#	copies or substantial portions of the Software.                                    #
#                                                                                      #
#	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR         #
#	IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,           #
#	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE        #
#	AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER             #
#	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,      #
#	OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE      #
#	SOFTWARE.                                                                          #
#                                                                                      #
########################################################################################


"""
<plugin key="sinopsys_tuya_smartplug_plugin" name="Tuya SmartPlug Config (simplified)" author="tixi_sincze" version="1.0.0" externallink=" https://github.com/sinopsys/Domoticz-Tuya-SmartPlug-Plugin">
	<params>
		<param field="Address" label="IP address" width="200px" required="true"/>
		<param field="Mode1" label="DevID" width="200px" required="true"/>
		<param field="Mode2" label="Local Key" width="200px" required="true"/>
		<param field="Mode3" label="DPS" width="200px" required="true" default="1"/>
		<param field="Mode4" label="ID Status;Amp;Watt;Volt" width="200px" required="true" default="1;4;5;6"/>
		<param field="Mode5" label="Debug" width="75px">
			<options>
				<option label="None"   value="0" default="true"/>
				<option label="Full"   value="1"/>
				<option label="Plugin"   value="2"/>
				<option label="Framework"   value="4"/>
				<option label="Devices"   value="8"/>
				<option label="Connections"  value="16"/>
				<option label="Images"  value="32"/>
				<option label="I/O"  value="64"/>
				<option label="MessageQ" value="128"/>
			</options>
		</param>
	</params>
</plugin>
"""



# https://wiki.domoticz.com/wiki/Developing_a_Python_plugin
# Debugging
# Value 	Meaning
# 0 		None. All Python and framework debugging is disabled.
# 1 		All. Very verbose log from plugin framework and plugin debug messages.
# 2 		Mask value. Shows messages from Plugin Domoticz.Debug() calls only.
# 4 		Mask Value. Shows high level framework messages only about major the plugin.
# 8 		Mask Value. Shows plugin framework debug messages related to Devices objects.
# 16 		Mask Value. Shows plugin framework debug messages related to Connections objects.
# 32 		Mask Value. Shows plugin framework debug messages related to Images objects.
# 64 		Mask Value. Dumps contents of inbound and outbound data from Connection objects.
# 128 		Mask Value. Shows plugin framework debug messages related to the message queue. 

import Domoticz
import pytuya
import json

########################################################################################
#
# plugin object
#
########################################################################################
class BasePlugin:
	
	#######################################################################
	#
	# constant definition
	#
	#######################################################################
	__HB_BASE_FREQ = 2			  #heartbeat frequency (val x 10 seconds)
	__VALID_CMD    = ('On','Off') #list of valid command
	_IDX_SWITCH		= 0
	_IDX_AMP		= 1
	_IDX_WATT		= 2
	_IDX_VOLT		=3


	#######################################################################
	#
	# constructor
	#
	#######################################################################
	def __init__(self):
		self.__address          = None          		#IP address of the smartplug
		self.__devID            = None          		#devID of the smartplug
		self.__localKey         = None          		#localKey of the smartplug
		self.__device           = None          		#pytuya object of the smartplug
		self.__status			= None					#key for status
		self.__ampere	        = None					#key for Ampere
		self.__watt             = None					#key for Watt
		self.__voltage          = None					#key for Voltage
		self.__runAgain         = self.__HB_BASE_FREQ	#heartbeat frequency
		return
		
	#######################################################################
	#		
	# onStart Domoticz function
	#
	#######################################################################
	def onStart(self):
		
		# Debug mode
		Domoticz.Debugging(int(Parameters["Mode5"]))
		Domoticz.Debug("onStart called")
			
		#get parameters
		self.__address  = Parameters["Address"]
		self.__devID    = Parameters["Mode1"]
		self.__localKey = Parameters["Mode2"]
		self.__status, self.__ampere, self.__watt, self.__voltage = Parameters["Mode4"].split(";")
		
		#set the next heartbeat
		self.__runAgain = self.__HB_BASE_FREQ
		
		#build internal maps (__unit2dps_id_list and __plugs)
		self.__unit2dps_id_list = {}
		max_unit                = 0
		max_dps					= 0
		needs_create				= len(Devices) == 0
		for val in sorted(list(map(int, Parameters["Mode3"].split(";")))):
			baseunit = val * 10
			devs = [
				{ "Name": "Tuya SmartPlug (Switch)"	, "UnitIdx": self._IDX_SWITCH	, "TypeName": "Switch"},
				{ "Name": "Tuya SmartPlug (A)" 		, "UnitIdx": self._IDX_AMP		, "TypeName": "Current (Single)"},
				{ "Name": "Tuya SmartPlug (kWh)"	, "UnitIdx": self._IDX_WATT		, "TypeName": "kWh"},
				{ "Name":"Tuya SmartPlug (V)"		, "UnitIdx": self._IDX_VOLT		, "TypeName": "Voltage"}
			]
			# create domoticz devices
			if (len(Devices) == 0):
				for d in devs:
					Domoticz.Device(Name=d["Name"], Unit= baseunit + d["UnitIdx"], TypeName=d["TypeName"]).Create()
					Domoticz.Log("{} #{}".format(d["Name"], val))

		#create the pytuya object
		self.__device = pytuya.OutletDevice(self.__devID, self.__address, self.__localKey)

	#######################################################################
	#		
	# onConnect Domoticz function
	#
	#######################################################################
	def onConnect(self, Connection, Status, Description):
		Domoticz.Debug("onConnect called")


	#######################################################################
	#		
	# onMessage Domoticz function
	#
	#######################################################################
	def onMessage(self, Connection, Data):
		Domoticz.Debug("onMessage called")

	#######################################################################
	#		
	# onCommand Domoticz function
	#
	#######################################################################
	def onCommand(self, Unit, Command, Level, Hue):
		Domoticz.Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + " Level: " + str(Level))
		
		if(Command not in self.__VALID_CMD):
			Domoticz.Error("Undefined command: " + Command)
			return
		newstatus = (Command == "On")
		self.__device.set_status(newstatus, int((Unit - (Unit % 10)) / 10))
		Devices[Unit].Update(nValue = 1 if newstatus else 0, sValue = Command)		

	#######################################################################
	#		
	# onDisconnect Domoticz function
	#
	#######################################################################
	def onDisconnect(self, Connection):
		Domoticz.Debug("onDisconnect called")

	#######################################################################
	#		
	# onHeartbeat Domoticz function
	#
	#######################################################################
	def onHeartbeat(self):
		Domoticz.Debug("onHeartbeat called ({})".format(self.__runAgain))
		self.__runAgain -= 1
		if self.__runAgain == 0:
			Domoticz.Debug("update status")

			data = self.__device.status()
			Domoticz.Debug("status is : %r" % data)

			states = data["dps"]
			if not isinstance(states, list):
				states = [states]
				
			for dps, d in enumerate(states, start=1):
				self._updateStatus(dps, d)

			self.__runAgain = self.__HB_BASE_FREQ

	def _updateStatus(self, dps, state):
				baseidx = dps * 10
				status = 1 if state[str(self.__status)] else 0
				if status != Devices[baseidx + self._IDX_SWITCH].nValue:
					Devices[baseidx + self._IDX_SWITCH].Update(nValue = status, sValue = "On" if status else "Off")
					Domoticz.Debug("Sync device " + str(baseidx + self._IDX_SWITCH))

				Devices[baseidx + self._IDX_AMP].Update(status, str(state[str(self.__ampere)] / 1000))  # TypeName="Current (Single)
				Devices[baseidx + self._IDX_WATT].Update(status, str(state[str(self.__watt)] / 10) + ";0")  # kWh / Calculated
				Devices[baseidx + self._IDX_VOLT].Update(status, str(state[str(self.__voltage)] / 10))  # TypeName="Voltage"

				Domoticz.Debug("Updated: " + str(state[str(self.__ampere)] / 1000) + " Ampere Key is:" + str(baseidx + self._IDX_AMP))
				Domoticz.Debug("Updated: " + str(state[str(self.__watt)] / 10) + " Watt Key is:" + str(baseidx + self._IDX_WATT))
				Domoticz.Debug("Updated: " + str(state[str(self.__voltage)] / 10) + " Voltage Key is:" + str(baseidx + self._IDX_VOLT))

	#######################################################################
	#		
	# onStop Domoticz function
	#
	#######################################################################
	def onStop(self):
		self.__device           = None

########################################################################################
#
# Domoticz plugin management
#
########################################################################################
global _plugin
_plugin = BasePlugin()

def onStart():
	global _plugin
	_plugin.onStart()

def onStop():
	global _plugin
	_plugin.onStop()

def onConnect(Connection, Status, Description):
	global _plugin
	_plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
	global _plugin
	_plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
	global _plugin
	_plugin.onCommand(Unit, Command, Level, Hue)

def onDisconnect(Connection):
	global _plugin
	_plugin.onDisconnect(Connection)

def onHeartbeat():
	global _plugin
	_plugin.onHeartbeat()

################################################################################
# Generic helper functions
################################################################################

def UpdateDevice(Unit, nValue, sValue, TimedOut=0, AlwaysUpdate=False):
	# Make sure that the Domoticz device still exists (they can be deleted) before updating it
	if Unit in Devices:
		if Devices[Unit].nValue != nValue or Devices[Unit].sValue != sValue or Devices[Unit].TimedOut != TimedOut or AlwaysUpdate:
			Devices[Unit].Update(nValue=nValue, sValue=str(sValue), TimedOut=TimedOut)
			Domoticz.Debug("Update " + Devices[Unit].Name + ": " + str(nValue) + " - '" + str(sValue) + "'")
