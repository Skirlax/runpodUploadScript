import runpod
from dotenv import load_dotenv, find_dotenv
from paramiko.sftp_client import SFTPClient
import os
# from runpod.api.ctl_commands import
load_dotenv(find_dotenv())
runpod.api_key = os.getenv("RUNPOD_API_KEY")


print(runpod.get_pods())