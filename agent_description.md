# Chat Agent

A conversational AI agent that uses a chat-based interface to interact with various tools and provide intelligent responses to user queries.

## Overview

This agent implements a chat-based conversational AI that can understand natural language queries, think through problems step-by-step, and use available tools to gather information before providing a final answer. It follows a structured thought process with explicit reasoning steps.

## Key Features

- **Structured Reasoning**: The agent follows a clear thought-action-observation pattern to solve problems systematically
- **Tool Integration**: Can utilize multiple external tools to gather information and perform actions
- **JSON-based Actions**: Uses structured JSON format to specify tool usage with precise action names and inputs
- **Conversational Interface**: Maintains context through chat-style interactions
- **Error Handling**: Robust parsing and error recovery mechanisms for handling unexpected outputs

## Inputs

- **Medium**: HTTP POST request to `/run` endpoint
- **Format**: JSON object containing:
  - `input`: User's question or request (string)
  - `chat_history`: Optional conversation history (list of message dictionaries)

## Outputs

- **Medium**: HTTP response
- **Format**: JSON object containing:
  - `status`: "success" or "error"
  - `output`: The agent's final answer or response (string)
  - `message`: Error message if status is "error"

## API Endpoints

- `POST /run`: Execute the agent with a given input
- `GET /`: Health check endpoint
- `GET /tools`: List all available tools the agent can use

## How It Works

1. The agent receives a question or task
2. It thinks about what needs to be done
3. If needed, it selects and uses appropriate tools with specific inputs
4. It observes the results from tool usage
5. This process repeats until the agent has enough information
6. Finally, it provides a comprehensive answer based on all gathered information

The agent is designed to be transparent about its reasoning process while delivering accurate and helpful responses to user queries.