from data_handler.oqmd.client import OQMDAsyncClient


class PerovskiteLoader:
    PEROVSKITE_GENERIC_COMPOSITION = "ABC3"
    PHASES_DF_FIELDS = ["name", "entry_id", "composition", "volume", "ntypes", "natoms", ]
    def __init__(self,
                 chunk_size: int = 1000,
                 ):
        self._client = OQMDAsyncClient()
        self.initial_offset = 0
        self.chunk_size = chunk_size

    def _load_by_chunk(self):
        ...

    def _load_phases_dataframe(self):
        ...


