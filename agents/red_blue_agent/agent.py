"""
demonstration of a multi agent system that supports conversations with each sub agent and the passing of data between them.

can be run with: 
PYTHONPATH=. adk web agents
PYTHONPATH=. adk run agents/red_blue_agent/
"""
from google.adk.agents import SequentialAgent, LlmAgent
from google.adk.tools import FunctionTool, ToolContext
from datetime import datetime

from . import prompts

def capture_selection_tool(
    object_type: str, color: str, tool_context: ToolContext
) -> dict:
    """
    Captures the user's selected object and its color, storing it in the session state.

    Args:
        object_type (str): The type of object selected by the user (e.g., "chair", "car").
        color (str): The color of the object selected (e.g., "red", "blue").
        tool_context (ToolContext): The context for the tool, allowing access to session state.

    Returns:
        dict: A confirmation message that the selection was recorded.
    """
    print(f"TOOL: User selected a {color} {object_type}.")

    tool_context.state[color] = f"{object_type}"

    return {"status": "success", "message": f"Recorded selection: {color} {object_type}."}

def get_selection_tool(
    tool_context: ToolContext
) -> dict:
    """
    Gets the user's selected object and its color from the session state.

    Args:
        tool_context (ToolContext): The context for the tool, allowing access to session state.

    Returns:
        dict: A message indicating the state of selections.
    """
    red = tool_context.state.get("red", None)
    blue = tool_context.state.get("blue", None)
    print(f"get_selection_tool: {red=}  {blue=}")

    if red is None:
        return {"status": "data incomplete", "message": f"Need a red selection"}
    if blue is None:
        return {"status": "data incomplete", "message": f"Need a blue selection"}
    else: 
        return {"status": "success", "message": f"A red {red} and a blue {blue} were selected."}

select_object_tool = FunctionTool(capture_selection_tool)
red_object_finder = LlmAgent(
    model='gemini-2.5-flash',
    name='red_object_finder',
    description='suggests red objects.',
    instruction="help the user identify a red object, when the user selects a red object state that object as your final response and pass control back to orchestrator_agent",
    tools=[FunctionTool(capture_selection_tool)
]
)

blue_object_finder = LlmAgent(
    model='gemini-2.5-flash',
    name='blue_object_finder',
    description='suggests blue objects.',
    instruction="help the user identify a blue object, when the user selects a blue object state that objec as your final response and pass control back to orchestrator_agent",
    tools=[FunctionTool(capture_selection_tool)
]
)

orchestrator_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='orchestrator_agent',
    description='At the begining of every turn use the `get_selection_tool` to get the state of red and blue and help you make decisions.'+ 
                'If red and blue are not <undefined>, Write a poem about red and blue. '+
                'if either are <undefined>. you have two sub agents to help you get them from the user that you must transfer control to as needed `red_object_finder` and `blue_object_finder`',
    sub_agents=[blue_object_finder, red_object_finder],
    tools=[FunctionTool(get_selection_tool)],
    include_contents='none'
)

root_agent = orchestrator_agent