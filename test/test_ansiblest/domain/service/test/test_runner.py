from queue import Queue
from mock import call, patch, Mock
from unittest import TestCase

from ansiblest.domain.model.events import TestFinishedEvent, TestStartedEvent, TestLifeCycleEvent, TestLifeCycleStage
from ansiblest.domain.model.test import Test, TestResult, TestResultStatus

from ansiblest.domain.service.test.runner import run_tests, run_single_test


class TestRunTestsFunction(TestCase):
    MAX_RUNNING_TESTS = 2

    INVENTORY_1 = "inventory1"
    SETUP_PLAYBOOK_1 = "setup1.yaml"
    TEST_PLAYBOOK_1 = "test1.yaml"
    TEARDOWN_PLAYBOOK_1 = "teardown1.yaml"

    INVENTORY_2 = "inventory2"
    SETUP_PLAYBOOK_2 = "setup2.yaml"
    TEST_PLAYBOOK_2 = "test2.yaml"
    TEARDOWN_PLAYBOOK_2 = "teardown2.yaml"

    @patch("ansiblest.domain.service.test.runner.Pool")
    def test__successful(self, pool_class_mock):
        tests = [
            Test(self.INVENTORY_1, self.SETUP_PLAYBOOK_1, self.TEST_PLAYBOOK_1, self.TEARDOWN_PLAYBOOK_1),
            Test(self.INVENTORY_2, self.SETUP_PLAYBOOK_2, self.TEST_PLAYBOOK_2, self.TEARDOWN_PLAYBOOK_2)
        ]
        results_queue = Queue()

        pool_instance_mock = pool_class_mock.return_value

        result_1 = Mock()
        result_2 = Mock()
        pool_instance_mock.apply_async.side_effect = [ result_1, result_2 ]
        result_1.get.return_value = TestResult(tests[0], TestResultStatus.successful)
        result_2.get.return_value = TestResult(tests[1], TestResultStatus.successful)

        expected = [ result_1.get.return_value, result_2.get.return_value ]

        returned = run_tests(tests, FakeConf(self.MAX_RUNNING_TESTS), results_queue)

        self.assertEqual(expected, returned)

        pool_class_mock.assert_called_once_with(processes=self.MAX_RUNNING_TESTS)

        self.assertEqual(2, pool_instance_mock.apply_async.call_count)
        pool_instance_mock.apply_async.assert_has_calls([
            call(func=run_single_test, args=[tests[0], results_queue]),
            call(func=run_single_test, args=[tests[1], results_queue])
        ])


class FakeConf(object):
    def __init__(self, max_running_tests):
        self.max_running_tests = max_running_tests


class TestRunSigleTestFunction(TestCase):
    TEST_NAME = "my-test"
    OUTPUT_FILE = "/tmp/output.file"

    INVENTORY = "inventory"
    SETUP_PLAYBOOK = "setup.yaml"
    TEST_PLAYBOOK = "test.yaml"
    TEARDOWN_PLAYBOOK = "teardown.yaml"

    @patch("ansiblest.domain.service.test.runner.run_ansible_playbook")
    @patch("ansiblest.domain.service.test.runner.NamedTemporaryFile")
    def test__setup_stage_error(self, ntf_class_mock, rap_mock):
        ntf_instance_mock = ntf_class_mock.return_value
        ntf_instance_mock.name = self.OUTPUT_FILE
        rap_mock.return_value = 1

        test = Test(self.INVENTORY, self.SETUP_PLAYBOOK, self.TEST_PLAYBOOK, self.TEARDOWN_PLAYBOOK)
        results_queue = Queue()
        expected_result_status = TestResultStatus.error
        expected = TestResult(test, expected_result_status)

        returned = run_single_test(test, results_queue)

        self.assertEqual(expected, returned)
        self.assertEqual(3, results_queue.qsize())
        self.assertEqual(TestStartedEvent(self.TEST_NAME, self.OUTPUT_FILE), results_queue.get())
        self.assertEqual(TestLifeCycleEvent(self.TEST_NAME, TestLifeCycleStage.setup), results_queue.get())
        self.assertEqual(TestFinishedEvent(self.TEST_NAME, expected_result_status), results_queue.get())

        rap_mock.assert_called_once_with(self.INVENTORY, self.SETUP_PLAYBOOK, self.OUTPUT_FILE)

    @patch("ansiblest.domain.service.test.runner.run_ansible_playbook")
    @patch("ansiblest.domain.service.test.runner.NamedTemporaryFile")
    def test__test_stage_failed(self, ntf_class_mock, rap_mock):
        ntf_instance_mock = ntf_class_mock.return_value
        ntf_instance_mock.name = self.OUTPUT_FILE
        rap_mock.side_effect = [0, 1]

        test = Test(self.INVENTORY, self.SETUP_PLAYBOOK, self.TEST_PLAYBOOK, self.TEARDOWN_PLAYBOOK)
        results_queue = Queue()
        expected_result_status = TestResultStatus.failed
        expected = TestResult(test, expected_result_status)

        returned = run_single_test(test, results_queue)

        self.assertEqual(expected, returned)
        self.assertEqual(4, results_queue.qsize())
        self.assertEqual(TestStartedEvent(self.TEST_NAME, self.OUTPUT_FILE), results_queue.get())
        self.assertEqual(TestLifeCycleEvent(self.TEST_NAME, TestLifeCycleStage.setup), results_queue.get())
        self.assertEqual(TestLifeCycleEvent(self.TEST_NAME, TestLifeCycleStage.test), results_queue.get())
        self.assertEqual(TestFinishedEvent(self.TEST_NAME, expected_result_status), results_queue.get())

        self.assertEqual(2, rap_mock.call_count)
        rap_mock.assert_has_calls([
            call(self.INVENTORY, self.SETUP_PLAYBOOK, self.OUTPUT_FILE),
            call(self.INVENTORY, self.TEST_PLAYBOOK, self.OUTPUT_FILE)
        ])

    @patch("ansiblest.domain.service.test.runner.run_ansible_playbook")
    @patch("ansiblest.domain.service.test.runner.NamedTemporaryFile")
    def test__teardown_stage_error(self, ntf_class_mock, rap_mock):
        ntf_instance_mock = ntf_class_mock.return_value
        ntf_instance_mock.name = self.OUTPUT_FILE
        rap_mock.side_effect = [0, 0, 1]

        test = Test(self.INVENTORY, self.SETUP_PLAYBOOK, self.TEST_PLAYBOOK, self.TEARDOWN_PLAYBOOK)
        results_queue = Queue()
        expected_result_status = TestResultStatus.error
        expected = TestResult(test, expected_result_status)

        returned = run_single_test(test, results_queue)

        self.assertEqual(expected, returned)
        self.assertEqual(5, results_queue.qsize())
        self.assertEqual(TestStartedEvent(self.TEST_NAME, self.OUTPUT_FILE), results_queue.get())
        self.assertEqual(TestLifeCycleEvent(self.TEST_NAME, TestLifeCycleStage.setup), results_queue.get())
        self.assertEqual(TestLifeCycleEvent(self.TEST_NAME, TestLifeCycleStage.test), results_queue.get())
        self.assertEqual(TestLifeCycleEvent(self.TEST_NAME, TestLifeCycleStage.teardown), results_queue.get())
        self.assertEqual(TestFinishedEvent(self.TEST_NAME, expected_result_status), results_queue.get())

        self.assertEqual(3, rap_mock.call_count)
        rap_mock.assert_has_calls([
            call(self.INVENTORY, self.SETUP_PLAYBOOK, self.OUTPUT_FILE),
            call(self.INVENTORY, self.TEST_PLAYBOOK, self.OUTPUT_FILE),
            call(self.INVENTORY, self.TEARDOWN_PLAYBOOK, self.OUTPUT_FILE)
        ])

    @patch("ansiblest.domain.service.test.runner.run_ansible_playbook")
    @patch("ansiblest.domain.service.test.runner.NamedTemporaryFile")
    def test__successful(self, ntf_class_mock, rap_mock):
        ntf_instance_mock = ntf_class_mock.return_value
        ntf_instance_mock.name = self.OUTPUT_FILE
        rap_mock.return_value = 0

        test = Test(self.INVENTORY, self.SETUP_PLAYBOOK, self.TEST_PLAYBOOK, self.TEARDOWN_PLAYBOOK)
        results_queue = Queue()
        expected_result_status = TestResultStatus.successful
        expected = TestResult(test, expected_result_status)

        returned = run_single_test(test, results_queue)

        self.assertEqual(expected, returned)
        self.assertEqual(5, results_queue.qsize())
        self.assertEqual(TestStartedEvent(self.TEST_NAME, self.OUTPUT_FILE), results_queue.get())
        self.assertEqual(TestLifeCycleEvent(self.TEST_NAME, TestLifeCycleStage.setup), results_queue.get())
        self.assertEqual(TestLifeCycleEvent(self.TEST_NAME, TestLifeCycleStage.test), results_queue.get())
        self.assertEqual(TestLifeCycleEvent(self.TEST_NAME, TestLifeCycleStage.teardown), results_queue.get())
        self.assertEqual(TestFinishedEvent(self.TEST_NAME, expected_result_status), results_queue.get())

        self.assertEqual(3, rap_mock.call_count)
        rap_mock.assert_has_calls([
            call(self.INVENTORY, self.SETUP_PLAYBOOK, self.OUTPUT_FILE),
            call(self.INVENTORY, self.TEST_PLAYBOOK, self.OUTPUT_FILE),
            call(self.INVENTORY, self.TEARDOWN_PLAYBOOK, self.OUTPUT_FILE)
        ])
