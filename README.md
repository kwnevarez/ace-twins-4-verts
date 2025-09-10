# ace-twins-4-verts

This project is composed of two main components: an activity logger and a multi-tool agent. The ultimate goal is for the agent to use the data collected by the activity logger to answer questions about user activity.

## Components

### Activity Logger (`activity_logging`)

This is a Python script that runs on macOS to track the user's active application window and idle time.

*   **How it works**: The script uses `PyObjC` to interface with the macOS window server and records the active application and window title at regular intervals.
*   **Output**: The logger generates a new CSV file each day containing the activity data.
*   **Dependencies**: `pyobjc-core`, `pyobjc-framework-quartz`

### Multi-Tool Agent (`agents/multi_tool_agent`)

This is an agent built with the Google Agent Development Kit (ADK).

*   **Current Capabilities**: The agent can currently answer questions about the time and weather.
*   **Future Goal**: The agent will be extended to process the data from the activity logger to provide insights into user behavior and activity patterns.
*   **Dependencies**: `google-adk`

## Future Work

*   Integrate the `activity_logging` output as a data source for the `multi_tool_agent`.
*   Develop tools for the agent to parse, analyze, and answer questions about the activity log data.

## Getting Started

### Prerequisites

'''bash
source venv/bin/activate
pip install -r requirements.txt
'''

### Running Tests

To run the tests for the agent, use the following command:

```bash
PYTHONPATH=./agents adk eval agents/multi_tool_agent tests/evaluation.test.json
```

The python path makes the tools module visible. 

### Interacting with the Agent

To interact with the agent, you can use the `adk web` command:

```bash
PYTHONPATH=. adk web agents
```

This will start a web server with a user interface where you can chat with the agent.
