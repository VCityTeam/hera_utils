from hera_utils import k8s_cluster
from hera_utils import num_exp_environment, Struct


class environment(num_exp_environment):

    def __init__(self, args, verbose=False):

        num_exp_environment.__init__(self, args, verbose)

        k8s = k8s_cluster(args)
        k8s.assert_cluster()

        ### Some tasks require to retrieve cluster specific environment
        # (e.g. HTTP_PROXY) values at runtime. This retrieval is done through an
        # ad-hoc k8s configuration map. Assert this map exists.
        k8s.assert_configmap(args.k8s_configmap_name)
        self.cluster.configmap = args.k8s_configmap_name

        ### A persistent volume (defined at the k8s level) can be used by
        # tasks of a workflow in order to flow output results from an upstream
        # task to a downstream one, and persist once the workflow is finished
        self.persisted_volume = Struct()
        k8s.assert_volume_claim(args.k8s_volume_claim_name)
        self.persisted_volume.claim_name = args.k8s_volume_claim_name

        # The mount path is technicality standing in between Environment and
        # Experiment related notions: more precisely it is a technicality that
        # should be dealt by the (Experiment) Conductor (refer to
        # https://gitlab.liris.cnrs.fr/expedata/expe-data-project/-/blob/master/lexicon.md#conductor )
        self.persisted_volume.mount_path = "/within-container-mount-point"
