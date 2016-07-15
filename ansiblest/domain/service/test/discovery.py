from ansiblest.domain.model.test import Test

from os import path, walk

import re

__YAML_EXTENSIONS = [ ".yaml", ".yml" ]

__INVENTORY_DIR_NAME = "inventory"
__SETUP_PLAYBOOK_NAMES = [ "setup" + ext for ext in __YAML_EXTENSIONS ]
__TEARDOWN_PLAYBOOK_NAMES = [ "teardown" + ext for ext in __YAML_EXTENSIONS ]
__TEST_NAME_REGEX = re.compile("test-.+(" + "|".join(__YAML_EXTENSIONS) + ")" )


def find_tests(tests_base_dir):
    previous_dir = None

    found = []

    for root, dirnames, filenames in walk(tests_base_dir):
        inventory = path.join(root, __INVENTORY_DIR_NAME) if __INVENTORY_DIR_NAME in dirnames else None
        setup_playbook = __find_first_playbook(root, filenames, __SETUP_PLAYBOOK_NAMES)
        teardown_playbook = __find_first_playbook(root, filenames, __TEARDOWN_PLAYBOOK_NAMES)
        found += [ Test(inventory, setup_playbook, path.join(root, filename), teardown_playbook)
                 for filename in filenames if __TEST_NAME_REGEX.fullmatch(filename)
        ]

    return found


def __find_first_playbook(root, filenames, playbooks_to_find):
    first_playbook = next(filter(lambda elem: elem in playbooks_to_find, filenames), None)

    if first_playbook:
        return path.join(root, first_playbook)
    else:
        return None
