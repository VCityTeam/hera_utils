import os
import configargparse
import logging


def define_parser(existing_parser=None, logger=logging.getLogger(__name__)):
    """Define a command line parser and parse the command arguments.

    :param default_service_account: the name of the service account that will be used as default value
    :return: the arguments that were retrieved by the parser
    """
    ### Retrieve the configuration files (when they are present)
    default_config_files = list()
    argo_homedir_configfile_path = "~/hera.config"
    if os.path.exists(argo_homedir_configfile_path):
        default_config_files.append(argo_homedir_configfile_path)
    argo_cwd_configfile_path = os.path.join(os.getcwd(), "hera.config")
    if os.path.exists(argo_cwd_configfile_path):
        default_config_files.append(argo_cwd_configfile_path)
    if os.environ.get("ARGOCONFIG"):
        argo_configfile_path = os.environ.get("ARGOCONFIG")
        if os.path.exists(argo_configfile_path):
            default_config_files.append(argo_configfile_path)
        else:
            logger.error(
                "Erroneous ARGOCONFIG environment variable value: ",
                argo_configfile_path,
            )
            print("Argo configuration file ", argo_configfile_path, " ignored")
    if default_config_files:
        print("hera_utils: using config file(s)", default_config_files)

    if existing_parser:
        print(
            "Warning: expected type of existing parser is ",
            type(configargparse.ArgParser()),
        )
        print("   Provide existing parser is of type:", type(existing_parser))
        parser = existing_parser
    else:
        parser = configargparse.ArgParser(default_config_files=default_config_files)

    parser.add(
        "--argo_server",
        help="The URL of the argo server. Default is the value of the ARGO_SERVER environment variable.",
        type=str,
        default=os.environ.get("ARGO_SERVER"),
    )

    parser.add(
        "--argo_token",
        help="The URL of the argo server. Default is the value of the ARGO_TOKEN environment variable.",
        type=str,
        default=os.environ.get("ARGO_TOKEN"),
    )

    parser.add(
        "--argo_namespace",
        help="The name of the namespace. Default is the value of the ARGO_NAMESPACE environment variable.",
        type=str,
        default=os.environ.get("ARGO_NAMESPACE"),
    )

    parser.add(
        "--argo_service_account",
        help="The name of the service account (holding the token). Default is the value of the ARGO_SERVICE_ACCOUNT environment variable.",
        type=str,
        default=os.environ.get("ARGO_SERVICE_ACCOUNT"),
    )
    return parser


if __name__ == "__main__":
    import logging

    logger = logging.getLogger(__name__)
    logging.basicConfig(filename="example.log", level=logging.DEBUG)

    parser = define_parser(logger=logger)
    args = parser.parse_args()
    print("Parsed arguments:", args)
