import os
import sys
import logging
import hera_utils


def parse_arguments(logger=logging.getLogger(__name__)):
    """Extend the default parser with the local needs"""
    parser = hera_utils.define_parser(logger)

    # Add the locally defined parser extensions
    parser.add(
        "--k8s_volume_claim_name",
        help="Name of the k8s volume claim to be used by numerical experiment.",
        type=str,
        default=os.environ.get("KUBEVOLUMECLAIMNAME"),
    )

    # Parse and assert that the default parser is satisfied
    args = parser.parse_args()
    args_are_correct = hera_utils.verify_args(args)
    if not args_are_correct:
        parser.print_help()
        sys.exit()

    # Eventually assert that the local extension is satisfied to
    if args.k8s_volume_claim_name is None:
        logger.debug("The optional name of the k8s volume claim name (used by")
        logger.debug("the numerical experiment to access a filesystem volume).")
        logger.debug("was not provided. When needed either try")
        logger.error("  - setting the KUBEVOLUMECLAIMNAME environment variable")
        logger.error(
            "  - setting the --k8s_volume_claim_name argument; refer to usage below"
        )
        parser.print_help()
        sys.exit()
    return args
