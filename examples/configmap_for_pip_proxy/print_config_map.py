# Test, at HERA level, whether a ConfigMap environment is properly defined.
from hera.workflows import (
    ConfigMapEnvFrom,
    Parameter,
    script,
)


@script(
    env_from=[
        # Assumes the corresponding config map is defined at k8s level
        ConfigMapEnvFrom(
            name="{{inputs.parameters.config_map_name}}",
            optional=False,
        )
    ],
)
def assert_configmap_environment(
    # Config_map_name argument is only used by the @script decorator and is
    # present here only because Hera seems to require it
    config_map_name,
):
    import os
    import sys
    import json

    environment_variables = dict(os.environ)
    if "HTTPS_PROXY" in environment_variables:
        print("HTTPS_PROXY environment variable found and (probably) defined")
        print("in the ", config_map_name, " ConfigMap.")
        print("HTTPS_PROXY value: ", environment_variables["HTTPS_PROXY"])
    else:
        print("HTTPS_PROXY environment variable NOT found.")
        print(
            "Something went wrong when defining of accessing the ",
            config_map_name,
            " ConfigMap.",
        )
        print("List of retrieved environment variables: ")
        print(json.dumps(dict(os.environ), indent=4))
        sys.exit(1)
    print("Exiting (from print_environment script).")


if __name__ == "__main__":
    # A workflow that tests whether the environment variables defined in
    # a Configmap can be retrieved (at Workflow runtime)
    from parse_arguments import parse_arguments
    from environment import environment
    from hera.workflows import (
        Container,
        DAG,
        Parameter,
        Task,
        Workflow,
    )

    args = parse_arguments()
    environment = environment(args)

    with Workflow(generate_name="test-environment-", entrypoint="main") as w:
        cowsayprint = Container(
            name="cowsayprint",
            image="docker/whalesay",
            env=[
                ConfigMapEnvFrom(
                    config_map_name=environment.cluster.configmap,
                    optional=False,
                )
            ],
            command=[
                "cowsay",
                "Argo can pull whalesay docker container (across HTTP proxies).",
            ],
        )
        with DAG(name="main"):
            t1 = assert_configmap_environment(
                arguments=Parameter(
                    name="config_map_name",
                    value=environment.cluster.configmap,
                ),
            )
            t2 = Task(name="cowsayprint", template=cowsayprint)
            t1 >> t2
    w.create()
