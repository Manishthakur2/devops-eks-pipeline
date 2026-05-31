variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
  default     = "devops-eks-cluster"
}

variable "instance_type" {
  description = "EC2 instance type for nodes"
  type        = string
  default     = "t3.medium"
}
