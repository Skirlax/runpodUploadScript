import argparse
import os
import time
import sys
import emoji
import paramiko
import runpod
from paramiko.sftp_client import SFTPClient
from dotenv import load_dotenv, find_dotenv

if getattr(sys, 'frozen', False):
    # The application is frozen
    application_path = sys._MEIPASS
else:
    # The application is not frozen
    # Change this bit to match where you store your data files:
    application_path = os.path.dirname(os.path.abspath(__file__))

dotenv_path = os.path.join(application_path, '.env')

load_dotenv(dotenv_path)
runpod.api_key = os.getenv("RUNPOD_API_KEY")

default_ignore = [".git", ".idea", ".vscode", ".venv", "venv", "env", "node_modules", "dist", "build", "dist", "dist",
                  ".env"]


def get_tcp_mapping(pod: dict):
    return [x for x in pod["runtime"]["ports"] if x["type"] == "tcp"][0]


def ssh_connect(pod_id: str):
    pod = runpod.get_pod(pod_id)
    tcp_mapping = get_tcp_mapping(pod)
    client = paramiko.client.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=tcp_mapping["ip"], port=tcp_mapping["publicPort"], username="root",
                   key_filename=os.getenv("RUNPOD_SSH_KEY"))
    return client


def create_pod():
    ex_mark_emoji = emoji.emojize(":double_exclamation_mark:")
    warning_emoji = emoji.emojize(":warning:")
    print(f"{ex_mark_emoji}\tWelcome to the RunPod runpod_script\t{ex_mark_emoji}")
    gpus = runpod.get_gpus()
    to_print = ""
    for index, item in enumerate(gpus):
        to_print += f"{item['displayName']}\t{index + 1}\n"
    print(to_print)
    num = int(input(f"{warning_emoji}\tPlease type the number of the GPU you are interested in: "))
    name = input(f"{warning_emoji}\tPlease choose a name for your new pod: ")
    pod = runpod.create_pod(name, "runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04",
                            gpus[num - 1]['id'], cloud_type="COMMUNITY", support_public_ip=True,
                            container_disk_in_gb=100, ports="22/tcp")
    pod_id = pod["id"]
    print("Waiting until connection details are available, please wait. (Pod is building)")
    while "runtime" not in pod.keys() or ("runtime" in pod.keys() and pod["runtime"] is None):
        pod = runpod.get_pod(pod_id)
        time.sleep(5)
    tcp_mapping = get_tcp_mapping(pod)
    print(
        f"{warning_emoji * 4}\nPod details:\nIP: {tcp_mapping['ip']}\nPUBLIC PORT: {tcp_mapping['publicPort']}\nID: {pod_id}\n{warning_emoji * 4}")


def upload_current_dir(pod_id: str, dir_path: str = None, no_files_greater_then_mb: int = 500):
    if dir_path is None:
        current_dir_abs_path = os.path.abspath(os.curdir)
    else:
        current_dir_abs_path = dir_path
    current_dir_name = current_dir_abs_path.split("/")[-1]
    client = ssh_connect(pod_id)
    sftp_client = client.open_sftp()
    host_dir = "/workspace/"
    try:
        sftp_client.remove(host_dir + current_dir_name)
    except FileNotFoundError:
        pass
    sftp_client.mkdir(host_dir + current_dir_name)
    sftp_client.chdir(host_dir + current_dir_name)
    upload_dir(current_dir_abs_path, sftp_client, no_files_greater_then_mb=no_files_greater_then_mb)


def upload_dir(dir_path: str, client: SFTPClient, no_files_greater_then_mb: int = 500):
    for item in os.listdir(dir_path):
        if item in default_ignore:
            continue
        item_path = os.path.join(dir_path, item)
        if os.path.isdir(item_path):
            client.mkdir(item)
            client.chdir(item)
            new_dir_path = os.path.join(dir_path, item)
            upload_dir(new_dir_path, client)
        else:
            if os.path.getsize(item_path) > no_files_greater_then_mb * 1000000:
                print(f"File {item} is too big, skipping")
            else:
                client.put(item_path, item)
    client.chdir("..")


def terminate_pod(pod_id: str):
    runpod.terminate_pod(pod_id)


def run_init_commands(pod_id: str, commands_path: str,debug: bool = False):
    client = ssh_connect(pod_id)
    with open(commands_path, "r") as file:
        commands = file.readlines()

    warnings = emoji.emojize(":warning:")
    print(f"{warnings}\tRunning commands from {commands_path}\t{warnings}")
    for command in commands:
        if command.startswith("!!!"):
            print(f"{warnings}\t{command[3:]}\t{warnings}")
            continue
        if command.startswith("##"):
            continue
        _, stdout, stderr = client.exec_command(command)
        stdout = stdout.read()
        stderr = stderr.read()
        if debug:
            print(stdout)
            print(stderr)


def list_user_pods():
    pods = runpod.get_pods()
    for pod in pods:
        print("-" * 20)
        print(f"Name: {pod['name']}\nID: {pod['id']}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='RunPod runpod_script')
    parser.add_argument('-cp', '--create_pod', action='store_true', help='Interactively create a pod.')
    parser.add_argument('-ucd', '--upload_current_dir', action='store_true', help='Upload current directory to pod.')
    parser.add_argument('-tp', '--terminate_pod', action='store_true', help='Terminate a pod')
    parser.add_argument('-pi', '--pod_id', type=str, help='The id of the pod')
    parser.add_argument('-ud', '--upload_dir', type=str, help='The dir to upload.')
    parser.add_argument("-ngt", '--no_files_greater_then_mb', type=int, help='The max size of files in MB')
    parser.add_argument("-rc", '--run_commands', type=str, help="Run commands from a file")
    parser.add_argument("-lp", '--list_pods', action='store_true', help="List user pods")
    parser.add_argument("-d", '--debug', action='store_true', help="Debug mode")
    args = parser.parse_args()
    if args.no_files_greater_then_mb is None:
        args.no_files_greater_then_mb = 100
    if args.create_pod:
        create_pod()
    elif args.list_pods:
        list_user_pods()
    elif args.run_commands is not None:
        run_init_commands(args.pod_id, args.run_commands,debug=args.debug)
    elif args.upload_dir is not None:
        upload_current_dir(args.pod_id, args.upload_dir, args.no_files_greater_then_mb)
    elif args.upload_current_dir:
        upload_current_dir(args.pod_id, no_files_greater_then_mb=args.no_files_greater_then_mb)
    elif args.terminate_pod:
        terminate_pod(args.pod_id)
