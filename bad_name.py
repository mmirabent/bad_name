import requests
import xml.etree.ElementTree as ET
import re
import json

################################################################################
# Load the settings from file                                                  #
################################################################################

f = open('settings.json','r')
params = json.load(f)

JSS = params['JSS']
USERNAME = params['USERNAME']
PASSWORD = params['PASSWORD']
JSS_API = '/JSSResource'
GOOD_NAME_REGEX = params['GOOD_NAME_REGEX']

################################################################################
# Functions definitions                                                        #
################################################################################

def assert_response(response, status, msg=""):
    if response.status_code != status:
        print("There was a problem " + msg)
        print("Status code: %d" % response.status_code)
        print(response.text)
        exit(1)

################################################################################
# Check all the names                                                          #
################################################################################

mobile_devices_uri = JSS + JSS_API + '/mobiledevices'
auth_tuple = (USERNAME,PASSWORD)

# Pull a list of ALL the mobile devices
r = requests.get(mobile_devices_uri, auth=auth_tuple, verify=False)

assert_response(r,200, "getting the list of mobile devices")

# This gets the content as raw bytes, before it's encoded (otherwise, etree
# will try to encode it again) and parses it into an ElementTree
root = ET.fromstring(r.content) 

# Compile the good_name regex
good_name = re.compile(GOOD_NAME_REGEX)

# findall makes an array of the mobile devices so we can iterate over them all
for mobile_device in root.findall('mobile_device'):
    
    # find finds the first child by that name, .text returns the text
    name = mobile_device.find('name').text
    
    # Using the compiled good_name regex to match the mobile_device names
    if good_name.match(name):
        root.remove(mobile_device)

# Set bad_names to root for clarity further down in the script
bad_names = root

mobile_device_groups_uri = JSS + JSS_API + '/mobiledevicegroups'

# Get a list of all the mobile device groups
r = requests.get(mobile_device_groups_uri, auth=auth_tuple, verify=False)

assert_response(r,200,"getting list of mobile devide groups")

# parse the xml
groups = ET.fromstring(r.content)

# Set up the variable to hold the bad_name_group
# TODO: Make this better, is there a more "pythonic" way to do this
bad_name_group = None

# Find the "bad names" group and make it bad_name_group
for group in groups.findall('mobile_device_group'):
    if group.find('name').text == "bad names":
        bad_name_group = group
        break

# If we didn't find the droids we were looking for, make one
if bad_name_group == None:
	new_root = ET.Element("mobile_device_group")
	name = ET.Element("name")
	name.text = "bad names"
	new_root.append(name)
	is_smart = ET.Element("is_smart")
	is_smart.text = "false"
	new_root.append(is_smart)
	xml = ET.tostring(new_root)
	r = requests.post(mobile_device_groups_uri + "/id/0", data=xml, auth=auth_tuple, verify=False)
	assert_response(r,201,"creating bad names group")
	print(r.text) # TODO: for debugging only
	bad_name_group = ET.fromstring(r.content)
	print("ID for new group is %s" % bad_name_group.findtext('id'))


# Build the URI for the 'bad names' mobile device groups
bad_names_group_uri = mobile_device_groups_uri + "/id/" + bad_name_group.find('id').text

# Pull the 'bad names' group object itself
r = requests.get(bad_names_group_uri, auth=auth_tuple, verify=False)
assert_response(r,200,"getting the \"bad names\" mobile devide group")

# Parse the xml for the 'bad names' group
print("Text of the bad names group xml")
print(r.text)
bad_name_group = ET.fromstring(r.content)

# Find and remove the mobile_devices object from the bad names group
mobile_devices = bad_name_group.find('mobile_devices')
bad_name_group.remove(mobile_devices)

# Add the bad names to the bad name group
bad_name_group.append(root)

# Make XML document back into a string
#xml = ET.tostring(root)
#print xml
xml = ET.tostring(bad_name_group)
# print xml

# Update the 'bad names' group
r = requests.put(bad_names_group_uri, data=xml, auth=auth_tuple, verify=False)
assert_response(r,201,"updating the \"bad names\" mobile devide group")

print(r.text)

