# Chat Agent

A conversational AI agent that uses a chat-based interface to interact with various tools and provide intelligent responses to user queries.

## Overview

This agent implements a chat-based reasoning system that can:
- Process natural language queries
- Determine which tools to use based on the question
- Execute tools with appropriate inputs
- Provide thoughtful, structured responses

The agent follows a structured thought process, considering what actions to take before executing them and observing the results to formulate comprehensive answers.

## Key Features

- **Tool Integration**: Dynamically selects and uses available tools based on the query context
- **Structured Reasoning**: Follows a Thought → Action → Observation pattern for transparent decision-making
- **JSON-based Actions**: Uses structured JSON format for precise tool invocation
- **Error Handling**: Gracefully manages parsing errors and unexpected outputs
- **Conversational Interface**: Maintains context and provides natural language responses

## Inputs

- **Medium**: HTTP POST request to `/run` endpoint
- **Format**: JSON object with:
  - `input` (string, required): The user's question or request
  - `chat_history` (array, optional): Previous conversation context

## Outputs

- **Medium**: HTTP response
- **Format**: JSON object with:
  - `status`: "success" or "error"
  - `output`: The agent's final answer (on success)
  - `message`: Error description (on error)

## Additional Endpoints

- `GET /`: Health check endpoint
- `GET /tools`: Returns the list of available tools the agent can use

## Usage

The agent processes queries by:
1. Analyzing the input question
2. Thinking about what needs to be done
3. Selecting appropriate tools
4. Executing actions and observing results
5. Formulating a final answer based on the gathered information

The agent continues this cycle until it has enough information to provide a comprehensive response to the original query.