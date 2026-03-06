# 🔐 Connecting Your Server to GitHub via SSH

This guide provides a step-by-step walkthrough for connecting your remote server (e.g., EC2) to GitHub using SSH keys. This process allows you to securely clone repositories and deploy applications, like Streamlit, directly through your VS Code terminal without entering credentials every time.

---

## Phase 1: Generate a New SSH Key

If your server doesn't have access to GitHub, you first need to generate a unique digital "handshake."

1. **Open your terminal** in VS Code (already connected to your server).
2. **Generate the key** by running the following command (replace the email with your GitHub email):
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

3. **Save the file:** When prompted to "Enter a file in which to save the key," simply press **Enter** to use the default location.
4. **Passphrase:** Press **Enter** twice to skip setting a passphrase (standard for automated server setups).

---

## Phase 2: Add the Key to the SSH Agent

Once the key is generated, you need to make sure your system is actively using it.

1. **Start the agent** in the background:
```bash
eval "$(ssh-agent -s)"
```

2. **Add your private key** to the agent:
```bash
ssh-add ~/.ssh/id_ed25519
```

---

## Phase 3: Add the Public Key to Your GitHub Account

Now you must tell GitHub to trust this specific server.

1. **Display your Public Key:** Run this command to see the code you need to copy:
```bash
cat ~/.ssh/id_ed25519.pub
```

2. **Copy the output** (it usually starts with `ssh-ed25519` and ends with your email).
3. **Go to GitHub:**
   - Navigate to **Settings** (click your profile picture).
   - In the left sidebar, click **SSH and GPG keys**.
   - Click the green **New SSH key** button.

4. **Fill the form:**
   - **Title:** Give it a name like "EC2-Streamlit-Server".
   - **Key:** Paste the code you copied from your terminal.
   - Click **Add SSH key** and confirm your GitHub password if asked.

---

## Phase 4: Verify and Clone

Before you start working, verify that the connection is "Live."

1. **Test the connection:**
```bash
ssh -T git@github.com
```

   - If asked "Are you sure you want to continue connecting?", type **yes**.
   - You should see: *"Hi [YourUsername]! You've successfully authenticated..."*

2. **Clone your repository:** Now, copy the **SSH link** from your GitHub repo and run:
```bash
git clone git@github.com:your-username/your-repo-name.git
```

---

## Summary Table: Key Commands

| Action | Command |
| --- | --- |
| **Generate Key** | `ssh-keygen -t ed25519 -C "email"` |
| **Start Agent** | `eval "$(ssh-agent -s)"` |
| **Add Key to Agent** | `ssh-add ~/.ssh/id_ed25519` |
| **View Public Key** | `cat ~/.ssh/id_ed25519.pub` |
| **Test GitHub Sync** | `ssh -T git@github.com` |

> [!TIP]
> Now that your code is on the server, your VS Code environment acts exactly like a local machine. You can edit files, run `pip install`, and launch your Streamlit app directly.


# Quick commands:

```bash

ssh-keygen -t ed25519 -C "email@gmail.com"


eval "$(ssh-agent -s)"

ssh-add ~/.ssh/id_ed25519
Identity added: /home/ec2-user/.ssh/id_ed25519 (bizomizweb@gmail.com)
cat ~/.ssh/
authorized_keys  id_ed25519       id_ed25519.pub
cat ~/.ssh/
authorized_keys  id_ed25519       id_ed25519.pub
cat ~/.ssh/id_ed25519.pub 

ssh -T git@github.com

git clone https://github.com/OMIXEC/AWS-multi-models-MLOPS.git
```