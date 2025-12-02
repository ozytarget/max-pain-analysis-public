# Deployment Guide

## Local Development

### Quick Start
```bash
# 1. Clone repo
git clone https://github.com/yourusername/max-pain-analysis-public.git
cd max-pain-analysis-public

# 2. Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API keys
cp .env.example .env
# Edit .env with your actual API keys

# 5. Run application
streamlit run app.py
```

## Server Deployment (Ubuntu/Linux)

### 1. Initial Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.12
sudo apt install python3.12 python3.12-venv python3.12-dev -y

# Install dependencies
sudo apt install git curl wget -y
```

### 2. Clone Repository
```bash
cd /opt
sudo git clone https://github.com/yourusername/max-pain-analysis-public.git
sudo chown -R $USER:$USER max-pain-analysis-public
cd max-pain-analysis-public
```

### 3. Create Virtual Environment
```bash
python3.12 -m venv venv
source venv/bin/activate
```

### 4. Install Python Packages
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### 5. Configure Environment
```bash
# Copy template
cp .env.example .env

# Edit with your API keys
nano .env

# Set permissions
chmod 600 .env
```

### 6. Create Systemd Service

Create `/etc/systemd/system/pro-scanner.service`:

```ini
[Unit]
Description=Pro Scanner - Financial Market Analysis
After=network.target

[Service]
Type=simple
User=scanner
WorkingDirectory=/opt/max-pain-analysis-public
Environment="PATH=/opt/max-pain-analysis-public/venv/bin"
EnvironmentFile=/opt/max-pain-analysis-public/.env
ExecStart=/opt/max-pain-analysis-public/venv/bin/streamlit run app.py --server.headless true --server.port 8501 --server.runOnSave false
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 7. Enable Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable pro-scanner
sudo systemctl start pro-scanner

# Check status
sudo systemctl status pro-scanner
```

### 8. Setup Reverse Proxy (Nginx)

Create `/etc/nginx/sites-available/pro-scanner`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/pro-scanner /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 9. Setup SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

### 10. Monitoring

Check logs:
```bash
sudo journalctl -u pro-scanner -f  # Follow logs
sudo journalctl -u pro-scanner -n 50  # Last 50 lines
```

Check memory usage:
```bash
top
# Or specific process
ps aux | grep streamlit
```

## Docker Deployment

### 1. Create Dockerfile
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app.py .
COPY auth_data/ ./auth_data/

# Expose port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.headless", "true", "--server.port", "8501"]
```

### 2. Create .dockerignore
```
.git
.gitignore
.env
__pycache__
*.pyc
venv/
.streamlit/
.DS_Store
README.md
SECURITY.md
AUDIT_REPORT.md
```

### 3. Build and Run
```bash
# Build
docker build -t pro-scanner:latest .

# Run
docker run -p 8501:8501 \
  --env-file .env \
  --name pro-scanner \
  pro-scanner:latest

# Run in background
docker run -d -p 8501:8501 \
  --env-file .env \
  --name pro-scanner \
  pro-scanner:latest
```

## Cloud Deployment (AWS, DigitalOcean, Heroku)

### Heroku Deployment

1. Create `Procfile`:
```
web: streamlit run app.py --server.headless true --server.port $PORT
```

2. Create `runtime.txt`:
```
python-3.12.0
```

3. Deploy:
```bash
heroku login
heroku create pro-scanner
heroku config:set KRAKEN_API_KEY=your_key
heroku config:set FMP_API_KEY=your_key
# ... set all API keys

git push heroku main
heroku logs --tail
```

## Maintenance

### Update Dependencies
```bash
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Backup Database
```bash
cp auth_data/passwords.db auth_data/passwords.db.backup
```

### Monitor Logs
```bash
tail -f logs/app.log
```

### Restart Service
```bash
sudo systemctl restart pro-scanner
```

## Troubleshooting

### High Memory Usage
- Check for memory leaks in data processing
- Limit cache TTL
- Use threading pool with max_workers

### Slow API Responses
- Verify internet connection
- Check API rate limits
- Add retry logic with backoff

### Port Already in Use
```bash
# Find process using port 8501
lsof -i :8501

# Kill process
kill -9 <PID>
```

### .env Not Loading
```bash
# Verify file exists and is readable
ls -la .env

# Check permissions
chmod 600 .env

# Verify env vars are loaded
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('KRAKEN_API_KEY'))"
```

## Security Checklist

- [ ] .env file is NOT committed to git
- [ ] All API keys are in environment variables
- [ ] .gitignore includes .env, auth_data/, __pycache__
- [ ] SSL/TLS enabled in production
- [ ] Firewall configured to allow only necessary ports
- [ ] Regular backups of passwords.db
- [ ] API keys rotated periodically
- [ ] Logs monitored for suspicious activity

---

**For more information, see SECURITY.md**
