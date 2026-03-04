# 📌 Setting Up an Elastic IP on AWS EC2

By default, when you stop and start an EC2 instance, AWS assigns it a **new dynamic Public IPv4 address**. This can be frustrating because you have to constantly update your SSH connections in VS Code and change the URL you use to access your Streamlit or FastAPI applications.

An **Elastic IP (EIP)** is a static, persistent public IP address that you can allocate to your AWS account and attach to your EC2 instance. As long as it is attached, your instance's IP will never change, even if you stop or reboot the server.

---

## Step 1: Allocate an Elastic IP

1. Log in to the **AWS Management Console**.
2. Navigate to the **EC2 Dashboard**.
3. In the left-hand navigation pane, under **Network & Security**, click on **Elastic IPs**.
4. Click the orange **Allocate Elastic IP address** button in the top right corner.
5. Leave the default settings (Network border group should match your region, e.g., `us-east-1`) and click **Allocate**.

*You now have a static IP address allocated to your AWS account.*

---

## Step 2: Associate the Elastic IP with Your EC2 Instance

Now that you have the IP, you need to link it to your server.

1. On the **Elastic IPs** page, select the newly allocated IP address (check the box next to it).
2. Click the **Actions** dropdown menu at the top right, and select **Associate Elastic IP address**.
3. In the association configuration screen:
   - **Resource type:** Ensure "Instance" is selected.
   - **Instance:** Click the search box and select your running (or stopped) EC2 instance from the dropdown list.
   - **Private IP address:** (Optional) You can leave this blank or select the private IP associated with your instance.
   - **Reassociation:** Check the box "Allow this Elastic IP address to be reassociated" (this is useful if you ever want to quickly move this IP to a new instance).
4. Click **Associate**.

---

## Step 3: Update Your Workflow

Now that your server has a permanent IP address, you should update a few things:

1. **Update VS Code SSH Configuration:**
   If you use the `~/.ssh/config` file to manage your connections, update the `HostName` to your new Elastic IP.
   ```text
   Host MyEC2Server
       HostName <YOUR_NEW_ELASTIC_IP>
       User ubuntu
       IdentityFile ~/.ssh/your-key.pem
   ```
2. **Accessing Your Apps:**
   You will now access your applications using the new IP address. It will not change anymore!
   - Streamlit: `http://<YOUR_NEW_ELASTIC_IP>:8501`
   - FastAPI: `http://<YOUR_NEW_ELASTIC_IP>:8000/docs`

---

## ⚠️ Important Considerations

- **Cost:** Elastic IPs are **free** as long as they are associated with a *running* EC2 instance. If your instance is stopped, or if the Elastic IP is unattached, AWS charges a small hourly fee (usually around $0.005/hour).
- **Cleanup:** If you terminate your EC2 instance permanently, remember to go back to the Elastic IPs dashboard, **Disassociate** the IP, and then **Release** it so you don't get charged for an unused IP.