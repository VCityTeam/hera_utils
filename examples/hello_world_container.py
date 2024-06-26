from hera_utils import parse_arguments
from environment import construct_environment

args = parse_arguments()
environment = construct_environment(args)

####
from hera.workflows import Container, Workflow

with Workflow(generate_name="hello-world-container", entrypoint="cowsay") as w:
    Container(name="cowsay", image="docker/whalesay", command=["cowsay", "Moo Hera"])
w.create()
