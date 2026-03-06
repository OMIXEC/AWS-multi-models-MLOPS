from google.cloud import compute_v1

project_id = 'your-gcp-project-id'
zone = 'us-central1-a'
instance_name = 'mlops-prod'

def teardown_instance():
    """Stops and removes the GCP Compute Engine instance."""
    client = compute_v1.InstancesClient()
    
    try:
        # 1. Stop the instance
        print(f"Stopping instance {instance_name}...")
        stop_operation = client.stop(project=project_id, zone=zone, instance=instance_name)
        stop_operation.result()  # Wait for the operation to complete
        print("Instance stopped successfully.")

        # 2. Delete (remove) the instance
        print(f"Deleting instance {instance_name}...")
        delete_operation = client.delete(project=project_id, zone=zone, instance=instance_name)
        delete_operation.result()  # Wait for the operation to complete
        print("Instance removed and terminated successfully.")
        
    except Exception as e:
        print(f"Failed to stop or delete instance {instance_name}: {e}
Ensure your project_id and zone are correctly set.")

if __name__ == "__main__":
    teardown_instance()
