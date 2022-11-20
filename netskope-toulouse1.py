#!/usr/bin/python

import json, sys, argparse, os, httpx, datetime, tarfile, requests, glob, re

# wget --timestamping http://dsi.ut-capitole.fr/blacklists/download/all.tar.gz
# http://dsi.ut-capitole.fr/blacklists/download/blacklists.tar.gz
# http://dsi.ut-capitole.fr/blacklists/download/ads.tar.gz

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--tenant", help="Tenant name. Without '.goskope.com' suffix. Required.", required=True)
parser.add_argument("-k", "--apikey", help="APIv2 key. Required.", required=True)
parser.add_argument("-a", "--action", help="Options to choose from", choices=["test", "prod"], required=True)
parser.add_argument("-v", "--verbose", help="Verbose output", action='store_true')
args = parser.parse_args()

#URLs
if args.action == "test":
	blocklist_url = "http://dsi.ut-capitole.fr/blacklists/download/dating.tar.gz"
else:
	blocklist_url = "http://dsi.ut-capitole.fr/blacklists/download/blacklists.tar.gz"
tenant_url = "https://" + args.tenant + ".goskope.com/api/v2/policy/urllist"
get_url_lists = tenant_url + "?pending=0"
post_file = tenant_url + "/file"
post_deploy = tenant_url + "/deploy"

#Payload
payload={}
headers = { 
	"Netskope-Api-Token": args.apikey,
    "Accept": "application/json",
}

#Global Variables
script_path = os.path.dirname(os.path.abspath(__file__))
temp_path = script_path + "/temp"
data_path = script_path + "/data"
date_now = datetime.datetime.now()
date_time = str(date_now.strftime("%Y%m%d_%H%M"))

#Logging and verbosity
def log_request(request):
	print(f"Request event hook: {request.method} {request.url} - Waiting for response")
def log_response(response):
	request = response.request
	print(f"Response event hook: {request.method} {request.url} - Status {response.status_code}")
if args.verbose:
	http_client = httpx.Client(verify=False, event_hooks={"request": [log_request], "response": [log_response]})
else:
	http_client = httpx.Client(verify=False)

# Verify folders
if os.path.isdir(data_path) == False:
    os.mkdir(data_path)
if os.path.isdir(temp_path) == False:
    os.mkdir(temp_path)

def get_blacklist(arg):
	blocklist_archive = temp_path + '/' + date_time + "_blacklists.gz"
	if args.verbose:
		print("Getting blocklist file from URL " + arg + " and extracting in folder " + temp_path)
	with open(blocklist_archive, 'w+b') as fichier:
		#write file
		with http_client.stream("GET", arg) as raw_blocklist:
			for chunk in raw_blocklist.iter_raw():
				fichier.write(chunk)
			#extract file
	blocklist_file = tarfile.open(blocklist_archive)
	blocklist_file.extractall(temp_path)
	blocklist_file.close()
	if args.verbose:
		print("Done")
	#os.remove() 
	#return file

def create_urllists(): 
	for root, sub_dirs, dir_files in os.walk(temp_path):
		for dir in sub_dirs:
			if args.verbose:
				print('Current directory: ' + dir)
				print('Full path: ' + os.path.join(os.path.abspath(root), dir))
			for file in dir_files:
				if args.verbose:
					print('Current file: ' + file)
				if file == "urls":
					# Si urllist existe, assigner id existant, sinon id= len+1
					with open(file, 'r') as urls_file:
						for url in urls_file:
							with open(data_path + '/' + date_time + '_' + dir + '_' + file + '.json', 'w') as urls_file_json:
								urls_file_json.write('' + '\n')
				if file != "very_restrictive_expression" and file != "usage" and file != "expressions"  and file != "urls":
					with open(file, 'r') as domains_file:
						for domain in domains_file:
							with open(data_path + '/' + date_time + '_' + dir + '_' + file + '.json', 'w') as domains_file_json:
								payload = json.dumps({
									"items": 
									[ 
										{ 
											"name": dir + '_' + file,
											"data": {
												"type": "exact",
												"urls": [
													domain,
													"*.cnav.fr",
													"ringtail.ch"
												], 
											} 
										}
									] 
								})
								domains_file_json.write('' + '\n')

def get_urllist_id(urllist_name):
	if args.verbose:
		print("Searching id for '" + urllist_name + "'  urllist in " + args.tenant + " if it exists ")
	urllist_id = 0
	response = http_client.get(get_url_lists,headers=headers)
	tenant_urllists = json.loads(response.text)
	total_records = len(tenant_urllists)
	for i in range(0,total_records):
		id = str(i+1)
		if tenant_urllists[i]["name"] == urllist_name:
			urllist_id = id
			if args.verbose:
				print("Urllist '" + urllist_name + "'  found in " + args.tenant + " with id=" + urllist_id)
			return urllist_id
	if args.verbose:
		print("Urllist " + urllist_name + " not found in " + args.tenant)
		print(json.dumps(response.json(), indent=4))
	return 0

def send_urllists(tenant):
	print("b")

if __name__ == "__main__":
	if args.action == "test":
		#get_blacklist(blocklist_url)
		#create_urllists()
		print(get_urllist_id("Nike"))
		print(get_urllist_id("Copain"))
	if args.action == "prod":
		get_blacklist(blocklist_url)
		create_urllists()
	# Clear temp folder 


