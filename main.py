from web_server import app, request
import batch_control
import opc_ua
import asyncio
import traceback
import json
from concurrent.futures import ThreadPoolExecutor

opc_ua_thread = ThreadPoolExecutor(max_workers=2)

@app.route('/recipe', methods=['POST'])
def create_batch():
    global manager, opc_ua_thread
    recipe = request.json
    try:
        # create production batch from recipe
        batch_control.create_from_recipe(recipe)
        # start OPC UA communication
        opc_ua_thread.shutdown(wait=True)
        opc_ua_thread = ThreadPoolExecutor(max_workers=2)
        opc_ua_thread.submit(asyncio.run, opc_ua.start_opc_ua(recipe), debug=True)
    except Exception as e:
        traceback.print_exc()
        return "Error:\n {}".format(e)
    return "Batch created"

@app.route('/nodes', methods=['GET'])
def get_nodes():
    return batch_control.manager.get_nodes()

@app.route('/state')
def get_state():
    '''Return state in json format.'''
    return json.dumps(batch_control.get_batch_state())

@app.route('/action', methods=['POST'])
def actions():
    action = request.json
    try:
        if action['action'] == 'start':
            batch_control.run_batch(action['product'])
        elif action['action'] == 'stop':
            batch_control.stop_batch()
    except Exception as e:
        traceback.print_exc()
        return "Error:\n {}".format(e)
    return "Action {} done".format(action['action'])

@app.route('/test')
def test():
    return "Hello World!"

@app.route('/post_test',methods=['POST'])
def post_test():
    return request.json

if __name__ == '__main__':
    app.run(port=5015, debug=True)