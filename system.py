import json
import subprocess

with open("conf.json", "r") as f:
	conf = json.load(f)
	print(conf)

if conf["pc"]["disable_firewall"]:
	subprocess.check_call('netsh.exe advfirewall set publicprofile state off')
else:
	subprocess.check_call('netsh.exe advfirewall set publicprofile state on')

enet = conf["ethernet"]

subprocess.check_call('netsh interface set interface name="{0}" admin=enabled'.format(enet["lan"]))
subprocess.check_call('netsh interface ip set address "{0}" static {1} {2} {3}'.format(
	enet["lan"], enet["ip"], enet["netmask"], enet["gateway"]))
	
try:
	if "DNS1" in enet and "DNS2" in enet:
		subprocess.check_call('netsh interface ip add dns "{0}" {1}'.format(
			enet["lan"], enet["DNS1"]))
		subprocess.check_call('netsh interface ip add dns "{0}" {1} index=2'.format(
			enet["lan"], enet["DNS2"]))
except Exception:
	pass

