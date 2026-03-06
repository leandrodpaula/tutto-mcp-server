terraform {
  backend "gcs" {
    # As configurações 'bucket' e 'prefix' são aplicadas dinamicamente
    # no terraform init através do script terraform.sh.
  }
}
