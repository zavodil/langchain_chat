# Chat Agent

A conversational AI agent that can interact with various tools to answer questions and perform tasks through natural language dialogue.

## Overview

This agent uses a chat-based interface to process user queries and execute actions using available tools. It follows a structured thought process, deciding which tools to use and how to apply them to answer questions effectively.

## Key Features

- **Tool Integration**: Can work with multiple tools dynamically, selecting the appropriate tool based on the user's query
- **Structured Reasoning**: Follows a clear thought-action-observation pattern to solve problems step by step
- **JSON-based Actions**: Uses structured JSON format to specify tool usage with precise action names and inputs
- **Conversational Interface**: Maintains context throughout the conversation to provide coherent responses

## Inputs

- **Medium**: HTTP POST request to `/run` endpoint
- **Format**: JSON object containing:
  - `input` (string, required): The user's question or request
  - `chat_history` (array, optional): Previous conversation context

## Outputs

- **Medium**: HTTP response
- **Format**: JSON object containing:
  - `status`: "success" or "error"
  - `output`: The agent's final answer to the user's question
  - `message`: Error details (only present when status is "error")

## Additional Endpoints

- `GET /`: Health check endpoint
- `GET /tools`: Returns the list of available tools the agent can use

## Usage

The agent processes queries by:
1. Analyzing the input question
2. Thinking about what needs to be done
3. Selecting and using appropriate tools
4. Observing the results
5. Repeating steps 2-4 as needed
6. Providing a final answer based on all observations