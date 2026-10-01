# Production-Grade AWS EKS CI/CD Pipeline

[![Terraform](https://img.shields.io/badge/IaC-Terraform-623CE4?logo=terraform&logoColor=white)](https://www.terraform.io/)
[![AWS EKS](https://img.shields.io/badge/AWS-EKS-FF9900?logo=amazon-aws&logoColor=white)](https://aws.amazon.com/eks/)
[![Docker](https://img.shields.io/badge/Container-Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Orchestration-Kubernetes-326CE5?logo=kubernetes&logoColor=white)](https://kubernetes.io/)
[![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub_Actions-2088FF?logo=github-actions&logoColor=white)](https://github.com/features/actions)

An automated end-to-end CI/CD pipeline that provisions cloud infrastructure on AWS using Terraform and deploys a containerized Python Flask REST API onto an Amazon EKS managed Kubernetes cluster using GitHub Actions.

---

## Architecture Flow

```text
[Developer Push]
       │
       ▼
[GitHub Actions Workflow]
  ├── Job 1: Build Docker Image ──► Push to Docker Hub
  ├── Job 2: Terraform Apply (S3 Backend + DynamoDB Lock) ──► Provisions VPC, Subnets, IAM, EKS Cluster & Node Groups
  └── Job 3: Authenticate kubectl (AWS STS) ──► Apply K8s Manifests (Deployment + LoadBalancer Service)
       │
       ▼
[AWS Load Balancer] ──► [EKS Worker Nodes / Pods] ──► Live Application
```
---

## Tech Stack

* **Cloud Provider:** AWS (VPC, EKS, EC2, IAM, S3, DynamoDB, ELB)
* **Infrastructure as Code (IaC):** Terraform
* **Containerization:** Docker
* **Container Orchestration:** Kubernetes (Amazon EKS)
* **CI/CD Pipeline:** GitHub Actions
* **Application Framework:** Python Flask
* **Registry:** Docker Hub

---

## Infrastructure Architecture (Terraform)

The Terraform configuration creates a reliable, isolated cloud environment:

* **Remote State Management:** Configured an S3 backend with DynamoDB table locking to prevent concurrent state modifications and race conditions.
* **Custom VPC:** 
  * Spans 2 Availability Zones (us-east-1a, us-east-1b) for high availability.
  * 2 Public Subnets tagged with "kubernetes.io/role/elb" = "1" for dynamic AWS Load Balancer discovery.
  * Internet Gateway (IGW) and Route Tables routing outbound traffic to 0.0.0.0/0.
* **IAM Least-Privilege Roles:**
  * **EKS Cluster Role:** Attached AmazonEKSClusterPolicy.
  * **EKS Node Group Role:** Attached AmazonEKSWorkerNodePolicy, AmazonEKS_CNI_Policy, and AmazonEC2ContainerRegistryReadOnly.
* **EKS Managed Node Group:** Configured with auto-scaling limits (min: 1, desired: 2, max: 3).

---

## Project Structure
```text
devops-eks-pipeline/
├── .github/
│   └── workflows/
│       └── deploy.yml
├── app/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── k8s/
│   ├── deployment.yml
│   └── service.yml
└── terraform/
    ├── main.tf
    ├── variables.tf
    └── outputs.tf
```
---

## CI/CD Pipeline Stages

The GitHub Actions workflow triggers automatically on push to the main branch:

1. **Build & Push (build):**
   * Checks out the repository.
   * Authenticates to Docker Hub using GitHub Encrypted Secrets.
   * Builds the Docker image from ./app/Dockerfile and pushes it with the :latest tag.

2. **Provision Infrastructure (terraform):**
   * Configures temporary AWS credentials via aws-actions/configure-aws-credentials.
   * Sets up Terraform CLI.
   * Runs terraform init and terraform apply -auto-approve against the remote S3 state backend.

3. **Deploy to Kubernetes (deploy):**
   * Assumes IAM deployment credentials.
   * Generates local kubeconfig using aws eks update-kubeconfig.
   * Applies Kubernetes manifests (deployment.yml and service.yml) to execute a rolling update.

---

## API Endpoints

Once the AWS Load Balancer finishes provisioning, the application exposes the following endpoints:

| Method | Endpoint | Description |
|---|---|---|
| GET | / | Service status welcome response |
| GET | /health | Container health check endpoint |
| GET | /todos | Returns sample task dataset |

---

## Setup & Deployment Guide

### Prerequisites
* An active AWS Account with programmatic access keys (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY).
* A Docker Hub account and access token.
* An active S3 Bucket and DynamoDB table created for the Terraform remote backend.

### 1. Configure GitHub Secrets
Navigate to Settings > Secrets and variables > Actions in your GitHub repository and add:
* AWS_ACCESS_KEY_ID
* AWS_SECRET_ACCESS_KEY
* DOCKERHUB_USERNAME
* DOCKERHUB_TOKEN

### 2. Trigger Automated Deployment
Commit and push code changes directly to the main branch:
```text
git add .
git commit -m "feat: trigger automated eks deployment"
git push origin main
```
Track the build and deployment progress under the Actions tab of the repository.

### 3. Teardown / Destroy Infrastructure
To prevent ongoing AWS compute and load balancer costs:
```text
cd terraform
terraform init
terraform destroy -auto-approve
```
---

## Real Engineering Challenges & Root Cause Analysis

Documenting production setup issues and their resolutions:

### 1. EKS Node Provisioning Failure (Instance Type Quotas)
* **Error:** Unable to launch EKS managed node group worker instances using t2.medium.
* **Root Cause:** Account/regional availability constraints and compute quota limits restricted t2.medium provisioning during deployment.
* **Resolution:** Parameterized the instance type variable to t3.small in variables.tf, verifying compatibility with EKS requirements while maintaining cost-efficiency.

### 2. IAM Role Conflicts (EntityAlreadyExists)
* **Error:** Terraform failed at aws_iam_role.eks_role stating the role name already existed in AWS IAM.
* **Root Cause:** An interrupted previous pipeline execution left orphaned IAM policies in AWS that were not recorded in the remote state file.
* **Resolution:** Cleaned up orphaned IAM resources from the AWS Console and ensured subsequent runs properly tracked all provisioned ARNs inside the remote S3 backend state.

### 3. Pipeline Deployment Stage Failure (deployment.yaml Not Found)
* **Error:** kubectl apply -f failed with file path errors during the final CI/CD stage.
* **Root Cause:** Discrepancy between manifest file naming in the repository (deployment.yml) versus the GitHub Actions configuration command (deployment.yaml).
* **Resolution:** Standardized all Kubernetes manifest references across repository files to use .yml.

### 4. Docker Hub Registry Authentication Failure
* **Error:** Docker CLI returned unauthorized: incorrect username or password during image push.
* **Root Cause:** The GitHub Actions workflow referenced the secret key ${{ secrets.DOCKERHUB_TOKEN }}, but the secret had been created under the key name DOCKERHUB_PASSWORD.
* **Resolution:** Aligned GitHub Actions secret references to match the exact secret key names defined in the repository settings.

---

## Author

**Munish Kumar**  
* **LinkedIn:** [Munish Kumar](https://www.linkedin.com/in/munish-kumar-a64277200/)  
* **GitHub:** [@Manishthakur2](https://github.com/Manishthakur2)
