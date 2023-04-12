def nb_update_devtype_int_name(dev_type_slug, old_int_name, new_int_name):
    """
    This function is intended to update interface names for a given device-type. 

    Function:

        1) Query Netbox API for the provided device_type 'slug'
        2) Loop through every device find by the query.
        3) Loop through every interface on each device.
        4) If the interface matches the 'old_int_name', update the name to match the 'new_int_name' variable.
    """
    import os
    import pynetbox
    from logger import myLogger
    from dotenv import load_dotenv

    logger = myLogger(__name__) # Initialize a logging object. 
    load_dotenv() # Loads all environment variables including the local .env file. 

    netbox_access_token = os.environ.get('NETBOX-ACCESS-TOKEN')
    netbox_url = os.environ.get('NETBOX-URL')

    nb = pynetbox.api(netbox_url, token=netbox_access_token) 

    nb_devices = nb.dcim.devices.filter(device_type=dev_type_slug) # 1) Query Netbox API for the provided device_type 'slug'

    for nb_device in nb_devices: # 2) Loop through every device find by the query.

        ints = nb.dcim.interfaces.filter(device=nb_device.name, name=old_int_name) # 3) Loop through every interface on each device.

        for interface in ints:

            print(nb_device.name, nb_device.id, interface.name)
            # if interface.name == old_int_name:

            #     # 4) If the interface matches the 'old_int_name', update the name to match the 'new_int_name' variable.
            #     res = nb.dcim.interfaces.get(interface.id)
            #     res.name = new_int_name
            #     res.save()
            #     logger.info(f"Updated {nb_device.name} ID:{nb_device.id} interface {interface.name} to {new_int_name}")


dev_type_slug = 'air-cap3702i-b-k9'
old_int_name = ''
new_int_name = ''

nb_update_devtype_int_name(dev_type_slug, old_int_name, new_int_name)