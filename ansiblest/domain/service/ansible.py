from subprocess import call

def run_ansible_playbook(playbook_path, output_path, inventory_path=None):
    with open(output_path, mode="wa") as output_file:
        command = [ "ansible-playbook", playbook_path ]

        if inventory_path is not None:
            command += [ "-i", inventory_path ]

        return call(command, stdout=output_file, stderr=output_file).returncode
