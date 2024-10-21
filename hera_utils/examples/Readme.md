# Tests and examples (of hera_utils)

- [Tests and examples (of hera\_utils)](#tests-and-examples-of-hera_utils)
  - [Configuring Argo Server and testing its Hera access](#configuring-argo-server-and-testing-its-hera-access)
  - [Submit simple example workflows with Hera](#submit-simple-example-workflows-with-hera)
  - [Print containers environment and assert volume claim mounting](#print-containers-environment-and-assert-volume-claim-mounting)
  - [Using ConfigMaps](#using-configmaps)

## Configuring Argo Server and testing its Hera access

If, in order to install the `hera_utils` package you used a virtual environment, first make sure that it is activated.

Then set up your [`hera_utils` configuration](../README.md/#configuring-the-access-to-the-kubernetes-and-argo-servers) (the simplest way being [through the usage of a configuration file](../README.md/#hera_utils-configuration-through-a-configuration-file)).
The proceed with testing the Hera access to the configured Argo Server with the commands

```bash
cd `git rev-parse --show-toplevel`/examples
python test.py
```

## Submit simple example workflows with Hera

```bash
cd `git rev-parse --show-toplevel`/examples
python simple/hera_coin_flip.py
```

## Print containers environment and assert volume claim mounting

The second example requires

- a more specific `hera_utils` configuration (file) that defines a volume claim name. Refer to the [./environment_and_volumes/hera.config.tmpl](./environment_and_volumes/hera.config.tmpl) and compare it with the simplest [hera.config.tmpl](./hera.config.tmpl). Customize (define the `k8s_volume_claim_name` variable) the [./environment_and_volumes/hera.config.tmpl](./environment_and_volumes/hera.config.tmpl) and place the declined results in [./environment_and_volumes/hera.config](./environment_and_volumes/hera.config) file,
- using an [`environment_and_volumes/environment.py` script](./environment_and_volumes/environment.py) that defines a `mount path` for the `volume claim`,
- using a [`environment_and_volumes/parse_arguments.py` script](./environment_and_volumes/parse_arguments.py) in order to customize the configuration parser.

```bash
cd `git rev-parse --show-toplevel`/examples
python environment_and_volumes/print_environment.py
python environment_and_volumes/check_volume_claim_and_mount_point.py
```

## Using ConfigMaps

The usage scenario assumes that the cluster administrator chose to set up an [http proxy server](https://stackoverflow.com/questions/7155529/how-does-http-proxy-work) thus constraining the containers (requiring http access) to configure that proxy.
In this hera_utils example, a container requires to dynamically [install a python package with the `pip` command](https://stackoverflow.com/questions/19080352/how-to-get-pip-to-work-behind-a-proxy-server).  
Let us further assume that the cluster administrator chose to transmit (to the cluster users) the URL of that proxy through a [ConfigMap (Configuration Mapping)](https://hera.readthedocs.io/en/stable/api/workflows/hera/?h=configmap#hera.workflows.ConfigMapEnvFrom).

First, let us temporarily take the role of the administrator, and manually define the ad-hoc ConfigMap with e.g. the following commands

```bash
cd `git rev-parse --show-toplevel`/examples/configmap_for_pip_proxy
# Define cluster specific variables
kubectl -n argo apply -f define_http_proxy_configmap.yml
# Assert the configmap was properly created (note that the ConfigMap 
# name is defined within define_http_proxy_configmap.yml)
kubectl -n argo get configmaps hera-utils-proxy-environment -o yaml
```

Then let us assert that this ConfigMap can be accessed from Workflow tasks with

```bash
python print_config_map.py
```

We can now make some usage (through the `pip install` command that recognizes the `HTTPS_PROXY` environment variable) of that ConfigMap values by running the following WorkFlow

```bash
python configmap_for_pip_proxy.py
```
