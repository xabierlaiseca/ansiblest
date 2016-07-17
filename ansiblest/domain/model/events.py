from enum import Enum

class EventTypes(object):
    TEST_STARTED = "event.test.started"
    TEST_LIFE_CYCLE = "event.test.lifecycle"
    TEST_FINISHED = "event.test.finished"

    TEST_SUITE_FINISHED = "event.suite.finished"

class _BaseEvent(object):
    def __init__(self, name):
        self.__name = name

    @property
    def name(self):
        return self.__name


    def __eq__(self, other):
        if isinstance(other, _BaseEvent):
            return super().__eq__(other) and \
                   self.name == other.name

class _BaseTestEvent(_BaseEvent):
    def __init__(self, name, test_name):
        super().__init__(name)
        self.__test_name = test_name

    @property
    def test_name(self):
        return self.__test_name

    def __eq__(self, other):
        if isinstance(other, _BaseTestEvent):
            return super().__eq__(other) and \
                   self.test_name == self.test_name
        else:
            return False


class TestStartedEvent(_BaseTestEvent):
    def __init__(self, test_name, output_file):
        super().__init__(EventTypes.TEST_STARTED, test_name)

        self.__output_file = output_file

    @property
    def output_file(self):
        return self.__output_file

    def __eq__(self, other):
        if self.__class__ == other.__class__:

            return super().__eq__(other) and \
                   self.output_file == other.output_file
        else:
            return False


class TestLifeCycleEvent(_BaseTestEvent):
    def __init__(self, test_name, stage):
        assert isinstance(stage, TestLifeCycleStage)

        super().__init__(EventTypes.TEST_LIFE_CYCLE, test_name)

        self.__stage = stage

    @property
    def stage(self):
        return self.__stage

    def __eq__(self, other):
        if self.__class__ == other.__class__:
            return super().__eq__(other) and \
                   self.stage == other.stage
        else:
            return False


class TestLifeCycleStage(Enum):
    setup = 1
    test = 2
    teardown = 3


class TestFinishedEvent(_BaseTestEvent):
    def __init__(self, test_name, test_result_status):
        super().__init__(EventTypes.TEST_STARTED, test_name)

        self.__test_result_status = test_result_status

    @property
    def test_result_status(self):
        return self.__test_result_status

    def __eq__(self, other):
        if self.__class__ == other.__class__:
            return super().__eq__(other) and \
                   self.test_result_status == other.test_result_status
        else:
            return False

class TestSuiteFinishedEvent(_BaseEvent):
    def __init__(self):
        super().__init__(EventTypes.TEST_SUITE_FINISHED)


    def __eq__(self, other):
        if self.__class__ == other.__class__:
            return super().__eq__(other)
        else:
            return False
