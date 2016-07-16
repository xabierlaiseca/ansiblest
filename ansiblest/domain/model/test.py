from enum import Enum

class Test(object):
    def __init__(self, test_playbook, inventory=None, setup_playbook=None, teardown_playbook=None):
        assert test_playbook is not None

        self.__test_playbook = test_playbook
        self.__inventory = inventory
        self.__setup_playbook = setup_playbook
        self.__teardown_playbook = teardown_playbook


    @property
    def test_playbook(self):
        return self.__test_playbook

    @property
    def name(self):
        return self.__test_playbook

    @property
    def inventory(self):
        return self.__inventory

    @property
    def setup_playbook(self):
        return self.__setup_playbook

    @property
    def teardown_playbook(self):
        return self.__teardown_playbook

    def __eq__(self, other):
        if self.__class__ == other.__class__:
            return self.test_playbook == other.test_playbook and \
                   self.inventory == other.inventory and \
                   self.setup_playbook == other.setup_playbook and \
                   self.teardown_playbook == other.teardown_playbook
        else:
            return False

class TestResultStatus(Enum):
    successful = 1
    failed = 2
    error = 3


class TestResult(object):
    def __init__(self, test, status):
        assert isinstance(status, TestResultStatus)

        self.__test = test
        self.__status = status

    @property
    def test(self):
        return self.__test

    @property
    def status(self):
        return self.__status

    def __eq__(self, other):
        if self.__class__ == other.__class__:
            return self.test == other.test and self.status == other.status
        else:
            return False
