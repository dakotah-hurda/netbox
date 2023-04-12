def nb_hostname_lowercase():
    """
    This function is meant to run regularly. 
    
    It uses the Netbox API to check all device hostnames and ensure that they are formatted in lowercase.
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

    nb_devices = nb.dcim.devices.all()

    for nb_device in nb_devices:
        old_name = nb_device.name
        if old_name is not None:
        
            new_name = old_name.lower()       

            if old_name == new_name:
                logger.debug(f"Skipping: {old_name}, {new_name}")
                continue
            else:
                logger.info(f"Updating: {old_name}, {new_name}")
                response = nb.dcim.devices.get(name=old_name)
                response.name = new_name
                response.save()
        else:
            logger.debug(f"Skipping NoneType object: {nb_device.serial}")

nb_hostname_lowercase()