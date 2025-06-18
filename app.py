from dotenv import load_dotenv
load_dotenv()
import os
import json
import argparse
import logging
from datetime import datetime
from typing import Dict, Any, List, Sequence, Optional
from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import BaseTool
from langchain_core.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain.agents.chat.base import ChatAgent
from langchain.agents.chat.output_parser import ChatOutputParser
from langchain.agents.agent import AgentOutputParser
from langchain.chains.llm import LLMChain
from langchain.agents import AgentExecutor

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

FORMAT_INSTRUCTIONS = """The way you use the tools is by specifying a json blob.
Specifically, this json should have a `action` key (with the name of the tool to use) and a `action_input` key (with the input to the tool going here).

The only values that should be in the "action" field are: {tool_names}

The $JSON_BLOB should only contain a SINGLE action, do NOT return a list of multiple actions. Here is an example of a valid $JSON_BLOB:

{{
  "action": $TOOL_NAME,
  "action_input": $INPUT
}}

ALWAYS use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action:
$JSON_BLOB
Observation: the result of the action
... (this Thought/Action/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question"""

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from input.json or specified config file."""
    default_config = {
        "llm_model": "claude-opus-4-20250514",
        "temperature": 0.7,
        "max_tokens": 2000,
        "default_tools": ["search", "calculator"],
        "default_input": "Hello, how can you help me?",
        "agent_config": {
            "verbose": True,
            "max_iterations": 10,
            "early_stopping_method": "generate"
        },
        "output_format": "json",
        "include_metadata": True
    }
    
    # Try to load input.json first
    if os.path.exists("input.json"):
        try:
            with open("input.json", "r") as f:
                loaded_config = json.load(f)
                default_config.update(loaded_config)
                logger.info("Loaded configuration from input.json")
        except Exception as e:
            logger.warning(f"Failed to load input.json: {e}")
    
    # Override with specified config file if provided
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                override_config = json.load(f)
                default_config.update(override_config)
                logger.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            logger.warning(f"Failed to load {config_path}: {e}")
    
    return default_config

def initialize_llm(config: Dict[str, Any]) -> BaseLanguageModel:
    """Initialize the language model based on configuration."""
    model_name = os.getenv('DEFAULT_MODEL_NAME', config.get('llm_model', 'claude-opus-4-20250514'))
    temperature = config.get('temperature', 0.7)
    max_tokens = config.get('max_tokens', 2000)

    try:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )
    except Exception as e:
        logger.error(f"Error initializing LLM: {e}")
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(temperature=temperature, max_tokens=max_tokens)

def initialize_tools(config: Dict[str, Any], llm: BaseLanguageModel) -> List[BaseTool]:
    """Initialize tools based on configuration."""
    tools = []
    tool_config = config.get("tool_config", {})
    
    for tool_name in config.get("default_tools", []):
        try:
            if tool_name == "search":
                from langchain_community.tools import DuckDuckGoSearchRun
                tools.append(DuckDuckGoSearchRun())
                logger.info("Initialized search tool")
            elif tool_name == "calculator":
                from langchain.chains import LLMMathChain
                from langchain.tools import Tool
                llm_math = LLMMathChain.from_llm(llm)
                tools.append(Tool(
                    name="Calculator",
                    description="useful for mathematical calculations",
                    func=llm_math.run
                ))
                logger.info("Initialized calculator tool")
        except Exception as e:
            if tool_config.get("handle_import_errors", True):
                logger.warning(f"Failed to initialize tool '{tool_name}': {e}")
            else:
                raise
    
    return tools

def create_agent(llm: BaseLanguageModel, tools: Sequence[BaseTool], config: Dict[str, Any]) -> AgentExecutor:
    """Create the ChatAgent with proper prompt setup."""
    # Create the prompt using ChatAgent's create_prompt method
    agent = ChatAgent.from_llm_and_tools(
        llm=llm,
        tools=tools,
        system_message_prefix="Answer the following questions as best you can. You have access to the following tools:",
        system_message_suffix="Begin! Reminder to always use the exact characters `Final Answer` when responding.",
        human_message="{input}\n\n{agent_scratchpad}",
        format_instructions=FORMAT_INSTRUCTIONS
    )
    
    # Create the executor
    agent_config = config.get("agent_config", {})
    executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        verbose=agent_config.get("verbose", True),
        max_iterations=agent_config.get("max_iterations", 10),
        early_stopping_method=agent_config.get("early_stopping_method", "generate")
    )
    
    return executor

def load_input(input_source: str) -> str:
    """Load input from file or return as string."""
    if os.path.isfile(input_source):
        with open(input_source, 'r') as f:
            return f.read().strip()
    return input_source

def save_output(result: Any, output_path: str, config: Dict[str, Any], error: Optional[str] = None):
    """Save the output to a JSON file with metadata."""
    output_data = {
        "timestamp": datetime.now().isoformat(),
        "config": {
            "llm_model": config.get("llm_model"),
            "temperature": config.get("temperature"),
            "max_tokens": config.get("max_tokens"),
            "tools": config.get("default_tools")
        }
    }
    
    if error:
        output_data["error"] = error
        output_data["success"] = False
    else:
        output_data["result"] = result
        output_data["success"] = True
    
    if config.get("include_metadata", True):
        output_data["metadata"] = {
            "agent_type": "ChatAgent",
            "execution_time": datetime.now().isoformat()
        }
    
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    logger.info(f"Output saved to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Run LangChain ChatAgent")
    parser.add_argument("--input", type=str, help="Input text or path to input file")
    parser.add_argument("--output", type=str, default="output.json", help="Output file path")
    parser.add_argument("--config", type=str, help="Path to configuration file")
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Set up logging level from config
    log_level = config.get("error_handling", {}).get("log_level", "INFO")
    logging.getLogger().setLevel(getattr(logging, log_level))
    
    try:
        # Initialize LLM
        llm = initialize_llm(config)
        logger.info("Initialized LLM")
        
        # Initialize tools
        tools = initialize_tools(config, llm)
        logger.info(f"Initialized {len(tools)} tools")
        
        # Create agent
        agent_executor = create_agent(llm, tools, config)
        logger.info("Created ChatAgent")
        
        # Get input
        if args.input:
            input_text = load_input(args.input)
        else:
            input_text = config.get("default_input", "Hello, how can you help me?")
        
        logger.info(f"Processing input: {input_text[:100]}...")
        
        # Execute agent
        result = agent_executor.invoke({"input": input_text})
        
        # Extract the output
        if isinstance(result, dict):
            output = result.get("output", str(result))
        else:
            output = str(result)
        
        # Save output
        save_output(output, args.output, config)
        
    except Exception as e:
        logger.error(f"Error during execution: {e}")
        if config.get("error_handling", {}).get("save_errors_to_output", True):
            save_output(None, args.output, config, error=str(e))
        raise

if __name__ == "__main__":
    main()