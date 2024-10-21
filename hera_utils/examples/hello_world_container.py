# Collect authentication info from env variables and/or config files and
# transmit that information to the hera library
from hera_utils import argo_server

argo_server()

#### Define the workflow
from hera.workflows import Container, Workflow

with Workflow(generate_name="hello-world-container", entrypoint="cowsay") as w:
    Container(name="cowsay", image="docker/whalesay", command=["cowsay", "Moo Hera"])
w.create()
