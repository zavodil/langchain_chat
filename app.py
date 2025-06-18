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
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain.agents.agent import Agent, AgentOutputParser
from langchain.agents.chat.output_parser import ChatOutputParser
from langchain.agents.chat.prompt import FORMAT_INSTRUCTIONS, HUMAN_MESSAGE, SYSTEM_MESSAGE_PREFIX, SYSTEM_MESSAGE_SUFFIX
from langchain.chains.llm import LLMChain
from langchain.agents import AgentExecutor
from langchain.agents.chat.base import ChatAgent

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config(config_path: str = "input.json") -> Dict[str, Any]:
    """Load configuration from JSON file."""
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
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                loaded_config = json.load(f)
                default_config.update(loaded_config)
                logger.info(f"Configuration loaded from {config_path}")
        except Exception as e:
            logger.warning(f"Error loading config from {config_path}: {e}. Using defaults.")
    
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
    handle_errors = tool_config.get("handle_import_errors", True)
    warn_missing = tool_config.get("warn_on_missing_tools", True)
    
    for tool_name in config.get("default_tools", []):
        if tool_name == "search":
            try:
                from langchain_community.tools import DuckDuckGoSearchRun
                tools.append(DuckDuckGoSearchRun())
                logger.info("Search tool initialized")
            except Exception as e:
                if handle_errors:
                    logger.warning(f"Could not initialize search tool: {e}")
                else:
                    raise
        elif tool_name == "calculator":
            try:
                from langchain.chains import LLMMathChain
                from langchain.tools import Tool
                llm_math = LLMMathChain.from_llm(llm)
                tools.append(Tool(
                    name="Calculator",
                    description="useful for mathematical calculations",
                    func=llm_math.run
                ))
                logger.info("Calculator tool initialized")
            except Exception as e:
                if handle_errors:
                    logger.warning(f"Could not initialize calculator tool: {e}")
                else:
                    raise
        else:
            if warn_missing:
                logger.warning(f"Unknown tool: {tool_name}")
    
    return tools

def read_input(input_source: str) -> str:
    """Read input from either direct text or file."""
    if os.path.isfile(input_source):
        with open(input_source, 'r') as f:
            return f.read().strip()
    return input_source

def save_output(result: Any, output_path: str, config: Dict[str, Any], input_text: str, error: Optional[str] = None):
    """Save output to JSON file with metadata."""
    output_data = {
        "timestamp": datetime.now().isoformat(),
        "input": input_text,
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
            "agent_type": "chat",
            "execution_time": datetime.now().isoformat()
        }
    
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    logger.info(f"Output saved to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Run LangChain ChatAgent")
    parser.add_argument("--input", type=str, help="Input text or path to input file")
    parser.add_argument("--output", type=str, default="output.json", help="Output file path")
    parser.add_argument("--config", type=str, default="input.json", help="Configuration file path")
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Set up logging level
    log_level = config.get("error_handling", {}).get("log_level", "INFO")
    logging.getLogger().setLevel(getattr(logging, log_level))
    
    # Get input
    if args.input:
        input_text = read_input(args.input)
    else:
        input_text = config.get("default_input", "Hello, how can you help me?")
    
    logger.info(f"Processing input: {input_text[:100]}...")
    
    try:
        # Initialize LLM
        llm = initialize_llm(config)
        logger.info("LLM initialized successfully")
        
        # Initialize tools
        tools = initialize_tools(config, llm)
        logger.info(f"Initialized {len(tools)} tools")
        
        # Create agent
        agent = ChatAgent.from_llm_and_tools(
            llm=llm,
            tools=tools,
            system_message_prefix=SYSTEM_MESSAGE_PREFIX,
            system_message_suffix=SYSTEM_MESSAGE_SUFFIX,
            human_message=HUMAN_MESSAGE,
            format_instructions=FORMAT_INSTRUCTIONS,
            input_variables=["input", "agent_scratchpad"]
        )
        logger.info("ChatAgent created successfully")
        
        # Create agent executor
        agent_config = config.get("agent_config", {})
        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=tools,
            verbose=agent_config.get("verbose", True),
            max_iterations=agent_config.get("max_iterations", 10),
            early_stopping_method=agent_config.get("early_stopping_method", "generate")
        )
        
        # Execute agent
        result = agent_executor.run(input_text)
        logger.info("Agent execution completed successfully")
        
        # Save output
        save_output(result, args.output, config, input_text)
        
    except Exception as e:
        logger.error(f"Error during execution: {e}")
        if config.get("error_handling", {}).get("save_errors_to_output", True):
            save_output(None, args.output, config, input_text, str(e))
        raise

if __name__ == "__main__":
    main()