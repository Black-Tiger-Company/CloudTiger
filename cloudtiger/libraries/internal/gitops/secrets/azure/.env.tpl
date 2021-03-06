export CREDENTIALS=$(pwd)/secrets/azure
export SERVICE_PRINCIPAL=$CREDENTIALS/service_principal.json
export SUBSCRIPTION_ID=$(cat $CREDENTIALS/az_account.json | grep subscriptionId | cut -d '"' -f 4)
export TF_VAR_client_id=$(cat $SERVICE_PRINCIPAL | grep appId | cut -d '"' -f 4)
export TF_VAR_client_secret=$(cat $SERVICE_PRINCIPAL | grep password | cut -d '"' -f 4)
export ARM_SUBSCRIPTION_ID=$SUBSCRIPTION_ID
export ARM_CLIENT_ID=$(cat $SERVICE_PRINCIPAL | grep appId | cut -d '"' -f 4)
export ARM_CLIENT_SECRET=$(cat $SERVICE_PRINCIPAL | grep password | cut -d '"' -f 4)
export ARM_TENANT_ID=$(cat $SERVICE_PRINCIPAL | grep tenant | cut -d '"' -f 4)
export ARM_ENVIRONMENT=public