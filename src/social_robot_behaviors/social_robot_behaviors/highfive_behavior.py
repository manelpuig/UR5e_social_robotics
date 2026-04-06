from ur5e_social_motion.social_motions import run_highfive_sequence


def execute_highfive_behavior(logger=None):
    if logger is not None:
        logger.info("Executing HIGH FIVE behavior")

    return run_highfive_sequence(logger=logger)