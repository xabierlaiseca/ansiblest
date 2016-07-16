from ansiblest.domain.model.test import Test

from os import path, sep as path_sep, walk

import re

__YAML_EXTENSIONS = [ ".yaml", ".yml" ]

__INVENTORY_DIR_NAME = "inventory"
__SETUP_PLAYBOOK_NAMES = [ "setup" + ext for ext in __YAML_EXTENSIONS ]
__TEARDOWN_PLAYBOOK_NAMES = [ "teardown" + ext for ext in __YAML_EXTENSIONS ]
__TEST_NAME_REGEX = re.compile("test-.+(" + "|".join(__YAML_EXTENSIONS) + ")" )


def find_tests(tests_base_dir):
    previous_dir = None

    found = []

    assoc_files_stack = []

    for current_dir, dirnames, filenames in walk(tests_base_dir):
        __drop_assoc_files_from_stack(assoc_files_stack, previous_dir, current_dir)

        __append_assoc_files(assoc_files_stack, current_dir, dirnames, filenames)

        assoc_files = __assoc_files_from_stack(assoc_files_stack)

        found += [ Test(test_playbook=path.join(current_dir, filename),
                        inventory=assoc_files.inventory,
                        setup_playbook=assoc_files.setup_playbook,
                        teardown_playbook=assoc_files.teardown_playbook)
                 for filename in filenames if __TEST_NAME_REGEX.fullmatch(filename)
        ]

        previous_dir = current_dir

    return found


def __drop_assoc_files_from_stack(assoc_files_stack, previous_dir, current_dir):
    if previous_dir is not None and not current_dir.startswith(previous_dir):
        previous_dir_splitted = __path_split(previous_dir)
        current_dir_splitted = __path_split(current_dir)

        while len(previous_dir_splitted) > 0 and \
              len(current_dir_splitted) > 0 and \
              previous_dir_splitted[0] == current_dir_splitted[0]:

            previous_dir_splitted.pop(0)
            current_dir_splitted.pop(0)

        for _ in previous_dir_splitted:
            assoc_files_stack.pop()

def __path_split(path_to_split):
    parent, current = path.split(path_to_split)

    if len(parent) is 0:
        return [ current ]
    else:
        return __path_split(parent) + [ current ]

def __append_assoc_files(assoc_files_stack, current_dir, dirnames, filenames):
    inventory = path.join(current_dir, __INVENTORY_DIR_NAME) if __INVENTORY_DIR_NAME in dirnames else None
    setup_playbook = __find_first_playbook(current_dir, filenames, __SETUP_PLAYBOOK_NAMES)
    teardown_playbook = __find_first_playbook(current_dir, filenames, __TEARDOWN_PLAYBOOK_NAMES)

    assoc_files_stack.append( __TestAssociatedFiles(inventory, setup_playbook, teardown_playbook) )


def __assoc_files_from_stack(assoc_files_stack):
    return __TestAssociatedFiles(
        inventory=__assoc_file_from_stack(assoc_files_stack, lambda elem: elem.inventory),
        setup_playbook=__assoc_file_from_stack(assoc_files_stack, lambda elem: elem.setup_playbook),
        teardown_playbook=__assoc_file_from_stack(assoc_files_stack, lambda elem: elem.teardown_playbook)
    )


def __assoc_file_from_stack(assoc_files_stack, extractor):
    assoc_files = filter(lambda elem: elem is not None, map(extractor, reversed(assoc_files_stack)))
    return next(assoc_files, None)


def __find_first_playbook(current_dir, filenames, playbooks_to_find):
    first_playbook = next(filter(lambda elem: elem in playbooks_to_find, filenames), None)

    if first_playbook:
        return path.join(current_dir, first_playbook)
    else:
        return None


class __TestAssociatedFiles(object):
    def __init__(self, inventory, setup_playbook, teardown_playbook):
        self.inventory = inventory
        self.setup_playbook = setup_playbook
        self.teardown_playbook = teardown_playbook
