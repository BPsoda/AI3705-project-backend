from web_server import app, request
import batch_control


@app.route('/recipe', methods=['POST'])
def create_batch():
    global manager
    recipe = request.json
    batch_control.create_from_recipe(recipe)

@app.route('/nodes', methods=['GET'])
def get_nodes():
    return batch_control.manager.get_nodes()

@app.route('/state')
def get_state():
    return batch_control.manager.get_state()

@app.route('/actions', methods=['POST'])
def actions():
    action = request.json
    if action['action'] == 'run':
        batch_control.manager.run()
    elif action['action'] == 'pause':
        batch_control.manager.pause()

if __name__ == '__main__':
    app.run(port=5015, debug=True)