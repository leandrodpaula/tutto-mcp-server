terraform {
  required_providers {
    alicloud = {
      source  = "aliyun/alicloud"
      version = ">= 1.210.0"
    }
  }

  required_version = ">= 1.5.0"
}

provider "alicloud" {
  region = var.region
}
