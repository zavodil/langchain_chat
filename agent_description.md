# Chat Agent

A conversational AI agent that can interact with various tools to answer questions and perform tasks through natural language dialogue.

## Overview

This agent uses a chat-based interface to process user queries, think through problems step-by-step, and leverage available tools to provide accurate answers. It follows a structured thought process: analyzing the question, determining which tools to use, executing actions, and formulating final responses.

## Key Features

- **Natural Language Processing**: Understands and responds to user queries in conversational format
- **Tool Integration**: Can utilize multiple external tools to gather information and perform actions
- **Structured Reasoning**: Follows a clear thought/action/observation pattern for transparent decision-making
- **JSON-based Tool Invocation**: Uses structured JSON format to call tools with specific parameters
- **Error Handling**: Gracefully manages parsing errors and unexpected outputs

## Inputs

- **Medium**: HTTP POST requests to `/run` endpoint
- **Format**: JSON payload with:
  - `input` (required): The user's question or request as a string
  - `chat_history` (optional): Previous conversation context as a list of message dictionaries

## Outputs

- **Medium**: HTTP JSON response
- **Format**: JSON object containing:
  - `status`: "success" or "error"
  - `output`: The agent's final answer or response (on success)
  - `message`: Error description (on failure)

## Additional Endpoints

- `GET /`: Health check endpoint
- `GET /tools`: Returns the list of available tools the agent can use

## Usage

The agent processes queries by:
1. Analyzing the input question
2. Determining which tools (if any) are needed
3. Executing tool actions with appropriate inputs
4. Observing results and reasoning about them
5. Providing a final answer based on gathered information

The agent maintains conversation context and can handle multi-step reasoning processes to arrive at comprehensive answers.