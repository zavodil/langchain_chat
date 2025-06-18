# Chat Agent

A conversational AI agent that can interact with various tools to answer questions and perform tasks through a chat-based interface.

## Overview

This agent uses a ReAct (Reasoning and Acting) approach to break down complex queries into a series of thoughts, actions, and observations. It can leverage multiple tools to gather information and provide comprehensive answers to user questions.

## Key Features

- **Tool Integration**: Dynamically uses available tools to gather information and perform actions
- **Structured Reasoning**: Follows a clear thought-action-observation pattern for transparent decision-making
- **JSON-based Actions**: Uses structured JSON format for tool invocation
- **Error Handling**: Robust parsing and error recovery mechanisms

## Inputs

- **Medium**: HTTP POST request to `/run` endpoint
- **Format**: JSON object with:
  - `input` (string, required): The user's question or request
  - `chat_history` (array, optional): Previous conversation context

## Outputs

- **Medium**: HTTP response
- **Format**: JSON object with:
  - `status`: "success" or "error"
  - `output`: The agent's final answer or response
  - `message`: Error details (only when status is "error")

## API Endpoints

- `POST /run`: Execute the agent with user input
- `GET /`: Health check endpoint
- `GET /tools`: List available tools for the agent

## How It Works

1. Receives a user question
2. Thinks about what needs to be done
3. Selects and executes appropriate tools with specific inputs
4. Observes the results from tool execution
5. Repeats the thinking/action cycle as needed
6. Provides a final answer based on gathered information