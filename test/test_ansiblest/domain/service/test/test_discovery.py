from ansiblest.domain.model.test import Test

from ansiblest.domain.service.test.discovery import find_tests

from mock import patch
from unittest import TestCase

class TestFindTestsFunction(TestCase):
    TESTS_DIR = "tests"

    @patch("ansiblest.domain.service.test.discovery.walk")
    def test__flat_tests_directory__no_tests(self, walk_mock):
        walk_mock.return_value = [
            [ self.TESTS_DIR, [ "other-dir" ], [ "something-1.yaml", "something-2.yml", "other.yaml", "test-data.txt" ]]
        ]

        expected_tests = []

        actual_tests = find_tests(self.TESTS_DIR)

        self.assertEqual(expected_tests, actual_tests)
        walk_mock.assert_called_once_with(self.TESTS_DIR)

    @patch("ansiblest.domain.service.test.discovery.walk")
    def test__flat_tests_directory__only_tests(self, walk_mock):
        walk_mock.return_value = [
            [ self.TESTS_DIR, [ "other-dir" ], [ "test-something-1.yaml", "test-something-2.yml", "other.yaml", "test-data.txt" ]]
        ]

        expected_tests = [
            Test(None, None, self.TESTS_DIR + "/test-something-1.yaml", None),
            Test(None, None, self.TESTS_DIR + "/test-something-2.yml", None)
        ]

        actual_tests = find_tests(self.TESTS_DIR)

        self.assertEqual(expected_tests, actual_tests)
        walk_mock.assert_called_once_with(self.TESTS_DIR)


    @patch("ansiblest.domain.service.test.discovery.walk")
    def test__flat_tests_directory__tests_and_inventory(self, walk_mock):
        walk_mock.return_value = [
            [ self.TESTS_DIR, [ "inventory", "other-dir" ], [ "test-something-1.yaml", "test-something-2.yml", "other.yaml", "test-data.txt" ]]
        ]

        expected_tests = [
            Test(self.TESTS_DIR + "/inventory", None, self.TESTS_DIR + "/test-something-1.yaml", None),
            Test(self.TESTS_DIR + "/inventory", None, self.TESTS_DIR + "/test-something-2.yml", None)
        ]

        actual_tests = find_tests(self.TESTS_DIR)

        self.assertEqual(expected_tests, actual_tests)
        walk_mock.assert_called_once_with(self.TESTS_DIR)


    @patch("ansiblest.domain.service.test.discovery.walk")
    def test__flat_tests_directory__tests_and_setup(self, walk_mock):
        walk_mock.return_value = [
            [ self.TESTS_DIR, [ "other-dir" ], [ "test-something-1.yaml", "test-something-2.yml", "setup.yaml", "test-data.txt" ]]
        ]

        expected_tests = [
            Test(None, self.TESTS_DIR + "/setup.yaml", self.TESTS_DIR + "/test-something-1.yaml", None),
            Test(None, self.TESTS_DIR + "/setup.yaml", self.TESTS_DIR + "/test-something-2.yml", None)
        ]

        actual_tests = find_tests(self.TESTS_DIR)

        self.assertEqual(expected_tests, actual_tests)
        walk_mock.assert_called_once_with(self.TESTS_DIR)


    @patch("ansiblest.domain.service.test.discovery.walk")
    def test__flat_tests_directory__tests_and_teardown(self, walk_mock):
        walk_mock.return_value = [
            [ self.TESTS_DIR, [ "other-dir" ],  [ "test-something-1.yaml", "test-something-2.yml", "teardown.yaml", "test-data.txt" ]]
        ]

        expected_tests = [
            Test(None, None, self.TESTS_DIR + "/test-something-1.yaml", self.TESTS_DIR + "/teardown.yaml"),
            Test(None, None, self.TESTS_DIR + "/test-something-2.yml", self.TESTS_DIR + "/teardown.yaml")
        ]

        actual_tests = find_tests(self.TESTS_DIR)

        self.assertEqual(expected_tests, actual_tests)
        walk_mock.assert_called_once_with(self.TESTS_DIR)


    @patch("ansiblest.domain.service.test.discovery.walk")
    def test__flat_tests_directory__tests_in_subdirectories(self, walk_mock):
        walk_mock.return_value = [
            [ self.TESTS_DIR, [ "test-dir-1", "test-dir-2" ],  [ "test-data.txt" ]],
            [ self.TESTS_DIR + "/test-dir-1", [ "inventory" ],  [ "test-something-1.yaml", "setup.yaml", "teardown.yaml" ]],
            [ self.TESTS_DIR + "/test-dir-2", [ "inventory" ],  [ "test-something-2.yaml", "setup.yaml", "teardown.yaml" ]]
        ]

        expected_tests = [
            Test(self.TESTS_DIR + "/test-dir-1/inventory",
                 self.TESTS_DIR + "/test-dir-1/setup.yaml",
                 self.TESTS_DIR + "/test-dir-1/test-something-1.yaml",
                 self.TESTS_DIR + "/test-dir-1/teardown.yaml"),

            Test(self.TESTS_DIR + "/test-dir-2/inventory",
                 self.TESTS_DIR + "/test-dir-2/setup.yaml",
                 self.TESTS_DIR + "/test-dir-2/test-something-2.yaml",
                 self.TESTS_DIR + "/test-dir-2/teardown.yaml")
        ]

        actual_tests = find_tests(self.TESTS_DIR)

        self.assertEqual(expected_tests, actual_tests)
        walk_mock.assert_called_once_with(self.TESTS_DIR)
