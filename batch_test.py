from batch_control import *
import time

if __name__ == '__main__':
    recipe_store = {
        "nodes": [
            {
                "type": "SourceTank",
                "id": "source"
            },
            {
                "type": "TankModel",
                "id": "storage"
            },
            {
                "type": "SinkTank",
                "id": "sink"
            }
        ],
        "connections": [
            {
                "from": "source",
                "to": "storage"
            },
            {
                "from": "storage",
                "to": "sink"
            }
        ],
        "products": [
            {
                "prod_type": "type1",
                "src_node_id": "source",
                "number": 1
            },
            {
                "prod_type": "type2",
                "src_node_id": "source",
                "number": 2
            },
            {
                "prod_type": "type3",
                "src_node_id": "source",
                "number": 3
            }
        ]
    }
    create_from_recipe(recipe_store)
    run_batch()
    for i in range(20):
        print(get_batch_state())
        time.sleep(1)
    stop_batch()