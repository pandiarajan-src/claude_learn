import anthropic
from dotenv import load_dotenv

# Load the API key from a .env file
load_dotenv()

# Create a client instance
client = anthropic.Anthropic()

# Conversation history memory
conversation = []

# For Sliding Window Strategy, we will keep only the last N messages in the conversation history
MAX_HISTORY_LENGTH = 3  # Adjust this value based on your needs

# Chat Method with Sliding Window Strategy for conversation history
def chat_with_claude_sliding_window(user_input):
    """Chat with Claude using the conversation history for context."""
    # Add user input to conversation history
    conversation.append({"role": "user", "content": user_input})
    
    # Implementing the sliding window strategy to keep only the last N messages in the conversation history
    if len(conversation) > MAX_HISTORY_LENGTH:
        # if first message is system, we want to keep it, otherwise we can pop it
        if conversation[0]["role"] == "system":
            conversation[:] = conversation[0:1] + conversation[-(MAX_HISTORY_LENGTH-1):]  # Keep the system message and remove the second oldest message
        else:
            conversation[:] = conversation[-MAX_HISTORY_LENGTH:]  # Keep only the last N messages

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


# Chat method for summarizaton to keep the conversation history concise
def chat_with_claude_summarization(user_input):
    """Chat with Claude using summarization to keep the conversation history concise."""
    # Add user input to conversation history
    conversation.append({"role": "user", "content": user_input})

    if len(conversation) > MAX_HISTORY_LENGTH:
        # Ask Claude to summarize conversation so far
        summary = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": f"Summarize this conversation in 3-4 sentences:\n{conversation}"
            }]
        )
        # Replace old messages with summary
        conversation = [
            {"role": "assistant", "content": f"Previous context: {summary}"},
            *conversation[-MAX_HISTORY_LENGTH:]  # Keep recent N messages
        ]    
    
    # Generate response from Claude with summarization
    with client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=conversation,
        summary=True  # Enable summarization
    ) as stream_response:
        for chunk in stream_response.text_stream:
            print(chunk, end="", flush=True)
    
    # Get the final message to access token usage
    final_message = stream_response.get_final_message()

    # Add Claude's (assistant) response to conversation history
    assistant_response = final_message.content[0].text
    conversation.append({"role": "assistant", "content": assistant_response})

    return assistant_response, final_message.usage


# Chat methhod for Semantic Compression (Advanced) Store important facts separately, inject only relevant ones:
def chat_with_claude_semantic_compression(user_input):
    """Chat with Claude using semantic compression to keep the conversation history concise."""
    # Add user input to conversation history
    conversation.append({"role": "user", "content": user_input})

    # Extract important facts from the conversation so far
    important_facts = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": f"Extract important facts from this conversation:\n{conversation}"
        }]
    )

    # Store important facts separately (for demonstration, we just print them here)
    print(f"\nImportant Facts: {important_facts}")

    # Generate response from Claude with semantic compression
    with client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=conversation,
    ) as stream_response:
        for chunk in stream_response.text_stream:
            print(chunk, end="", flush=True)

    # Get the final message to access token usage
    final_message = stream_response.get_final_message()

    # Add Claude's (assistant) response to conversation history
    assistant_response = final_message.content[0].text
    conversation.append({"role": "assistant", "content": assistant_response})

    return assistant_response, final_message.usage


# Multi-turn conversation
if __name__ == "__main__":
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting the chat. Goodbye!")
            break

        #claude_response, usage = chat_with_claude_sliding_window(user_input)
        #claude_response, usage = chat_with_claude_summarization(user_input)
        claude_response, usage = chat_with_claude_semantic_compression(user_input)
        print(f"\nClaude: {claude_response}")
        print(f"\nInput tokens: {usage.input_tokens}\nOutput tokens: {usage.output_tokens}")
