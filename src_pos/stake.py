
class Stake(object):
    def __init__(self):
        # self.addresses = []
        # self.balance = {}
        self.addresses = ["kHdwGTsh3TiS6CDUjnw8E9mtOpGQkKoD+ODj+XaWnpg/pYriRUkP4bXUZdvkt7cHYOzlaJLFRrGIakrfTuT2kA=="]
        self.balance = {"kHdwGTsh3TiS6CDUjnw8E9mtOpGQkKoD+ODj+XaWnpg/pYriRUkP4bXUZdvkt7cHYOzlaJLFRrGIakrfTuT2kA==": 10}

    def initialize(self, address):
        if address not in self.balance:
            self.balance[address] = 0
            self.addresses.append(address)

    def addStake(self, _from, amount):
        self.initialize(_from)
        self.balance[_from] += amount

    def getStake(self, address):
        self.initialize(address)
        return self.balance[address]

    def getMax(self, addresses):
        balance = -1
        leader = ""
        for address in addresses:
            if self.getBalance(address) > balance:
                leader = address
                balance = self.balance[address]
        return leader

    def update(self, transaction):
        amount = transaction.output["amount"]
        _from = transaction.input["from"]
        self.addStake(_from, amount)

    def getBalance(self, address):
        self.initialize(address)
        return self.balance[address]


class Validators(object):
    def __init__(self):
        self.list = ["kHdwGTsh3TiS6CDUjnw8E9mtOpGQkKoD+ODj+XaWnpg/pYriRUkP4bXUZdvkt7cHYOzlaJLFRrGIakrfTuT2kA=="]

    def update(self, transaction):
        if transaction.output["amount"] == 10 and transaction.output["to"] == "0":
            self.list.append(transaction.input["from"])
            return True
        return False
