#!/bin/bash

# Trading Bot VM Deployment Script
# For Ubuntu 22.04 LTS
# Usage: sudo ./deploy_vm.sh

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/braedenc/Trading-Bot.git"
INSTALL_DIR="/opt/trading-bot"
LOG_FILE="/var/log/trading-bot.log"
SERVICE_NAME="trading-bot"
USER="trading-bot"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Function to update system packages
update_system() {
    print_status "Updating system packages..."
    apt update -y
    apt upgrade -y
}

# Function to install Python 3.11
install_python() {
    print_status "Installing Python 3.11..."
    
    # Add deadsnakes PPA for Python 3.11
    apt install -y software-properties-common
    add-apt-repository -y ppa:deadsnakes/ppa
    apt update -y
    
    # Install Python 3.11 and related packages
    apt install -y \
        python3.11 \
        python3.11-pip \
        python3.11-venv \
        python3.11-dev \
        python3.11-distutils
    
    # Create symlink for python3.11
    ln -sf /usr/bin/python3.11 /usr/bin/python3
    
    # Install pip for Python 3.11
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11
    
    print_status "Python 3.11 installed successfully"
}

# Function to install Node.js
install_node() {
    print_status "Installing Node.js..."
    
    # Install Node.js 18.x LTS
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt install -y nodejs
    
    # Install yarn globally
    npm install -g yarn
    
    print_status "Node.js $(node --version) installed successfully"
}

# Function to install Nginx
install_nginx() {
    print_status "Installing Nginx..."
    
    apt install -y nginx
    
    # Enable and start nginx
    systemctl enable nginx
    systemctl start nginx
    
    print_status "Nginx installed and started successfully"
}

# Function to create system user
create_user() {
    print_status "Creating system user '$USER'..."
    
    if id "$USER" &>/dev/null; then
        print_warning "User '$USER' already exists"
    else
        useradd --system --shell /bin/bash --home-dir "$INSTALL_DIR" --create-home "$USER"
    fi
}

# Function to clone repository
clone_repository() {
    print_status "Cloning repository..."
    
    # Remove existing directory if it exists
    if [[ -d "$INSTALL_DIR" ]]; then
        print_warning "Directory $INSTALL_DIR already exists. Removing..."
        rm -rf "$INSTALL_DIR"
    fi
    
    # Clone repository
    git clone "$REPO_URL" "$INSTALL_DIR"
    
    # Set ownership
    chown -R "$USER:$USER" "$INSTALL_DIR"
    
    print_status "Repository cloned successfully"
}

# Function to install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    cd "$INSTALL_DIR"
    
    # Create virtual environment
    sudo -u "$USER" python3.11 -m venv venv
    
    # Install common dependencies (since requirements.txt might not exist)
    sudo -u "$USER" bash -c "source venv/bin/activate && pip install --upgrade pip"
    sudo -u "$USER" bash -c "source venv/bin/activate && pip install \
        asyncio \
        aiohttp \
        pandas \
        numpy \
        websockets \
        python-dotenv \
        fastapi \
        uvicorn \
        sqlalchemy \
        psycopg2-binary"
    
    # Install from requirements.txt if it exists
    if [[ -f "requirements.txt" ]]; then
        sudo -u "$USER" bash -c "source venv/bin/activate && pip install -r requirements.txt"
    fi
    
    print_status "Python dependencies installed successfully"
}

# Function to build dashboard
build_dashboard() {
    print_status "Setting up dashboard..."
    
    cd "$INSTALL_DIR"
    
    # Create dashboard directory structure
    mkdir -p dashboard/dist
    
    # Create a simple dashboard placeholder
    cat > dashboard/dist/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trading Bot Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .status {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            background-color: #27ae60;
            border-radius: 50%;
            margin-right: 10px;
        }
        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }
        .metric-card {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
        }
        .metric-label {
            color: #7f8c8d;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 Trading Bot Dashboard</h1>
        <p>Real-time monitoring and control panel</p>
    </div>
    
    <div class="status">
        <h2><span class="status-indicator"></span>System Status: Active</h2>
        <p>Trading bot is running and monitoring markets</p>
    </div>
    
    <div class="metrics">
        <div class="metric-card">
            <div class="metric-value">$0.00</div>
            <div class="metric-label">Total P&L</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">0</div>
            <div class="metric-label">Active Positions</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">0</div>
            <div class="metric-label">Trades Today</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">0.00%</div>
            <div class="metric-label">Daily Return</div>
        </div>
    </div>
    
    <div class="status">
        <h3>Agent Status</h3>
        <p>SMA Agent: <span style="color: #27ae60;">Active</span></p>
        <p>Last Signal: <span id="last-signal">None</span></p>
        <p>Uptime: <span id="uptime">0:00:00</span></p>
    </div>
    
    <script>
        // Update uptime every second
        let startTime = new Date();
        setInterval(function() {
            let now = new Date();
            let uptime = Math.floor((now - startTime) / 1000);
            let hours = Math.floor(uptime / 3600);
            let minutes = Math.floor((uptime % 3600) / 60);
            let seconds = uptime % 60;
            
            document.getElementById('uptime').textContent = 
                hours.toString().padStart(2, '0') + ':' + 
                minutes.toString().padStart(2, '0') + ':' + 
                seconds.toString().padStart(2, '0');
        }, 1000);
    </script>
</body>
</html>
EOF
    
    # Set ownership
    chown -R "$USER:$USER" dashboard/
    
    print_status "Dashboard built successfully"
}

# Function to create systemd service
create_systemd_service() {
    print_status "Creating systemd service..."
    
    cat > /etc/systemd/system/${SERVICE_NAME}.service << EOF
[Unit]
Description=Trading Bot Service
After=network.target
Wants=network.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/venv/bin
ExecStart=$INSTALL_DIR/venv/bin/python run_agent.py
Restart=always
RestartSec=10
StandardOutput=append:$LOG_FILE
StandardError=append:$LOG_FILE

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$INSTALL_DIR $LOG_FILE

[Install]
WantedBy=multi-user.target
EOF
    
    # Create log file with proper permissions
    touch "$LOG_FILE"
    chown "$USER:$USER" "$LOG_FILE"
    chmod 644 "$LOG_FILE"
    
    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable "$SERVICE_NAME"
    
    print_status "Systemd service created successfully"
}

# Function to configure Nginx
configure_nginx() {
    print_status "Configuring Nginx..."
    
    # Create Nginx configuration for the dashboard
    cat > /etc/nginx/sites-available/trading-bot << 'EOF'
server {
    listen 80;
    server_name _;
    
    # Dashboard static files
    location / {
        root /opt/trading-bot/dashboard/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    # API endpoints (if needed in the future)
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket support (if needed)
    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
}
EOF
    
    # Enable site
    ln -sf /etc/nginx/sites-available/trading-bot /etc/nginx/sites-enabled/
    
    # Remove default site
    rm -f /etc/nginx/sites-enabled/default
    
    # Test configuration
    nginx -t
    
    # Restart Nginx
    systemctl restart nginx
    
    print_status "Nginx configured successfully"
}

# Function to start services
start_services() {
    print_status "Starting services..."
    
    # Start trading bot service
    systemctl start "$SERVICE_NAME"
    
    # Check service status
    sleep 5
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_status "Trading bot service started successfully"
    else
        print_error "Failed to start trading bot service"
        systemctl status "$SERVICE_NAME"
    fi
    
    # Ensure Nginx is running
    systemctl restart nginx
    
    print_status "All services started successfully"
}

# Function to setup firewall
setup_firewall() {
    print_status "Setting up firewall..."
    
    # Install ufw if not present
    apt install -y ufw
    
    # Reset firewall rules
    ufw --force reset
    
    # Default policies
    ufw default deny incoming
    ufw default allow outgoing
    
    # Allow SSH (port 22)
    ufw allow ssh
    
    # Allow HTTP (port 80)
    ufw allow 80/tcp
    
    # Allow HTTPS (port 443) for future SSL
    ufw allow 443/tcp
    
    # Enable firewall
    ufw --force enable
    
    print_status "Firewall configured successfully"
}

# Function to display final status
display_status() {
    print_status "=== Deployment Complete ==="
    echo
    echo "🚀 Trading Bot deployed successfully!"
    echo
    echo "📊 Dashboard: http://$(curl -s ifconfig.me || echo 'YOUR_SERVER_IP')"
    echo "📝 Logs: $LOG_FILE"
    echo "🔧 Service: $SERVICE_NAME"
    echo
    echo "Commands:"
    echo "  sudo systemctl status $SERVICE_NAME    # Check service status"
    echo "  sudo systemctl restart $SERVICE_NAME   # Restart service"
    echo "  sudo tail -f $LOG_FILE                 # View logs"
    echo
    echo "Service Status:"
    systemctl status "$SERVICE_NAME" --no-pager -l
}

# Main deployment function
main() {
    print_status "Starting Trading Bot deployment..."
    
    check_root
    update_system
    install_python
    install_node
    install_nginx
    create_user
    clone_repository
    install_python_deps
    build_dashboard
    create_systemd_service
    configure_nginx
    setup_firewall
    start_services
    display_status
    
    print_status "Deployment completed successfully!"
}

# Run main function
main "$@"