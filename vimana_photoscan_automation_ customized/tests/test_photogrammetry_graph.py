import unittest

from vimana.photoscan_automation.photogrammetry_graph import *


class TestWorkflowGraph(unittest.TestCase):

    def setUp(self):
        self.wg = WorkflowGraph(self)

    def test_graph(self):
        assert self.wg is not None
        assert self.wg.G is not None

    def test_add_step(self):
        self.wg.add_workflow_step('hello')
        assert self.wg.step_exists('hello')

    def test_add_next(self):
        self.wg.add_workflow_step('first')
        self.wg.add_workflow_step('second')
        self.wg.add_next_step('first', 'second')

        assert self.wg.get_next('first') == 'second'
        assert self.wg.get_next('second') is None


if __name__ == '__main__':
    unittest.main()
