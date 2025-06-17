# Chat Agent

A conversational AI agent that uses a chat-based interface to interact with various tools and provide intelligent responses to user queries.

## Overview

This agent implements a chat-based conversational AI that can understand natural language queries and use available tools to provide accurate responses. It follows a structured thought process, taking actions when needed and providing final answers to user questions.

## Key Features

- **Natural Language Understanding**: Processes user queries in natural language
- **Tool Integration**: Can utilize multiple tools to gather information and perform actions
- **Structured Reasoning**: Follows a clear thought-action-observation pattern for transparent decision-making
- **JSON-based Actions**: Uses structured JSON format for tool invocation
- **Flexible Configuration**: Supports customization of system messages and prompts

## Inputs

- **Medium**: HTTP POST request to `/run` endpoint
- **Format**: JSON object with:
  - `input` (string, required): The user's question or query
  - `chat_history` (array, optional): Previous conversation context

## Outputs

- **Medium**: HTTP response
- **Format**: JSON object with:
  - `status`: "success" or "error"
  - `output`: The agent's response to the query (on success)
  - `message`: Error description (on error)

## API Endpoints

- `POST /run`: Execute the agent with a user query
- `GET /`: Health check endpoint
- `GET /tools`: List available tools for the agent

## How It Works

The agent processes queries through a structured approach:
1. Analyzes the user's question
2. Thinks about what actions to take
3. Executes tools if needed to gather information
4. Observes the results
5. Repeats the process if necessary
6. Provides a final answer to the user

The agent maintains context throughout the conversation and can handle complex multi-step reasoning tasks.