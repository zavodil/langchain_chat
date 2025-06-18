# Chat Agent

A conversational AI agent that uses a structured approach to answer questions and perform tasks through natural language interaction. This agent follows a systematic thought-action-observation pattern to break down complex queries and provide well-reasoned responses.

## Overview

The Chat Agent is designed to engage in natural conversations while leveraging various tools to accomplish tasks. It uses a JSON-based action format to interact with tools and follows a structured reasoning process to arrive at answers.

## Key Features

- **Structured Reasoning**: Follows a clear thought-action-observation cycle for transparent decision-making
- **Tool Integration**: Can utilize multiple tools to enhance its capabilities
- **JSON Action Format**: Uses a standardized JSON format for tool interactions
- **Error Handling**: Robust parsing and error management for reliable operation
- **Conversational Memory**: Maintains context through conversation history

## Inputs

- **Medium**: HTTP POST request to `/run` endpoint
- **Format**: JSON payload with:
  - `input` (string, required): The user's question or request
  - `chat_history` (array, optional): Previous conversation context

## Outputs

- **Medium**: HTTP response
- **Format**: JSON response containing:
  - `status`: "success" or "error"
  - `output`: The agent's final answer or response
  - `message`: Error details (only on failure)

## API Endpoints

- `POST /run`: Execute the agent with a given input
- `GET /`: Health check endpoint
- `GET /tools`: List available tools for the agent

## How It Works

1. Receives a question or request
2. Analyzes what needs to be done
3. Selects and uses appropriate tools if needed
4. Observes the results
5. Continues reasoning until reaching a final answer
6. Returns the complete response

The agent maintains a clear separation between thinking, acting, and observing, making its reasoning process transparent and traceable.