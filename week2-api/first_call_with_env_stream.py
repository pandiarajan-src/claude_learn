from anthropic import Anthropic

# Load the API key from a .env file
from dotenv import load_dotenv
load_dotenv()

# Create a client instance
client = Anthropic()

# Make a first API call to generate a response
with client.messages.stream(
    model="claude-sonnet-4-20250514",
    max_tokens=1000,    
    messages=[
        {
            "role": "user",
            "content": "Explain API calls in one sentence using a restaurant analogy"
        }
    ]
) as stream_response:
    for chunk in stream_response.text_stream:
        print(chunk, end="", flush=True)

# Get the final message to access token usage
final_message = stream_response.get_final_message()
print(f"\nInput tokens Used: {final_message.usage.input_tokens}")
print(f"Output tokens Used: {final_message.usage.output_tokens}")
print(f"Total tokens Used: {final_message.usage.input_tokens + final_message.usage.output_tokens}")



