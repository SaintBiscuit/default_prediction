terraform {
  required_version = ">= 1.0"

  required_providers {
    yandex = {
      source  = "yandex-cloud/yandex"
      version = "0.175.0"
    }
  }
}

provider "yandex" {
  cloud_id  = "b1grcvfftgev56mu0j7q"
  folder_id = "b1gvf0jo3m8s213vn84h"
  zone      = "ru-central1-a"

  service_account_key_file = "../yc-terraform-key.json"
}
# VPC network
resource "yandex_vpc_network" "mlops_net" {
  name        = "mlops-credit-scoring-net"
  description = "VPC for MLOps credit scoring PJ"
}

# Subnets in different zones
resource "yandex_vpc_subnet" "subnet_a" {
  name           = "subnet-ru-central1-a"
  zone           = "ru-central1-a"
  network_id     = yandex_vpc_network.mlops_net.id
  v4_cidr_blocks = ["10.1.0.0/24"]
}

resource "yandex_vpc_subnet" "subnet_b" {
  name           = "subnet-ru-central1-b"
  zone           = "ru-central1-b"
  network_id     = yandex_vpc_network.mlops_net.id
  v4_cidr_blocks = ["10.2.0.0/24"]
}

resource "yandex_vpc_subnet" "subnet_d" {
  name           = "subnet-ru-central1-d"
  zone           = "ru-central1-d"
  network_id     = yandex_vpc_network.mlops_net.id
  v4_cidr_blocks = ["10.3.0.0/24"]
}
# Managed Kubernetes cluster
resource "yandex_kubernetes_cluster" "credit_scoring_cluster" {
  name        = "credit-scoring-cluster"
  description = "Managed Kubernetes for credit scoring MLOps PJ"

  network_id = yandex_vpc_network.mlops_net.id

  master {
    version = "1.30"

    zonal {
      zone      = "ru-central1-a"
      subnet_id = yandex_vpc_subnet.subnet_a.id
    }

    public_ip = true

    maintenance_policy {
      auto_upgrade = true

      maintenance_window {
        day        = "monday"
        start_time = "03:00"
        duration   = "3h"
      }
    }
  }

  service_account_id      = "ajefch1h45aa9f5qmmmm"  # твой ID
  node_service_account_id = "ajefch1h45aa9f5qmmmm"  # тот же

  release_channel = "REGULAR"
  network_policy_provider = "CALICO"
}

# CPU node group
resource "yandex_kubernetes_node_group" "cpu_nodes" {
  cluster_id = yandex_kubernetes_cluster.credit_scoring_cluster.id
  name       = "cpu-nodes"
  version    = "1.30"

  instance_template {
    platform_id = "standard-v3"

    resources {
      memory = 8
      cores  = 4
    }

    boot_disk {
      type = "network-ssd"
      size = 64
    }

    scheduling_policy {
      preemptible = false
    }
  }

  scale_policy {
    auto_scale {
      min     = 2
      max     = 10
      initial = 2
    }
  }

  allocation_policy {
    location {
      zone = "ru-central1-a"
    }
  }

  maintenance_policy {
    auto_upgrade = true
    auto_repair  = true
  }
}

# GPU node group (опционально, но для баллов — добавляем 1 GPU ноду)
resource "yandex_kubernetes_node_group" "gpu_nodes" {
  cluster_id = yandex_kubernetes_cluster.credit_scoring_cluster.id
  name       = "gpu-nodes"
  version    = "1.30"

  instance_template {
    platform_id = "g2.v1"  # GPU platform (NVIDIA Tesla T4)

    resources {
      memory = 32
      cores  = 8
      gpus   = 1
    }

    boot_disk {
      type = "network-ssd"
      size = 100
    }

    scheduling_policy {
      preemptible = false
    }
  }

  scale_policy {
    fixed_scale {
      size = 1
    }
  }

  allocation_policy {
    location {
      zone = "ru-central1-b"
    }
  }
}