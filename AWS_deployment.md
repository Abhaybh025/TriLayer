# TriLayer — AWS EC2 Deployment

Complete deployment guide for the **TriLayer AI Resume Screener** using AWS EC2, Streamlit, systemd, Nginx, FreeDNS, and HTTPS.

## Architecture

```text
FreeDNS
   ↓
AWS EC2
   ↓
Nginx :80 / :443
   ↓
Streamlit :8501
   ↓
TriLayer App
```

---

## 1. AWS Budget

Create an AWS Budget to monitor your spending.

Example:

```text
Monthly Budget: $20
Alert Threshold: 80% (~$16)
```

> AWS Budgets provide alerts; they do not automatically stop EC2 resources.

For a temporary deployment, stop unused AWS resources when finished.

---

## 2. Create EC2 Instance

Create an Ubuntu EC2 instance.

Recommended Security Group inbound rules:

| Port | Protocol | Source | Purpose |
|---|---|---|---|
| 22 | TCP | Your IP | SSH |
| 80 | TCP | `0.0.0.0/0` | HTTP |
| 443 | TCP | `0.0.0.0/0` | HTTPS |

Port `8501` does **not** need to be publicly exposed because Nginx will proxy requests to Streamlit internally.

---

## 3. SSH Into EC2

From WSL/Linux:

```bash
ssh -i ~/aws-keys/resume-matcher-key.pem ubuntu@YOUR_PUBLIC_IP
```

Verify:

```bash
whoami
```

Expected:

```text
ubuntu
```

---

## 4. Set Up the Project

```bash
cd ~/TriLayer
```

Create and activate the virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Keep API keys and secrets inside `.env`.

Make sure `.env` is included in `.gitignore`:

```gitignore
.env
```

Never commit API keys or other secrets to GitHub.

---

## 5. Test Streamlit

Run Streamlit manually first:

```bash
/home/ubuntu/TriLayer/venv/bin/streamlit run /home/ubuntu/TriLayer/app.py \
--server.port 8501 \
--server.address 0.0.0.0
```

Test from EC2:

```bash
curl -I http://127.0.0.1:8501
```

Expected:

```text
HTTP/1.1 200 OK
```

Stop the manual server:

```text
Ctrl + C
```

---

## 6. Create systemd Service

Create:

```bash
sudo nano /etc/systemd/system/resume-matcher.service
```

Add:

```ini
[Unit]
Description=AI Resume Screener Streamlit App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/TriLayer
ExecStart=/home/ubuntu/TriLayer/venv/bin/streamlit run /home/ubuntu/TriLayer/app.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=5
EnvironmentFile=/home/ubuntu/TriLayer/.env

[Install]
WantedBy=multi-user.target
```

Reload systemd:

```bash
sudo systemctl daemon-reload
```

Start the service:

```bash
sudo systemctl start resume-matcher.service
```

Enable it at boot:

```bash
sudo systemctl enable resume-matcher.service
```

Check:

```bash
sudo systemctl status resume-matcher.service --no-pager
```

Expected:

```text
Active: active (running)
```

---

## 7. Verify Streamlit

Check port `8501`:

```bash
sudo ss -tulpn | grep 8501
```

Expected:

```text
LISTEN ... 0.0.0.0:8501 ... streamlit
```

Test:

```bash
curl -I http://127.0.0.1:8501
```

---

## 8. Install Nginx

On EC2:

```bash
sudo apt update
sudo apt install nginx -y
```

Enable Nginx:

```bash
sudo systemctl enable nginx
```

Check:

```bash
sudo systemctl status nginx
```

---

## 9. Configure Nginx

Create:

```bash
sudo nano /etc/nginx/sites-available/resume-matcher
```

Add:

```nginx
server {
    listen 80;
    server_name YOUR_PUBLIC_IP;

    location / {
        proxy_pass http://127.0.0.1:8501;

        proxy_http_version 1.1;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/resume-matcher /etc/nginx/sites-enabled/
```

Remove the default site:

```bash
sudo rm /etc/nginx/sites-enabled/default
```

Test:

```bash
sudo nginx -t
```

Reload:

```bash
sudo systemctl reload nginx
```

Test in your browser:

```text
http://YOUR_PUBLIC_IP
```

---

## 10. FreeDNS

Create an **A record** in FreeDNS.

```text
Type: A
Hostname: YOUR_SUBDOMAIN
Destination: YOUR_EC2_PUBLIC_IP
```

Example:

```text
trilayer.example.com → 3.107.52.10
```

Verify from WSL:

```bash
nslookup YOUR-FREEDNS-HOSTNAME
```

The hostname should resolve to your EC2 public IP.

---

## 11. Update Nginx for FreeDNS

Edit:

```bash
sudo nano /etc/nginx/sites-available/resume-matcher
```

Change:

```nginx
server_name YOUR_PUBLIC_IP;
```

to:

```nginx
server_name YOUR-FREEDNS-HOSTNAME;
```

Test:

```bash
sudo nginx -t
```

Reload:

```bash
sudo systemctl reload nginx
```

Test:

```text
http://YOUR-FREEDNS-HOSTNAME
```

---

## 12. Install Certbot

Install Certbot:

```bash
sudo snap install --classic certbot
```

Create the command symlink:

```bash
sudo ln -s /snap/bin/certbot /usr/local/bin/certbot
```

Verify:

```bash
certbot --version
```

---

## 13. Enable HTTPS

Run:

```bash
sudo certbot --nginx
```

Enter your email address and accept the terms.

When asked about HTTP → HTTPS redirection, select:

```text
Redirect HTTP traffic to HTTPS
```

Then access:

```text
https://YOUR-FREEDNS-HOSTNAME
```

Your Streamlit application should now be available over HTTPS.

---

## 14. Verify HTTPS Renewal

Check the Certbot renewal timer:

```bash
sudo systemctl status snap.certbot.renew.timer
```

Test renewal without actually renewing:

```bash
sudo certbot renew --dry-run
```

A successful dry run confirms that automatic renewal is configured correctly.

---

## 15. Troubleshooting

### 502 Bad Gateway

Check Streamlit:

```bash
sudo systemctl status resume-matcher.service --no-pager
```

Check port:

```bash
sudo ss -tulpn | grep 8501
```

Test Streamlit directly:

```bash
curl -I http://127.0.0.1:8501
```

If this fails, fix Streamlit/systemd first.

If this returns `HTTP/1.1 200 OK`, investigate Nginx.

---

### 504 Gateway Timeout

Check Streamlit:

```bash
curl -I http://127.0.0.1:8501
```

Check Nginx logs:

```bash
sudo tail -50 /var/log/nginx/error.log
```

---

### Check Streamlit Logs

```bash
sudo journalctl -u resume-matcher.service -n 50 --no-pager
```

Live logs:

```bash
sudo journalctl -u resume-matcher.service -f
```

---

### Check Nginx

```bash
sudo nginx -t
```

```bash
sudo systemctl status nginx
```

---

### FreeDNS Not Resolving

```bash
nslookup YOUR-FREEDNS-HOSTNAME
```

Make sure the A record points to the **current EC2 public IP**.

---

## 16. Useful Commands

### Streamlit

```bash
sudo systemctl start resume-matcher.service
sudo systemctl stop resume-matcher.service
sudo systemctl restart resume-matcher.service
sudo systemctl status resume-matcher.service
sudo systemctl enable resume-matcher.service
```

### Nginx

```bash
sudo systemctl start nginx
sudo systemctl stop nginx
sudo systemctl restart nginx
sudo systemctl reload nginx
sudo systemctl status nginx
sudo nginx -t
```

### Network

```bash
sudo ss -tulpn | grep 8501
curl -I http://127.0.0.1:8501
nslookup YOUR-FREEDNS-HOSTNAME
```

---

## 17. Security Checklist

- [ ] `.env` is in `.gitignore`
- [ ] API keys are not committed to GitHub
- [ ] `.pem` SSH key is not committed
- [ ] Port 22 is restricted to your IP when possible
- [ ] Ports 80 and 443 are publicly accessible
- [ ] Port 8501 is not publicly exposed
- [ ] AWS Budget alert is configured
- [ ] HTTPS is enabled
- [ ] Certbot renewal is enabled
- [ ] Unused AWS resources are stopped

---

## 18. Final Deployment

The final architecture is:

```text
User
  ↓
FreeDNS
  ↓
EC2 Public IP
  ↓
Nginx :443
  ↓
HTTPS / Let's Encrypt
  ↓
127.0.0.1:8501
  ↓
Streamlit
  ↓
TriLayer AI Resume Screener
```

Final URL:

```text
https://trilayer.mooo.com
```

### Note

This deployment intentionally uses a normal EC2 public IPv4 address instead of an Elastic IP because it is a temporary learning/demo deployment.

If the instance is **stopped and started**, the public IP may change. If that happens:

1. Get the new EC2 public IP.
2. Update the FreeDNS A record.
3. Access the same FreeDNS hostname again.

The Nginx configuration can continue using the hostname, so the `server_name` does not need to change.

---

## Deployment Complete 🚀

The application is now deployed publicly with:

- AWS cost monitoring
- EC2
- Ubuntu
- Python virtual environment
- Streamlit
- systemd
- Nginx reverse proxy
- FreeDNS
- HTTPS / Let's Encrypt
- Automatic certificate renewal