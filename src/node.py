from blockchain import Blockchain
import config
import json
import requests
from time import time
from uuid import uuid4


class Node(object):
    def __init__(self, host, port):
        self.socket = host+":"+str(port)
        self.peers = set()
        self.users = dict()
        self.transaction_pool = dict()
        self.user_balence_pool = dict()
        self.blockchain = Blockchain()

    def get_socket(self):
       return self.socket

    def clone_from_peer(self, peer):
        try:
            response = requests.get(url=f'http://{peer}/node/clone', timeout=config.CONNECTION_TIMEOUT)
            if response.status_code == 200:
                replica = response.json()  
                for p in replica.get('peers'):
                    self.add_peer(p)
                self.users = replica.get('users')
                self.transaction_pool = replica.get('transaction_pool')
                self.user_balence_pool = replica.get('user_balence_pool')
                return True
        except Exception as e:
            print(e)
        return False


    def get_peers(self):
       return list(self.peers)

    def register_peer(self, peer):
        if peer!=self.socket:
            try:
                response = requests.get(url=f'http://{peer}/', timeout=config.CONNECTION_TIMEOUT)
                if response.status_code == 200:
                    self.broadcast_peer(peer)
                    self.peers.add(peer)
                    return True
            except Exception as e:
                print(e)
        return False

    def add_peer(self, peer):
        if peer!=self.socket:
            self.peers.add(peer)

    def broadcast_peer(self, peer):
        pass


    def get_users(self):
        return self.users

    def register_user(self, user, password):
        if user in self.users:
            return False
        self.add_user(user, password)
        self.broadcast_user(user, password)
        return True

    def add_user(self, user, password):
        if user not in self.users:
            self.users[user] = password
            self.user_balence_pool[user] = config.NEW_USER_REWARD #TODO: coinbase transaction?

    def authenticate_user(self, user, password):
        return self.users.get(user) == password

    def broadcast_user(self, user, password):
        pass


    def get_transaction_pool(self):
        return self.transaction_pool

    def start_transaction(self, sender, recipient, amount):
        if self.verify_transaction(sender, recipient, amount):
            transaction = self.create_transaction(sender, amount, recipient)
            self.transaction_pool[transaction.get('transaction_id')] = transaction
            self.update_user_balence_pool(sender, recipient, amount)
            self.broadcast_transaction(transaction)
            return transaction
        else:
            return None

    def add_transaction(self, transaction):
        transaction_id = transaction.get('transaction_id')
        sender = transaction.get('sender')
        recipient = transaction.get('recipient')
        amount = transaction.get('amount')
        if self.verify_transaction(sender, recipient, amount):
            self.transaction_pool[transaction_id] = transaction
            self.update_user_balence_pool(sender, recipient, amount)

    def verify_transaction(self, sender, recipient, amount):
       if self.user_balence_pool.get(sender) is None or self.user_balence_pool.get(recipient) is None:
          return False
       return self.user_balence_pool.get(sender) >= amount

    @staticmethod
    def create_transaction(sender, amount, recipient):
        return {
            'transaction_id': str(uuid4()),
            'sender': sender, 
            'recipient': recipient, 
            'amount': amount,
            'timestamp': int(time())
        }

    def broadcast_transaction(self, transaction):
        pass


    def get_user_balence_pool(self):
        return self.user_balence_pool

    def update_user_balence_pool(self, sender, recipient, amount):
        self.user_balence_pool[sender] = self.user_balence_pool.get(sender)-amount
        self.user_balence_pool[recipient] = self.user_balence_pool.get(recipient)+amount





    

    def get_full_chain(self):
        return self.blockchain.get_chain()

    def get_last_block(self):
        return self.blockchain.get_last_block()

    
    def broadcast_block(self, block):
        pass

    def broadcast_chain(self, chain):
        pass
    
    def add_block(self, block):
        self.add_block(block, self.peers)

    def add_chain(self, chain):
        self.add_block(chain, self.peers)

 
    def mine(self):
        new_block = self.blockchain.mine(self.transcations_pool, self.balence_pool)
        if new_block is not None:
            self.broadcast_block(new_block)
    
    

