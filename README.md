# Computer use from a Mendix App using Large Language Models


## Introduction
This repository is meant to support the GenAI pattern of the computer use in a Mendix app. An example setup was described in the [blog post](https://www.mendix.com/blog/control-a-virtual-computer-from-your-mendix-app-using-gen-ai/) about Computer Use in a Mendix App.
The steps in this README describe how to recreate the setup.

The setup displayed in the blog post consists of the following parts:

- A Mendix app with the newest versions of these modules: GenAI Commons, Amazon Bedrock Connector, Conversational UI. We use the [GenAI Showcase App](https://marketplace.mendix.com/link/component/220475) from the Mendix Marketplace for our setup.
- A page and microflow logic to invoke the computer use LLM and execute tools. In the GenAI Showcase app, look for ComputerUse_AmazonBedrock to see the microflows used in the blog post example.
- A Docker image for a VM (virtual machine) container including a virtual desktop. We used the [Anthropic Quickstarts repository](https://github.com/anthropics/anthropic-quickstarts) as a basis.
- A http server that runs inside of the Docker container so that the Mendix app can call it. To get the example from the blog post, we added the python scripts from this current repository to the Docker image.

Keep in mind: computer use is still in beta for most major LLM providers, including [OpenAI](https://platform.openai.com/docs/guides/tools-computer-use) and [Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/computer-use.html), so things are changing fast. 


# First time setup

## Get the required code bases

1. Clone the current repository in a folder on your file system.
1. Clone the [Anthropic Quickstarts repository](https://github.com/anthropics/anthropic-quickstarts) into a dedicated folder on your file system, e.g. `C:\my-computer-use\`. A folder `anthropic-quickstarts` will be created, and it will contain a `computer-use demo`, that is located in a location such as: `C:\my-computer-use\anthropic-quickstarts\computer-use-demo\`
1. Take the most recent version of the [GenAI Showcase app](https://marketplace.mendix.com/link/component/220475) and make sure the `ComputerUse_AmazonBedrock` showcase module is present. Change the [runtime and admin ports](https://docs.mendix.com/refguide/configuration/) to 8082/8092. See notes under **Technical considerations** for more information about the different ports.


## Configure the LLM

1. Make sure to have a deployment for Anthropic Claude Sonnet 3.7 in Amazon Bedrock. Make note of the model ID, e.g. `us.anthropic.claude-3-7-sonnet-20250219-v1:0`, you need it later.
1. Run the GenAI Showcase app, and [configure the connection to Amazon Bedrock](https://docs.mendix.com/appstore/modules/aws/amazon-bedrock/#configuration). Synchronize the models as necessary.
    If your model is using a [CRI profile](https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html), you may need to add the model manually to the list of models in the Mendix App. Use the model ID from the earlier step.
1. Set the *model name* field to `Anthropic Claude 3.7 Sonnet`.
1. Optionally, verify in a chat completions showcase that the model works for simple text generation calls. 


## Modify the computer use image

1. Take `my_server.py` from this repository and add it to your local copy of the Anthropic claude code base folder, so that it is located at `C:\my-computer-use\anthropic-quickstarts\computer-use-demo\computer_use_demo\my_server.py`
1. In the `computer-use-demo\image\` folder, modify the `entrypoint.sh` file to also start my_server by adding the following line above the streamlit startup command: `python computer_use_demo/my_server.py > /tmp/my_server_logs.txt 2>&1 &`


## Build and run the computer use image as Docker Container

1. Make sure [Docker desktop](https://docs.docker.com/get-started/introduction/get-docker-desktop/) is installed on your machine and check that it is running.
1. Using the command line tool, navigate to the right directory `C:\my-computer-use\anthropic-quickstarts\computer-use-demo\`
1. Build the image using the following command:\
`docker build -t claude-computer-use-demo .` Make sure to copy the whole command, including the dot at the end.
1. Run a container using the following command:\
`docker run -p 5900:5900 -p 8501:8501 -p 6080:6080 -p 8080:8080 -p 8081:8081 -it claude-computer-use-demo`
You can ignore the instructions in the terminal to open http://localhost:8082 in your browser to begin, because we will see the VM inside the running GenAI Showcase app.



## Try it out!

1. Make sure the Docker container is up and running.
1. In the running GenAI Showcase app, navigate to the Computer Use showcase.
1. In the chat box, enter an instruction, e.g. *open a web browser, please*.
1. Watch the computer use agent interact with the virtual desktop.
1. Track the tool calls in the console log.



# Read more
- [Mendix Blog post about Computer Use](https://www.mendix.com/blog/control-a-virtual-computer-from-your-mendix-app-using-gen-ai/)



# Technical considerations

- The Mendix app needs to run on a different port than the servers in the Anthropic computer use demo VM. The GenAI Showcase typically runs on 8080, so either change the GenAI Showcase app, or change the 8080 of the anthropic http_server.py (in our setup this http_server is not strictly needed anyway so it can also be removed from entrypoint.sh) and update the ports list in the docker run command accordingly.
- The streamlit chat UI in the anthropic demo image is present by default at port `8501`, but not strictly needed or used for our setup. 
- The VM interface runs on port `6080` by default. This can be used to see what the model is executing: the virtual desktop can be shown in the browser via [http://127.0.0.1:6080/vnc.html?&resize=scale&autoconnect=1&view_only=1&reconnect=1&reconnect_delay=2000](http://127.0.0.1:6080/vnc.html?&resize=scale&autoconnect=1&view_only=1&reconnect=1&reconnect_delay=2000) which also takes care of reconnecting and refreshing automatically.
- If using Mac with Parallels: the Docker container (and hence http servers) typically runs on Mac and the Mendix app runs in Parallels. When port forwarding cannot be used, the constant in the ComputerUse_AmazonBedrock  module called `LocalhostIPAddress` needs to be changed in Studio Pro: replace `127.0.0.1` which is the default localhost IP address with your IP address. You can find this in your wifi settings or use the IPv4 value from whatismyip.com to get your IP address.
- The server from `my_server.py` runs on port `8081` by default. If the Docker image is so that this server runs on a different port, you can change the location in the Call REST (POST) operation in the ComputerUseTool microflow in the ComputerUse_AmazonBedrock showcase module in Studio Pro.
- The computer use version is by default set to `computer_20250124` in both the Mendix showcase (action microflow `ChatContext_ChatWithHistory_ActionMicroflow_ComputerUse`) and `my_server.py` when filtering the `tool_group`. If a different version (at the time of writing `computer_use_20241022` is an alternative) is required, it needs to be changed on both sides.

# Troubleshooting

- Executing the `docker run` command runs into an error similar to the following: `exec ./entrypoint.sh: no such file or directory` or `./entrypoint.sh: ./start_all.sh: /bin/bash^M: bad interpreter: No such file or directory`.
    - This is most likely due to using Windows apps for editing files and running causing specific behavior in line feed encodings.
    - As a solution: change the "End of Line Sequence" to **LF** using the setting at the bottom bar in VS Code, typically it says **CRLF** by default. This needs to be changed to **LF** for at least the following files:
      - Dockerfile
      - image/entrypoint.sh
      - image/mutter_startup.sh
      - image/novnc_startup.sh
      - image.start_all.sh
      - image/tint2_startup.sh
      - image/x11vnc_startup.sh
      - image/xvfb_startup.sh
      - image/.config/tint2/tin2rc
      - image/.config/tint2/applications/firefox-custom.desktop
      - image/.config/tint2/applications/gedit.desktop
      - image/.config/tint2/applications/terminal.desktop
    - Build the image and run the docker container again.
- The computer use agent seems unable to type properly in text fields.
    - This is most likely due to screenshot behavior in the virtual computer.
    - As a workaround for this issue, locate script `C:\my-computer-use\anthropic-quickstarts\computer-use-demo\computer_use_demo\tools\computer.py`. Edit the file: add a line `await asyncio.sleep(0.5)` after line 172 (in the "type" action, just before taking the base64 screenshot). Do not forget to build the Docker image again and run it.
- Executing the `docker build` command runs into an error similar to the following: `"docker buildx build" requires exactly 1 argument.` Make sure to copy the whole command, including the dot at the end.`docker build -t claude-computer-use-demo .`
