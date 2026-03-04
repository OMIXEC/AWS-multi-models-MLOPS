# ⏰ Auto-Starting Streamlit with Crontab on EC2

When you deploy your Streamlit application to an AWS EC2 instance, you want it to automatically start running whenever the server reboots. Otherwise, if the server stops or restarts, your application will be killed and won't come back online automatically.

This guide provides a step-by-step walkthrough for configuring `crontab` on your Linux server to run your Streamlit application on startup.

---

## Step 1: Find Your Python Path

Before setting up the cron job, you need the absolute path to the Python executable that runs your application. If you are using a virtual environment or Anaconda, you must use that specific Python binary, not the system's default Python.

1. Connect to your EC2 instance via SSH (e.g., using VS Code Remote Explorer).
2. Activate your virtual environment (if applicable):
   ```bash
   source venv/bin/activate
   ```
3. Find the Python path:
   ```bash
   which python
   ```
   *Copy the output (e.g., `/home/ubuntu/venv/bin/python` or `/opt/conda/bin/python`).*

---

## Step 2: Get Your Absolute Application Path

You also need the absolute path to your Streamlit `app.py` file to avoid any directory confusion when the system boots.

1. Navigate to your Streamlit app directory:
   ```bash
   cd ~/ml-ops-and-model-deployment-on-aws-main/infrastructure/aws/04-local-app-development/streamlit/cloud/
   ```
   *(Adjust the path based on exactly where you cloned the repository).*
2. Print the working directory:
   ```bash
   pwd
   ```
   *Your full app path will be the output of `pwd` plus `/app.py` (e.g., `/home/ubuntu/ml-ops-and-model-deployment-on-aws-main/infrastructure/aws/04-local-app-development/streamlit/cloud/app.py`).*

---

## Step 3: Configure Crontab

Now we will add the startup command to the server's cron table.

1. Open the crontab editor with `sudo` privileges:
   ```bash
   sudo crontab -e
   ```
2. **Select an editor:** If this is your first time running crontab, it will ask you to choose an editor. Press `1` and hit **Enter** to select `nano` (the easiest option).
3. Scroll to the very bottom of the file using the arrow keys.
4. Add the `@reboot` directive followed by your command. The structure looks like this:

   ```bash
   @reboot [YOUR_PYTHON_PATH] -m streamlit run [YOUR_APP_PATH] > [YOUR_LOG_PATH] 2>&1
   ```

   **Example Command:**
   ```bash
   @reboot /home/ubuntu/venv/bin/python -m streamlit run /home/ubuntu/ml-ops-and-model-deployment-on-aws-main/infrastructure/aws/04-local-app-development/streamlit/cloud/app.py > /home/ubuntu/streamlit.log 2>&1
   ```
   
   *Explanation of the command:*
   - `@reboot`: Tells the server to run this exactly once when it boots up.
   - `/home/ubuntu/venv/bin/python`: The explicit python environment.
   - `-m streamlit run`: Runs Streamlit as a python module.
   - `/home/ubuntu/.../app.py`: The absolute path to your script.
   - `> /home/ubuntu/streamlit.log 2>&1`: Captures all output and errors into a log file so you can troubleshoot if it fails.

5. **Save and Exit:**
   - Press `Ctrl + O` (Letter O) to write out the changes.
   - Press **Enter** to confirm the file name.
   - Press `Ctrl + X` to exit Nano.
   
   You should see a message saying: `crontab: installing new crontab`.

---

## Step 4: Verify and Test

To test that your configuration works:

1. Restart your EC2 instance. You can do this from the AWS Console by selecting your instance, clicking **Instance state**, and choosing **Reboot instance** (or Stop and Start).
   *Note: If you Stop and Start the instance, your Public IPv4 address will change unless you are using an Elastic IP. See our [Elastic IP Guide](ELASTIC_IP_GUIDE.md) to learn how to make your server's IP static.*
2. Wait a minute or two for the server to fully boot.
3. Open your browser and navigate to `http://<YOUR_EC2_PUBLIC_IP>:8501` (or whatever port Streamlit is running on). 
4. If your app loads, success! If it doesn't, reconnect to the server and check the log file you specified:
   ```bash
   cat /home/ubuntu/streamlit.log
   ```

You now have a resilient Streamlit application that survives server restarts automatically!