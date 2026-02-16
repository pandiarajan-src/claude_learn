from anthropic import Anthropic

# Load the API key from an OS environment variable
import os
api_key = os.getenv("ANTHROPIC_API_KEY")

# Create a client instance
client = Anthropic(api_key=api_key)

# Make a first API call to generate a response
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1000,
    messages=[
        {
            "role": "user",
            "content": "Explain API calls in one sentence using a restaurant analogy"
        }
    ]
)

# Print the response
print(f"\n{response.content[0].text}\n")

# print the tokens used in the response
print(f"Input tokens Used: {response.usage.input_tokens}")
print(f"Output tokens Used: {response.usage.output_tokens}")



