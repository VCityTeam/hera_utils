import sys
import inspect
from hera.shared._global_config import GlobalConfig
from hera.workflows import WorkflowsService
import requests.exceptions
import hera.exceptions
from .parser import parser


class argo_server:
    """
    The Argo server is a part of the (Execution) Environment of the Experiment
    Refer to https://gitlab.liris.cnrs.fr/expedata/expe-data-project/-/blob/master/lexicon.md#execution-environment
    for a definition
    """

    def __init__(self, args=None):

        self.server = None
        self.token = None
        self.service_account = None
        self.service_namespace = None

        if not args:
            args = parser().parse_args()
        if not hasattr(args, "argo_server"):
            print("Mandatory URL of Argo server not provided.")
            print("Exiting.")
            sys.exit()

        ### For some undocumented reason the ARGO_SERVER value given by the argo UI
        # can be of the form `server.domain.org:443` when Hera expects an URL of
        # form `https://server.domain.org`. Try to fix that on the fly.
        # This is kludgy and completely ad-hoc and I will deny having written that
        # excuse for a code (and yes my github account was hacked).
        self.argo_server_configured_value = args.argo_server
        if args.argo_server.endswith(":443"):
            args.argo_server = args.argo_server.replace(":443", "")
        if args.argo_server.endswith("http://"):
            args.argo_server = args.argo_server.replace("http://", "https://")
        if not args.argo_server.startswith("https://"):
            args.argo_server = "https://" + args.argo_server
        self.server = args.argo_server
        if self.argo_server_configured_value != self.server:
            print("hera_utils: warning trying some kludgy argo_server fix.")
            print("  Configured argo_server value:", self.argo_server_configured_value)
            print("  Fixed argo_server value:", self.server)

        if not hasattr(args, "argo_token"):
            print("Warning: optional argo server token not provided.")
        else:
            self.token = args.argo_token

        if not hasattr(args, "argo_service_account"):
            print("Warning: optional argo server service account not provided.")
            print("  Task to task result transmission will NOT be possible")
        else:
            self.service_account = args.argo_service_account

        if not hasattr(args, "argo_namespace"):
            print("Warning: optional argo server namespace not provided.")
        else:
            self.namespace = args.argo_namespace
        self.configure_hera()
        self.check_server_availability()

    def configure_hera(self):
        """

        Note: Hera handles its own context/environment (which ArgoWorkflows to use)
        Note: Hera handles its own context/environment (which ArgoWorkflows to use)
          by defining the "GlobalConfig" global variable that
          - aggregates its lower level configuration variables
          - acts as a pervasive context for all Hera classes
          - acts as a pervasive context for all Hera classes
          There is thus nothing to be returned or accessed since the information
          flow is done through global variable accesses.
        """

        ### Parameters (including credentials) designating the cluster as passed to
        # Hera.
        GlobalConfig.host = self.server
        GlobalConfig.token = self.token

        ### The service account seems to be required as soon as the workflow has
        # to transmit the output results of a Task to the input of another Task.
        GlobalConfig.service_account_name = self.service_account
        GlobalConfig.namespace = self.namespace

    def check_server_availability(self):
        try:
            result = WorkflowsService().list_workflows(self.namespace)
        except requests.exceptions.ConnectionError as e:
            print(
                "ConnectionError exception thrown by requests module (used by hera): "
            )
            print("   Hint: check the validity of configured value of argo_server?")
            print("   Hint: configured value is", self.server)
            print("   Exception details: ", e)
            print("   Exiting.")
            sys.exit()
        except hera.exceptions.Unauthorized as e:
            print("Unauthorized exception thrown by hera module: ")
            print("   Hint: check the validity of configured value of argo_token?")
            print("   Hint: currently configured value is", self.token)
            print("   Exception details: ", e)
            print("   Exiting.")
            sys.exit()
        except hera.exceptions.Forbidden as e:
            print("Forbidden exception thrown by hera module: ")
            print("   Hint: check the validity of configured value of argo_namespace?")
            print("   Hint: currently configured value is", self.namespace)
            print("   Exception details: ", e)
            print("   Exiting.")
            sys.exit()
        except Exception as e:
            frm = inspect.trace()[-1]
            mod = inspect.getmodule(frm[0])
            module_name = mod.__name__ if mod else frm[1]
            print("Exception unknown to argo_server class.")
            print("Name of Python module defining the exception: ", module_name)
            print("Exception name: ", e.__class__.__name__)
            print("Exception details: ", e)
            print("Exiting.")
            sys.exit()

    def print_config(self):
        print("hera_utils: parameters used by Hera to submit workflows:")
        print("   host (argo_server) =", GlobalConfig.host)
        if self.argo_server_configured_value != self.server:
            print(
                "      Warning: initially configured host/server value: ",
                self.argo_server_configured_value,
            )
        print("   Namespace =", GlobalConfig.namespace)
        print("   Service account =", GlobalConfig.service_account_name)
        print("   Token = <found>")
