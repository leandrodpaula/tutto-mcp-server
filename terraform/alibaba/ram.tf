resource "alicloud_ram_role" "app_role" {
  role_name                   = "${var.service_name}-role-${var.environment}"
  assume_role_policy_document = <<EOF
  {
    "Statement": [
      {
        "Action": "sts:AssumeRole",
        "Effect": "Allow",
        "Principal": {
          "Service": [
            "sae.aliyuncs.com"
          ]
        }
      }
    ],
    "Version": "1"
  }
  EOF
}

resource "alicloud_ram_policy" "app_policy" {
  policy_name     = "${var.service_name}-policy-${var.environment}"
  policy_document = <<EOF
  {
    "Statement": [
      {
        "Action": [
          "kms:GetSecretValue",
          "kms:DescribeSecret"
        ],
        "Effect": "Allow",
        "Resource": "*"
      },
      {
        "Action": [
          "cr:GetAuthorizationToken",
          "cr:PullRepository"
        ],
        "Effect": "Allow",
        "Resource": "*"
      }
    ],
    "Version": "1"
  }
  EOF
}

resource "alicloud_ram_role_policy_attachment" "app_attach" {
  policy_name = alicloud_ram_policy.app_policy.policy_name
  policy_type = "Custom"
  role_name   = alicloud_ram_role.app_role.role_name
}
