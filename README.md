# Bad Names

In order to make this work, you need to add a `settings.json` file to the base
directory that has at least these contents

    {
        "USERNAME": "",
        "PASSWORD": "",
        "GOOD_NAME_REGEX": "[a-zA-Z]+[0-9]{5}",
        "JSS": "https://mdm.example.com:8443"
    }
 
 This is parsed by the script to determine the appropriate credentials to use,
 which JSS to contact and what qualifies as a good name

 The script will use the above params to determine the mobiledevices with bad names
 and put them into a group names "bad names"

