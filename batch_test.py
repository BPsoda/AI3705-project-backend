from batch_control import *
import time

if __name__ == '__main__':
    recipe_store = {
        "nodes": [
            {
                "dtype": "Start",
                "id": "start"
            },
            {
                "dtype": "SourceTank",
                "id": "source"
            },
            {
                "dtype": "TankModel",
                "id": "storage"
            },
            {
                "dtype": "SinkTank",
                "id": "sink"
            }
        ],
        "edges": [
            {
                "source": "start",
                "target": "source"
            },
            {
                "source": "source",
                "target": "storage"
            },
            {
                "source": "storage",
                "target": "sink"
            }
        ]
    }
    product_cfg = {
        "type": "碳酸基料",
        "number": 10
    }
    create_from_recipe(recipe_store)
    run_batch(product_cfg)
    for i in range(20):
        print(get_batch_state())
        time.sleep(1)
    stop_batch()