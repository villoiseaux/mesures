#!/usr/bin/python
# File created by adm on host labo32 (id="007f0101")
# Sun  5 Feb 17:53:02 CET 2023

import serial
import sys
import io
import os
import re
import time
import usbtmc
import struct
import pylab
import matplotlib.pyplot as plt
import math

# acruacy (step within 10th)
ACR=1
# Magnitude
MAG=7
# Tension IN (V)
UIN=10

def listDevices(idnTemplate):
	ports = []
	correctPorts = []

# List all serial ACM port
	for entry in os.listdir(r'/dev'):
		if (re.search(r"^ttyACM.*$",entry)):
			ports.append(entry)

# Check the port with correct 'IDN'
	for port in ports:
		device=serial.Serial(
			port='/dev/'+port,\
			baudrate=115200)
		device.write(b'*IDN?\n') 
		line=device.readline().decode()
		if (re.search(idnTemplate,line)):
			correctPorts.append(port)
		device.close()
	return correctPorts


def resetDevice(port):
	if (port.isOpen()):
		port.write(b'*RST\n')
		return 0
	else:
		sys.stderr.write ("ERROR: try to work on close port "+port.name()+"\n")
		return -1

def getDiviceId(port):
	if (port.isOpen()):
		port.write(b'*IDN?\n')
		line=port.readline().decode()
		return line
	else:
		sys.stderr.write ("ERROR: try to work on close port "+port.name()+"\n")
		return -1

def applyCommand(port,command):
	#print (command)
	port.write(command+b'\n')

# First check user is root

if (os.geteuid()!=0):
	sys.stderr.write ("This command require root privileges. Try sudo.\n")
	exit (-3)

sys.stderr.write ("\n+--------------+\n")
sys.stderr.write ("|Setup         |\n")
sys.stderr.write ("+--------------+\n\n")
	
sys.stderr.write ("Locate the function generator:\n")

portList=listDevices(r"^GW INSTEK.*")

nbPorts=len(portList)
if (nbPorts<1):
	sys.stderr.write ("ERROR: No GW INSTEK device found\n")
	exit (-1)
else:
	if (nbPorts>1):
		sys.stderr.write ("ERROR: Too many ports\n")
		exit (-2)
	else:
		geneFunct=serial.Serial(port="/dev/"+portList[0], baudrate=115200)
		resetDevice(geneFunct)
		sys.stderr.write ("\tFunction generator \""+getDiviceId(geneFunct).rstrip()+"\" ready as \""+"/dev/"+portList[0]+"\"\n")
		

sys.stderr.write ("Locate the multimetre:\n")
instr =  usbtmc.Instrument("USB::0x5345::0x1234::INSTR")
instr.ask("*RST");
sys.stderr.write("\tMultimetre \""+instr.ask("*IDN?")+"\" ready as \"USB::0x5345::0x1234::INSTR\".\n")

sys.stderr.write ("\n+---------------+\n")
sys.stderr.write ("|Start measures |\n")
sys.stderr.write ("+---------------+\n\n")

sys.stderr.write ("# Set signal\n")

applyCommand(geneFunct,b'SOURCE1:APPLY:SIN 50,5')
sys.stderr.write ("* SIN\n* 50 Hz\n* 5 Vpp\n\n")

sys.stderr.write ("# check signal\n")
instr.ask("VOLT:AC:RANGE 6")
instr.ask("SENS:FUNC2 \"FREQ\"")
time.sleep(2)

reqF=[]
valU=[]
valF=[]
gain=[]

UI=UIN/math.sqrt(2)
of=open('output.csv', 'w')

for fo in range (-1,MAG,1):
	for fin in range (1,10,ACR):
		fr=fin*10**fo
		print ("Set frequency :"+str(fr)+" Hz")
		applyCommand(geneFunct,bytes('SOURCE1:APPLY:SIN '+str(fr)+","+str(UIN),'ascii'))
		time.sleep(8)
		u=float(instr.ask("MEAS1?"))
		f=float(instr.ask("MEAS2?"))
		if (u>0):
			reqF.append(fr)
			valU.append(u)
			valF.append(fr)
			gain.append(20*math.log10(u/UI))
		print (fr,UI,u,f,sep=',')
		of.write(str(fr)+","+str(UI)+","+str(u)+","+str(f)+"\n")

of.close()

plt.plot(reqF,gain)
plt.xscale('log',base=10) 
plt.xlabel('appliquée Hz')
plt.ylabel('gain dB')
plt.title("Gain en tension "+str(UIN)+"V ")
plt.show()

