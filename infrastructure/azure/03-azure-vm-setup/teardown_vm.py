from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource import ResourceManagementClient

credential = DefaultAzureCredential()
subscription_id = 'your-subscription-id'
resource_group_name = 'mlops-rg'
vm_name = 'mlops-prod-vm'

def teardown_vm_and_rg():
    """Stops the Azure VM, deletes it, and removes the associated resource group to clean up disks and IPs."""
    compute_client = ComputeManagementClient(credential, subscription_id)
    resource_client = ResourceManagementClient(credential, subscription_id)

    try:
        # 1. Stop (Deallocate) the VM
        print(f"Stopping (Deallocating) VM {vm_name}...")
        poller_stop = compute_client.virtual_machines.begin_deallocate(resource_group_name, vm_name)
        poller_stop.result()
        print("VM stopped and deallocated successfully.")

        # 2. Delete the VM
        print(f"Deleting VM {vm_name}...")
        poller_delete = compute_client.virtual_machines.begin_delete(resource_group_name, vm_name)
        poller_delete.result()
        print("VM deleted successfully.")

        # 3. Delete the Resource Group (Crucial in Azure to avoid dangling disks/IPs)
        print(f"Deleting entire resource group '{resource_group_name}' to clean up disks, NICs, and IPs...")
        poller_rg = resource_client.resource_groups.begin_delete(resource_group_name)
        poller_rg.result()
        print("Resource group and all associated resources removed successfully.")

    except Exception as e:
        print(f"Failed during teardown: {e}
Ensure your subscription_id is correctly set.")

if __name__ == "__main__":
    teardown_vm_and_rg()
