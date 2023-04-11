from extras.scripts import *

from dcim.choices import DeviceStatusChoices
from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site, Location, Rack
from utilities.exceptions import AbortScript


class NewBackstockDevice(Script):
    class Meta:
        name = "Import New Backstock Device"
        description = "Create a new Device object and add to Backstock."

    location = ObjectVar(
        description='What backstock location will this new device be stored in? Default: 633 Storage Room.',
        model=Location,
        query_params={"site_id": "61"},
        default="25",  # 633-fl11-storage
    )

    new_device_serial = StringVar(description="Enter the new device's serial number here.", min_length=5)

    #TODO: Add feature to track POs with custom field. 
    # new_device_purchase_order = StringVar(description="Enter the PO this device was purchased with.") 

    new_device_asset = StringVar(description="Enter the new device's asset-tag here.", required=False)

    manufacturer = ObjectVar(
        description='Who manufactured the new device? Default: Cisco',
        default=1,
        model=Manufacturer,
        required=False,  # Cisco
    )

    new_device_model = ObjectVar(
        description="What is the model of the new device? Be as exact as possible. If the right model doesn't exist, let an engineer know before continuing.",
        default=1834,  # C9200L-48P-4X
        model=DeviceType,
        query_params={'manufacturer_id': '$manufacturer'},
    )

    def test_serial_num(self, serial_number):
        try:
            serial_lookup = Device.objects.get(serial=serial_number)
            assert serial_lookup is None
            self.log_success(f"Serial validation passed.")

        except AssertionError:
            raise AbortScript(f"Duplicate serial found matching your entered serial: {serial_number}")

        except Exception as e:
            if str(e) == "Device matching query does not exist.":
                self.log_success(f"Serial validation passed.")

            else:
                raise e

    def parse_asset_tag(self, asset_tag):
        """
        Checks length of asset tag to allow zero-length tags on creation.
        """

        if len(asset_tag) > 0:
            return asset_tag
        else:
            return None

    def run(self, data, commit=False):
        # Define all the new_device vars for deployment.
        serial_number = data['new_device_serial']
        device_role = DeviceRole.objects.get(name='backstock')
        device_type = data['new_device_model']
        site_id = data['location'].site  # Backstock 'site'
        location = data['location']
        asset_tag = self.parse_asset_tag(data['new_device_asset'])

        self.test_serial_num(serial_number)  # Validate that the entered serial_num is unique

        new_device = Device(
            name=None,
            device_role=device_role,
            device_type=device_type,
            serial=serial_number,
            asset_tag=asset_tag,
            site=site_id,
            location=location,
            status=DeviceStatusChoices.STATUS_ACTIVE,
        )

        new_device.save()
        device_lookup = Device.objects.get(serial=serial_number)
        self.log_success(f"Created new device: https://633-fl11-netbox-sv01/dcim/devices/{device_lookup.id}")


class deploy_device(Script):
    class Meta:
        name = "Deploy Device From Backstock"
        description = "Deploy an existing device from backstock to an existing Netbox site. If you don't know any of the variables here, or something is missing, ask an engineer."

    device_serial = StringVar(description="Enter the device's serial number here.", min_length=5)

    CHOICES = (  # This tuple used below to let the user pick what type of device they're deploying.
        ('sw', 'Switch'),
        ('rt', 'Router'),
        ('ap', 'Access Point'),
        ('ups', 'UPS'),
        ('fw', 'Firewall'),
        # ('phone?', 'Phone') TODO: do we want to add phones to this?
    )

    # device_type = ChoiceVar(choices=CHOICES, description="What kind of device are you deploying?")

    site = ObjectVar(
        description='What site will this device be installed at?', model=Site, query_params={'status': 'active'}
    )

    floor = ObjectVar(
        description='What floor will this device be installed on?', model=Location, query_params={"site_id": "$site"}
    )

    netrack = ObjectVar(
        description='What network rack will this device be cabled to?',
        model=Rack,
        query_params={"location_id": "$floor"},
    )

    device_ip = IPAddressWithMaskVar(
        label="Device MGMT IP:", description="Enter the device's management IP in CIDR notation, e.g. 10.0.0.1/24"
    )

    def hostname_generator(self, lookup_value, hostname_type):
        '''
        This function queries for hostnames matching the provided lookup_value,
        then determines a hostname for the new new_device based on the results.
        '''
        # TODO: Figure out how to handle racks with stacked switchs. E.g. ch-fl02-nr02-sw01_1, sw01_2, etc.
        found_hostname_list = []

        for result in Device.objects.filter(name__startswith=lookup_value):
            found_hostname_list.append(result.name)

        if len(found_hostname_list) == 0:
            hostname = lookup_value + '01'
            return hostname

        else:
            new_device_nums = []
            for found_hostname in found_hostname_list:
                new_device_number = found_hostname.split(hostname_type)[1]
                new_device_nums.append(int(new_device_number))

            new_device_id = max(new_device_nums) + 1

            if new_device_id < 10:
                new_device_id = f"0{new_device_id}"

            hostname = lookup_value + str(new_device_id)
            return hostname

    def determine_device_role(self, lookup_value):
        """
        This function provides a quick reference between device_type tag and associated device role.
        """
        lookup_dict = {
            'model-switch': 'production-switches',
            'model-router': 'production-routers',
            'model-accesspoint': 'production-aps',
            'model-ups': 'production-ups',
            'model-firewall': 'production-firewalls',
        }

        return lookup_dict[lookup_value]

    def determine_device_type(self, serial_number):
        device_lookup = Device.objects.get(serial=serial_number)  # Searches for the Device object.
        device_type_lookup = DeviceType.objects.get(
            slug=device_lookup.device_type.slug
        )  # Retrieves the Device's device_type.

        # A custom tag is 'model-switch', for example.
        # Identifies what kind of device the device_type is.
        type_tags = list(device_type_lookup.tags.all())
        for type_tag in type_tags:
            if "model-" in type_tag.name:
                device_type = type_tag.name

        return device_type

    def determine_hostname_type(self, device_type):
        """
        This function provides a quick reference between a provided device_type tag and its associated hostname type.

        e.g. -sw01, -rt01, -ap01.
        """
        lookup_dict = {
            'model-switch': 'sw',
            'model-router': 'rt',
            'model-accesspoint': 'ap',
            'model-ups': 'ups',
            'model-firewall': 'fw',
        }

        return lookup_dict[device_type]

    def serial_lookup(self, serial_number):
        try:
            serial_lookup = Device.objects.get(serial=serial_number)
            assert serial_lookup is not None
            self.log_success(f"Serial validation passed.")

        except AssertionError:
            raise AbortScript(f"No serial found matching your entered serial: {serial_number}")

        except Exception as e:
            if str(e) == "Device matching query does not exist.":
                raise AbortScript(f"No serial found matching your entered serial: {serial_number}")

            else:
                raise e

    def run(self, data, commit=False):
        serial_number = data['device_serial']
        self.serial_lookup(serial_number)  # Validates if the serial actually exists on NB.

        site = data['site']  # User-selected site.
        netrack = data['netrack']  # User-selected rack.
        netrack_slug = str(netrack.name)  # Netrack, sluggified for generating hostname below.
        location = data['floor']  # User-selected location.

        device_type = self.determine_device_type(serial_number)

        device_role = self.determine_device_role(device_type)  # Determine the role name.
        device_role = DeviceRole.objects.get(name=device_role)  # Query for the role name, assign role object.

        hostname_type = self.determine_hostname_type(device_type)

        hostname = self.hostname_generator(lookup_value=f"{netrack_slug}-{hostname_type}", hostname_type=hostname_type)

        self.log_info(f"{hostname}, {device_type}, {device_role}")

        new_device = Device(
            name=hostname,
            device_role=device_role,
            serial=serial_number,
            site=site,
            location=location,
            rack=netrack,
            status=DeviceStatusChoices.STATUS_ACTIVE,
        )

        # new_device.save()
        self.log_success(f"Created new new_device: {new_device.name}")  # TODO: change this message
