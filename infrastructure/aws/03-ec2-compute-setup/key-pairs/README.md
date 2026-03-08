# EC2 Key Pairs

This directory contains an example SSH key pair for demonstration purposes.

**Important:** The `omixec.pem` file included here is an example only. In production, you should:

1. Generate your own key pair using AWS EC2 console or CLI:
   ```bash
   aws ec2 create-key-pair --key-name my-key-pair --query 'KeyMaterial' --output text > my-key-pair.pem
   ```

2. Or use AWS Systems Manager Parameter Store to store keys securely

3. Never commit actual private keys to version control

This example demonstrates how to authenticate to EC2 instances using SSH key-based authentication.
