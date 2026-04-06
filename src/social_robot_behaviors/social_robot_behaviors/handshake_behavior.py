from ur5e_social_motion.social_motions import run_handshake_sequence


def execute_handshake_behavior(logger=None):
    if logger is not None:
        logger.info("Executing HANDSHAKE behavior")

    return run_handshake_sequence(logger=logger)