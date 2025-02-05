import logging
from dataclasses import dataclass

from perovskite_data_analysis.oqmd.client import OQMDClient
from perovskite_data_analysis.oqmd.perovskite_data import PerovskiteDataHandler


@dataclass
class Configuration:
    logger: logging.Logger
    client: OQMDClient
    handler: PerovskiteDataHandler


def build_configuration():
    logger = logging.getLogger(__file__)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
    client = OQMDClient(logger=logger)
    handler = PerovskiteDataHandler(client)
    return Configuration(
        logger=logger,
        client=client,
        handler=handler
    )
