if __name__ == "__main__":
    import logging
    from hera_utils import argo_server, define_parser

    logger = logging.getLogger(__name__)
    logging.basicConfig(filename="example.log", level=logging.DEBUG)

    args = define_parser(logger=logger).parse_args()
    argo_server = argo_server(args)
    argo_server.print_config()
