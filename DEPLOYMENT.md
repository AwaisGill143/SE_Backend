# Deployment Guide

## Pre-Deployment Checklist

- [ ] All environment variables configured
- [ ] Database backups in place
- [ ] SSL certificates obtained
- [ ] API keys validated
- [ ] Load testing completed
- [ ] Security audit completed
- [ ] Documentation updated
- [ ] Rollback plan documented

---

## Deployment Options

## 1. Heroku Deployment

### Prerequisites
- Heroku account and CLI installed
- Git repository initialized

### Steps

1. **Create Heroku App**
```bash
heroku create careerlaunch-api
```

2. **Add PostgreSQL Add-on**
```bash
heroku addons:create heroku-postgresql:standard-0 --app careerlaunch-api
```

3. **Add Redis Add-on**
```bash
heroku addons:create heroku-redis:premium-0 --app careerlaunch-api
```

4. **Set Environment Variables**
```bash
heroku config:set OPENAI_API_KEY=sk-... --app careerlaunch-api
heroku config:set SECRET_KEY=... --app careerlaunch-api
# ... set other variables
```

5. **Deploy**
```bash
git push heroku main
```

6. **View Logs**
```bash
heroku logs --tail --app careerlaunch-api
```

---

## 2. AWS EC2 Deployment

### Prerequisites
- AWS Account
- EC2 instance running Ubuntu 20.04+
- SSH access configured

### Steps

1. **Connect to Instance**
```bash
ssh -i your-key.pem ubuntu@your-instance-ip
```

2. **Install Dependencies**
```bash
sudo apt update
sudo apt install -y python3.11 python3-pip postgresql postgresql-contrib redis-server nginx
```

3. **Clone Repository**
```bash
cd /home/ubuntu
git clone <your-repo-url> careerlaunch-backend
cd careerlaunch-backend
```

4. **Setup Virtual Environment**
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

5. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with production settings
```

6. **Setup Database**
```bash
sudo -u postgres createdb careerlaunch_db
sudo -u postgres createuser careerlaunch
```

7. **Run Migrations**
```bash
alembic upgrade head
```

8. **Create Systemd Service**
```bash
sudo nano /etc/systemd/system/careerlaunch.service
```

Add:
```ini
[Unit]
Description=CareerLaunch AI Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/careerlaunch-backend
ExecStart=/home/ubuntu/careerlaunch-backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

9. **Enable Service**
```bash
sudo systemctl enable careerlaunch
sudo systemctl start careerlaunch
```

10. **Configure Nginx**
```bash
sudo nano /etc/nginx/sites-available/careerlaunch
```

Add reverse proxy configuration (similar to nginx.conf)

11. **Enable Nginx Site**
```bash
sudo ln -s /etc/nginx/sites-available/careerlaunch /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

---

## 3. Docker Swarm Deployment

### Prerequisites
- Docker and Docker Compose installed
- Multiple Docker hosts (for clustering)

### Steps

1. **Initialize Swarm**
```bash
docker swarm init
docker swarm join-token worker
```

2. **Deploy Stack**
```bash
docker stack deploy -c docker-compose.yml careerlaunch
```

3. **Verify Deployment**
```bash
docker stack services careerlaunch
docker service logs careerlaunch_backend
```

4. **Scale Service**
```bash
docker service scale careerlaunch_backend=3
```

---

## 4. Kubernetes Deployment

### Prerequisites
- Kubernetes cluster (EKS, GKE, AKS, or local)
- kubectl configured
- Docker images pushed to registry

### Steps

1. **Create Namespace**
```bash
kubectl create namespace careerlaunch
```

2. **Create ConfigMap for Environment**
```bash
kubectl create configmap backend-config --from-file=.env -n careerlaunch
```

3. **Create Deployment**
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: careerlaunch
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: your-registry/careerlaunch-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            configMapKeyRef:
              name: backend-config
              key: DATABASE_URL
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
```

4. **Create Service**
```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: careerlaunch
spec:
  type: LoadBalancer
  selector:
    app: backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
```

5. **Deploy**
```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

6. **Monitor**
```bash
kubectl get pods -n careerlaunch
kubectl logs -n careerlaunch pod/backend-xxxxx
```

---

## SSL/TLS Setup

### Using Let's Encrypt with Nginx

1. **Install Certbot**
```bash
sudo apt install certbot python3-certbot-nginx
```

2. **Get Certificate**
```bash
sudo certbot certonly --nginx -d your-domain.com
```

3. **Update Nginx Configuration**
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # ... rest of configuration
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

4. **Auto-Renewal**
```bash
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

---

## Monitoring & Logging

### Application Monitoring

1. **Setup Prometheus**
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'careerlaunch'
    static_configs:
      - targets: ['localhost:8000']
```

2. **Setup Grafana**
```bash
docker run -d -p 3000:3000 grafana/grafana
```

### Log Aggregation

1. **Using ELK Stack**
```bash
docker-compose up -d elasticsearch kibana logstash
```

2. **Configure Logstash to Collect Logs**
```logstash
input {
  file {
    path => "/var/log/careerlaunch/*.log"
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
  }
}
```

---

## Performance Optimization

### Database Optimization
```bash
# Analyze slow queries
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';

# Create indexes
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_job_analysis_user ON job_analyses(user_id);
```

### Caching Strategy
```python
# Cache learning paths
@cache.cached(timeout=3600)
def get_learning_paths(user_id):
    return LearningPathService.get_user_learning_paths(user_id)
```

### Load Balancing
```nginx
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
    least_conn;
}
```

---

## Rollback Plan

### Database Rollback
```bash
# Create backup before deployment
pg_dump careerlaunch_db > pre_deployment_backup.sql

# If something goes wrong
psql careerlaunch_db < pre_deployment_backup.sql
```

### Application Rollback
```bash
# Docker rollback
docker service update --image registry/careerlaunch:old-version careerlaunch_backend

# Kubernetes rollback
kubectl rollout undo deployment/backend -n careerlaunch
```

---

## Disaster Recovery

### Backup Strategy
```bash
# Daily backups
0 2 * * * /scripts/backup.sh

# Weekly backups
0 3 * * 0 /scripts/backup-full.sh
```

### Backup Script
```bash
#!/bin/bash
BACKUP_DIR=/backups
DATE=$(date +%Y%m%d_%H%M%S)

pg_dump -Fc careerlaunch_db > $BACKUP_DIR/db_$DATE.sql
tar -czf $BACKUP_DIR/app_$DATE.tar.gz /home/ubuntu/careerlaunch-backend
aws s3 cp $BACKUP_DIR/ s3://my-backups/ --recursive
```

---

## Maintenance & Updates

### Update Dependencies
```bash
pip list --outdated
pip install --upgrade package-name
```

### Database Maintenance
```bash
# Vacuum and analyze
VACUUM ANALYZE;

# Monitor connections
SELECT count(*) FROM pg_stat_activity;
```

---

## Troubleshooting Deployment Issues

### Out of Memory
```bash
# Check memory usage
free -h
top

# Increase swap (temporary)
sudo swapon /swapfile
```

### High CPU Usage
```bash
# Identify processes
ps aux --sort=-%cpu
```

### Slow Queries
```sql
-- Enable slow query log
SET log_min_duration_statement = 5000;

-- Check query performance
SELECT query, calls, mean_time FROM pg_stat_statements ORDER BY mean_time DESC;
```

---

**For production deployments, always test in a staging environment first!**
