def content_check_hostname4(nb_device):
    import re

    hostname = nb_device.name
    nb_site = nb_device.site.slug # Not to be confused with the 'site' field below. This is the site the device is associated with on NB. 

    print(f"Evaluating {hostname} under hostname4")
    fields = hostname.split("-") # Breaks the hostname into multiple hyphenated fields. 

    site = fields[0] # Not to be confused with the 'nb_site' above. This is the 'site' field of the hostname. 
    location = str(fields[1])
    rack = fields[2]
    device_type = fields[3]

    # Check 'site' field
    if site == nb_site:
        print(f"Succeeded site field parsing. Expected site field: {nb_site}, Parsed site field: {site}")
        pass
    else:
        return(False, f"Failed site field parsing. Expected site field: {nb_site}, Parsed site field: {site}")

    # Check 'location' field
    match = re.match(r'fl\d\d', location, re.I)
    
    print(f"Evaluating {hostname} location: {location}")
    print(type(location))
    print(match)

    if match:
        print("Succeeded location field parsing.")
        pass
    else:
        print(f"Failed location field parsing.")
        return(False, "Failed location field parsing")

    # Check 'rack' field
    match = re.match(r'nr\d\d', rack, re.I)
    if match:
        pass
    else:
        return(False, "Failed rack field parsing")
    
    # Check 'device_type' field
    match = re.match(r'sw|ds|vsw|vds|rt|ups|ap|fw\d\d', device_type, re.I)
    if match:
        pass
    else:
        return(False, "Failed device_type field parsing")
    
    # All fields succeed, return success with no 'fail reason'
    return(True, "")
               
def content_check_hostname5(nb_device):
    import re

    hostname = nb_device.name
    nb_site = nb_device.site.slug # Not to be confused with the 'site' field below. This is the site the device is associated with on NB. 
    print(f"Evaluating {hostname} under hostname5")
    fields = hostname.split("-") # Breaks the hostname into multiple hyphenated fields. 

    site = fields[0] # Not to be confused with the 'nb_site' above. This is the 'site' field of the hostname. #TODO: This should be the first 3 hyphenated fields. 
    building = fields[1]
    location = fields[2]
    rack = fields[3]
    device_type = fields[4]

    # Check 'site' field
    if site == nb_site:
        print(f"Succeeded site field parsing. Expected site field: {nb_site}, Parsed site field: {site}")
        pass
    else:
        return(False, f"Failed site field parsing. Expected site field: {nb_site}, Parsed site field: {site}")

    # Check 'building' field. Note that this regex is just checking to make sure that there are NO numbers in this field. 
    match = re.match(r"^[^0-9]+$", building, re.I)
    if match:
        print(f"Building check passed for {hostname}")
        pass
    else:
        return(False, "Failed building field parsing")    
    
    # Check 'location' field
    match = re.match(r"fl\d\d", location, re.I)
    if match:
        print(f"Location check passed for {hostname}")
        pass
    else:
        return(False, "Failed location field parsing")

    # Check 'rack' field
    match = re.match(r"nr\d\d", rack, re.I)
    if match:
        print(f"Rack check passed for {hostname}")
        pass
    else:
        return(False, "Failed location field parsing")
    
    # Check 'device_type' field
    match = re.match(r"sw|ds|rt|ups|ap|fw\d\d", device_type, re.I)
    if match:
        print(f"Device_type check passed for {hostname}")
        pass
    else:
        return(False, "Failed device_type field parsing")
    
    # All fields succeed, return success with no 'fail reason'
    print(f"All checks passed for {hostname}")
    return(True, "")

def hostname_check(nb_device) -> tuple:
        """
        This function is used to verify that the device's hostname matches our naming standard through a series of automated checks. 

        Returns a tuple with pass/fail result and a reason for any failures. 

        Tuple format: [TRUE/FALSE, reason]

        """        
        
        hostname = nb_device.name
        name_hyphen_check = hostname.split("-") # Split the hostname into multiple hyphenated fields. 
        hyphen_check_bool = False # Used for checking how many hyphenated fields are in the name. 
        name_test_bool = False # Used for checking if the name matches a standard regex after hyphen_check_bool passes
        reason = "" # Used to describe what check the hostname failed for further processing, if desired. 

        # --- This section is for checking hyphenated fields --- #

        if len(name_hyphen_check) <= 3:
            reason = f"Failed due to not enough hyphenated fields in hostname"
            return(name_test_bool, reason)   

        if len(name_hyphen_check) >= 6:
            reason = f"Failed due to too many hyphenated fields in hostname"
            return(name_test_bool, reason)   

        if len(name_hyphen_check) == 4 or len(name_hyphen_check) == 5:
            hyphen_check_bool = True
        
        # --- This section is for checking the hostname to see if the content matches our standards --- #            

        if hyphen_check_bool == True:
            if len(name_hyphen_check) == 4:
                name_test_bool, reason = content_check_hostname4(nb_device)
                return(name_test_bool, reason)
            

            elif len(name_hyphen_check) == 5:
                name_test_bool, reason = content_check_hostname5(nb_device)
                return(name_test_bool, reason)    
        
        else:
            print(f"Hostname {hostname} failed hyphen_check_bool")
            return(name_test_bool, reason) 

def nb_verify_hostnames():
    """
    This script is meant to iterate through all production devices in Netbox and verify that their hostname is configured per our standard. 

    It is intended to be ran on a scheduled basis and email a .CSV report and/or report to a Solarwinds dashboard. 
    """
    import csv
    import os
    import pynetbox
    from logger import myLogger
    from dotenv import load_dotenv
    from _emailer import emailer

    logger = myLogger(__name__) # Initialize a logging object. 
    load_dotenv() # Loads all environment variables including the local .env file. 
    
    netbox_access_token = os.environ.get('NETBOX-ACCESS-TOKEN')
    netbox_url = os.environ.get('NETBOX-URL')

    nb = pynetbox.api(netbox_url, token=netbox_access_token) 

    nb_devices = nb.dcim.devices.all()
    
    with open('./reporting/validated-hostnames.csv', 'w+', encoding='UTF8', newline='') as s_f:
        fieldnames = ['device-name']
        succeed_writer = csv.writer(s_f) # creates the 'writer' object we can use below. 
        succeed_writer.writerow(fieldnames) # write the header names. 
        
        with open('./reporting/failed-hostnames.csv', 'w+', encoding='UTF8', newline='') as f_f:
            fail_fieldnames = ['device-name', 'failure-reason']
            fail_writer = csv.writer(f_f) # creates the 'writer' object we can use below. 
            fail_writer.writerow(fail_fieldnames) # write the header names. 
        
            for nb_device in nb_devices:
                if 'production-' in nb_device.device_role.slug: # Only filtering for production devices, so backstock/inventory isn't evaluated. 
                    print(f"Evaluating {nb_device.name}")
                    name_test_bool, reason = hostname_check(nb_device)
                    print(f"Done evaluating {nb_device.name}: BOOL: {name_test_bool}, REASON: {reason}")

                    if name_test_bool == True:
                        logger.info(f"SUCCESS:Hostname {nb_device.name} successfully validated.")
                        succeed_writer.writerow([nb_device.name])
                    
                    else:
                        logger.error(f"FAILURE:Hostname {nb_device.name} FAILED hostname validation. Reason: {reason}")
                        fail_writer.writerow([nb_device.name, reason])

    fail_email_body = """
    This email was sent automatically via a Python script -- nb_verify_hostnames.py
    
    The script looped through all production devices found in Netbox and evaluated their hostnames for compliancy to our naming standard. 

    Reminder that the standard is slightly different based on a site-by-site basis:

        4-field: [site]-[floor]-[rack]-[device+number] -- 633-fl11-nr01-sw01
        5-field: [site]-[bldg]-[floor]-[rack]-[device+number] -- zoo-admin-fl01-nr01-sw01

    Attached to this email is a .CSV that reports what hostnames have failed the compliancy check, including a reason why.     
    """

    fail_email_subject = "AutoReport: Hostname Compliancy"

    emailer('./reporting/failed-hostnames.csv', fail_email_body, fail_email_subject)

            
nb_verify_hostnames()