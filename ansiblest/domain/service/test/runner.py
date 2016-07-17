from ..ansible import run_ansible_playbook

from ansiblest.domain.model.events import TestFinishedEvent, TestStartedEvent, TestLifeCycleEvent, TestLifeCycleStage, \
                                          TestSuiteFinishedEvent
from ansiblest.domain.model.test import TestResult, TestResultStatus

from concurrent.futures import ThreadPoolExecutor

from functools import partial

from os.path import basename

from tempfile import NamedTemporaryFile

import asyncio

@asyncio.coroutine
def run_tests(tests, events_callback, max_parallel_tests=1):
    executor = ThreadPoolExecutor(max_workers=max_parallel_tests)
    loop = asyncio.get_event_loop()

    futures = [ loop.run_in_executor(executor, run_single_test, test, events_callback) for test in tests ]

    for future in futures:
        yield from future

    events_callback(TestSuiteFinishedEvent())


def run_single_test(test, events_callback):
    tf = NamedTemporaryFile(prefix=basename(test.name))
    test_started_event = TestStartedEvent(test.name, tf.name)
    events_callback(test_started_event)

    run_current_test_stage = partial(__run_test_stage, test=test, output_path=tf.name, events_callback=events_callback)

    test_result = run_current_test_stage(stage=TestLifeCycleStage.setup, status_on_error_code=TestResultStatus.error) or \
                  run_current_test_stage(stage=TestLifeCycleStage.test) or \
                  run_current_test_stage(stage=TestLifeCycleStage.teardown, status_on_error_code=TestResultStatus.error) or \
                  TestResult(test, TestResultStatus.successful)

    test_finished_event = TestFinishedEvent(test_result.test.name, test_result.status)
    events_callback(test_finished_event)

    return test_result


def __run_test_stage(test, stage, output_path, events_callback, status_on_error_code=TestResultStatus.failed):
    event = TestLifeCycleEvent(test.name, stage)
    events_callback(event)

    return_code = run_ansible_playbook(test.inventory, __get_stage_playbook(test, stage), output_path)

    if return_code is 0:
        return None
    else:
        return TestResult(test, status_on_error_code)


def __get_stage_playbook(test, stage):
    if stage == TestLifeCycleStage.setup:
        return test.setup_playbook
    elif stage == TestLifeCycleStage.test:
        return test.test_playbook
    elif stage == TestLifeCycleStage.teardown:
        return test.teardown_playbook
    else:
        raise RuntimeError("Unexpected test stage: '%s'" % stage)
