# 💻 Connecting to EC2 via VS Code Remote SSH

This guide explains how to connect your VS Code environment directly to your EC2 instance. This allows you to edit files, run terminals, and debug code on the server as if it were your local machine.

---

## Step 1: Install the Extension
1. Open **VS Code**.
2. Click on the **Extensions** icon (or press `Ctrl+Shift+X`).
3. Search for and install: **"Remote - SSH"** (by Microsoft).

---

## Step 2: Configure the Connection
1. Click the **Remote Explorer** icon in the left sidebar (it looks like a small computer screen).
2. Click the **+** (plus) icon to add a new SSH target.
3. Enter the connection command:
   ```bash
   ssh -i "/path/to/your-key.pem" ubuntu@<YOUR_EC2_PUBLIC_IP>
   ```
   *Note: If you are using an **Elastic IP**, use that IP here.*
4. Select the configuration file to update (usually `~/.ssh/config`).

---

## Step 3: Connect and Open Folder
1. In the **Remote Explorer** list, find your new connection.
2. Click the **Connect in New Window** icon next to it.
3. If asked, select **Linux** as the platform and click **Continue**.
4. Once connected, click **Open Folder** in the Explorer view.
5. Select the path to your project (e.g., `/home/ubuntu/ml-ops-and-model-deployment-on-aws-main`).

---

## Step 4: Troubleshooting IP Changes
As discussed in the lecture, if you are **not** using an Elastic IP and you stop/start your server, your connection will break because the IP has changed.

1. Copy the **new Public IP** from the AWS Console.
2. In VS Code, click the **Settings (gear icon)** in the Remote Explorer.
3. Select your `config` file.
4. Update the `HostName` value to the new IP:
   ```text
   Host MyEC2Server
       HostName <NEW_IP_ADDRESS>
       User ubuntu
       IdentityFile "/path/to/your-key.pem"
   ```
5. Save the file and reconnect.

> [!TIP]
> To avoid this manual update every time, follow the [Elastic IP Guide](ELASTIC_IP_GUIDE.md) to assign a permanent, static IP to your server.
