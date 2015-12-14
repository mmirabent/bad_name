import requests
import xml.etree.ElementTree as ET
import re
import json


f = open('settings.json','r')
params = json.load(f)

JSS = params['JSS']
USERNAME = params['USERNAME']
PASSWORD = params['PASSWORD']
JSS_API = '/JSSResource'
GOOD_NAME_REGEX = params['GOOD_NAME_REGEX']

################################################################################
# Do not edit below this line                                                  #
################################################################################

good_name = re.compile(GOOD_NAME_REGEX)

mobile_devices_uri = JSS + JSS_API + '/mobiledevices'
auth_tuple = (USERNAME,PASSWORD)

# Pull a list of ALL the mobile devices
r = requests.get(mobile_devices_uri, auth=auth_tuple, verify=False)

# This gets the content as raw bytes, before it's encoded (otherwise, etree
# will try to encode it again) and parses it into an ElementTree
root = ET.fromstring(r.content) 

# findall makes an array of the mobile devices so we can iterate over them all
for mobile_device in root.findall('mobile_device'):
    
    # find finds the first child by that name, .text returns the text
    name = mobile_device.find('name').text
    
    # Using the compiled good_name regex to match the mobile_device names
    if good_name.match(name):
        root.remove(mobile_device)

# At this point, root is the root of an element tree with all the bad names in it, so now we update the bad_names group

mobile_device_groups_uri = 'https://mdm.pacehs.com:8443/JSSResource/mobiledevicegroups'

# Get a list of all the mobile device groups
r = requests.get(mobile_device_groups_uri, auth=auth_tuple, verify=False)

# TODO: Check for a good response

# parse the xml
groups = ET.fromstring(r.content)

# Set up the variable to hold the bad_name_group
# TODO: Make this better, is there a more "pythonic" way to do this
bad_name_group = ET.Element('dummy')

# Find the "bad names" group and make it bad_name_group
for group in groups.findall('mobile_device_group'):
    if group.find('name').text == "bad names":
        bad_name_group = group
        break

# Build the URI for the 'bad names' mobile device groups
bad_names_group_uri = mobile_device_groups_uri + "/id/" + bad_name_group.find('id').text

# Pull the 'bad names' group object itself
r = requests.get(bad_names_group_uri, auth=auth_tuple, verify=False)

# Parse the xml for the 'bad names' group
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

# print r.status_code
# print r.text
