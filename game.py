import string
import random
import collections


Request = collections.namedtuple('Request', ['agent', 'resource', 'value'])


class Config(object):

    def __init__(self, resources, produce_count=2, consume_count=2):
        self.production_per_tick = {i: 1 for i in random.sample(resources, produce_count)}
        self.consumption_per_tick = {i: 1 for i in random.sample(resources, consume_count)}

    def all_items(self):
        return set(self.consumption_per_tick.keys()) | set(self.production_per_tick.keys())


class State(object):

    def __init__(self, items=set(), health=1.0, happiness=1.0):
        self.health = health
        self.happiness = happiness
        self.inventory = {i: 0 for i in items}
        self.neighbors = {}


class Bot(object):
    """Base class for any AI written for the simulation.
    """

    def __init__(self):
        self.config = None              #: Configuration for this bot.
        self.state = None               #: State data for this bot.

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
        return [Request(agent=n, resource=i, value=1)]

    def accept_trade(self, requests):
        return random.sample(requests, 1)


class Agent(object):

    def __init__(self, bot, config, state):
        self.bot = bot
        self.config = config
        self.state = state

        self.requests = []

    def is_healthy(self):
        return self.state.health > 0.0

    def is_happy(self):
        return self.state.happiness > 0.0

    def produce(self):
        """Agent produces goods at a fixed rate per turn.
        """
        for item, value in self.config.production_per_tick.items():
            self.state.inventory[item] += value

    def consume(self):
        """Agent consumes good at a fixed rate per turn.
        """
        for item, value in self.config.consumption_per_tick.items():
            if self.state.inventory[item] >= value:
                self.state.inventory[item] -= value
            else:
                self.state.health -= value

    def request_trade(self):
        """For all required resources, submit a request to a random agent.
        """
        if len(self.state.neighbors) == 0:
            return

        requests = self.bot.request_trade(list(self.state.neighbors.keys()), list(self.state.inventory.items()))
        for r in requests:
            request = Request(agent=self, resource=r.resource, value=r.value)
            r.agent.requests.append(request)

    def accept_trade(self):
        """Process all of the requests that were sent which can be fulfilled.
        """
        if len(self.requests) == 0:
            return

        for r in self.bot.accept_trade(self.requests):
            if self.state.inventory.get(r.resource, 0) < r.value:
                continue

            self.state.inventory[r.resource] -= r.value
            r.agent.state.inventory[r.resource] += r.value

            self.state.happiness += 1.0
            r.agent.state.happiness += 1.0


class Simulation(object):

    def __init__(self, resources=string.ascii_uppercase, agent_count=100, agent_health=1.0):
        self.agents = [self.make_agent(resources, agent_health) for _ in range(agent_count)]

    def make_agent(self, resources, health):
        config = Config(resources)
        return Agent(bot=RandomBot(), config=config, state=State(items=config.all_items(), health=health))

    def connect_all(self):
        for a in self.agents:
            a.state.neighbors = {n: 0.0 for n in self.agents if a != n}

    def tick(self):
        for a in self.agents:
            a.produce()

        for a in self.agents:
            a.request_trade()

        for a in self.agents:
            a.accept_trade()

        for a in self.agents:
            a.consume()

    def run(self, iterations=1000):
        for _ in range(iterations):
            self.tick()

    def count_living_agents(self):
        return len([a for a in self.agents if a.is_healthy()])

    def count_happy_agents(self):
        return len([a for a in self.agents if a.is_happy()])


if __name__ == "__main__":
    sim = Simulation()
    sim.run()
