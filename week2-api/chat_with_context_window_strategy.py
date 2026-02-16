import anthropic
from dotenv import load_dotenv

# Load the API key from a .env file
load_dotenv()

# Create a client instance
client = anthropic.Anthropic()

# Conversation history memory
conversation = []

# Chat Method
def chat_with_claude(user_input):
    """Chat with Claude using the conversation history for context."""
    # Add user input to conversation history
    conversation.append({"role": "user", "content": user_input})
    
    # Generate response from Claude
    with client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=conversation
    ) as stream_response:
        for chunk in stream_response.text_stream:
            print(chunk, end="", flush=True)
    
    # Get the final message to access token usage
    final_message = stream_response.get_final_message()

    # Add Claude's (assistant) response to conversation history
    assistant_response = final_message.content[0].text
    conversation.append({"role": "assistant", "content": assistant_response})

    return assistant_response, final_message.usage