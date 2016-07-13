from subprocess import call

def run_ansible_playbook(inventory_path, playbook_path, output_path):
    with open(output_path, mode="wa") as output_file:
        command = [ "ansible-playbook", "-i", inventory_path, playbook_path ]
        return call(command, stdout=output_file, stderr=output_file).returncode
