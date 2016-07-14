from .ansible import run_ansible_playbook

from ansiblest.domain.model.events import TestFinishedEvent, TestStartedEvent, TestLifeCycleEvent, TestLifeCycleStage
from ansiblest.domain.model.test import TestResult, TestResultStatus

from functools import partial

from multiprocessing import Pool

from os.path import basename

from tempfile import NamedTemporaryFile

def run_tests(tests, conf, results_queue):
    pool = Pool(processes=conf.max_running_tests)

    async_results = [ pool.apply_async( func=run_single_test, args=[test, results_queue]) for test in tests ]

    return [async_result.get() for async_result in async_results]


def run_single_test(test, results_queue):
    tf = NamedTemporaryFile(prefix=basename(test.name))
    test_started_event = TestStartedEvent(test.name, tf.name)
    results_queue.put(test_started_event)

    run_current_test_stage = partial(__run_test_stage, test=test, output_path=tf.name, results_queue=results_queue)

    test_result = run_current_test_stage(stage=TestLifeCycleStage.setup, status_on_error_code=TestResultStatus.error) or \
                  run_current_test_stage(stage=TestLifeCycleStage.test) or \
                  run_current_test_stage(stage=TestLifeCycleStage.teardown, status_on_error_code=TestResultStatus.error) or \
                  TestResult(test, TestResultStatus.successful)

    test_finished_event = TestFinishedEvent(test_result.test.name, test_result.status)
    results_queue.put(test_finished_event)

    return test_result


def __run_test_stage(test, stage, output_path, results_queue, status_on_error_code=TestResultStatus.failed):
    event = TestLifeCycleEvent(test.name, stage)
    results_queue.put(event)

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
