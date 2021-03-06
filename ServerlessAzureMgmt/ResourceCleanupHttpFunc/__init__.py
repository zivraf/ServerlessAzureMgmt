import logging
import os

import azure.functions as func
import datetime 
from dateutil.parser import parse
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource import ResourceManagementClient
import azure.mgmt.resource.resources.models
from azure.common.credentials import ServicePrincipalCredentials

credentials = ServicePrincipalCredentials(
        client_id=os.environ['AZURE_CLIENT_ID'],
        secret=os.environ['AZURE_CLIENT_SECRET'],
        tenant=os.environ['AZURE_TENANT_ID']
    )

resource_client = ResourceManagementClient(credentials, os.environ['AZURE_SUBSCRIPTION_ID'])
   
compute_client = ComputeManagementClient(credentials, os.environ['AZURE_SUBSCRIPTION_ID'])


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('ResourceCleanupFunction was called (HTTP Trigger).')

    rgList = resource_client.resource_groups.list()

    for rg in rgList:
        print_item (rg)
        # In case there are no tags or no tag with 'Project' name, tag the resource group as unknown and set an expiration date
        if rg.tags != None and 'ExpirationDate' in rg.tags:
            expDate = datetime.datetime.strptime(rg.tags['ExpirationDate'], '%Y-%m-%d')
            if (expDate < datetime.datetime.today()) :
                logging.info("ResourceCleanupFunction: Cleanup time for  {} ".format(rg.name))
                #uncomment the following two commands if you wish to ACTUALLY delete the resource group
                #delete_async_operation = client.resource_groups.delete(rg.name)
                #delete_async_operation.wait()

    return func.HttpResponse(f"ResourceCleanupFunction - Completed")
            


def print_item(group):
    """Print a ResourceGroup instance."""
    logging.info("\tName: {}".format(group.name))
    logging.info("\tId: {}".format(group.id))
    logging.info("\tLocation: {}".format(group.location))
    logging.info("\tTags: {}".format(group.tags))
    print_properties(group.properties)


def print_properties(props):
    """Print a ResourceGroup properties instance."""
    if props and props.provisioning_state:
        logging.info("\tProperties:")
        logging.info("\t\tProvisioning State: {}".format(props.provisioning_state))
    logging.info("\n\n")
