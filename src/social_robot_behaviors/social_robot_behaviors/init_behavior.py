from ur5e_social_motion.social_motions import run_init_sequence


def execute_init_behavior(logger=None):
    if logger is not None:
        logger.info("Executing INIT behavior")

    return run_init_sequence(logger=logger)