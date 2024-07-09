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


@script(
    inputs=[
        Parameter(name="claim_name"),
        Parameter(name="mount_path"),
    ],
    volumes=[
        ExistingVolume(
            name="dummy",
            claim_name="{{inputs.parameters.claim_name}}",
            mount_path="{{inputs.parameters.mount_path}}",
        )
    ],
)
def does_the_mounted_appear_in_list(
    # claim_name argument is only used by the @script decorator and is present
    # here only because Hera seems to require it
    claim_name,
    mount_path,
):
    import subprocess
    import sys
    import os

    subprocess.check_call([sys.executable, "-m", "pip", "install", "psutils"])
    print("Psutils python package successfully installed.")
    volume_present = set(
        filter(
            lambda x: str(x.mountpoint) == mount_path,
            psutil.disk_partitions(),
        )
    )
    if len(volume_present) == 1:
        print(f"The persisted volume directory {mount_path} is duly mounted")
        sys.exit(1)

    # The persisted volume directory does NOT seem to be properly mounted
    # but this could be due to a failure of usage of
    # psutil.disk_partitions(). Let use assume this is the case and still
    # try to assert that the directory exists and is accessible:
    if not os.path.isdir(mount_path):
        print(f"Persisted volume directory {mount_path} not found.")
        print("Exiting")
        sys.exit(1)

    # Just to give some debug feedback by listing the files
    # Refer to
    # https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
    # for the one liner on listing files
    filenames = next(os.walk(mount_path), (None, None, []))[2]
    print(f"Persisted volume directory file access check: {filenames}")
    print(f"The persisted volume directory {mount_path} is properly mounted.")


@script(
    inputs=[
        Parameter(name="claim_name"),
        Parameter(name="mount_path"),
    ],
    volumes=[
        ExistingVolume(
            name="dummy",
            claim_name="{{inputs.parameters.claim_name}}",
            mount_path="{{inputs.parameters.mount_path}}",
        )
    ],
)
def list_persistent_volume_files(
    # claim_name argument is only used by the @script decorator and is present
    # here only because Hera seems to require it
    claim_name,
    mount_path,
):
    import os

    print(
        "Numerical experiment environment: persistent volume claim_name is ",
        claim_name,
    )
    print(
        "Numerical experiment environment: persistent volume mount path ",
        mount_path,
    )
    print(
        "Numerical experiment persistent volume directory list: ",
        os.listdir(mount_path),
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

    with Workflow(generate_name="check-volume-claim-and-mount-point-", entrypoint="main") as w:
        cowsayprint = Container(
            name="cowsayprint",
            image="docker/whalesay",
            command=[
                "cowsay",
                "Testing "
                + environment.persisted_volume.claim_name
                + " volume claim name",
            ],
        )
        with DAG(name="main"):
            t1 = print_environment()
            t2 = Task(name="cowsayprint", template=cowsayprint)
            t3 = list_persistent_volume_files(
                arguments=[
                    Parameter(
                        name="claim_name",
                        value=environment.persisted_volume.claim_name,
                    ),
                    Parameter(
                        name="mount_path",
                        value=environment.persisted_volume.mount_path,
                    ),
                ],
            )
            t1 >> t2 >> t3
    w.create()
