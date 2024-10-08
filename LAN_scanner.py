import struct
import os
from sys import platform
import socket
from colorama import Fore, Style
import threading
import time
import uuid
from icmplib import ping
import sys
threads_limit = 100 # Ограничение потоков
total = 1
ip_mac=[[0 for a in range(-1,1)] for b in range(1)]

def ip_key(ip):
    return struct.unpack("!I", socket.inet_aton(ip))[0]

class ProgressBar:
    def __init__(self, total):
        self.total = total
        self.progress = 0

    def next(self):
        if self.progress < self.total:
            self.progress += 1
            self.show()

    def show(self):
        percent = (self.progress / self.total) * 100
        bar_length = 23
        filled_length = int(bar_length * self.progress // self.total)
        bar = (Fore.GREEN+'#'+Style.RESET_ALL) * filled_length + '-' * (bar_length - filled_length)
        sys.stdout.write(f'\r[{bar}] {percent:.2f}%')
        sys.stdout.flush()

    def clear(self):
        sys.stdout.write('\r' + ' ' * (50 + 20) + '\r')  # Очистка строки
        sys.stdout.flush()

def OS_NAME():
	if (platform == "linux" or platform == "linux2"):
		ping_com = "ping -c 1 "
		os.system("clear")
		return "linux", ping_com
	elif platform == "darwin":
		ping_com = "ping -c 1 "
		os.system("clear")
		return "MAC OS", ping_com
	elif platform == "win32":
		ping_com = "ping -n 1 "
		os.system("cls")
		return "WINDOWS", ping_com
def add_ip(ip, total):
	global ip_mac
	ip_mac.append([0]*2)
	ip_mac[total][0] = ip

def beautiful_print(ip_mac, ip):
	for i in ip_mac:
		if(i[0] != ip):
			max_len_ip = 15
			space = max_len_ip - len(i[0])
			print(Fore.GREEN + str(i[0]) + ' '*space + " => is available" + ' '*3 + Fore.WHITE + "MAC: " + str(i[1]) + Style.RESET_ALL)
			time.sleep(0.02)
def SCAN_IP(i, j):
	global total
	p = '.'
	flag = 0
	need_ip = ip_split[0] + p + ip_split[1] + p + str(i) + p + str(j)
	host = ping(need_ip, count=1, interval=0.2)
	if(host.is_alive):
		add_ip(need_ip, total)
		total += 1

def find_mac(os_name):
	global ip_mac
	global total
	if(os_name == "MAC OS"):
		arp = os.popen("arp -a")
		arp = arp.read()
		for i in range(1, total):
			mac = ""
			mac_len = 0
			skip = arp.find(ip_mac[i][0])
			mac_skip = arp.find("at", skip) + 3
			if(mac_skip + mac_len < len(arp)):
				while(arp[mac_skip + mac_len] != ' '):
					mac += arp[mac_skip + mac_len]
					mac_len += 1
				ip_mac[i][1] = mac
	elif(os_name == "WINDOWS" or os_name == "linux"):
		arp = os.popen("arp -a")
		arp = arp.read()
		for i in range(1, total):
			mac = ""
			mac_len = 0
			skip = arp.find(ip_mac[i][0])
			mac_skip = 0
			while(arp[mac_skip + mac_skip] == ' '):
				mac_skip += 1
			while(arp[mac_skip + mac_skip] != ' '):
				mac += arp[mac_skip + mac_len]
				mac_len += 1
	else:
		print("ERROR unknown OS!")
		exit(0)
	ip_mac.sort(key=lambda x: ip_key(x[0]))
print("Choose your mode!")
print("""subnet mask
1) 24 -- 255.255.255.0
2) 20 -- 255.255.240.0
3) 16 -- 255.255.0.0""")
while(True):
	mode = int(input("=> "))
	if(mode != 1, 2):
		break
if(mode == 1):mode=8
if(mode == 2):mode=12
if(mode == 3):mode=16
start_time = time.time()
ip = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ip.connect(("8.8.8.8", 80))
ip = ip.getsockname()[0]
ip_mac[0][0] = ip
os_name, ping_com = OS_NAME()
print(Fore.GREEN + "PROGRAM START" + Style.RESET_ALL)
print("-"*25 + f"\nIP: {ip}")
print(f"OS: {os_name}")
print('-'*25)
ip_split = ip.split('.')

threads = []*threads_limit
count = 0

max = 2**mode-2
patrs = -(-max//25)
bar = ProgressBar(max)
bar.show()
for i in range(0, int((2**mode)/256)):
	for j in range(1, 255):
		try:
			if(((i == int(ip_split[2])) and (j == int(ip_split[3]))) or ((mode <= 8) and (j == int(ip_split[3])))):
				bar.next()
				continue
			if(len(threads) % threads_limit == 0):
				save_len = len(threads)
				help_arr = threads
				for thread in help_arr:
					if(thread.is_alive() == 0):
						threads.remove(thread)
				if(len(threads) == save_len):
					for thread in threads:
						if(thread.is_alive() == 1):
							thread.join()
							threads.remove(thread)
							break
					for thread in threads:
						if(thread.is_alive() == 0):
							threads.remove(thread)
				count = 0
			if(mode <= 8):
				i = ip_split[2]
			flow = threading.Thread(target=SCAN_IP, args=[i, j])
			flow.start()
			time.sleep(0.001)
			bar.next()
			threads.append(flow)
			count += 1
		except ValueError:
			print('')

while(True):
	for thread in threads:
		if(thread.is_alive() == 0):
			bar.next()
			threads.remove(thread)
	if(not(len(threads))):
		bar.clear()
		find_mac(os_name)
		beautiful_print(ip_mac, ip)
		stop_time = time.time()
		result_time = round(stop_time - start_time, 3)
		print(f"Time: {result_time}\nTotal: {total-1}")
		timeout = input("\nPRESS ENTER TO CLOSE...")
		break
