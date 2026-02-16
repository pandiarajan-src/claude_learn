import anthropic
from dotenv import load_dotenv

# Load the API key from a .env file
load_dotenv()

# Create a client instance
client = anthropic.Anthropic()

# Print welcome message
print("Welcome to Claude CLI Chat (type 'quit' to exit)\n")

# Conversation history memory
conversation = []

# Start a simple chat loop
while True:
    user_input = input("\nYou: ")
    if user_input.lower() in ["exit", "quit"]:
        print("Exiting the chat. Goodbye!")
        break

    # Add user input to conversation history
    conversation.append({"role": "user", "content": user_input})

    # Generate response from Claude using streaming
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

    print(f"\nInput tokens Used: {final_message.usage.input_tokens}")
    print(f"Output tokens Used: {final_message.usage.output_tokens}")
