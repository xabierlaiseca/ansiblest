from ansiblest.domain.model.events import TestSuiteFinishedEvent
from ansiblest.domain.model.test import Test
from ansiblest.domain.service.test.runner import run_tests

from mock import patch

from nose.tools import assert_equal

from queue import Queue

from unittest import TestCase

import asyncio



def _run_single_test_fake(event, callback):
    callback(event)


class TestRunTestsFunction(TestCase):
    MAX_PARALLEL_TESTS = 2

    INVENTORY_1 = "inventory1"
    SETUP_PLAYBOOK_1 = "setup1.yaml"
    TEST_PLAYBOOK_1 = "test1.yaml"
    TEARDOWN_PLAYBOOK_1 = "teardown1.yaml"

    INVENTORY_2 = "inventory2"
    SETUP_PLAYBOOK_2 = "setup2.yaml"
    TEST_PLAYBOOK_2 = "test2.yaml"
    TEARDOWN_PLAYBOOK_2 = "teardown2.yaml"

    def setUp(self):
        self.queue = Queue()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    @patch("ansiblest.domain.service.test.runner.run_single_test", new=_run_single_test_fake)
    def test__successful(self):
        tests = [
            Test(self.TEST_PLAYBOOK_1, self.INVENTORY_1, self.SETUP_PLAYBOOK_1, self.TEARDOWN_PLAYBOOK_1),
            Test(self.TEST_PLAYBOOK_2, self.INVENTORY_2, self.SETUP_PLAYBOOK_2, self.TEARDOWN_PLAYBOOK_2)
        ]

        self.__run_coroutine_sync(run_tests(tests, self.__events_callback, self.MAX_PARALLEL_TESTS))

        for _ in range(len(tests)):
            event = self.queue.get(timeout=1)
            assert event in tests
            tests.remove(event)

        assert TestSuiteFinishedEvent() == self.queue.get(timeout=1)
        assert self.queue.empty()


    def __events_callback(self, event):
        self.queue.put(event)

    def __run_coroutine_sync(self, coro):
        task = self.loop.create_task(coro)
        self.loop.run_until_complete(task)
