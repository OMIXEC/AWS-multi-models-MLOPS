import boto3
import argparse
import sys

def terminate_instance(instance_name):
    """Stops and terminates the specified EC2 instance by its tag 'Name'."""
    ec2 = boto3.client('ec2')
    
    print(f"Looking for EC2 instances with Name tag: {instance_name}...")
    response = ec2.describe_instances(
        Filters=[{'Name': 'tag:Name', 'Values': [instance_name]}]
    )
    
    instances_to_terminate = []
    for reservation in response.get('Reservations', []):
        for instance in reservation.get('Instances', []):
            state = instance['State']['Name']
            if state not in ['terminated', 'shutting-down']:
                instances_to_terminate.append(instance['InstanceId'])
    
    if instances_to_terminate:
        print(f"Found active instances: {instances_to_terminate}")
        print(f"Stopping instances: {instances_to_terminate}...")
        ec2.stop_instances(InstanceIds=instances_to_terminate)
        
        # Wait for the instances to stop completely
        waiter_stop = ec2.get_waiter('instance_stopped')
        waiter_stop.wait(InstanceIds=instances_to_terminate)
        print("Instances stopped successfully.")
        
        print(f"Terminating instances: {instances_to_terminate}...")
        ec2.terminate_instances(InstanceIds=instances_to_terminate)
        
        # Wait for the instances to terminate completely
        waiter_term = ec2.get_waiter('instance_terminated')
        waiter_term.wait(InstanceIds=instances_to_terminate)
        print("Instances removed and terminated successfully.")
    else:
        print(f"No active instances found with name '{instance_name}' to terminate.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Teardown AWS EC2 instances by Name tag.")
    parser.add_argument(
        '-n', '--name', 
        type=str, 
        default='mlops-prod',
        help='The Name tag of the EC2 instance to terminate (default: mlops-prod)'
    )
    
    args = parser.parse_args()
    terminate_instance(args.name)
