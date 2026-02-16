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
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=conversation
    )
    
    # Add Claude's (assistant) response to conversation history
    assistant_response = response.content[0].text
    conversation.append({"role": "assistant", "content": assistant_response})

    return assistant_response, response.usage
    
# Multi-turn conversation
print("***Turn 1:***")
claude_response, usage = chat_with_claude("My favorite color is blue")  # Claude learns this fact!
print(claude_response)
print(f"\nInput tokens: {usage.input_tokens}\nOutput tokens: {usage.output_tokens}")

print("\n\n***Turn 2:***")
claude_response, usage = chat_with_claude("What's my favorite color?")  # Claude remembers!
print(claude_response)
print(f"\nInput tokens: {usage.input_tokens} \nOutput tokens: {usage.output_tokens}")

print("\n\n***Turn 3:***")
claude_response, usage = chat_with_claude("What did we just discuss?")  # Full context!
print(claude_response)
print(f"\nInput tokens: {usage.input_tokens}\nOutput tokens: {usage.output_tokens}")
    
