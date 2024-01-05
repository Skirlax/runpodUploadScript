# RunPod Utility Script
A simple script for easily creating a RunPod pod, uploading files, executing given commands and other utilities. This can be very helpful when you often create different pods and have to set them up a certain way.
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

# Usage

To see all possible options run the script with the --help flag:
````
./rp_utility_script --help
````

# Examples
## Create a pod
````
./rp_utility_script -cp
````
This will launch an interactive script, that will allow you to create a pod.

## Upload files to a pod
````
./rp_utility_script -ud <dir/path/> -pi <pod_id> -ngt 100
````
This will upload all files smaller then 100 MBs in size from the given directory to the given pod.

## Run commands on the pod
````
./rp_utility_script -rc <commands/file/path/> -pi <pod_id>
````
This will read all the commands from <commands/file/path/> and execute them on the host. The should be one command per line in the specified file. Lines starting with ## will be treated as comments and ignored. Lines starting with !!! will be printed to the console. If your command contains \, please remove them and put the entire command on one line.