terraform {
  backend "oss" {
    # Configurações 'bucket', 'prefix', 'region' etc. são aplicadas dinamicamente
    # no terraform init via variáveis de ambiente ou parâmetros.
    # Exemplo:
    # terraform init \
    #   -backend-config="bucket=<your-oss-bucket>" \
    #   -backend-config="prefix=tutto-mcp-server/terraform" \
    #   -backend-config="region=cn-hangzhou"
  }
}
