# RunPod Utility Script
A simple script for easily creating a RunPod pod, uploading files, executing given commands and other utilities. 
# Build the project
First, create a .env file in the project directory, with the following keys: [RUNPOD_API_KEY,RUNPOD_SSH_KEY]. 
- Where RUNPOD_API_KEY is the API key for your RunPod account, found in settings. RUNPOD_SSH_KEY is the path to the private SSH key you use to connect to any runpod pod.
After that, install the requirements for this script:
```
pip install -r requirements.txt
```
Next, install pyinstaller:
```
pip install pyinstaller
```
and then run the following command in the project directory:
```
pyinstaller script.spec
```
Now you should be able to move the script from dist/script anywhere you want and execute it like any other executable.
