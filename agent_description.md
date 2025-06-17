# Chat Agent

A conversational AI agent that uses a chat-based interface to interact with various tools and provide intelligent responses to user queries.

## Overview

This agent implements a chat-based conversational AI that can:
- Process natural language queries
- Use multiple tools to gather information and perform actions
- Provide structured responses in a conversational format
- Handle multi-turn conversations with context awareness

## Key Features

- **Tool Integration**: Dynamically integrates with various tools based on configuration
- **Flexible LLM Support**: Works with OpenAI-compatible language models
- **Structured Output**: Uses JSON-based action formatting for reliable tool execution
- **Error Handling**: Gracefully handles parsing errors and provides meaningful feedback

## Inputs

- **Medium**: HTTP POST requests to `/run` endpoint
- **Format**: JSON payload with:
  - `input` (required): The user's question or request as a string
  - `chat_history` (optional): Previous conversation context as a list of message dictionaries

## Outputs

- **Medium**: HTTP JSON response
- **Format**: JSON object containing:
  - `status`: "success" or "error"
  - `output`: The agent's response text (on success)
  - `message`: Error description (on error)

## API Endpoints

- `POST /run`: Execute the agent with user input
- `GET /`: Health check endpoint
- `GET /tools`: List available tools configured for the agent

## Configuration

The agent requires:
- OpenAI API credentials (via environment variables)
- Tool configuration file (`tools.json`)
- Input configuration file (`input.json`)

The agent uses a thought-action-observation loop to process requests, allowing it to reason about the query, select appropriate tools, and formulate comprehensive responses.