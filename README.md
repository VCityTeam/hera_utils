# hera_utils: an embryonic python library of Hera workflows utilities<!-- omit from toc -->

## Table of contents<!-- omit from toc -->

- [hera\_utils in a nutshell](#hera_utils-in-a-nutshell)
- [The difficulty and a proposed solution](#the-difficulty-and-a-proposed-solution)
- [Configuring hera\_utils](#configuring-hera_utils)
  - [Retrieve your Argo Server credentials (for CLI usage)](#retrieve-your-argo-server-credentials-for-cli-usage)
  - [Choose a mode of persistence for your configuration](#choose-a-mode-of-persistence-for-your-configuration)
  - [hera\_utils configuration through environment variables](#hera_utils-configuration-through-environment-variables)
  - [hera\_utils configuration through a designated configuration file](#hera_utils-configuration-through-a-designated-configuration-file)
  - [hera\_utils configuration CLI arguments](#hera_utils-configuration-cli-arguments)
- [Using (hera with) `hera_utils`](#using-hera-with-hera_utils)
  - [`hera_utils` package installation](#hera_utils-package-installation)
  - [Assert the installation/configuration by running the examples](#assert-the-installationconfiguration-by-running-the-examples)
- [For developers](#for-developers)
  - [Setting up the development context](#setting-up-the-development-context)
  
## hera_utils in a nutshell

`hera_utils` is a python package, using [`ConfigArgParse`](https://github.com/bw2/ConfigArgParse) features, facilitating the authentication required by any concrete [`hera`](https://github.com/argoproj-labs/hera/blob/main/README.md) usage, through a combination of command line args, config files, hard-coded defaults, and in some cases, environment variables.
`hera_utils` facilitates the abstraction/separation of [Hera-based workflows](https://github.com/argoproj-labs/hera) based scripts from the concrete servers that shall be used to run them.

## The difficulty and a proposed solution

`hera_utils` is a python package facilitating the abstraction/separation of [Hera based workflows](https://github.com/argoproj-labs/hera) based scripts from the [authentication](https://hera.readthedocs.io/en/stable/walk-through/authentication/) required for running them on concrete servers.

Consider some arbitrary workflow defined in say an `hera_hello.py` file

```python
# hera_hello.py file: missing cluster dependent authentication information
from hera.workflows import Workflow, Container

with Workflow(generate_name="test-",entrypoint="c",) as w:
    Container(name="c", image="alpine:3.13", command=["sh", "-c", "echo hello world"])
w.create()
```

In order to successfully submit this workflow to some `argo_server_one` argo server, you will need to provide `argo_server_one` [proper authentication information](https://hera.readthedocs.io/en/stable/walk-through/authentication/), for which you might choose to derive `hera_hello.py` to become the `hera_hello_server_one.py` script defined as e.g.

```python
# hera_hello_server_one.py file: authentication makes the script cluster dependent

# New authentication related code is cluster dependent
from hera.shared import global_config
global_config.host = "https://the-argo-server-one-host.com"
global_config.token = "abc-123"

# The rest of the hera_hello.py script remains unchanged (and gets copied here) 
from hera.workflows import Workflow, Container
with Workflow(generate_name="test-",entrypoint="c",) as w:
    Container(name="c", image="alpine:3.13", command=["sh", "-c", "echo hello world"])
w.create()
```

Of course the drawbacks are that you do not respect the [DRY principle](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself) and thus you will have as many `hera_hello_server_xxx.py` (very redundant) files as argo servers on which you want to execute your workflow (and you generally need a development and some production servers).

The purpose of `hera_utils` python package is to maintain a single workflow definition script while being to able to handle many (separated) argo server configurations (e.g. configuration file).

With hera utils the `hera_hello.py` can be slightly changed to become

```python
# hera_hello.py file: authentication stands eg. in a configuration file

# Collect authentication from 
# - env variables and/or 
# - config files and/or
# - CLI arguments
# and transmit that information to the hera library
from hera_utils import argo_server

argo_server()   # Hera cluster configuration is done behind this line

# The rest of the hera_hello.py script remains unchanged (and gets copied here) 
from hera.workflows import Workflow, Container
with Workflow(generate_name="test-",entrypoint="c",) as w:
    Container(name="c", image="alpine:3.13", command=["sh", "-c", "echo hello world"])
w.create()
```

## Configuring hera_utils

### Retrieve your Argo Server credentials (for CLI usage)

In analogy with the retrieval of a Kubernetes Cluster credentials, the retrieval of your Argo Server credentials (for CLI level access) can be done through the Argo Server web-UI.

The credentials of the Argo server can be retrieved through the UI of the Argo server on your k8s cluster.
For this, authenticate/sign-on the Argo Server UI, and then

- select the `User` Tab within the left icon bar,
- within the `Using Your Login With The CLI` section of the `User` page use the `Copy to clipboard` button to retrieve your credentials (in the form of a set of environment variables e.g. `ARGO_SERVER`),
- trigger a shell and define those environment variables within that shell (paste the commands held in the "clipboard"),
- if not already done, install [argo CLI](https://github.com/argoproj/argo-workflows/releases/),
- assert that you can access your Argo Server with `argo CLI` e.g. with the commands
  
  ```bash
  argo list
  ```

### Choose a mode of persistence for your configuration

`hera_utils` offers three concrete means (that can be combined) in order to specify the argo server that Hera will need to access in order to submit your hera workflow:

- by using environment variables: this assumes that it is the responsibility of the user to persist the required environment variables (most often within a [shell script](https://en.wikipedia.org/wiki/Shell_script) e.g. [this argo.bash script](./examples/argo.bash.tmpl)),
- an ad-hoc `hera_utils` configuration file (e.g. [this hera.config file](./examples/hera.config.tmpl)),
- dedicated command line arguments (that can be retrieved with the `--help` or `-h` CLI option)

The three following chapters respectively present the above way of things.

### hera_utils configuration through environment variables

Although the above mentioned environment variables

- `ARGO_SERVER`,
- `ARGO_TOKEN`,
- `ARGO_NAMESPACE` and
- `ARGO_SERVICE_ACCOUNT`

can be  classically persisted with some shell script file e.g. your [shell](https://en.wikipedia.org/wiki/Unix_shell) rc [(run command)](https://en.wikipedia.org/wiki/RUNCOM) e.g. your `~/.bash_login` or `~/.bashrc` file, doing so wouldn't allow for concurrent (different argo severs) configuration.
A more functional method, consists in copying the [the `argo.bash.tmpl` script](./examples/argo.bash.tmpl) to e.g. `argo_server_one.bash` and to customize it with the `one` argo server credentials.
This script can then be imported into your current active shell

- either with e.g. `set -a && . ./argo_server_one.bash && set +a` command
- or by defining a function (in your `~/.bashrc` or `~/.bash_aliases`) of the
  form

  ```bash
  importenv() {
  set -a
  source "$1"
  set +a
  }
  ```
  
  and then invoking the `importenv argo_server_one.bash` command from your current active shell.
  At this stage, and if you installed argo CLI, the command

  ```bash
  argo list
  ```

  should provide you with a meaningful list of executed workflows

  Technical note: using commands like `export $(grep -v '^#' argo.bash | xargs)` will most likely fail since argo "Bearer" tokens generally contain a whitespace character (references: [1](https://unix.stackexchange.com/questions/79064/how-to-export-variables-from-a-file), [2](https://unix.stackexchange.com/questions/543455/exporting-variables-from-environment-file-with-spaces-in-values), [3](https://unix.stackexchange.com/questions/196759/setting-environment-vars-containing-space-with-env)...)

You can now keep as many hera_utils configuration files (`argo_server_one.bash`, `argo_server_two.bash`, `argo_server_minikube.bash`...) as you have clusters.

### hera_utils configuration through a designated configuration file

For this `hera_utils` configuration mode, copy the [this hera.config file](./examples/hera.config.tmpl) and customize/decline it for your argo server (running on some k8s cluster) and with your credentials.
By default hera_utils will check for the presence of the following configuration files (in this order of priority)

- `~/hera.config` (that is the `hera.config` file within your home directory)
- `hera.config` of the current working directory,
- `$ARGOCONFIG` that is the file designated by the `ARGOCONFIG` environment variable.

### hera_utils configuration CLI arguments

`hera_utils` uses the [`ConfigArgParse`](https://github.com/bw2/ConfigArgParse) Python package that defines the `--help` (and `-h`) flags in order to display help.
If you use `python <your_hera_script.py> --help` you should retrieve the following CLI options

```bash
  -h, --help            
    Show this help message and exit
  --argo_server ARGO_SERVER
    The URL of the argo server. Default is the value of the ARGO_SERVER environment
    variable.
  --argo_token ARGO_TOKEN
    The URL of the argo server. Default is the value of the ARGO_TOKEN environment
    variable.
  --argo_namespace ARGO_NAMESPACE
    The name of the namespace. Default is the value of the ARGO_NAMESPACE environment
    variable.
  --argo_service_account ARGO_SERVICE_ACCOUNT
    The name of the service account (holding the token). Default is the value of the
    ARGO_SERVICE_ACCOUNT environment variable.
```

## Using (hera with) `hera_utils`

### `hera_utils` package installation

You might wish to use a [(python) virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) and activate it e.g. with

```bash
python3.10 -m venv venv
source venv/bin/activate
```

Then proceed with the `hera_utils` package installation

```bash
python -m pip install git+https://github.com/VCityTeam/hera_utils
```

In order to quickly check the installation use

```bash
python -c "import hera_utils"
```

Note: un-installation goes

```bash
python -m pip uninstall -y hera_utils        # No confirmation asked
```

### Assert the installation/configuration by running the examples

If you're using a virtual environment, make sure it is activated.
Then [choose a mode to define your configuration](#choose-a-mode-of-persistence-for-your-configuration).

For example for the configuration file mode, copy the [this hera.config file](./hera_utils/examples/hera.config.tmpl) and customize/decline it for your argo server (running on some k8s cluster) and with your credentials.

Then try running the `hera-check-server` command or equivalently run the
`python -m hera_utils.examples.check_server_availability` module.

Then proceed with other hera scripts avaible as example modules provided in the [`hera_utils/examples`](https://github.com/VCityTeam/hera_utils/examples) directory e.g.

```bash
python -m hera_utils.examples.hello_world_container
python -m hera_utils.examples.hera_coin_flip
```

## For developers

### Setting up the development context

```bash
git clone https://github.com/VCityTeam/hera_utils.git
cd hera_utils
python3.10 -m venv venv
 . venv/bin/activate
python setup.py install      # Installs local version
```
