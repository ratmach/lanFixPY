# -*- coding: utf-8 -*-

import json
import subprocess
import os
from appJar import gui

with open("conf.json", "r") as f:
	conf = json.load(f)
	#print(conf)


def fixFirewall():
	try:
		if conf["pc"]["disable_firewall"]:
			subprocess.check_call('netsh.exe advfirewall set publicprofile state off')
		else:
			subprocess.check_call('netsh.exe advfirewall set publicprofile state on')
	except Exception:
		print("could not disable firewall")
		
def fixEthernet(param=None):
	enet = conf["ethernet"]
	try:
		print('netsh interface set interface name="{0}" admin=enabled'.format(enet["lan"]))
		subprocess.check_call('netsh interface set interface name="{0}" admin=enabled'.format(enet["lan"]))
		print('netsh interface ip set address "{0}" static {1} {2} {3} 1'.format(
			enet["lan"], enet["ip"], enet["netmask"], enet["gateway"]))
		subprocess.check_call('netsh interface ip set address "{0}" static {1} {2} {3} 1'.format(
			enet["lan"], enet["ip"], enet["netmask"], enet["gateway"]))
	except Exception:
		displayError()
	try:
		if "DNS1" in enet and "DNS2" in enet:
			subprocess.check_call('netsh interface ip add dns "{0}" {1}'.format(
				enet["lan"], enet["DNS1"]))
			subprocess.check_call('netsh interface ip add dns "{0}" {1} index=2'.format(
				enet["lan"], enet["DNS2"]))
	except Exception:
		pass

def userExists(username):
	try:
		subprocess.check_call('net user {0}'.format(username))
		return True
	except Exception:
		return False

def fixUsers():
	pc = conf["pc"]
	if(not userExists(pc["user"])):
		subprocess.check_call('net user {0} {1} /ADD'.format(pc["user"], pc["password"]))
		conf["updateRequired"] = True
	else:
		subprocess.check_call('net user {0} {1}'.format(pc["user"], pc["password"]))
	
	try:
		p = subprocess.Popen('hostname', stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
		name = p.communicate()[0].strip()
		if not name == pc["name"]:
			subprocess.check_call("WMIC computersystem where caption='{0}' rename {1}".format(name, pc["name"]))
			conf["updateRequired"] = True
	except Exception:
		pass
	
	try:
		p = subprocess.Popen('net config workstation', stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
		#name = p.communicate()[0].split("Workstation domain")[1].split("\n")[0].strip()
		if not name == pc["workgroup"]:
			subprocess.check_call("Wmic computersystem where name='{0}' call joindomainorworkgroup name={1}".format(name, pc["workgroup"]))
			conf["updateRequired"] = True
	except Exception as e:
		print(e)
	
	
def fixShare():
	for folder in conf["share"]:
		try:
			base = os.path.basename(folder)
			p = subprocess.Popen('net share {0}={1} /GRANT:EVERYONE,FULL'.format(base, folder), stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
		except Exception as e:
			pass
		
def displayError():
	app = gui("დაფიქსირდა პრობლემა", "600x200")
	app.setFont(16)
	app.setBg("red")
	app.addLabel("title", "გთხოვთ დარწმუნდეთ, \n რომ ქსელის კაბელი \n ფიზიკურად მიერთებულია \n კომპიუტერზე და დააჭიროთ ღილაკს გააგრძელე", 0, 0, 2)
	app.addButtons(["გააგრძელე"], fixEthernet, 3, 0, 2)
	app.go()


fixUsers()
fixShare()
fixEthernet()
fixFirewall()

if "updateRequired" in conf:
	print("restart required")
	subprocess.check_call("shutdown -r -t 10")