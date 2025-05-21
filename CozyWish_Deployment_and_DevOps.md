# CozyWish Deployment and DevOps Strategy

This document outlines the deployment architecture, infrastructure setup, and DevOps practices for the CozyWish application.

## Deployment Environments

### Local Development Environment

**Purpose**: Individual developer environments for feature development and testing.

**Components**:
- Django development server
- SQLite database
- Local file storage
- Debug mode enabled
- Django Debug Toolbar

**Setup Instructions**:
```bash
# Clone repository
git clone https://github.com/organization/cozywish.git
cd cozywish

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with local settings

# Set up database
make setup-dev-environment

# Run development server
python manage.py runserver
```

### Staging Environment

**Purpose**: Testing environment that mirrors production for QA and integration testing.

**Components**:
- AWS EC2 instance (t3.medium)
- PostgreSQL RDS database
- AWS S3 for media storage
- Nginx web server
- Gunicorn application server
- Redis for caching
- Reduced debug information
- Staging-specific settings

**Deployment Process**:
- Automated deployment from the `develop` branch
- Database migrations run automatically
- Static files collected and uploaded to S3
- Smoke tests run after deployment

### Production Environment

**Purpose**: Live environment for end users.

**Components**:
- AWS EC2 instances with load balancing
- PostgreSQL RDS database with read replicas
- AWS S3 for media storage
- CloudFront CDN for static assets
- Nginx web server
- Gunicorn application server
- Redis for caching
- ElastiCache for session storage
- Debug mode disabled
- HTTPS enforcement
- Production-specific settings

**Deployment Process**:
- Automated deployment from the `main` branch
- Database migrations run with caution
- Static files collected and uploaded to S3
- Comprehensive test suite run before deployment
- Canary deployment strategy

## Infrastructure as Code

The infrastructure is defined and managed using Terraform:

```hcl
# Example Terraform configuration for AWS resources

provider "aws" {
  region = "us-west-2"
}

# VPC and networking
resource "aws_vpc" "cozywish_vpc" {
  cidr_block = "10.0.0.0/16"
  
  tags = {
    Name = "cozywish-vpc"
    Environment = var.environment
  }
}

# EC2 instances
resource "aws_instance" "web_server" {
  ami           = var.ami_id
  instance_type = var.instance_type
  key_name      = var.key_name
  
  vpc_security_group_ids = [aws_security_group.web_sg.id]
  subnet_id              = aws_subnet.public_subnet.id
  
  tags = {
    Name = "cozywish-web-${var.environment}"
    Environment = var.environment
  }
}

# RDS database
resource "aws_db_instance" "postgres" {
  allocated_storage    = 20
  storage_type         = "gp2"
  engine               = "postgres"
  engine_version       = "13.4"
  instance_class       = var.db_instance_class
  name                 = "cozywish"
  username             = var.db_username
  password             = var.db_password
  parameter_group_name = "default.postgres13"
  skip_final_snapshot  = true
  
  tags = {
    Name = "cozywish-db-${var.environment}"
    Environment = var.environment
  }
}

# S3 bucket for media storage
resource "aws_s3_bucket" "media_bucket" {
  bucket = "cozywish-media-${var.environment}"
  acl    = "private"
  
  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT", "POST"]
    allowed_origins = ["*"]
    max_age_seconds = 3000
  }
  
  tags = {
    Name = "cozywish-media-${var.environment}"
    Environment = var.environment
  }
}
```

## Continuous Integration and Deployment

### GitHub Actions Workflows

#### CI Workflow

```yaml
name: CI

on:
  push:
    branches: [ develop, main ]
  pull_request:
    branches: [ develop, main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: github_actions
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: Lint with flake8
      run: |
        pip install flake8
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        
    - name: Run unit and integration tests
      run: |
        python manage.py test
        
    - name: Run E2E tests
      run: |
        pip install pytest pytest-playwright
        playwright install
        pytest tests/e2e
```

#### CD Workflow for Staging

```yaml
name: Deploy to Staging

on:
  push:
    branches: [ develop ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: staging
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: Run tests
      run: |
        python manage.py test
        
    - name: Deploy to staging
      env:
        DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
        SERVER_IP: ${{ secrets.STAGING_SERVER_IP }}
        SERVER_USER: ${{ secrets.SERVER_USER }}
      run: |
        # Install SSH key
        mkdir -p ~/.ssh
        echo "$DEPLOY_KEY" > ~/.ssh/id_rsa
        chmod 600 ~/.ssh/id_rsa
        
        # Add server to known hosts
        ssh-keyscan -H $SERVER_IP >> ~/.ssh/known_hosts
        
        # Deploy using rsync
        rsync -avz --exclude '.git' --exclude 'venv' --exclude '__pycache__' ./ $SERVER_USER@$SERVER_IP:/var/www/cozywish-staging/
        
        # Run remote commands for deployment
        ssh $SERVER_USER@$SERVER_IP 'cd /var/www/cozywish-staging && source venv/bin/activate && pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput && sudo systemctl restart cozywish-staging'
```

#### CD Workflow for Production

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    needs: [deploy-staging]  # Require staging deployment first
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: Run tests
      run: |
        python manage.py test
        
    - name: Deploy to production
      env:
        DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
        SERVER_IP: ${{ secrets.PRODUCTION_SERVER_IP }}
        SERVER_USER: ${{ secrets.SERVER_USER }}
      run: |
        # Install SSH key
        mkdir -p ~/.ssh
        echo "$DEPLOY_KEY" > ~/.ssh/id_rsa
        chmod 600 ~/.ssh/id_rsa
        
        # Add server to known hosts
        ssh-keyscan -H $SERVER_IP >> ~/.ssh/known_hosts
        
        # Deploy using rsync
        rsync -avz --exclude '.git' --exclude 'venv' --exclude '__pycache__' ./ $SERVER_USER@$SERVER_IP:/var/www/cozywish-production/
        
        # Run remote commands for deployment
        ssh $SERVER_USER@$SERVER_IP 'cd /var/www/cozywish-production && source venv/bin/activate && pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput && sudo systemctl restart cozywish-production'
```

## Server Configuration

### Nginx Configuration

```nginx
# /etc/nginx/sites-available/cozywish

upstream cozywish_app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name cozywish.com www.cozywish.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name cozywish.com www.cozywish.com;
    
    ssl_certificate /etc/letsencrypt/live/cozywish.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/cozywish.com/privkey.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options SAMEORIGIN;
    add_header X-XSS-Protection "1; mode=block";
    
    # Static files
    location /static/ {
        alias /var/www/cozywish/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }
    
    # Media files
    location /media/ {
        alias /var/www/cozywish/media/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }
    
    # Proxy requests to Django
    location / {
        proxy_pass http://cozywish_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

### Gunicorn Service Configuration

```ini
# /etc/systemd/system/cozywish.service

[Unit]
Description=Gunicorn daemon for CozyWish
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/cozywish
ExecStart=/var/www/cozywish/venv/bin/gunicorn \
    --access-logfile /var/log/cozywish/access.log \
    --error-logfile /var/log/cozywish/error.log \
    --workers 3 \
    --bind 127.0.0.1:8000 \
    project_root.wsgi:application

[Install]
WantedBy=multi-user.target
```

## Database Management

### Backup Strategy

1. **Automated Daily Backups**: RDS automated backups with 7-day retention
2. **Weekly Manual Backups**: Stored in a separate S3 bucket with 3-month retention
3. **Pre-Deployment Backups**: Full database backup before each production deployment

### Backup Script

```bash
#!/bin/bash
# /var/www/cozywish/scripts/backup_db.sh

# Set variables
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/var/backups/cozywish"
S3_BUCKET="cozywish-backups"
DB_NAME="cozywish"
DB_USER="cozywish_user"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Create database dump
pg_dump -U $DB_USER $DB_NAME > $BACKUP_DIR/$DB_NAME\_$TIMESTAMP.sql

# Compress the dump
gzip $BACKUP_DIR/$DB_NAME\_$TIMESTAMP.sql

# Upload to S3
aws s3 cp $BACKUP_DIR/$DB_NAME\_$TIMESTAMP.sql.gz s3://$S3_BUCKET/

# Remove backups older than 7 days
find $BACKUP_DIR -name "*.sql.gz" -type f -mtime +7 -delete
```

### Database Migration Strategy

1. **Development**: Migrations created and tested locally
2. **Staging**: Migrations applied automatically during deployment
3. **Production**: Migrations reviewed and applied manually or with caution during deployment
4. **Rollback Plan**: Backup taken before migration, rollback scripts prepared for complex migrations

## Monitoring and Logging

### Logging Configuration

```python
# settings.py

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/django.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'cozywish': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### Monitoring Tools

1. **AWS CloudWatch**: Server metrics, logs, and alarms
2. **Sentry**: Error tracking and performance monitoring
3. **Uptime Robot**: External uptime monitoring
4. **New Relic**: Application performance monitoring

### Alert Configuration

Alerts are configured for:

1. **Server Health**: CPU, memory, disk usage
2. **Application Errors**: Error rate thresholds
3. **Database Performance**: Slow queries, connection count
4. **Security Events**: Failed login attempts, suspicious activity

## Scaling Strategy

### Horizontal Scaling

1. **Web Tier**: Add EC2 instances behind load balancer
2. **Database Tier**: Read replicas for read-heavy operations
3. **Cache Tier**: Distributed Redis cluster

### Vertical Scaling

1. **Web Tier**: Increase EC2 instance size for CPU/memory-bound workloads
2. **Database Tier**: Upgrade RDS instance class for better performance
3. **Cache Tier**: Increase ElastiCache node size

### Auto Scaling Configuration

```hcl
# Auto Scaling Group for web servers
resource "aws_autoscaling_group" "web_asg" {
  name                 = "cozywish-web-asg"
  launch_configuration = aws_launch_configuration.web_lc.id
  min_size             = 2
  max_size             = 10
  desired_capacity     = 2
  
  vpc_zone_identifier  = [aws_subnet.public_subnet_1.id, aws_subnet.public_subnet_2.id]
  
  target_group_arns    = [aws_lb_target_group.web_tg.arn]
  health_check_type    = "ELB"
  
  tag {
    key                 = "Name"
    value               = "cozywish-web-server"
    propagate_at_launch = true
  }
}

# Auto Scaling Policy based on CPU utilization
resource "aws_autoscaling_policy" "web_scale_up" {
  name                   = "web-scale-up"
  scaling_adjustment     = 1
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 300
  autoscaling_group_name = aws_autoscaling_group.web_asg.name
}

resource "aws_cloudwatch_metric_alarm" "web_cpu_high" {
  alarm_name          = "web-cpu-high"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "120"
  statistic           = "Average"
  threshold           = "80"
  
  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.web_asg.name
  }
  
  alarm_description = "Scale up if CPU > 80% for 2 minutes"
  alarm_actions     = [aws_autoscaling_policy.web_scale_up.arn]
}
```

## Security Practices

1. **Environment Variables**: Sensitive configuration stored in environment variables
2. **Secret Management**: AWS Secrets Manager for production credentials
3. **Network Security**: VPC with private subnets, security groups, and NACLs
4. **Web Application Firewall**: AWS WAF to protect against common attacks
5. **Regular Security Updates**: Automated security patches for servers
6. **Dependency Scanning**: Regular scanning of dependencies for vulnerabilities

## Disaster Recovery

### Backup and Restore

1. **Database**: Daily automated backups with point-in-time recovery
2. **Media Files**: S3 with versioning enabled
3. **Configuration**: Infrastructure as code with version control

### Recovery Time Objective (RTO)

- **Staging Environment**: 1 hour
- **Production Environment**: 4 hours

### Recovery Point Objective (RPO)

- **Staging Environment**: 24 hours
- **Production Environment**: 1 hour

## Conclusion

This deployment and DevOps strategy provides a robust foundation for the CozyWish application, ensuring reliable operation, scalability, and security. By following these practices, the application can be deployed, monitored, and maintained effectively across development, staging, and production environments.
