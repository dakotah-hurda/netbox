from dcim.choices import DeviceStatusChoices, SiteStatusChoices, RackStatusChoices, LocationStatusChoices
from dcim.models import Device, Site, Location, Rack
from extras.reports import Report
import napalm
import socket, dns.resolver

class hostname_compliancy(Report):
    description = """Reports what hostnames fail compliancy standards and why.
    Features: Global uniqueness, hyphenated-field check, attribute-assignment check, field-content check, device-id regex.
    """

    def hostname_check4(self, device, name_hyphen_check):
        import re

        # The below section established our baseline variables for use in this function.

        site = device.site.slug
        role = device.device_role.slug

        fld1 = name_hyphen_check[0] 
        fld2 = name_hyphen_check[1] 
        fld3 = name_hyphen_check[2]
        fld4 = name_hyphen_check[3]

        ant_site = fld1                         # 633
        ant_loc = fld1 + "-" + fld2             # 633-fl11
        ant_rack = ant_loc + "-" + fld3         # 633-fl11-nr01

        # The below section confirms attributes are assigned in Netbox and fails the device if they are not. 

        nb_assignment_check = False 

        if device.location is not None:
            location = device.location.slug
            
            if device.rack is not None:
                rack = device.rack.name
                nb_assignment_check = True
            
            elif device.rack is None:
                self.log_failure(device, "Device is not assigned to a network rack.")
        
        elif device.location is None:
            self.log_failure(device, "Device is not assigned to a location.")

        # The below section evaluates the device's role and comes up with a hostname 'type' for it. Example: sw, rt, ap
        # TODO: This could be improved by making a custom variable assigned to each device role, then querying it from Netbox. But, I am lazy. 

        role_id = { 
            'lab-routers': 'rt', 
            'production-routers': 'rt',
            
            'lab-switches': 'sw',
            'production-switches': 'sw',
            
            'lab-aps': 'ap',
            'production-aps': 'ap', 
            
            'lab-fws': 'fw',
            'production-fws': 'fw', 

            'production-lte': 'cp',
            'production-ups': 'ups',

        }

        if role in role_id.keys():
            dv_role_id = role_id[role]
        
        elif role not in role_id.keys():
            self.log_failure(device, "Either the device role is misconfigured, or it has a role that has not been added to this script. See 'role_id' var in report.")
        
        # The below section evaluates if all field-values match their assigned Netbox counterparts. 

        if nb_assignment_check == True:
            
            if ant_site == site:
                if ant_loc == location:
                    if ant_rack == rack:
                        
                        pattern = f'{dv_role_id}\d\d' # Hostname uniqueness was already checked earlier in the script, so no need to check here.
                        result = re.match(pattern, fld4)

                        if result:
                            self.log_success(device, "All parameters meet hostname standard.")
                        else:
                            self.log_failure(device, f"Field-4 '{fld4} does not equal allowed pattern: {dv_role_id}\d\d")
                        
                    elif ant_rack != rack:
                        self.log_failure(device, f"Field-3 '{ant_rack}' does not equal assigned rack: '{rack}'")
                elif ant_loc != location:
                    self.log_failure(device, f"Field-2 '{ant_loc}' does not equal assigned location: '{location}'")
            elif ant_site != site:
                self.log_failure(device, f"Field-1 '{ant_site}' does not equal assigned site: '{site}'")
                          
    def hostname_check5(self, device, name_hyphen_check):
        import re

        # The below section established our baseline variables for use in this function.

        site = device.site.slug
        role = device.device_role.slug

        fld1 = name_hyphen_check[0] 
        fld2 = name_hyphen_check[1] 
        fld3 = name_hyphen_check[2]
        fld4 = name_hyphen_check[3]
        fld5 = name_hyphen_check[4]

        ant_site = fld1                             # zoo
        ant_loc = fld1 + "-" + fld2 + "-" + fld3    # zoo-admin-fl00
        ant_rack = ant_loc + "-" + fld4             # zoo-admin-fl00-nr01

        # The below section confirms attributes are assigned in Netbox and fails the device if they are not. 

        nb_assignment_check = False 

        if device.location is not None:
            location = device.location.slug
            
            if device.rack is not None:
                rack = device.rack.name
                nb_assignment_check = True
            
            elif device.rack is None:
                self.log_failure(device, "Device is not assigned to a network rack.")
        
        elif device.location is None:
            self.log_failure(device, "Device is not assigned to a location.")

        # The below section evaluates the device's role and comes up with a hostname 'type' for it. Example: sw, rt, ap
        # TODO: This could be improved by making a custom variable assigned to each device role, then querying it from Netbox. But, I am lazy. 

        role_id = { 
            'lab-routers': 'rt', 
            'production-routers': 'rt',
            
            'lab-switches': 'sw',
            'production-switches': 'sw',
            
            'lab-aps': 'ap',
            'production-aps': 'ap', 
            
            'lab-fws': 'fw',
            'production-fws': 'fw', 

            'production-lte': 'cp',
            'production-ups': 'ups',

        }

        if role in role_id.keys():
            dv_role_id = role_id[role]
        
        elif role not in role_id.keys():
            self.log_failure(device, "Either the device role is misconfigured, or it has a role that has not been added to this script. See 'role_id' var in report.")
        
        # The below section evaluates if all field-values match their assigned Netbox counterparts. 

        if nb_assignment_check == True:
            
            if ant_site == site:
                if ant_loc == location:
                    if ant_rack == rack:

                        pattern = f'{dv_role_id}\d\d' # Hostname uniqueness was already checked earlier in the script, so no need to check here.
                        result = re.match(pattern, fld5)

                        if result:
                            self.log_success(device, "All parameters meet hostname standard.")
                        else:
                            self.log_failure(device, f"Field-5 '{fld5} does not equal allowed pattern: {dv_role_id}\d\d")
                        
                    elif ant_rack != rack:
                        self.log_failure(device, f"Field-3 '{ant_rack}' does not equal assigned rack: '{rack}'")
                elif ant_loc != location:
                    self.log_failure(device, f"Field-2 '{ant_loc}' does not equal assigned location: '{location}'")
            elif ant_site != site:
                self.log_failure(device, f"Field-1 '{ant_site}' does not equal assigned site: '{site}'")
                                  
    def test_hostname_compliancy(self):
        
        all_hostnames = []

        for device in Device.objects.filter(status=DeviceStatusChoices.STATUS_ACTIVE):
            if device.name in all_hostnames:
                self.log_failure(device, "Hostname is not globally unique within Netbox.")

            else:
                all_hostnames.append(device.name)

        for device in Device.objects.filter(status=DeviceStatusChoices.STATUS_ACTIVE):

            name_hyphen_check = str(device.name).split("-")

            if len(name_hyphen_check) < 4:
                self.log_failure(device, "Hostname does not have enough hyphenated fields.")
                continue

            elif len(name_hyphen_check) == 4:
                # self.log_info(device, "Device has 4 hyphenated fields. Parsing hostname contents now.")

                self.hostname_check4(device, name_hyphen_check)

            elif len(name_hyphen_check) == 5:
                # self.log_info(device, "Device has 5 hyphenated fields. Parsing hostname contents now.")
                
                self.hostname_check5(device, name_hyphen_check)
                

            elif len(name_hyphen_check) > 5:
                self.log_failure(device, "Hostname has too many hyphenated fields.")
                continue

    def retrieve_napalm_driver(self, device):
        
        if device.platform is None:
            self.log_failure(device, "No platform (IOS version) configured for device.")

        else:

            if device.platform.napalm_driver is None or device.platform.napalm_driver == '':
                self.log_failure(device, "No NAPALM driver configured for device.")
                return ''

            else: 
                # driver = napalm.get_network_driver(str(device.platform.napalm_driver))
                return str(device.platform.napalm_driver)
    
    def test_nb_matches_live_hostname(self):
        for device in Device.objects.filter(status=DeviceStatusChoices.STATUS_ACTIVE):
            
            if device.primary_ip4 is None:
                self.log_failure(device, "No primary IP address assigned to device.")
                continue
            
            else:
                
                driver_name = self.retrieve_napalm_driver(device)
                
                if driver_name is not None:
                    if len(driver_name) > 0:
                        driver = napalm.get_network_driver(str(driver_name))

                        self.log(f"{device.name} {driver}")

                        napalm_device = driver(
                            hostname = device.primary_ip4,
                            username = 'dhurda.a', 
                            password = 'password',
                        )

                        self.log(f"{napalm_device}")
                        self.log(napalm_device.get_facts())

                        # with driver('10.38.0.169', 'dhurda.a', 'password') as napalm_device:
                        #     self.log(napalm_device.get_facts())


class Check_DNS_A_Record(Report):
    description = "Check if device's primary IPv4 has DNS records."

    def resolve_primary_ip4(self, device, query_name):

        if device.primary_ip4_id is not None:
            try:
                addr = socket.gethostbyname(query_name)
                ip4 = str(device.primary_ip4).split("/")[0]
        
                if addr == ip4:
                    self.log_success(device, f"Device succeeded. DNS Lookup Value: {query_name}, IP Address: {ip4}")
                else:
                    self.log_failure(device,"DNS: " + addr + " - Netbox: " + ip4)
        
            except socket.gaierror as err:
                self.log_info(device, "No DNS Resolution")
        
        else:
            try:
                addr = socket.gethostbyname(query_name)
                self.log_warning(device, "No IPv4 set.  Could be: " + addr)
            except socket.gaierror as err:
                self.log_info(device, "No IP or DNS found.")

    def test_dna_a_record(self):

        device_role_ignore_list = ['production-phones'] # Ignoring models that might take this script take longer than usual. 
        
        self.log(f"This report is skipping the following device_roles for brevity: {device_role_ignore_list}")

        for device in Device.objects.filter(status=DeviceStatusChoices.STATUS_ACTIVE):
            
            query_name = device.name

            if device.virtual_chassis is not None:
                if device.name == device.virtual_chassis.master.name:
                    query_name = device.virtual_chassis.name
                    
                else:
                    self.log_info(device, "Skipping device due to vchassis exemption.")
                    continue

            if str(device.device_role) in device_role_ignore_list:
                continue

            if device.interfaces is None:
                continue

            if device.name is None:
                self.log_info(device, "No device name")
                continue
            
            self.resolve_primary_ip4(device, query_name)
