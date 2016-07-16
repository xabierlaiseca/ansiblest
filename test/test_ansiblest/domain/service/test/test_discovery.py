from ansiblest.domain.model.test import Test

from ansiblest.domain.service.test.discovery import find_tests

from mock import patch
from unittest import TestCase

class TestFindTestsFunction(TestCase):
    TESTS_DIR = "tests"


    @patch("ansiblest.domain.service.test.discovery.walk")
    def test__extra_files__not_yaml_file(self, walk_mock):
        walk_mock.return_value = [
            [ self.TESTS_DIR, [ "inventory" ], [ "setup.yaml", "teardown.yml", "test-data.txt" ] ]
        ]

        expected_tests = []

        actual_tests = find_tests(self.TESTS_DIR)

        self.assertEqual(expected_tests, actual_tests)
        walk_mock.assert_called_once_with(self.TESTS_DIR)


    @patch("ansiblest.domain.service.test.discovery.walk")
    def test__extra_files__no_test_prefix(self, walk_mock):
        walk_mock.return_value = [
            [ self.TESTS_DIR, [ "inventory" ], [ "setup.yaml", "teardown.yml", "other.yaml" ] ]
        ]

        expected_tests = []

        actual_tests = find_tests(self.TESTS_DIR)

        self.assertEqual(expected_tests, actual_tests)
        walk_mock.assert_called_once_with(self.TESTS_DIR)


    @patch("ansiblest.domain.service.test.discovery.walk")
    def test__flat_tests_directory__only_tests(self, walk_mock):
        walk_mock.return_value = [
            [ self.TESTS_DIR, [ "other-dir" ], [ "test-something-1.yaml", "test-something-2.yml" ] ]
        ]

        expected_tests = [
            Test(test_playbook=self.TESTS_DIR + "/test-something-1.yaml"),
            Test(test_playbook=self.TESTS_DIR + "/test-something-2.yml")
        ]

        actual_tests = find_tests(self.TESTS_DIR)

        self.assertEqual(expected_tests, actual_tests)
        walk_mock.assert_called_once_with(self.TESTS_DIR)


    @patch("ansiblest.domain.service.test.discovery.walk")
    def test__flat_tests_directory__tests_and_inventory(self, walk_mock):
        walk_mock.return_value = [
            [ self.TESTS_DIR, [ "inventory" ], [ "test-something-1.yaml", "test-something-2.yml" ] ]
        ]

        expected_tests = [
            Test(test_playbook=self.TESTS_DIR + "/test-something-1.yaml", inventory=self.TESTS_DIR + "/inventory"),
            Test(test_playbook=self.TESTS_DIR + "/test-something-2.yml", inventory=self.TESTS_DIR + "/inventory")
        ]

        actual_tests = find_tests(self.TESTS_DIR)

        self.assertEqual(expected_tests, actual_tests)
        walk_mock.assert_called_once_with(self.TESTS_DIR)


    @patch("ansiblest.domain.service.test.discovery.walk")
    def test__flat_tests_directory__tests_and_setup(self, walk_mock):
        walk_mock.return_value = [
            [ self.TESTS_DIR, [], [ "test-something-1.yaml", "test-something-2.yml", "setup.yaml" ] ]
        ]

        expected_tests = [
            Test(test_playbook=self.TESTS_DIR + "/test-something-1.yaml", setup_playbook=self.TESTS_DIR + "/setup.yaml"),
            Test(test_playbook=self.TESTS_DIR + "/test-something-2.yml", setup_playbook=self.TESTS_DIR + "/setup.yaml")
        ]

        actual_tests = find_tests(self.TESTS_DIR)

        self.assertEqual(expected_tests, actual_tests)
        walk_mock.assert_called_once_with(self.TESTS_DIR)


    @patch("ansiblest.domain.service.test.discovery.walk")
    def test__flat_tests_directory__tests_and_teardown(self, walk_mock):
        walk_mock.return_value = [
            [ self.TESTS_DIR, [], [ "test-something-1.yaml", "test-something-2.yml", "teardown.yaml" ] ]
        ]

        expected_tests = [
            Test(test_playbook=self.TESTS_DIR + "/test-something-1.yaml",
                 teardown_playbook=self.TESTS_DIR + "/teardown.yaml"),

            Test(test_playbook=self.TESTS_DIR + "/test-something-2.yml",
                 teardown_playbook=self.TESTS_DIR + "/teardown.yaml")
        ]

        actual_tests = find_tests(self.TESTS_DIR)

        self.assertEqual(expected_tests, actual_tests)
        walk_mock.assert_called_once_with(self.TESTS_DIR)


    @patch("ansiblest.domain.service.test.discovery.walk")
    def test__flat_tests_directories__tests_in_subdirectories(self, walk_mock):
        walk_mock.return_value = [
            [ self.TESTS_DIR, [ "dir-1", "dir-2" ], [ "test-data.txt" ] ],
            [ self.TESTS_DIR + "/dir-1", [ "inventory" ], [ "test-something-1.yaml", "setup.yaml", "teardown.yaml" ] ],
            [ self.TESTS_DIR + "/dir-2", [ "inventory" ], [ "test-something-2.yaml", "setup.yaml", "teardown.yaml" ] ]
        ]

        expected_tests = [
            Test(test_playbook=self.TESTS_DIR + "/dir-1/test-something-1.yaml",
                 inventory=self.TESTS_DIR + "/dir-1/inventory",
                 setup_playbook=self.TESTS_DIR + "/dir-1/setup.yaml",
                 teardown_playbook=self.TESTS_DIR + "/dir-1/teardown.yaml"),

            Test(test_playbook=self.TESTS_DIR + "/dir-2/test-something-2.yaml",
                 inventory=self.TESTS_DIR + "/dir-2/inventory",
                 setup_playbook=self.TESTS_DIR + "/dir-2/setup.yaml",
                 teardown_playbook=self.TESTS_DIR + "/dir-2/teardown.yaml")
        ]

        actual_tests = find_tests(self.TESTS_DIR)

        self.assertEqual(expected_tests, actual_tests)
        walk_mock.assert_called_once_with(self.TESTS_DIR)


    @patch("ansiblest.domain.service.test.discovery.walk")
    def test__hierarchy_tests_directories__inventory_from_parent(self, walk_mock):
        walk_mock.return_value = [
            [ self.TESTS_DIR, [ "inventory" ], [] ],
            [ self.TESTS_DIR + "/dir-1", [], [ "test-something-1.yaml" ] ]
        ]

        expected_tests = [
            Test(test_playbook=self.TESTS_DIR + "/dir-1/test-something-1.yaml",
                 inventory=self.TESTS_DIR + "/inventory")
        ]

        actual_tests = find_tests(self.TESTS_DIR)

        self.assertEqual(expected_tests, actual_tests)
        walk_mock.assert_called_once_with(self.TESTS_DIR)


    @patch("ansiblest.domain.service.test.discovery.walk")
    def test__hierarchy_tests_directories__setup_playbook_from_parent(self, walk_mock):
        walk_mock.return_value = [
            [ self.TESTS_DIR, [], [ "setup.yaml" ] ],
            [ self.TESTS_DIR + "/dir-1", [], [ "test-something-1.yaml" ] ]
      ]

        expected_tests = [
            Test(test_playbook=self.TESTS_DIR + "/dir-1/test-something-1.yaml",
                 setup_playbook=self.TESTS_DIR + "/setup.yaml")
        ]

        actual_tests = find_tests(self.TESTS_DIR)

        self.assertEqual(expected_tests, actual_tests)
        walk_mock.assert_called_once_with(self.TESTS_DIR)


    @patch("ansiblest.domain.service.test.discovery.walk")
    def test__hierarchy_tests_directories__teardown_playbook_from_parent(self, walk_mock):
        walk_mock.return_value = [
            [ self.TESTS_DIR, [], [ "teardown.yaml" ] ],
            [ self.TESTS_DIR + "/dir-1", [], [ "test-something-1.yaml" ] ]
        ]

        expected_tests = [
            Test(test_playbook=self.TESTS_DIR + "/dir-1/test-something-1.yaml",
                 teardown_playbook=self.TESTS_DIR + "/teardown.yaml")
        ]

        actual_tests = find_tests(self.TESTS_DIR)

        self.assertEqual(expected_tests, actual_tests)
        walk_mock.assert_called_once_with(self.TESTS_DIR)


    @patch("ansiblest.domain.service.test.discovery.walk")
    def test__hierarchy_tests_directories__preference_current_dir_inventory(self, walk_mock):
        walk_mock.return_value = [
            [ self.TESTS_DIR, [ "inventory" ], [] ],
            [ self.TESTS_DIR + "/dir-1", [ "inventory" ], [ "test-something-1.yaml" ] ]
        ]

        expected_tests = [
            Test(test_playbook=self.TESTS_DIR + "/dir-1/test-something-1.yaml",
                 inventory=self.TESTS_DIR + "/dir-1/inventory")
        ]

        actual_tests = find_tests(self.TESTS_DIR)

        self.assertEqual(expected_tests, actual_tests)
        walk_mock.assert_called_once_with(self.TESTS_DIR)


    @patch("ansiblest.domain.service.test.discovery.walk")
    def test__hierarchy_tests_directories__preference_current_dir_setup_playbook(self, walk_mock):
        walk_mock.return_value = [
            [ self.TESTS_DIR, [], [ "setup.yaml" ] ],
            [ self.TESTS_DIR + "/dir-1", [], [ "test-something-1.yaml", "setup.yaml" ] ]
        ]

        expected_tests = [
            Test(test_playbook=self.TESTS_DIR + "/dir-1/test-something-1.yaml",
                 setup_playbook=self.TESTS_DIR + "/dir-1/setup.yaml")
        ]

        actual_tests = find_tests(self.TESTS_DIR)

        self.assertEqual(expected_tests, actual_tests)
        walk_mock.assert_called_once_with(self.TESTS_DIR)


    @patch("ansiblest.domain.service.test.discovery.walk")
    def test__hierarchy_tests_directories__preference_current_dir_teardown_playbook(self, walk_mock):
        walk_mock.return_value = [
            [ self.TESTS_DIR, [], [ "teardown.yaml" ] ],
            [ self.TESTS_DIR + "/dir-1", [], [ "test-something-1.yaml", "teardown.yaml" ] ]
        ]

        expected_tests = [
            Test(test_playbook=self.TESTS_DIR + "/dir-1/test-something-1.yaml",
                 teardown_playbook=self.TESTS_DIR + "/dir-1/teardown.yaml")
        ]

        actual_tests = find_tests(self.TESTS_DIR)

        self.assertEqual(expected_tests, actual_tests)
        walk_mock.assert_called_once_with(self.TESTS_DIR)


    @patch("ansiblest.domain.service.test.discovery.walk")
    def test__multiple_hierarchies_tests_directories__inventory_from_sibling_discarded(self, walk_mock):
        walk_mock.return_value = [
            [ self.TESTS_DIR, [ "inventory" ], [] ],
            [ self.TESTS_DIR + "/dir-1", [ "inventory" ], [] ],
            [ self.TESTS_DIR + "/dir-2", [], [ "test-1.yaml" ] ]
        ]

        expected_tests = [
            Test(test_playbook=self.TESTS_DIR + "/dir-2/test-1.yaml",
                 inventory=self.TESTS_DIR + "/inventory")
        ]

        actual_tests = find_tests(self.TESTS_DIR)

        self.assertEqual(expected_tests, actual_tests)
        walk_mock.assert_called_once_with(self.TESTS_DIR)


    @patch("ansiblest.domain.service.test.discovery.walk")
    def test__multiple_hierarchies_tests_directories__setup_playbook_from_sibling_discarded(self, walk_mock):
        walk_mock.return_value = [
            [ self.TESTS_DIR, [], [ "setup.yaml" ] ],
            [ self.TESTS_DIR + "/dir-1", [], [ "setup.yaml" ] ],
            [ self.TESTS_DIR + "/dir-2", [], [ "test-1.yaml" ] ]
        ]

        expected_tests = [
            Test(test_playbook=self.TESTS_DIR + "/dir-2/test-1.yaml",
                 setup_playbook=self.TESTS_DIR + "/setup.yaml")
        ]

        actual_tests = find_tests(self.TESTS_DIR)

        self.assertEqual(expected_tests, actual_tests)
        walk_mock.assert_called_once_with(self.TESTS_DIR)


    @patch("ansiblest.domain.service.test.discovery.walk")
    def test__multiple_hierarchies_tests_directories__teardown_playbook_from_sibling_discarded(self, walk_mock):
        walk_mock.return_value = [
            [ self.TESTS_DIR, [], [ "teardown.yaml" ] ],
            [ self.TESTS_DIR + "/dir-1", [], [ "teardown.yaml" ] ],
            [ self.TESTS_DIR + "/dir-2", [], [ "test-1.yaml" ] ]
        ]

        expected_tests = [
            Test(test_playbook=self.TESTS_DIR + "/dir-2/test-1.yaml",
                 teardown_playbook=self.TESTS_DIR + "/teardown.yaml")
        ]

        actual_tests = find_tests(self.TESTS_DIR)

        self.assertEqual(expected_tests, actual_tests)
        walk_mock.assert_called_once_with(self.TESTS_DIR)
