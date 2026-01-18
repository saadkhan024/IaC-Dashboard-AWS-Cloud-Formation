# AWS Infrastructure as Code Dashboard

A full-stack web application for managing AWS infrastructure through CloudFormation with a single click.

<img width="2048" height="2048" alt="IaC_dashboard-1" src="https://github.com/user-attachments/assets/08efb92d-819c-482c-b9d8-77efec7ca62e" />


## 🎯 Overview

This dashboard allows you to create, manage, and delete AWS resources (EC2, S3, Lambda, RDS) using AWS CloudFormation. Features both demo mode for testing and production mode for real infrastructure deployment.

**Live Demo:** http://Your_Public_IP

---<img width="1893" height="908" alt="iac-dashboard" src="https://github.com/user-attachments/assets/1452ba3e-5ea7-409a-abc5-0b19a9f0ec61" />


## ✨ Features

- ✅ One-click infrastructure deployment
- ✅ Real-time metrics dashboard
- ✅ Cost tracking and monitoring
- ✅ Demo mode (free testing) and Production mode
- ✅ Activity logs with CloudFormation events
- ✅ Support for EC2, S3, Lambda, and RDS

---

## 🛠️ Tech Stack

**Backend:**
- Python 3.11
- Flask 3.0
- Boto3 1.34

**Frontend:**
- Vanilla JavaScript
- HTML5 / CSS3

**Infrastructure:**
- AWS CloudFormation
- AWS EC2, S3, Lambda, RDS

**Deployment:**
- Docker 24.0
- Docker Compose 2.21
- Ubuntu Server 24.04

---

## 📁 Project Structure
```
aws-iac-dashboard/
├── app.py                 # Flask backend API (500 lines)
├── static/
│   └── index.html        # Frontend dashboard (600 lines)
├── Dockerfile            # Docker container definition
├── docker-compose.yml    # Deployment configuration
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (create this)
├── .gitignore           
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose installed
- AWS account with IAM credentials
- (Optional) AWS EC2 instance for deployment

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/aws-iac-dashboard.git
cd aws-iac-dashboard
```

### 2. Configure Environment

Create `.env` file:
```bash
DEMO_MODE=False
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_DEFAULT_REGION=us-east-1
```

### 3. Run with Docker
```bash
# Build and start
docker-compose up --build -d

# Check logs
docker-compose logs -f

# Stop
docker-compose down
```

### 4. Access Dashboard

Open browser: `http://localhost:5000`

---

## ☁️ Deploy to AWS EC2

### On EC2 Ubuntu Server:
```bash
# Install Docker
sudo apt update && sudo apt install -y docker.io docker-compose

# Clone and configure
git clone https://github.com/yourusername/aws-iac-dashboard.git
cd aws-iac-dashboard
nano .env  # Add your AWS credentials

# Deploy
docker-compose up --build -d

# Access
http://YOUR-EC2-PUBLIC-IP:5000
```

### Optional: Setup Nginx (Port 80)
```bash
sudo apt install -y nginx

sudo tee /etc/nginx/sites-available/iac-dashboard > /dev/null <<EOF
server {
    listen 80;
    server_name YOUR_IP;
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host \$host;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/iac-dashboard /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo systemctl restart nginx
```

Access: `http://YOUR-EC2-PUBLIC-IP`

---

## 🔑 AWS IAM Permissions

Required IAM permissions for the user/role:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "cloudformation:*",
                "ec2:*",
                "s3:*",
                "lambda:*",
                "rds:*",
                "iam:CreateRole",
                "iam:AttachRolePolicy",
                "iam:PassRole"
            ],
            "Resource": "*"
        }
    ]
}
```

---

## 💰 Cost Estimate

**Free Tier:**
- EC2 t2.micro: 750 hours/month (FREE)
- S3: 5GB storage (FREE)
- Lambda: 1M requests (FREE)

**Production:**
- EC2 t2.small: ~$17/month
- Created resources: Variable (delete after testing!)

**⚠️ Remember to delete test resources to avoid charges!**

---

## 🎮 Demo Mode vs Production Mode

### Demo Mode (`DEMO_MODE=True`)
- Simulates resource creation
- No AWS credentials required
- Zero cost
- Perfect for testing UI

### Production Mode (`DEMO_MODE=False`)
- Creates real AWS resources
- Requires AWS credentials
- Incurs AWS costs
- Manages actual infrastructure

---

## 🧪 Usage

1. **Select Service:** Click on EC2, S3, Lambda, or RDS
2. **Create Stack:** Click "Create Stack" button
3. **Monitor:** Watch real-time logs and metrics
4. **Delete:** Click "Delete Last Stack" when done

---

## 📚 Key Technologies Explained

### Why CloudFormation?
- ✅ Infrastructure as Code
- ✅ Repeatable deployments
- ✅ Version controlled
- ✅ Automatic rollback on failures

### Why Docker?
- ✅ Consistent environments
- ✅ Easy deployment
- ✅ No "works on my machine" issues

---

## 🐛 Troubleshooting

### Dashboard shows DEMO MODE but .env has False
```bash
# Rebuild without cache
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### API returns 401 Unauthorized
- Check AWS credentials in `.env`
- Verify IAM permissions
- Ensure credentials are not expired

### Stack creation fails
- Check CloudFormation Events tab in AWS Console
- Verify IAM permissions
- Check AWS service quotas

### Port 5000 already in use
```bash
# Change port in docker-compose.yml
ports:
  - "8080:5000"  # Use 8080 instead
```

---

## 🔒 Security Notes

- ⚠️ Never commit `.env` file
- ✅ Use IAM roles on EC2 (better than access keys)
- ✅ Rotate credentials regularly
- ✅ Set up AWS billing alerts
- ✅ Use least-privilege IAM policies

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 🙏 Acknowledgments

- AWS Documentation
- Flask & Boto3 communities
- Docker community
- Stack Overflow

---

## 📧 Contact

**Author:** Saad Khan
**Email:** khansaad92211@gmail.com
**LinkedIn:** [linkedin.com/in/yourname](https://linkedin.com/in/saadkhan04)  
**GitHub:** [github.com/yourusername](https://github.com/saadkhan024)

---

## ⭐ Support

If you find this project helpful:
- ⭐ Star the repository
- 🔄 Fork and contribute
- 🐛 Report issues
- 💬 Share feedback

---

**Built with ☕ and lots of debugging**
