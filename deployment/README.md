# Deployment Instructions

## Prerequisites
- AWS EC2 instance running Ubuntu 22.04
- Python 3.8+
- Git installed
- MongoDB URI

## Deployment Steps
1. Connect to EC2:
```bash
ssh -i "your-key.pem" ubuntu@your-ec2-ip
```

2. Set environment variables:
```bash
export SECRET_KEY="your-secret-key"
export MONGO_URI="your-mongo-uri"
```

3. Run deployment script:
```bash
chmod +x deploy.sh
./deploy.sh
```

4. Setup Nginx and systemd:
```bash
sudo cp nginx.conf /etc/nginx/sites-available/dbaas
sudo ln -s /etc/nginx/sites-available/dbaas /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo systemctl restart nginx

sudo cp dbaas.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start dbaas
sudo systemctl enable dbaas
```

## Monitoring
- Check application status: `sudo systemctl status dbaas`
- View logs: `sudo journalctl -u dbaas`
- Monitor Nginx: `sudo tail -f /var/log/nginx/dbaas_error.log`