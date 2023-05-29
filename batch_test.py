from batch_control import *

if __name__ == '__main__':
    recipe = {
        "nodes": [
            {
                "type": "SourceNode",
                "id": "source"
            },
            {
                "type": "StorageNode",
                "id": "storage"
            },
            {
                "type": "SinkNode",
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
    create_from_recipe(recipe)
    manager.run()
    print(manager.get_state())