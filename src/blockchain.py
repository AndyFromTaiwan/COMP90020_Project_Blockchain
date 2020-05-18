class Blockchain(object):
    def __init__(self):
        self.chain = []

        # Create the genesis block
        #self.new_block(previous_hash=1, proof=100)



    def get_chain(self):
        return self.chain

    def get_last_block(self):
        return self.chain[-1];
   



    def new_block(self, proof, previous_hash=None):
        # Creates a new Block and adds it to the chain
        """
        Create a new Block in the Blockchain
        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': None,
            'user_balences': None,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions

        self.chain.append(block)
        return block


    def add_block(self, block, peers):
        return True


    def mine(self, transcations_pool, balence_pool):
        #TODO
        block = {}
        return block


    def verify_block(self, block):
        return True;

    def verify_chain(self, block):
        return True;




