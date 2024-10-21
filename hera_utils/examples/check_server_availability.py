import sys
import logging
from ..argo_server import argo_server
from ..parser import parser


def main():
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename="example.log", level=logging.DEBUG)

    args = parser(logger=logger).parse_args()  # Because we might want to log
    try:
        server = argo_server(args)
    except:
        print("hera_utils: argo server not properly configured. Exiting.")
        sys.exit(1)
    server.print_config()
    print("Argo server authentication properly set. Hera ready for usage.")


if __name__ == "__main__":
    main()
