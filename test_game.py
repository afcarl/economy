import unittest
from game import Simulation


class TestDisconnectedGraph(unittest.TestCase):

    def setUp(self):
        self.s = Simulation(resources='AB', agent_count=2)
        del self.s.agents[0].config.production_per_tick['A']
        del self.s.agents[0].config.consumption_per_tick['B']
        del self.s.agents[1].config.production_per_tick['B']
        del self.s.agents[1].config.consumption_per_tick['A']

    def test_EverybodyDies(self):
        self.s.tick()
        assert self.s.count_living_agents() == 0

    def test_DictatorSurvives(self):
        self.s.agents[0].state.inventory['A'] = 1
        self.s.tick()
        assert self.s.count_living_agents() == 1

    def test_DictatorEventuallyDies(self):
        self.s.tick()
        assert self.s.count_living_agents() == 0


class TestFullyConnectedMatrix(unittest.TestCase):

    def setUp(self):
        self.s = Simulation(resources='AB', agent_count=2)
        self.s.connect_all()

    def test_ResourcesBothSurvive(self):
        self.s.tick()
        assert self.s.count_living_agents() == 2

    def test_ResourcesNoneSurvive(self):
        for a in self.s.agents:
            a.state.inventory['A'] = -1
        self.s.tick()
        assert self.s.count_living_agents() == 0
