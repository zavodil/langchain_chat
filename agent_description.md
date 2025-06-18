# Chat Agent

A conversational AI agent that uses a chat-based interface to interact with various tools and provide intelligent responses. This agent follows a structured thought-action-observation pattern to solve complex tasks.

## Overview

The Chat Agent is built on the LangChain framework and provides a natural language interface for executing tasks using available tools. It processes user queries through a systematic approach:

1. **Analyzes** the user's question
2. **Thinks** about what action to take
3. **Executes** the appropriate tool with specific inputs
4. **Observes** the results
5. **Iterates** as needed until reaching a final answer

## Key Features

- **Tool Integration**: Seamlessly integrates with multiple tools to extend its capabilities
- **Structured Reasoning**: Uses a clear thought process with explicit reasoning steps
- **JSON-based Actions**: Executes tools using structured JSON commands
- **Iterative Problem Solving**: Can perform multiple actions to arrive at comprehensive answers
- **Error Handling**: Gracefully manages parsing errors and unexpected outputs

## Inputs

- **Medium**: HTTP POST requests to `/run` endpoint
- **Format**: JSON payload with:
  - `input` (required): The user's question or request as a string
  - `chat_history` (optional): Previous conversation context as a list of message dictionaries

## Outputs

- **Medium**: HTTP JSON response
- **Format**: JSON object containing:
  - `status`: Either "success" or "error"
  - `output`: The agent's final answer (on success)
  - `message`: Error description (on error)

## API Endpoints

- `POST /run`: Execute the agent with a user query
- `GET /`: Health check endpoint
- `GET /tools`: List all available tools the agent can use

## Usage Example

Send a POST request to `/run` with:
json
{
  "input": "What is the weather in New York and how does it compare to London?"
}


The agent will process this request, potentially using weather tools for both cities, and return a comprehensive comparison.