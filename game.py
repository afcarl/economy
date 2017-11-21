import random
import collections


Request = collections.namedtuple('Request', ['neighbor', 'resource', 'value'])


class Bot(object):

    def __init__(self):
        self.inventory = None

    def request_trade(self, neighbors, resources):
        """Return a list of trade requests to make.
        """
        raise NotImplementedError

    def accept_trade(self, requests):
        raise NotImplementedError


class RandomBot(Bot):

    def request_trade(self, neighbors, resources):
        """Return a list of requests to make.
        """
        i, v = random.choice(resources)
        n = random.choice(neighbors)
        return [Request(neighbor=n, resource=i, value=1.0)]

    def accept_trade(self, requests):
        return random.sample(requests, 1)


class Agent(object):

    def __init__(self, bot, health=1.0, happiness=0.0):
        self.bot = bot
        self.health = health
        self.happiness = happiness
        self.inventory = [0.0]
        self.requests = []
        self.neighbors = []
    
    def is_healthy(self):
        return self.health > 0.0

    def is_happy(self):
        return self.happiness > 0.0

    def produce(self):
        """Agent produces goods at a fixed rate per turn.
        """
        for i, _ in enumerate(self.inventory):
            self.inventory[i] += 1.0

    def consume(self):
        """Agent consumes good at a fixed rate per turn.
        """
        for i, c in enumerate(self.inventory):
            if c >= 1.0:
                self.inventory[i] -= 1.0
            else:
                self.health -= 1.0

    def request_trade(self):
        """For all required resources, submit a request to a random agent.
        """
        if len(self.neighbors) == 0:
            return

        requests = self.bot.request_trade(list(self.neighbors.keys()), list(enumerate(self.inventory)))
        for r in requests:
            request = Request(neighbor=self, resource=r.resource, value=r.value)
            r.neighbor.requests.append(request)

    def accept_trade(self):
        """Process all of the requests that were sent which can be fulfilled.
        """
        if len(self.requests) == 0:
            return

        for r in self.bot.accept_trade(self.requests):
            if self.inventory[r.resource] < r.value:
                continue

            self.inventory[r.resource] -= r.value
            r.neighbor.inventory[r.resource] += r.value

            self.happiness += 1.0
            r.neighbor.happiness += 1.0


class Simulation(object):

    def __init__(self, agent_count=100, agent_health=1.0):
        self.agents = [Agent(bot=RandomBot(), health=agent_health) for _ in range(agent_count)]

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
