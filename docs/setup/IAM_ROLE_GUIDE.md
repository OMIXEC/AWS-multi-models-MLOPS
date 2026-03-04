# 🔐 IAM Role & Instance Profile Association

To allow your EC2 instance to securely access S3 buckets (to download models) without hardcoding AWS credentials, you must use an **IAM Role**. This guide explains how to create the role once and how to associate it with your instances either manually or via code.

---

## 1. One-Time Setup: Create the IAM Role (Console)

As mentioned in the lecture, creating the role is a one-time process typically done through the UI.

1. Go to the **IAM Dashboard** in the AWS Console.
2. Click **Roles** > **Create role**.
3. Select **AWS service** as the trusted entity and **EC2** as the use case.
4. Search for and check the policy: **`AmazonS3FullAccess`**.
5. Name the role: `ec2-s3-full-access`.
6. Click **Create role**. 
   *Note: AWS automatically creates an "Instance Profile" with the same name.*

---

## 2. Manual Association (For POC)

If you have an existing instance and want to give it S3 access quickly:

1. Go to the **EC2 Dashboard** > **Instances**.
2. Select your instance.
3. Click **Actions** > **Security** > **Modify IAM role**.
4. Select `ec2-s3-full-access` from the dropdown and click **Update IAM role**.

---

## 3. Automated Association (For Production/Boto3)

When you are automating the creation of multiple instances in a production environment, you use the Boto3 SDK to handle the association. 

### Python Code Snippet:
```python
import boto3

iam = boto3.client('iam')
ec2 = boto3.client('ec2')

role_name = "ec2-s3-full-access"
instance_id = "i-xxxxxxxxxxxx" # Your Instance ID from run_instances()

# 1. Get the Role information
response = iam.get_role(RoleName=role_name)
role_arn = response['Role']['Arn']

# 2. Ensure an Instance Profile exists (usually named the same as the role)
try:
    iam.get_instance_profile(InstanceProfileName=role_name)
except iam.exceptions.NoSuchEntityException:
    iam.create_instance_profile(InstanceProfileName=role_name)
    iam.add_role_to_instance_profile(
        InstanceProfileName=role_name,
        RoleName=role_name
    )

# 3. Associate the Instance Profile with your EC2 instance
ec2.associate_iam_instance_profile(
    IamInstanceProfile={'Name': role_name},
    InstanceId=instance_id
)
```

> [!IMPORTANT]
> This automation ensures that as soon as your server starts, it has the necessary permissions to download the models from S3, enabling a fully automated MLOps pipeline.
