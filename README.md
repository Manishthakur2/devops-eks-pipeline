# DevOps EKS Pipeline

A production-grade CI/CD pipeline that automatically deploys a containerized Python Flask application on AWS EKS using Terraform, Docker, Kubernetes, and GitHub Actions.

## Architecture

Developer pushes code -> GitHub Actions triggers -> Docker builds image -> pushes to DockerHub -> Terraform creates VPC + EKS -> Kubernetes deploys app -> AWS LoadBalancer -> app live!

## Tech Stack

- AWS EKS - Managed Kubernetes cluster
- Terraform - Infrastructure as Code
- Docker - Containerization
- Kubernetes - Container orchestration
- GitHub Actions - CI/CD pipeline
- Python Flask - REST API
- AWS VPC - Networking
- AWS IAM - Security and permissions

## Project Structure

devops-eks-pipeline/
├── app/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── k8s/
│   ├── deployment.yml
│   └── service.yml
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
└── .github/
    └── workflows/
        └── deploy.yml

## CI/CD Pipeline

3 Jobs:
1. build     - Builds Docker image and pushes to DockerHub
2. terraform - Creates AWS infrastructure (VPC, EKS)
3. deploy    - Deploys app on Kubernetes

## Infrastructure

Created with Terraform:
- VPC with public subnets in 2 availability zones
- Internet Gateway and Route Tables
- EKS Cluster with managed node groups
- IAM Roles and policies
- AWS LoadBalancer for external access

## API Endpoints

GET  /        - Welcome message
GET  /health  - Health check
GET  /todos   - Get all todos

## How to Run

Prerequisites:
- AWS Account
- DockerHub Account
- Terraform installed
- kubectl installed

Setup GitHub Secrets:
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- DOCKERHUB_USERNAME
- DOCKERHUB_TOKEN

Deploy:
git push origin main
GitHub Actions will automatically deploy!

Destroy Infrastructure:
cd terraform
terraform destroy

## Challenges & Solutions

1. EKS Cluster Creation Failed — Instance Type Restriction
**Error:** Unable to create EKS cluster using t2.medium on AWS Free Tier  
**Root Cause:** AWS Free Tier does not support t2.medium for EKS node groups  
**Solution:** Changed instance type to t3.small in Terraform configuration  
**Learning:** Always verify AWS Free Tier limitations before defining infrastructure specs

---

2. IAM Role Conflict — Resource Already Exists
**Error:** IAM roles could not be created because identical roles already existed in AWS  
**Root Cause:** Previous failed pipeline run had partially created IAM resources  
**Solution:** Manually deleted conflicting IAM roles via AWS Console, then reran pipeline  
**Learning:** Terraform state can become inconsistent after partial runs — always verify resource state before rerunning

---

3. Deployment File Name Mismatch
**Error:** Deploy stage failed — could not find deployment file  
**Root Cause:** File was named deployment.yml but workflow referenced deployment.yaml  
**Solution:** Standardized file extension to match workflow configuration  
**Learning:** File naming consistency is critical in CI/CD pipelines

---

4. DockerHub Authentication Failure
**Error:** Pipeline could not login to DockerHub during deploy stage  
**Root Cause:** GitHub Secret was saved as DOCKERHUB_PASSWORD but workflow referenced DOCKERHUB_TOKEN  
**Solution:** Updated workflow variable name to match the GitHub Secret exactly  
**Learning:** Secret naming must be identical between GitHub Secrets and workflow references

## Author
Manish Thakur
LinkedIn: https://www.linkedin.com/in/munish-kumar-a64277200/
GitHub: https://github.com/Manishthakur2/devops-eks-pipeline
