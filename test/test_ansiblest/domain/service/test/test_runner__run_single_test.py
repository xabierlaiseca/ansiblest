from mock import call, patch, Mock
from unittest import TestCase

from ansiblest.domain.model.events import TestFinishedEvent, TestStartedEvent, TestLifeCycleEvent, TestLifeCycleStage
from ansiblest.domain.model.test import Test, TestResult, TestResultStatus

from ansiblest.domain.service.test.runner import run_single_test


class FakeConf(object):
    def __init__(self, max_parallel_tests):
        self.max_parallel_tests = max_parallel_tests


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

        test = Test(self.TEST_PLAYBOOK, self.INVENTORY, self.SETUP_PLAYBOOK, self.TEARDOWN_PLAYBOOK)
        events_callback = Mock()
        expected_result_status = TestResultStatus.error
        expected = TestResult(test, expected_result_status)

        returned = run_single_test(test, events_callback)

        self.assertEqual(expected, returned)

        self.assertEqual(3, events_callback.call_count)
        events_callback.assert_has_calls([
            call(TestStartedEvent(self.TEST_NAME, self.OUTPUT_FILE)),
            call(TestLifeCycleEvent(self.TEST_NAME, TestLifeCycleStage.setup)),
            call(TestFinishedEvent(self.TEST_NAME, expected_result_status))
        ])

        rap_mock.assert_called_once_with(self.INVENTORY, self.SETUP_PLAYBOOK, self.OUTPUT_FILE)

    @patch("ansiblest.domain.service.test.runner.run_ansible_playbook")
    @patch("ansiblest.domain.service.test.runner.NamedTemporaryFile")
    def test__test_stage_failed(self, ntf_class_mock, rap_mock):
        ntf_instance_mock = ntf_class_mock.return_value
        ntf_instance_mock.name = self.OUTPUT_FILE
        rap_mock.side_effect = [0, 1]

        test = Test(self.TEST_PLAYBOOK, self.INVENTORY, self.SETUP_PLAYBOOK, self.TEARDOWN_PLAYBOOK)
        events_callback = Mock()
        expected_result_status = TestResultStatus.failed
        expected = TestResult(test, expected_result_status)

        returned = run_single_test(test, events_callback)

        self.assertEqual(expected, returned)

        self.assertEqual(4, events_callback.call_count)

        events_callback.assert_has_calls([
            call(TestStartedEvent(self.TEST_NAME, self.OUTPUT_FILE)),
            call(TestLifeCycleEvent(self.TEST_NAME, TestLifeCycleStage.setup)),
            call(TestLifeCycleEvent(self.TEST_NAME, TestLifeCycleStage.test)),
            call(TestFinishedEvent(self.TEST_NAME, expected_result_status))
        ])

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

        test = Test(self.TEST_PLAYBOOK, self.INVENTORY, self.SETUP_PLAYBOOK, self.TEARDOWN_PLAYBOOK)
        events_callback = Mock()
        expected_result_status = TestResultStatus.error
        expected = TestResult(test, expected_result_status)

        returned = run_single_test(test, events_callback)

        self.assertEqual(expected, returned)

        self.assertEqual(5, events_callback.call_count)
        events_callback.assert_has_calls([
            call(TestStartedEvent(self.TEST_NAME, self.OUTPUT_FILE)),
            call(TestLifeCycleEvent(self.TEST_NAME, TestLifeCycleStage.setup)),
            call(TestLifeCycleEvent(self.TEST_NAME, TestLifeCycleStage.test)),
            call(TestLifeCycleEvent(self.TEST_NAME, TestLifeCycleStage.teardown)),
            call(TestFinishedEvent(self.TEST_NAME, expected_result_status))
        ])

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

        test = Test(self.TEST_PLAYBOOK, self.INVENTORY, self.SETUP_PLAYBOOK, self.TEARDOWN_PLAYBOOK)
        events_callback = Mock()
        expected_result_status = TestResultStatus.successful
        expected = TestResult(test, expected_result_status)

        returned = run_single_test(test, events_callback)

        self.assertEqual(expected, returned)

        self.assertEqual(5, events_callback.call_count)
        events_callback.assert_has_calls([
            call(TestStartedEvent(self.TEST_NAME, self.OUTPUT_FILE)),
            call(TestLifeCycleEvent(self.TEST_NAME, TestLifeCycleStage.setup)),
            call(TestLifeCycleEvent(self.TEST_NAME, TestLifeCycleStage.test)),
            call(TestLifeCycleEvent(self.TEST_NAME, TestLifeCycleStage.teardown)),
            call(TestFinishedEvent(self.TEST_NAME, expected_result_status))
        ])

        self.assertEqual(3, rap_mock.call_count)
        rap_mock.assert_has_calls([
            call(self.INVENTORY, self.SETUP_PLAYBOOK, self.OUTPUT_FILE),
            call(self.INVENTORY, self.TEST_PLAYBOOK, self.OUTPUT_FILE),
            call(self.INVENTORY, self.TEARDOWN_PLAYBOOK, self.OUTPUT_FILE)
        ])
