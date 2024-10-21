# Collect authentication info from env variables and/or config files and
# transmit that information to the hera library
from hera_utils import argo_server, parser

# Define hera_utils default parser.
parser = parser()

# Possibly extend this parser to comply with the workflow definition needs
# ... parser = extend_parser(parser)

# Postponed actual parsing can now be down with the extended parser
args = parser.parse_args()

argo_server(args)

###############################################################################
# The following is a copy of
# https://github.com/argoproj-labs/hera/blob/5.1.7/examples/workflows/coinflip.py
from hera.workflows import DAG, Workflow, script


@script()
def flip():
    import random

    result = "heads" if random.randint(0, 1) == 0 else "tails"
    print(result)


@script()
def heads():
    print("it was heads")


@script()
def tails():
    print("it was tails")


with Workflow(generate_name="coinflip-", entrypoint="d") as w:
    with DAG(name="d") as s:
        f = flip()
        heads().on_other_result(f, "heads")
        tails().on_other_result(f, "tails")
w.create()
