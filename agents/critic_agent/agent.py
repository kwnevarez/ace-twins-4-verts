"""Critic agent for identifying and verifying statements using search tools."""

from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_response import LlmResponse
from google.adk.tools import google_search
from google.genai import types

from . import prompt


def _render_reference(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> LlmResponse:
    """Appends grounding references to the response."""
    # No-op if the callback context is not used.
    del callback_context
    # Return the original response if it's empty or has no grounding metadata.
    if (
        not llm_response.content or
        not llm_response.content.parts or
        not llm_response.grounding_metadata
    ):
        return llm_response
    references = []
    # Loop through each grounding chunk to extract reference information.
    for chunk in llm_response.grounding_metadata.grounding_chunks or []:
        title, uri, text = '', '', ''
        # Extract title, URI, and text from retrieved context or web context.
        if chunk.retrieved_context:
            title = chunk.retrieved_context.title
            uri = chunk.retrieved_context.uri
            text = chunk.retrieved_context.text
        elif chunk.web:
            title = chunk.web.title
            uri = chunk.web.uri
        # Create a list of parts to display, filtering out empty strings.
        parts = [s for s in (title, text) if s]
        # If a URI is available, format the first part as a markdown link.
        if uri and parts:
            parts[0] = f'[{parts[0]}]({uri})'
        # If there are parts to display, join them and add to the references list.
        if parts:
            references.append('* ' + ': '.join(parts) + '\n')
    # If references were found, append them to the response content.
    if references:
        reference_text = ''.join(['\n\nReference:\n\n'] + references)
        llm_response.content.parts.append(types.Part(text=reference_text))
    # Extract the text from all parts of the response.
    texts = [
        part.text for part in llm_response.content.parts if part.text is not None
    ]
    # If all parts have text, merge them into a single text part.
    if len(texts) == len(llm_response.content.parts):
        all_text = '\n'.join(texts)
        llm_response.content.parts[0].text = all_text
        del llm_response.content.parts[1:]
    return llm_response


# Create an Agent instance for the critic agent.
# This agent is responsible for identifying and verifying statements.
critic_agent = Agent(
    # Use the 'gemini-2.5-flash' model for the agent.
    model='gemini-2.5-flash',
    # Set the name of the agent to 'critic_agent'.
    name='critic_agent',
    # Use the CRITIC_PROMPT as the instruction for the agent.
    instruction=prompt.CRITIC_PROMPT,
    # Provide the google_search tool to the agent.
    tools=[google_search],
    # Set the _render_reference function as the callback to be executed after the model's response.
    after_model_callback=_render_reference,
)
