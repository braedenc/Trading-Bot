# Trading Bot VM Deployment Guide

This guide provides step-by-step instructions for deploying the Trading Bot on a fresh Ubuntu 22.04 server.

## Prerequisites

- **Server**: Ubuntu 22.04 LTS droplet (minimum 1GB RAM, 1 CPU)
- **Access**: SSH root access to the server
- **Network**: Server should have internet access for package installation

## Quick Deployment

### 1. Connect to Your Server

```bash
ssh root@YOUR_SERVER_IP
```

### 2. Download and Run Deployment Script

```bash
# Download the deployment script
wget https://raw.githubusercontent.com/braedenc/Trading-Bot/main/scripts/deploy_vm.sh

# Make it executable
chmod +x deploy_vm.sh

# Run the deployment
sudo ./deploy_vm.sh
```

The script will automatically:
- Update system packages
- Install Python 3.11, Node.js, and Nginx
- Clone the repository
- Set up the systemd service
- Configure logging
- Set up the dashboard
- Configure firewall

### 3. Verify Deployment

After successful deployment, verify the service is running:

```bash
sudo systemctl status trading-bot
```

Expected output:
```
● trading-bot.service - Trading Bot Service
   Loaded: loaded (/etc/systemd/system/trading-bot.service; enabled; vendor preset: enabled)
   Active: active (running) since Mon 2024-01-01 12:00:00 UTC; 1min ago
   Main PID: 1234 (python)
```

## Manual Deployment Steps

If you prefer to deploy manually or need to troubleshoot, follow these detailed steps:

### Step 1: Update System

```bash
sudo apt update -y
sudo apt upgrade -y
```

### Step 2: Install Python 3.11

```bash
# Add deadsnakes PPA
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update -y

# Install Python 3.11
sudo apt install -y python3.11 python3.11-pip python3.11-venv python3.11-dev
sudo ln -sf /usr/bin/python3.11 /usr/bin/python3

# Install pip
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11
```

### Step 3: Install Node.js

```bash
# Install Node.js 18.x LTS
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo bash -
sudo apt install -y nodejs

# Install yarn
sudo npm install -g yarn
```

### Step 4: Install Nginx

```bash
sudo apt install -y nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

### Step 5: Create System User

```bash
sudo useradd --system --shell /bin/bash --home-dir /opt/trading-bot --create-home trading-bot
```

### Step 6: Clone Repository

```bash
sudo git clone https://github.com/braedenc/Trading-Bot.git /opt/trading-bot
sudo chown -R trading-bot:trading-bot /opt/trading-bot
```

### Step 7: Install Python Dependencies

```bash
cd /opt/trading-bot
sudo -u trading-bot python3.11 -m venv venv
sudo -u trading-bot bash -c "source venv/bin/activate && pip install --upgrade pip"
sudo -u trading-bot bash -c "source venv/bin/activate && pip install asyncio aiohttp pandas numpy websockets python-dotenv fastapi uvicorn sqlalchemy psycopg2-binary"
```

### Step 8: Set Up Dashboard

```bash
sudo mkdir -p /opt/trading-bot/dashboard/dist
# Dashboard files will be created automatically by the script
```

### Step 9: Create Systemd Service

Create `/etc/systemd/system/trading-bot.service`:

```ini
[Unit]
Description=Trading Bot Service
After=network.target
Wants=network.target

[Service]
Type=simple
User=trading-bot
Group=trading-bot
WorkingDirectory=/opt/trading-bot
Environment=PATH=/opt/trading-bot/venv/bin
ExecStart=/opt/trading-bot/venv/bin/python run_agent.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/trading-bot.log
StandardError=append:/var/log/trading-bot.log

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/trading-bot /var/log/trading-bot.log

[Install]
WantedBy=multi-user.target
```

### Step 10: Configure Nginx

Create `/etc/nginx/sites-available/trading-bot`:

```nginx
server {
    listen 80;
    server_name _;
    
    # Dashboard static files
    location / {
        root /opt/trading-bot/dashboard/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    # API endpoints (future use)
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

Enable the site:

```bash
sudo ln -sf /etc/nginx/sites-available/trading-bot /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

### Step 11: Set Up Firewall

```bash
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

### Step 12: Start Services

```bash
sudo systemctl daemon-reload
sudo systemctl enable trading-bot
sudo systemctl start trading-bot
```

## Post-Deployment

### Access the Dashboard

Open your web browser and navigate to:
```
http://YOUR_SERVER_IP
```

You should see the Trading Bot Dashboard with system status and metrics.

### Service Management

Common service management commands:

```bash
# Check service status
sudo systemctl status trading-bot

# Start service
sudo systemctl start trading-bot

# Stop service
sudo systemctl stop trading-bot

# Restart service
sudo systemctl restart trading-bot

# View logs
sudo tail -f /var/log/trading-bot.log

# View recent logs
sudo journalctl -u trading-bot -f
```

### Log Files

- **Application logs**: `/var/log/trading-bot.log`
- **System logs**: `sudo journalctl -u trading-bot`
- **Nginx logs**: `/var/log/nginx/access.log` and `/var/log/nginx/error.log`

### File Locations

- **Application**: `/opt/trading-bot/`
- **Virtual environment**: `/opt/trading-bot/venv/`
- **Dashboard**: `/opt/trading-bot/dashboard/dist/`
- **Service file**: `/etc/systemd/system/trading-bot.service`
- **Nginx config**: `/etc/nginx/sites-available/trading-bot`

## Troubleshooting

### Service Won't Start

1. Check service status:
   ```bash
   sudo systemctl status trading-bot
   ```

2. Check logs:
   ```bash
   sudo tail -f /var/log/trading-bot.log
   sudo journalctl -u trading-bot -f
   ```

3. Check if Python dependencies are installed:
   ```bash
   cd /opt/trading-bot
   sudo -u trading-bot bash -c "source venv/bin/activate && python -c 'import asyncio; print(\"OK\")'"
   ```

### Dashboard Not Loading

1. Check Nginx status:
   ```bash
   sudo systemctl status nginx
   ```

2. Check Nginx configuration:
   ```bash
   sudo nginx -t
   ```

3. Check if dashboard files exist:
   ```bash
   ls -la /opt/trading-bot/dashboard/dist/
   ```

### Permission Issues

1. Check file ownership:
   ```bash
   sudo chown -R trading-bot:trading-bot /opt/trading-bot
   ```

2. Check log file permissions:
   ```bash
   sudo chown trading-bot:trading-bot /var/log/trading-bot.log
   ```

### Network Issues

1. Check firewall status:
   ```bash
   sudo ufw status
   ```

2. Check if ports are listening:
   ```bash
   sudo netstat -tlnp | grep :80
   ```

## Security Considerations

- The service runs as a non-root user (`trading-bot`)
- Firewall is configured to allow only necessary ports
- Security headers are set in Nginx configuration
- The service has restricted filesystem access

## Updating the Application

To update the trading bot to the latest version:

```bash
# Stop the service
sudo systemctl stop trading-bot

# Update the code
cd /opt/trading-bot
sudo -u trading-bot git pull origin main

# Update dependencies if needed
sudo -u trading-bot bash -c "source venv/bin/activate && pip install --upgrade -r requirements.txt"

# Restart the service
sudo systemctl start trading-bot
```

## Monitoring

### Health Check

Create a simple health check script:

```bash
#!/bin/bash
# /opt/trading-bot/health_check.sh

if systemctl is-active --quiet trading-bot; then
    echo "✅ Trading Bot is running"
    exit 0
else
    echo "❌ Trading Bot is not running"
    exit 1
fi
```

### Log Rotation

Set up log rotation to prevent log files from growing too large:

```bash
sudo tee /etc/logrotate.d/trading-bot > /dev/null <<EOF
/var/log/trading-bot.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    sharedscripts
    postrotate
        systemctl reload trading-bot
    endscript
}
EOF
```

## Support

For issues or questions:
1. Check the logs first
2. Verify all services are running
3. Consult the main repository documentation
4. Create an issue in the GitHub repository

---

**Last Updated**: January 2024
**Compatible with**: Ubuntu 22.04 LTS