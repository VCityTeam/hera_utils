# Tests and examples (of hera_utils)

- [Tests and examples (of hera\_utils)](#tests-and-examples-of-hera_utils)
  - [Configuring Argo Server and testing its Hera access](#configuring-argo-server-and-testing-its-hera-access)
  - [Submit simple example workflows with Hera](#submit-simple-example-workflows-with-hera)
  - [Print containers environment and assert volume claim mounting](#print-containers-environment-and-assert-volume-claim-mounting)

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
