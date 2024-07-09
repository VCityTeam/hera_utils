# Test, at HERA level, whether the environment is properly defined.
# See also CityGMLto3DTiles_Example/test_experiment_setup.py that in addition
# to checking the environment, also checks the experiment inputs.
from hera.workflows import (
    ExistingVolume,
    Parameter,
    script,
)


@script()
def print_environment():
    import os
    import json

    print("Hera on PaGoDa can run python scripts...")
    print(
        "Retrieve the python script environment variables: ",
        json.dumps(dict(os.environ), indent=4),
    )
    print("Done.")


if __name__ == "__main__":
    # A workflow that tests whether the defined environment is correct as
    # seen and used from within the Argo server engine (at Workflow runtime)
    from parse_arguments import parse_arguments
    from environment import environment
    from hera.workflows import (
        Container,
        DAG,
        Task,
        Workflow,
    )

    args = parse_arguments()
    environment = environment(args)

    with Workflow(generate_name="print-environment-", entrypoint="main") as w:
        cowsayprint = Container(
            name="cowsayprint",
            image="docker/whalesay",
            command=[
                "cowsay",
                "Print environment as seen from within the k8s cluster.",
            ],
        )
        with DAG(name="main"):
            t1 = Task(name="cowsayprint", template=cowsayprint)
            t2 = print_environment()
            t1 >> t2
    w.create()
