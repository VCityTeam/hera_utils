if __name__ == "__main__":
    import json
    from hera_utils import (
        check_version,
        num_exp_environment,
        print_version,
        parse_arguments,
    )

    if not check_version("5.6.0"):
        print("Hera version ")
        print_version()
        print(" is untested.")

    args = parse_arguments()
    print("CLI arguments/environment variables:")
    print(json.dumps(args.__dict__, indent=4))
    print("")

    environment = num_exp_environment(args, verbose=True)
