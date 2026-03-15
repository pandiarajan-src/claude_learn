import anthropic
from dotenv import load_dotenv
import json

# load environment variables from .env file
load_dotenv()

# Create a client instance
client = anthropic.Anthropic()

# Define the calculator tool
tools = [
    {
        "name": "calculator",
        "description": "A simple calculator that can add, subtract, multiply, or divide two numbers",
        "input_schema": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"],
                    "description": "The mathematical operation to perform"
                },
                "num1": {
                    "type": "number",
                    "description": "The first number"
                },
                "num2": {
                    "type": "number",
                    "description": "The second number"
                }
            },
            "required": ["operation", "num1", "num2"]
        }
    }
]

# Function to perform the calculation based on the tool input
def calculator(operation, num1, num2):
    """
    Calculator function to perform basic arithmetic operations.
    :param operation: The mathematical operation to perform ("add", "subtract", "multiply", "divide")
    :param num1: The first number
    :param num2: The second number
    :return: The result of the calculation or an error message
    """
    if operation == "add":
        return num1 + num2
    elif operation == "subtract":
        return num1 - num2
    elif operation == "multiply":
        return num1 * num2
    elif operation == "divide":
        if num2 != 0:
            return num1 / num2
        else:
            return "Error: Division by zero is not allowed."
    else:
        return "Error: Invalid operation."


# Chat method to interact with Claude and use the calculator tool
def chat_with_claude_and_calculator(user_input):
    """Chat with Claude and use the calculator tool when needed."""
    # Create the message for Claude, including the tool definition
    messages = [
        {"role": "user", "content": user_input}
    ]

    # Generate response from Claude
    response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            tools=tools,  # ← Pass the tools!
            messages=messages
        )

    print("=== INITIAL RESPONSE ===")
    print(f"Stop reason: {response.stop_reason}")
    print(f"Content: {response.content}")

    # Check if Claude wants to use a tool
    if response.stop_reason == "tool_use":
        # Extract tool use request
        tool_use_block = next(block for block in response.content if block.type == "tool_use")

        print(f"\n=== CLAUDE WANTS TO USE TOOL ===")
        print(f"Tool: {tool_use_block.name}")
        print(f"Input: {tool_use_block.input}")

        # Execute the tool
        tool_result = calculator(**tool_use_block.input)

        print(f"\n=== TOOL RESULT ===")
        print(f"Result: {tool_result}")

        # Send result back to Claude
        final_response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            tools=tools,
            messages=[
                {"role": "user", "content": user_input},  # Original user input for context
                {"role": "assistant", "content": response.content},  # Claude's tool request
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use_block.id,
                            "content": str(tool_result)
                        }
                    ]
                }
            ]
        )

        print(f"\n=== FINAL ANSWER ===")
        print(final_response.content[0].text)
        return final_response.usage
    else:
        print("\nClaude did not request to use the tool.")
        return response.usage

# Example usage
if __name__ == "__main__":
    while True:
        usr_msg = input("\nEnter a calculation (e.g., 'What is 5 plus 3?') or 'exit' to quit: ")
        if usr_msg.lower() == "exit":
            print("Exiting the chat. Goodbye!")
            break
        usage = chat_with_claude_and_calculator(usr_msg)
        print(f"\nInput tokens: {usage.input_tokens}\nOutput tokens: {usage.output_tokens}")

