import dataclasses

@dataclasses.dataclass
class BaseProduct:
    prod_type: str
    src_node_id: str
    number: int=1
