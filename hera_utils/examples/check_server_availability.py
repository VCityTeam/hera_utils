import logging
from ..argo_server import argo_server, define_parser


def main():
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename="example.log", level=logging.DEBUG)

    args = define_parser(logger=logger).parse_args()
    server = argo_server(args)
    server.print_config()


if __name__ == "__main__":
    main()
