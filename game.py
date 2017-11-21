import string
import random
import collections


Request = collections.namedtuple('Request', ['neighbor', 'resource', 'value'])


class Config(object):

    def __init__(self):
        self.production_per_tick = {i: 1 for i in random.sample(string.ascii_uppercase, 4)}
        self.consumption_per_tick = {i: 1 for i in random.sample(string.ascii_uppercase, 4)}


class Bot(object):
    """Base class for any AI written for the simulation.
    """

    def __init__(self):
        self.config = None              #: Configuration for this agent.

    def request_trade(self, neighbors, inventory):
        """Return a list of trade requests to make.
        """
        raise NotImplementedError

    def accept_trade(self, requests):
        raise NotImplementedError


class RandomBot(Bot):

    def request_trade(self, neighbors, inventory):
        """Return a list of requests to make.
        """
        i, _ = random.choice(inventory)
        n = random.choice(neighbors)
        return [Request(neighbor=n, resource=i, value=1.0)]

    def accept_trade(self, requests):
        return random.sample(requests, 1)


class Agent(object):

    def __init__(self, bot, config, health=1.0, happiness=0.0):
        self.bot = bot
        self.config = config
        self.health = health
        self.happiness = happiness

        items = set(self.config.consumption_per_tick.keys()) | set(self.config.production_per_tick.keys())
        self.inventory = {i: 0 for i in items}
        self.requests = []
        self.neighbors = []

    def is_healthy(self):
        return self.health > 0.0

    def is_happy(self):
        return self.happiness > 0.0

    def produce(self):
        """Agent produces goods at a fixed rate per turn.
        """
        for item, value in self.config.production_per_tick.items():
            self.inventory[item] += value

    def consume(self):
        """Agent consumes good at a fixed rate per turn.
        """
        for item, value in self.config.consumption_per_tick.items():
            if self.inventory[item] >= value:
                self.inventory[item] -= value
            else:
                self.health -= value

    def request_trade(self):
        """For all required resources, submit a request to a random agent.
        """
        if len(self.neighbors) == 0:
            return

        requests = self.bot.request_trade(list(self.neighbors.keys()), list(self.inventory.items()))
        for r in requests:
            request = Request(neighbor=self, resource=r.resource, value=r.value)
            r.neighbor.requests.append(request)

    def accept_trade(self):
        """Process all of the requests that were sent which can be fulfilled.
        """
        if len(self.requests) == 0:
            return

        for r in self.bot.accept_trade(self.requests):
            if self.inventory.get(r.resource, 0) < r.value:
                continue

            self.inventory[r.resource] -= r.value
            r.neighbor.inventory[r.resource] += r.value

            self.happiness += 1.0
            r.neighbor.happiness += 1.0


class Simulation(object):

    def __init__(self, agent_count=100, agent_health=1.0):
        self.agents = [Agent(bot=RandomBot(), config=Config(), health=agent_health) for _ in range(agent_count)]

    def connect_all(self):
        for a in self.agents:
            a.neighbors = {n: 0.0 for n in self.agents if a != n}

    def tick(self):
        for a in self.agents:
            a.produce()

        for a in self.agents:
            a.request_trade()

        for a in self.agents:
            a.accept_trade()

        for a in self.agents:
            a.consume()

    def run(self):
        while True:
            self.tick()

    def count_living_agents(self):
        return len([a for a in self.agents if a.is_healthy()])

    def count_happy_agents(self):
        return len([a for a in self.agents if a.is_happy()])
