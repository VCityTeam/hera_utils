from hera_utils import parse_arguments, num_exp_environment

args = parse_arguments()
environment = num_exp_environment(args)  # Configures Hera

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
