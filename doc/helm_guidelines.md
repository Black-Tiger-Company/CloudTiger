# Helm development guidelines

This document provides useful guidelines and tips for developing new Helm Chart with the help of CloudTiger.

## Chart creation

You can create a stub for a new Helm Chart with the Helm command :

```bash
helm create <chart-name>
```

## Applying a chart with Helm from a CloudTiger scope folder

If you move to a CloudTiger scope folder attached to a scope used for the creation of a Kubernetes cluster (using the `dataplatform` features of CloudTiger, for example, see [here](./platform.md)), you can easily deploy a Helm Chart on your cluster:

```bash
export SCOPE=platform ### set your scope name here
cd gitops ### replace 'gitops' by the name of your CloudTiger root project
cd scopes/$SCOPE/inventory
export KUBECONFIG=./k8s-<ENVIRONMENT>-<CUSTOMER>/kube
export CHART_NAME=chart_name ### set your chart name
export CHART_PATH=chart_path ### set the path to your development chart folder (absolute or relative)
export CHART_NAMESPACE=chart_namespace ### set the namespace to deploy your chart
export CHART_VERSION=chart_version ### set the version of your chart - should match the version declared in your Chart folder
export VALUES_FILE=values.yml ### set the path to a custom values file
helm upgrade $CHART_NAME $CHART_PATH --install --namespace $CHART_NAMESPACE --create-namespace -f $VALUES_FILE --version $CHART_VERSION
```

__NOTA BENE__ :

- using `helm upgrade` instead of `helm install` ensure idempotency of you command in case of an already installed chart
- since you use `helm upgrade`, you need the `--install` flag to install the chart if it is not installed yet
- using `--create-namespace` ensure to create the namespace if it does not exist yet

## Generating a chart containing jinja tags for development

If you create a chart using jinja tags for dynamic instantiation, you can check the result of the instantiation using a set of values (provided for example using `-f $VALUES_FILE` option) with this command :

```bash
helm template $CHART_NAME $CHART_PATH -f $VALUES_FILE --version $CHART_VERSION > test.yml
```

This command will output the resulting Kubernetes resources of the chart for the values provided in the file `test.yml`.