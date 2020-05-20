from argparse import ArgumentParser
import config
from flask import Flask, jsonify, request
from node import Node
import requests
import threading
import utility


# Instantiate our Node
app = Flask(__name__)


@app.route('/', methods=['GET'])
def get_node_availability():
    host_port = node.get_socket()
    response = {
        'message': f'Node on http://{host_port} is available!'
    }
    return jsonify(response), 200


@app.route('/node/init', methods=['POST'])
def init_node_from_peer():
    body = request.get_json()
    if body is None or body.get('peer') is None:
        response = {
            'error': 'Invalid request body'
        }
        return jsonify(response), 400
    peer = body.get('peer')
    if peer == node.get_socket():
        response = {
            'error': 'Invalid peer node'
        }
        return jsonify(response), 400

    try:
        response = requests.post(url=f'http://{peer}/peer/new', json={'peer': node.get_socket()} ,timeout=config.CONNECTION_TIMEOUT_IN_SECONDS)
        if response.status_code == 201:
            node.peers.add(peer)
            if node.clone_from_peer(peer):
                response = {
                    'message': f'Successful initialization from http://{peer}'
                }
                return jsonify(response), 201
    except Exception as e:
        print(e)
        response = {
            'error': f'Failed to initialize from http://{peer}'
        }
        return jsonify(response), 400


@app.route('/node/clone', methods=['GET'])
def get_node_replica():
    host_port = node.get_socket()
    peers = node.get_peers()
    users = node.get_users()
    transaction_pool = node.get_transaction_pool()
    user_balence_pool = node.get_user_balence_pool()
    blockchain = node.get_full_chain()
    response = {
        'host_port': host_port,
        'peers': peers,
        'users': users,
        'transaction_pool': transaction_pool,
        'user_balence_pool': user_balence_pool,
        'blockchain': blockchain
    }
    return jsonify(response), 200



@app.route('/peer/list', methods=['GET'])
def get_node_peers():
    peers = node.get_peers()
    response = {
        'peers': peers
    }
    return jsonify(response), 200


@app.route('/peer/new', methods=['POST'])
def post_peer_registration():
    body = request.get_json()
    if body is None or body.get('peer') is None:
        response = {
            'error': 'Invalid request body'
        }
        return jsonify(response), 400

    if node.register_peer(peer=body.get('peer')):
        response = {
            'message': 'Your peer registration is successful!'
        }
        return jsonify(response), 201
    else:
        response = {
            'error': 'Failed to access this peer node'
        }
        return jsonify(response), 400


@app.route('/peer/add', methods=['POST'])
def add_new_peer():
    body = request.get_json()
    if body is None or body.get('peer') is None:
        response = {
            'error': 'Invalid request body'
        }
        return jsonify(response), 400

    if node.add_peer(peer=body.get('peer')):
        response = {
            'message': 'Added this peer node successfully!'
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Peer node not added'
        }
        return jsonify(response), 201



@app.route('/user/profiles', methods=['GET'])
def get_all_user_profile():
    users = node.get_users()
    response = {
        'users': users
    }
    return jsonify(response), 200


@app.route('/user/names', methods=['GET'])
def get_all_user_list():
    users = node.get_users()
    response = {
        'users': list(users.keys()) 
    }
    return jsonify(response), 200


@app.route('/user/new', methods=['POST'])
def post_user_registration():
    body = request.get_json()
    if body is None or body.get('username') is None or body.get('password') is None:
        response = {
            'error': 'Invalid request body'
        }
        return jsonify(response), 400

    if node.register_user(user=body.get('username'), password=body.get('password')):
        response = {
            'message': 'Your user registration is successful!'
        }
        return jsonify(response), 201
    else:
        response = {
            'error': 'Duplicated registration'
        }
        return jsonify(response), 400


@app.route('/user/add', methods=['POST'])
def add_new_user():
    body = request.get_json()
    if body is None or body.get('username') is None or body.get('password') is None:
        response = {
            'error': 'Invalid request body'
        }
        return jsonify(response), 400

    if node.add_user(user=body.get('username'), password=body.get('password')):
        response = {
            'message': 'Added this user successfully!'
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'User not added'
        }
        return jsonify(response), 201



@app.route('/user/balence', methods=['POST'])
def get_user_balence():
    body = request.get_json()
    if body is None or body.get('username') is None or body.get('password') is None:
        response = {
            'error': 'Invalid request body'
        }
        return jsonify(response), 400
    user = body.get('username')
    password = body.get('password')
    if not node.authenticate_user(user=user, password=password):
        response = {
            'error': 'User authentication failed'
        }
        return jsonify(response), 401

    balence_from_blockchain = node.get_last_block()['user_balences'].get(user)
    balence_from_pool = node.get_user_balence_pool().get(user)
    response = {
        'balence_from_blockchain': balence_from_blockchain,
        'balence_from_pool': balence_from_pool
    }
    return jsonify(response), 200



@app.route('/balence/pool', methods=['GET'])
def get_balence_pool():
    user_balence_pool = node.get_user_balence_pool()
    response = {
        'user_balence_pool': user_balence_pool
    }
    return jsonify(response), 200



@app.route('/transaction/pool', methods=['GET'])
def get_transaction_pool():
    transaction_pool = node.get_transaction_pool()
    response = {
        'transaction_pool': transaction_pool
    }
    return jsonify(response), 200


@app.route('/transaction/list', methods=['GET'])
def get_uncommitted_transactions():
    uncommitted_transactions = node.get_transaction_pool_as_list()
    response = {
        'uncommitted_transactions': uncommitted_transactions
    }
    return jsonify(response), 200


@app.route('/transaction/new', methods=['POST'])
def post_user_transaction():
    body = request.get_json()
    if body is None: 
        response = {
            'error': 'Invalid request body'
        }
        return jsonify(response), 400
    required_fields = ['sender', 'authentication','recipient', 'amount']
    for k in required_fields:
        if body.get(k) is None:
            response = {
                'error': 'Invalid request body'
            }
            return jsonify(response), 400

    sender = body.get('sender')
    authentication = body.get('authentication')
    recipient = body.get('recipient')
    amount = body.get('amount')
    if not node.authenticate_user(user=sender, password=authentication):
        response = {
            'error': 'Sender authentication failed'
        }
        return jsonify(response), 401
    if sender == recipient or amount<=0: 
        response = {
            'error': 'Illigial transaction'
        }
        return jsonify(response), 400

    transaction = node.start_transaction(sender=sender, recipient=recipient, amount=body.get('amount'))
    if transaction is None:
        response = {
            'error': 'Nor enough balence or invalid recipient'
        }
        return jsonify(response), 400
    else:
        response = {
            'message': 'Your transaction will be added to Blockchain!',
            'transaction': transaction
        }
        return jsonify(response), 201


@app.route('/transaction/add', methods=['POST'])
def add_new_transaction():
    body = request.get_json()
    if body is None or body.get('transaction') is None:
        response = {
            'error': 'Invalid request body'
        }
        return jsonify(response), 400
    if node.add_transaction(transaction=body.get('transaction')):
        response = {
            'message': 'Added this transaction successfully!'
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Transaction not added'
        }
        return jsonify(response), 201



@app.route('/blockchain/chain', methods=['GET'])
def get_full_blockchain():
    blockchain = node.get_full_chain()
    response = {
        'blockchain': blockchain,
        'length': len(blockchain)
    }
    return jsonify(response), 200


@app.route('/blockchain/last_block', methods=['GET'])
def get_last_block_blockchain():
    last_block = node.get_last_block()
    response = {
        'last_block': last_block
    }
    return jsonify(response), 200


@app.route('/blockchain/mine', methods=['POST'])
def mine_new_block():
    body = request.get_json()
    if body is None or body.get('username') is None or body.get('password') is None:
        response = {
            'error': 'Invalid request body'
        }
        return jsonify(response), 400
    user = body.get('username')
    password = body.get('password')
    if not node.authenticate_user(user=user, password=password):
        response = {
            'error': 'User authentication failed'
        }
        return jsonify(response), 401

    new_block = node.mine(user)

    if new_block is None:
        response = {
            'error': 'Mining aborted'
        }
        return jsonify(response), 500
    else:
        response = {
            'message': 'New block forged',
            'mining_reward': config.MINING_REWARD,
            'new_block': new_block
        }
        return jsonify(response), 201


@app.route('/blockchain/add', methods=['POST'])
def add_new_blockchain():
    body = request.get_json()
    if body is None or body.get('blockchain') is None:
        response = {
            'error': 'Invalid request body'
        }
        return jsonify(response), 400

    if node.add_chain(chain=body.get('blockchain')):
        response = {
            'message': 'Update blockchain successfully!'
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Blockchain node not updated'
        }
        return jsonify(response), 201



if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    parser.add_argument('-d', '--debug', default=True, type=utility.str2bool, help='enable flask debug mode')
    args = parser.parse_args()

    host = '127.0.0.1' #TODO
    port = args.port
    debug = args.debug
    node = Node(host=host, port=port)
    app.run(host=host, port=port, debug=debug)
