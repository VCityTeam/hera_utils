# hera_utils: an embryonic python library of Hera workflows utilities

`hera_utils` is a python package gathering helpers

- facilitating the abstraction/separation of [Hera based workflows](https://github.com/argoproj-labs/hera) based scripts from the concrete servers that shall be used to running them,
- proposing a simple/direct organizational structure of numerical experiments scripts based on [Hera (workflows)](https://github.com/argoproj-labs/hera).

The purpose of `hera_utils` boils down to a comment of the following diagrams

```mermaid
classDiagram
class Experimentation["(Numerical) Experiment (description)"]
class Environment["Environment (of execution)"]
class Workflow["Workflow (HERA code)"]
class WorkflowLanguage["ArgoWorkflows (HERA language)"]
class Layout["Layout (files' organisation)"]
class Inputs["Inputs (parameters)"]
Experimentation o-- Workflow
Workflow ..> WorkflowLanguage
Experimentation o-- Layout
Experimentation o-- Inputs
Experimentation o-- Environment
```

The description of a (numerical) experiment (more generaly of a job) may be structured on top of the following separated concerns

- the expression of the specific atomic computations (tasks) that should be realized and their possible organization within a [**computational workflow**](https://en.wikipedia.org/wiki/Scientific_workflow_system) e.g. [Hera](https://github.com/argoproj-labs/hera)
- the experiment **inputs**: what concrete set of parameters should be used
- the experiment **layout** (naming convention, organisational structure) of its inputs/outputs: where (in which file, directory, database...) does each task take its (file) inputs from and where does that task store its outputs to (and how does it name them)
- the (execution) environment that is the set of ressources required for the execution of the experiment e.g. a [persistent volume](https://kubernetes.io/docs/concepts/storage/persistent-volumes/), a container registry...

Once given (the description of) an Experiment, one uses an `execution engine` in order to proceed with its realization. When executing an Experiment, the ArgoWorkflows engine (say a Python interpreter) will

1. [provision](https://en.wikipedia.org/wiki/Provisioning) a concrete instance of the Environment (of execution),
2. launch the computations (most often) by delegating/submiting it to Workflow to some ArgoWorkflows server. The set of information required for that submission is gathered within an Environment of submission.

The execution engine will thus need to hold the following data model

```mermaid
classDiagram

class Experiment {
    - Workflow
    - Layout
    - Inputs
}
style Experiment fill:#1a1
class EnvironmentExecution[":Environment (of execution)"]
<<hera_utils>> EnvironmentExecution
style EnvironmentExecution fill:#faa

class ExecutionPlatform["Execution Platform"]
style ExecutionPlatform fill:#aaf
class WorkflowEngine["ArgoWorkflows Server"]
style WorkflowEngine fill:#aaf
class Cluster["Kubernetes Cluster"]
style Cluster fill:#aaf

class CLIContext[":Parsed Command Line Arguments"]
<<hera_utils>> CLIContext
style CLIContext fill:#faa
class ExecutionEngine

class EnvironmentSubmission[":Environment (of submission: HERA)"]
<<hera_utils>> EnvironmentSubmission
style EnvironmentSubmission fill:#faa

ExecutionEngine *-- EnvironmentSubmission
ExecutionEngine ..> ExecutionPlatform: depends

ExecutionEngine o-- Experiment
Experiment o-- EnvironmentExecution
ExecutionEngine *-- EnvironmentExecution


EnvironmentExecution ..> CLIContext: constructed with
ExecutionEngine *-- CLIContext
EnvironmentSubmission ..> CLIContext: constructed with

CLIContext --> WorkflowEngine
EnvironmentSubmission o-- WorkflowEngine

EnvironmentExecution o-- Cluster
CLIContext --> Cluster
WorkflowEngine ..> Cluster
ExecutionPlatform *-- Cluster

ExecutionPlatform *-- WorkflowEngine
```

The objects depicted with the `<<hera_utils>>` [(UML) stereotype](https://www.uml-diagrams.org/stereotype.html) are susceptible to benefit from the `hera_utils` package.

## The big lines of what hera_utils helps you to set up

```python
import hera_utils

# Make sure that all the elements of the HERA context can be extracted from either
# the Command Line Arguments (CLI) or the environment variables:
args = hera_utils.parse_arguments()      

# Assert that the k8s cluster (designated by the CLI arguments) is accessible:
cluster = hera_utils.k8s_cluster(args)

# Assert that the ArgoWorkflows server (also designated by the CLI arguments and running
# on the above cluster), is accessible:
argo_server = hera_utils.argo_server(cluster, args)

# Eventually transmit to the Hera workflow the environment of submission that it expects
# (the argo server, an associated access token, the ad-hoc namespace...): 
argo_server.define_argo_server_part_of_environment()
```

Your python script (more precisely, your Experiment expressed as a python script) can now proceed with expressing its dependencies, that is its environment (of execution), input and layout

```python
from environment import numerical_experiment_environment
environment = numerical_experiment_environment(cluster, args)
from my_specific_input import inputs
from my_experiment_layout import experiment_layout
layout = experiment_layout(inputs.constants)
```

Eventually define the workflow code with the Hera library and on top of the environment, input and layout variables

```python
define_hera_workflow(environment, input, layout)   # Based-on/uses hera.worflows
```

## A more complete example

The above code snippets were voluntarily sketchy/abstract in order to simplify the understanding of the functionnal logic of an (hera based) Experiment.
The following example slightly improves on the usage of `hera_utils` by hiding technical functionnal details under the hood: refer to the [`numerical_experiment_environment::construct_environment(args)` method within `examples/environment.py`](./examples/environment.py) for some clues on how this encapsulation is realized.

Additionnaly the following code also provides more detailed comments

```python
if __name__ == "__main__":
    from hera_utils import parse_arguments
    # Retrieve the parsed CLI arguments and environment variables (of the python script)
    # that designates (and provides access to e.g. through credentials):
    #   1. a `k8s_cluster`: an accessible Kubernetes cluster
    #   2. an `argo_server`: an ArgoWorkflows server (running on the above k8s cluster)
    # Hera (when interpred with Python) will use this `argo_server` to submit the workflow 
    # (that is the server on which the following workflow will be executed):
    args = parse_arguments()

    from environment import construct_environment
    # The environment might also depend on the CLI argument and/on environment variables in
    # order for the numertical experiment to retrieve e.g. 
    # - some k8s volume claims (for its inputs/outputs)
    # - k8s config maps used to retrieve cluster specific information (HTTP proxy...)
    # The construct_environment() function encapsulates/hides 
    # - the usage of the k8s_cluster of provision the Experiment execution environment
    # - the construction of the Hera (library) submission environment
    environment = construct_environment(args)

    # Import the inputs (aka parameters) of this numerical experiment
    from my_specific_input import inputs

    # Define the numerical experiment input/output file layout (directory hierarchy, 
    # filenames for each task...)
    from my_experiment_layout import experiment_layout
    layout = layout(inputs.constants)

    # Proceed with the definition of the workflow that is solely based on the above
    # defined abstractions/encapsulations that is the
    # - environment (what must be changed when the k8s cluster changes)
    # - inputs (what must be changed when the numerical experiment changes: its parameters)
    # - layout (how the numerical experiment names its input/output (files, generated
    #   container) and organizes them (directory structure)
    # This is the part where hera.workflows library is used in order to define the tasks/workflow.
    # The following workflow definition restricts its inputs to the following variables:
    # - environment, 
    # - input, 
    # - layout
    from hera.workflows import DAG, Task, Workflow
    with Workflow(generate_name="do-some-stuff-", entrypoint="dag") as w:
        with DAG(name="dag"):
            # Definition of some tasks and containers
            dummy_fanin_t = print_script(name="print-results")
            collect_c = collect_container_constructor(
                environment,      # Used e.g. to access the container registry
                inputs.constants, # Used e.g. to select/name the ad-hoc container
            )
            
            # Loop on the numerical experiment parameters
            for vintage in inputs.parameters.vintages:
                # The result directory depends both on
                #  - a k8s volume claim pertaining to the environment
                #  - an organisational choice encapsulated in the layout class
                #    (and parametrized with the input)
                results_dir = os.path.join(
                    environment.persisted_volume.mount_path,
                    layout.collect_output_dir(vintage)
                )
                collect_t = Task(
                    name="collect-" + layout.container_name_postend(vintage),
                    template=collect_c,
                    arguments={
                        "vintage": vintage,
                        "results_dir": results_dir,
                    },
                    with_items=inputs.parameters.boroughs,
                )
                # Use Hera syntax to hookup the tasks in a workflow
                collect_t >> dummy_fanin_t
    w.create()
```

## Installation

```bash
python -m pip install git+https://github.com/VCityTeam/ExpeData-Workflows_testing/tree/master/ArgoWorkflows/Workflows_In_Hera/hera_utils
```

and uninstalling goes

```bash
python -m pip uninstall -y hera_utils        # No confirmation asked
```

Quick importation check

```bash
python -c "import hera_utils"
```

## For developers

## Setting up the development context

```bash
git clone https://github.com/VCityTeam/ExpeData-Workflows_testing.git
cd ArgoWorkflows/Workflows_In_Hera/hera_utils
python3.10 -m venv venv
 . venv/bin/activate
pip install -r requirements.txt      # Installs hera_utils
```
