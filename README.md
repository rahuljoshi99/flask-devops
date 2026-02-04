Automated CI/CD Pipeline for a 2-Tier Flask Application on AWS
Project Overview
This project implements a fully automated CI/CD pipeline for deploying a 2-tier web application (Flask + MySQL) on AWS using containerization with Docker and orchestration with Jenkins. The pipeline automates the entire build and deployment process triggered by code commits to a GitHub repository.

Author: Rahul Joshi
Date: February 04, 2026
Technology Stack: AWS EC2, Docker, Docker Compose, Jenkins, Flask, MySQL, Git

Table of Contents
Architecture Overview

Prerequisites & Setup

AWS Infrastructure Configuration

Dependency Installation

Jenkins Setup

Application Configuration Files

Pipeline Implementation

Deployment Verification

Diagrams

Conclusion & Future Enhancements

Architecture Overview
System Architecture
text
Developer → GitHub Repository → Jenkins Server (EC2) → Application Server (EC2)
                                                              ↓
                                              Docker Container: Flask
                                                              ↓
                                              Docker Container: MySQL
Workflow
Code Commit: Developer pushes code to GitHub repository

Trigger: Jenkins detects changes via webhook

Build: Jenkins clones repository and builds Docker image

Deploy: Docker Compose orchestrates multi-container deployment

Verification: Application health checks and service availability

Prerequisites & Setup
Required Tools & Accounts
AWS Account (Free Tier eligible)

GitHub Account

Basic understanding of Linux commands

SSH client for EC2 access

AWS Infrastructure Configuration
EC2 Instance Launch
AMI: Ubuntu 22.04 LTS

Instance Type: t3.small (Free Tier eligible)

Key Pair: New key pair created for SSH access

Storage: 8GB GP2 EBS volume

Security Group Configuration
Type	Protocol	Port	Source	Purpose
SSH	TCP	22	Your IP	Secure shell access
HTTP	TCP	80	0.0.0.0/0	Web traffic
Custom TCP	TCP	5000	0.0.0.0/0	Flask application
Custom TCP	TCP	8080	0.0.0.0/0	Jenkins dashboard
Security Group Screenshot:
https://github.com/user-attachments/assets/3b0fcc11-f98e-43ac-aeb0-f776b40890e9

Connection to EC2
bash
ssh -i /path/to/your-key.pem ubuntu@<ec2-public-ip>
Dependency Installation
System Update & Upgrade
bash
sudo apt update && sudo apt upgrade -y
Install Core Dependencies
bash
# Install Git, Docker, and Docker Compose
sudo apt install git docker.io docker-compose-v2 -y

# Start and enable Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add current user to docker group
sudo usermod -aG docker $USER
newgrp docker
Jenkins Setup
Java Installation
bash
sudo apt install openjdk-17-jdk -y
Jenkins Installation
bash
# Add Jenkins repository
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key | sudo tee \
  /usr/share/keyrings/jenkins-keyring.asc > /dev/null

echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
  https://pkg.jenkins.io/debian-stable binary/ | sudo tee \
  /etc/apt/sources.list.d/jenkins.list > /dev/null

# Install Jenkins
sudo apt update
sudo apt install jenkins -y

# Start and enable Jenkins
sudo systemctl start jenkins
sudo systemctl enable jenkins
Jenkins Initial Configuration
Retrieve initial admin password:

bash
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
Access Jenkins dashboard:

text
http://<ec2-public-ip>:8080
Complete setup wizard:

Install suggested plugins

Create admin user

Configure instance settings

Grant Docker Permissions to Jenkins
bash
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
Jenkins Dashboard Screenshot:
https://github.com/user-attachments/assets/dde829b5-30e6-47f0-98ee-31cf123ccc5f

Application Configuration Files
Dockerfile
dockerfile
# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for mysqlclient
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements file to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]
docker-compose.yml
yaml
version: "3.8"

services:
  mysql:
    container_name: mysql
    image: mysql
    environment:
      MYSQL_DATABASE: "devops"
      MYSQL_ROOT_PASSWORD: "root"
    ports:
      - "3306:3306"
    volumes:
      - mysql-data:/var/lib/mysql
    networks:
      - two-tier
    restart: always
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-uroot", "-proot"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 60s

  flask:
    build:
      context: .
    container_name: two-tier-app
    ports:
      - "5000:5000"
    environment:
      - MYSQL_HOST=mysql
      - MYSQL_USER=root
      - MYSQL_PASSWORD=root
      - MYSQL_DB=devops
    networks:
      - two-tier
    depends_on:
      - mysql
    restart: always
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:5000/health || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 60s

volumes:
  mysql-data:

networks:
  two-tier:
Jenkinsfile (Pipeline-as-Code)
groovy
pipeline {
  agent any
    
  stages {
        stage('Clone Repository') {
            steps {
                git branch: 'main', 
                url: 'https://github.com/your-username/your-repo.git'
            }
        }
        
  stage('Build Docker Image') {
            steps {
                sh 'docker build -t flask-app:latest .'
            }
        }
        
  stage('Deploy with Docker Compose') {
            steps {
                // Stop existing containers if they are running
                sh 'docker compose down || true'
                // Start the application, rebuilding the flask image
                sh 'docker compose up -d --build'
            }
        }
        
  stage('Health Check') {
            steps {
                script {
                    sleep 30  # Wait for services to start
                    sh 'curl -f http://localhost:5000/health || exit 1'
                }
            }
        }
    }
    
  post {
        success {
            echo 'Pipeline executed successfully!'
            echo 'Application deployed at http://<ec2-public-ip>:5000'
        }
        failure {
            echo 'Pipeline execution failed!'
        }
    }
}
Pipeline Implementation
Jenkins Pipeline Configuration
Create New Pipeline Job

Navigate to Jenkins Dashboard → New Item

Enter project name (e.g., "flask-app-ci-cd")

Select "Pipeline" and click OK

Configure Pipeline Settings

Definition: Pipeline script from SCM

SCM: Git

Repository URL: Your GitHub repository

Branch Specifier: */main

Script Path: Jenkinsfile

Webhook Configuration (Optional)

Configure GitHub webhook to trigger pipeline on push

Webhook URL: http://<ec2-public-ip>:8080/github-webhook/

Pipeline Execution
bash
# Manual trigger from Jenkins dashboard
# Or automatic trigger via GitHub webhook
Pipeline Execution Screenshot:
https://github.com/user-attachments/assets/3aa5f58b-34e3-415e-a8d8-f20b2f37d270

Deployment Verification
Verify Running Containers
bash
# Check container status
docker ps

# Expected output
CONTAINER ID   IMAGE          COMMAND                  STATUS       PORTS
xxxxxxxxxxxx   flask-app      "python app.py"          Up 5 min     0.0.0.0:5000->5000/tcp
xxxxxxxxxxxx   mysql:latest   "docker-entrypoint..."   Up 5 min     0.0.0.0:3306->3306/tcp
Access Application
Flask Application: http://<ec2-public-ip>:5000

Health Endpoint: http://<ec2-public-ip>:5000/health

Jenkins Dashboard: http://<ec2-public-ip>:8080

View Application Logs
bash
# Flask application logs
docker logs two-tier-app

# MySQL container logs
docker logs mysql

# Combined logs via Docker Compose
docker compose logs -f
Diagrams
Infrastructure Architecture
https://github.com/user-attachments/assets/8d79ea29-ceb1-475b-beb0-73c26625ea13

Workflow Diagram
https://github.com/user-attachments/assets/c32c0623-6bc2-4eeb-8406-b2cb0faeb625

Detailed Architecture Flow
text
+-----------------+     +----------------------+     +---------------------------+
|   Developer     |---->|     GitHub Repo      |---->|       Jenkins Server      |
| (pushes code)   |     | (Source Code Mgmt)   |     |        (on EC2)           |
+-----------------+     +----------------------+     +---------------------------+
                                                                  |
                                                                  | (Executes Pipeline)
                                                                  v
                                                    +---------------------------+
                                                    |    Application Server     |
                                                    |        (Same EC2)         |
                                                    |                           |
                                                    | +-----------------------+ |
                                                    | | Docker: Flask App     | |
                                                    | | Port: 5000            | |
                                                    | +-----------------------+ |
                                                    |                           |
                                                    | +-----------------------+ |
                                                    | | Docker: MySQL         | |
                                                    | | Port: 3306            | |
                                                    | +-----------------------+ |
                                                    +---------------------------+
Conclusion & Future Enhancements
Project Achievements
✅ Complete CI/CD Pipeline Implementation
✅ Automated Build and Deployment Process
✅ Containerized Application with Docker
✅ Infrastructure as Code (IaC) Approach
✅ Health Monitoring and Auto-recovery
✅ Source Control Integration with GitHub

Future Enhancements
Infrastructure as Code: Implement Terraform for AWS resource management

Container Orchestration: Migrate to Kubernetes for better scalability

Monitoring Stack: Integrate Prometheus and Grafana for observability

Security Enhancement: Implement secret management with HashiCorp Vault

Multi-environment Setup: Staging and production environments

Testing Integration: Add unit, integration, and security testing stages

Notification System: Slack/Email notifications for pipeline status

Key Learnings
AWS EC2 instance management and security group configuration

Docker containerization and multi-service orchestration

Jenkins pipeline-as-code implementation

CI/CD best practices for web applications

Automated health checks and monitoring

Integration of multiple technologies in a cohesive workflow

Troubleshooting Tips
Jenkins permission issues: Ensure Jenkins user is in docker group

Port conflicts: Verify no other services are using ports 5000, 8080, or 3306

Docker build failures: Check network connectivity and Dockerfile syntax

Application not accessible: Verify security group rules and container status

Database connection issues: Ensure MySQL container is healthy before Flask starts

Repository Structure Recommendation
text
flask-two-tier-app/
├── README.md                    # Project documentation (this file)
├── src/
│   ├── app.py                   # Flask application
│   ├── requirements.txt         # Python dependencies
│   ├── templates/               # HTML templates
│   └── static/                  # Static files
├── docker/
│   ├── Dockerfile              # Docker configuration
│   └── docker-compose.yml      # Multi-container orchestration
├── jenkins/
│   └── Jenkinsfile             # Pipeline definition
├── terraform/                  # Infrastructure as Code (future)
│   └── main.tf
├── scripts/                    # Deployment scripts
│   └── deploy.sh
├── tests/                      # Test cases
│   └── test_app.py
└── docs/                       # Additional documentation
    └── architecture.md
Note: This project demonstrates a production-ready CI/CD pipeline setup. For production deployment, consider implementing additional security measures, proper secret management, and comprehensive monitoring solutions.

Contact: For questions or contributions, please open an issue in the GitHub repository.
