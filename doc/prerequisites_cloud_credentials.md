# Prerequisites for running CloudTiger on public cloud providers
- [Prerequisites for running CloudTiger on public cloud providers](#prerequisites-for-running-cloudtiger-on-public-cloud-providers)
	- [GCP](#gcp)
	- [AWS](#aws)
	- [Azure](#azure)
	- [vSphere](#vsphere)
	- [Nutanix](#nutanix)

In order to run CloudTiger on a public cloud providers (AWS, Azure or GCP) or a private one (vSphere, Nutanix) for infrastructure hosting, you will need to collect the credentials associated with a cloud account, in a format readable by Terraform (the tool used by CloudTiger under the hood for managing cloud infrastructures).

Follow the instructions for the cloud provider of your choice :

## GCP

You will need to create an SSH key locally :

```bash
ssh-keygen -o -t rsa -b 4096 -C "<YOUR_EMAIL>"
```

In order to prepare Terraform for GCP use, you will need to follow the tutorial [here](https://cloud.google.com/community/tutorials/getting-started-on-gcp-with-terraform) until the 'Getting project credentials' section included.

At the end of this section, you will be able to download a json file containing project credentials to access the GCP APIs remotely with Terraform.

In order to download this json credentials file, once you have created your account, you can go directly to this [link](https://console.cloud.google.com/apis/credentials/serviceaccountkey).

Once it is done, get credential templates for GCP :

```
cp secrets/gcp/.env.tpl secrets/gcp/.env
cp secrets/gcp/credentials.json.tpl secrets/gcp/credentials.json
```

And use the json file you just downloaded to fill the `secrets/gcp/credentials.json`, and the `secrets/gcp/.env`.

You will also need to 'enable' the APIs for the services you need by activating the following links :

- [kubernetes](https://console.cloud.google.com/apis/api/container.googleapis.com)
- [compute](https://console.cloud.google.com/apis/api/compute.googleapis.com)
- [containerregistry](https://console.cloud.google.com/apis/api/containerregistry.googleapis.com)
- [iamcredentials](https://console.cloud.google.com/apis/api/iamcredentials.googleapis.com)
- [iam](https://console.cloud.google.com/apis/api/iam.googleapis.com)

The link to all the service APIs is [here](https://console.cloud.google.com/apis/dashboard). You can activate other services' API if needed.

## AWS

In order to prepare Terraform for AWS use, you will need to get Programmatic Access credentials, following the tutorial [here](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys)

You will obtain a .csv file containing your programmatic access credentials

First, get a credential template for AWS :

```
cp secrets/aws/.env.tpl secrets/aws/.env
```

Then, use the content of the csv to fill the file `secrets/aws/.env`.

## Azure

In order to prepare Terraform for Azure use, you will need to follow the tutorial [here]](https://docs.microsoft.com/en-us/azure/virtual-machines/linux/terraform-install-configure)

Get the subscription ID for Azure CLI

```bash
az account show --query "{subscriptionId:id, tenantId:tenantId}"
export SUBSCRIPTION_ID=$(az account show --query "{subscriptionId:id, tenantId:tenantId}" | grep subscriptionId | cut -d '"' -f 4)
```

Then

```bash
az account set --subscription="${SUBSCRIPTION_ID}"
az ad sp create-for-rbac --role="Owner" --scopes="/subscriptions/${SUBSCRIPTION_ID}"
```

First, get credential templates for Azure :

```
cp secrets/azure/.env.tpl secrets/azure/.env
cp secrets/azure/az_account.json.tpl secrets/azure/az_account.json
cp secrets/azure/service_principal.json.tpl secrets/azure/service_principal.json
```

Then, use the output of the `az` command above to fill the file `secrets/azure/.env`, `secrets/azure/az_account.json` and `secrets/azure/service_principal.json`.

## vSphere

In order to use the vSphere modules with a vSphere cluster, you will need to set the following `secrets/vsphere/.env` file :

```
export TF_VAR_vsphere_user=<YOUR_NUTANIX_USERNAME>
export TF_VAR_vsphere_password=<YOUR_NUTANIX_PASSWORD>
export TF_VAR_vsphere_url=<YOUR_NUTANIX_ENDPOINT>
```

## Nutanix

In order to use the Nutanix modules with a Nutanix cluster, you will need to set the following `secrets/nutanix/.env` file :

```
export TF_VAR_nutanix_user=<YOUR_NUTANIX_USERNAME>
export TF_VAR_nutanix_password=<YOUR_NUTANIX_PASSWORD>
export TF_VAR_nutanix_endpoint=<YOUR_NUTANIX_ENDPOINT>
```

You will need to manually create a Nutanix cluster on the web GUI.

To get the value of your Nutanix Endpoint, log in as admin to your Nutanix account, then go to the "admin" tab on top right, then clic on "REST API explorer". You will land on a swagger-Rest webpage, with the value of the endpoint at the top in a text form. Get the text between "https://" and "/static/v3/swagger.json" : it is your endpoint.