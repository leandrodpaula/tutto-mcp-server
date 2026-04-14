data "alicloud_zones" "default" {
  available_resource_creation = "VSwitch"
}

resource "alicloud_vpc" "default" {
  vpc_name   = "${var.service_name}-vpc-${var.environment}"
  cidr_block = "10.4.0.0/16"
}

resource "alicloud_vswitch" "default" {
  vswitch_name = "${var.service_name}-vswitch-${var.environment}"
  cidr_block   = "10.4.0.0/24"
  vpc_id       = alicloud_vpc.default.id
  zone_id      = data.alicloud_zones.default.zones[0].id
}

resource "alicloud_security_group" "default" {
  security_group_name = "${var.service_name}-sg-${var.environment}"
  vpc_id              = alicloud_vpc.default.id
}

resource "alicloud_security_group_rule" "allow_ingress_tcp_app_port" {
  type              = "ingress"
  ip_protocol       = "tcp"
  nic_type          = "intranet"
  policy            = "accept"
  port_range        = "${var.app_port}/${var.app_port}"
  priority          = 1
  security_group_id = alicloud_security_group.default.id
  cidr_ip           = "0.0.0.0/0"
}
