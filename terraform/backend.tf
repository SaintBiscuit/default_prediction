# terraform {
#   backend "s3" {
#     endpoints = {
#       s3 = "https://storage.yandexcloud.net"
#     }
#     bucket = "tf-state-credit-scoring"
#     region = "ru-central1"
#     key    = "mlops-pj/terraform.tfstate"
#
#     skip_region_validation      = true
#     skip_credentials_validation = true
#     skip_s3_checksum            = true
#     skip_requesting_account_id  = true
#     skip_metadata_api_check     = true
#   }
# }

# Remote backend отключён на время разработки
# State будет храниться локально в файле terraform.tfstate
