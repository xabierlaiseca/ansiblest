from mock import Mock, patch
from unittest import TestCase

from ansiblest.domain.service.ansible import run_ansible_playbook

class TestRunAnsiblePlaybookFunction(TestCase):
    PLAYBOOK_PATH = "main.yaml"
    INVENTORY_PATH = "inventory"
    OUTPUT_PATH = "output.txt"

    RETURN_CODE = 10



    @patch("ansiblest.domain.service.ansible.call")
    @patch("builtins.open")
    def test__run_ansible_playbook__without_inventory(self, open_mock, call_mock):
        open_mock.return_value.__enter__.return_value = output_file_mock = Mock()
        call_mock.return_value = FakeCallReturnValue(self.RETURN_CODE)

        expected_cmd = [ "ansible-playbook", self.PLAYBOOK_PATH ]

        return_code = run_ansible_playbook(self.PLAYBOOK_PATH, self.OUTPUT_PATH)

        open_mock.assert_called_once_with(self.OUTPUT_PATH, mode="wa")
        call_mock.assert_called_once_with(expected_cmd, stdout=output_file_mock, stderr=output_file_mock)

        self.assertEqual(self.RETURN_CODE, return_code, msg="unexpected status code")


    @patch("ansiblest.domain.service.ansible.call")
    @patch("builtins.open")
    def test__run_ansible_playbook__with_inventory(self, open_mock, call_mock):
        open_mock.return_value.__enter__.return_value = output_file_mock = Mock()
        call_mock.return_value = FakeCallReturnValue(self.RETURN_CODE)

        expected_cmd = [ "ansible-playbook", self.PLAYBOOK_PATH, "-i", self.INVENTORY_PATH ]

        return_code = run_ansible_playbook(self.PLAYBOOK_PATH, self.OUTPUT_PATH, self.INVENTORY_PATH)

        open_mock.assert_called_once_with(self.OUTPUT_PATH, mode="wa")
        call_mock.assert_called_once_with(expected_cmd, stdout=output_file_mock, stderr=output_file_mock)

        self.assertEqual(self.RETURN_CODE, return_code, msg="unexpected status code")


class FakeCallReturnValue(object):
    def __init__(self, returncode):
        self.returncode = returncode
