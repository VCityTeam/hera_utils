import types
import json
from hera_utils import parse_arguments, k8s_cluster, argo_server


class Struct:
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class num_exp_environment(Struct):
    """
    The role of the NUMerical EXPeriment ENVIRONMENT class consists in
    separating the CLI command arguments into three distinctive sub-environments
    (blocks of concerns):
    - the sub-environment concerning the underlying k8s cluster,
    - the sub-environment concerning the Argo server,
    - the numerical experiment environment per se that gathers remaining
      arguments that are technically required to run the workflows.
    """

    def __init__(self, args, verbose=False):
        """
        :param args: the CLI arguments holding the environment tidbits.
        """
        ### First transmit to Hera what it requires in order to properly
        # submit the workflows. Notice that both the k8s cluster and the argo
        # servers that are (technically) used in this constructor are NOT
        # stored in the numerical experiment environment.
        k8s = k8s_cluster(args)
        k8s.assert_cluster()
        if verbose:
            k8s.print_config()
            print("Kubernetes cluster seems ok.")
            print("")

        argo = argo_server(k8s, args)
        # The following line transmits the argo server related arguments to
        # the Hera library:
        argo.define_argo_server_part_of_environment()
        if verbose:
            argo.print_config()
            print("Argo server looks ok.")
            print("")

        # In opposition to the above temporary variables, the information that
        # is "close/related" to k8s server, and that will be required to run
        # the workflows, is stored in the environment.
        self.cluster = types.SimpleNamespace(
            docker_registry="harbor.pagoda.os.univ-lyon1.fr/"
        )

    def print_config(self):
        print("Environment of numerical experiment (at Python level):")
        print(self.toJSON())
