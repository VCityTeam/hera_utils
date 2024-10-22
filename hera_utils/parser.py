import os
import configargparse
import logging


class parser:
    """Define a command line parser or extend an existing one."""

    def __init__(self, existing_parser=None, logger=logging.getLogger(__name__)):
        self.parser = None
        ### Retrieve the configuration files (when they are present)
        self.default_config_files = list()

        argo_cwd_config_file_path = os.path.join(os.getcwd(), "hera.config")
        if os.path.exists(argo_cwd_config_file_path):
            self.default_config_files.append(argo_cwd_config_file_path)

        if os.environ.get("ARGOCONFIG"):
            argo_config_file_path = os.environ.get("ARGOCONFIG")
            if os.path.exists(argo_config_file_path):
                self.default_config_files.append(argo_config_file_path)
            else:
                logger.error(
                    "Erroneous ARGOCONFIG environment variable value: ",
                    argo_config_file_path,
                )
                print("Argo configuration file ", argo_config_file_path, " ignored")

        argo_homedir_config_file_path = "~/hera.config"
        if os.path.exists(argo_homedir_config_file_path):
            self.default_config_files.append(argo_homedir_config_file_path)
        if self.default_config_files:
            if len(self.default_config_files) > 1:
                print(
                    "hera_utils: multiple config file(s) found:",
                    self.default_config_files,
                )
            elif len(self.default_config_files) == 1:
                print(
                    "hera_utils: using config file ",
                    self.default_config_files[0],
                )
            else:
                print(
                    "hera_utils: no config file found, using environnement variables ?"
                )

        if existing_parser:
            print(
                "Warning: expected type of existing parser is ",
                type(configargparse.ArgParser()),
            )
            print("   Provide existing parser is of type:", type(existing_parser))
            self.parser = existing_parser
        else:
            self.parser = configargparse.ArgParser(
                default_config_files=self.default_config_files
            )

        self.parser.add(
            "--argo_server",
            help="The URL of the argo server. Default is the value of the ARGO_SERVER environment variable.",
            type=str,
            default=os.environ.get("ARGO_SERVER"),
        )

        self.parser.add(
            "--argo_token",
            help="The URL of the argo server. Default is the value of the ARGO_TOKEN environment variable.",
            type=str,
            default=os.environ.get("ARGO_TOKEN"),
        )

        self.parser.add(
            "--argo_namespace",
            help="The name of the namespace. Default is the value of the ARGO_NAMESPACE environment variable.",
            type=str,
            default=os.environ.get("ARGO_NAMESPACE"),
        )

        self.parser.add(
            "--argo_service_account",
            help="The name of the service account (holding the token). Default is the value of the ARGO_SERVICE_ACCOUNT environment variable.",
            type=str,
            default=os.environ.get("ARGO_SERVICE_ACCOUNT"),
        )

    def get_config_files(self):
        return self.default_config_files
        
    def parse_args(self):
        return self.parser.parse_args()

    def get_parser(self):
        return self.parser


if __name__ == "__main__":
    import logging

    logger = logging.getLogger(__name__)
    logging.basicConfig(filename="example.log", level=logging.DEBUG)

    # Parser definition exposed for possible caller extension
    parser = parser(logger=logger)
    # Parsing postponed after optional extension by caller
    args = parser.parse_args()
    print("Parsed arguments:", args)
