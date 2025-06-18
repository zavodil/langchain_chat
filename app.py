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
            logger.warning(f"Error loading config from {config_path}: {e}")
    
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
                logger.info("Search tool initialized")
            elif tool_name == "calculator":
                from langchain.chains import LLMMathChain
                from langchain.tools import Tool
                llm_math = LLMMathChain.from_llm(llm)
                tools.append(Tool(
                    name="Calculator",
                    description="useful for mathematical calculations",
                    func=llm_math.run
                ))
                logger.info("Calculator tool initialized")
            else:
                logger.warning(f"Unknown tool: {tool_name}")
        except Exception as e:
            if tool_config.get("handle_import_errors", True):
                logger.error(f"Error initializing tool {tool_name}: {e}")
                if tool_config.get("warn_on_missing_tools", True):
                    logger.warning(f"Tool {tool_name} could not be initialized and will be skipped")
            else:
                raise
    
    return tools

def create_agent(llm: BaseLanguageModel, tools: Sequence[BaseTool], config: Dict[str, Any]) -> AgentExecutor:
    """Create the ChatAgent with proper configuration."""
    from langchain.agents.chat.base import ChatAgent
    
    # Create the agent using from_llm_and_tools
    agent = ChatAgent.from_llm_and_tools(
        llm=llm,
        tools=tools,
        system_message_prefix=SYSTEM_MESSAGE_PREFIX,
        system_message_suffix=SYSTEM_MESSAGE_SUFFIX,
        human_message=HUMAN_MESSAGE,
        format_instructions=FORMAT_INSTRUCTIONS
    )
    
    # Create AgentExecutor
    agent_config = config.get("agent_config", {})
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=agent_config.get("verbose", True),
        max_iterations=agent_config.get("max_iterations", 10),
        early_stopping_method=agent_config.get("early_stopping_method", "generate")
    )
    
    return agent_executor

def load_input(input_source: str) -> str:
    """Load input from file or return as string."""
    if os.path.isfile(input_source):
        with open(input_source, 'r') as f:
            return f.read().strip()
    return input_source

def save_output(result: Any, output_path: str, config: Dict[str, Any], error: Optional[str] = None):
    """Save the output to a JSON file."""
    output_data = {
        "timestamp": datetime.now().isoformat(),
        "success": error is None
    }
    
    if error:
        output_data["error"] = error
        if config.get("error_handling", {}).get("save_errors_to_output", True):
            output_data["error_details"] = str(error)
    else:
        output_data["result"] = result
    
    if config.get("include_metadata", True):
        output_data["metadata"] = {
            "llm_model": os.getenv('DEFAULT_MODEL_NAME', config.get('llm_model', 'claude-opus-4-20250514')),
            "temperature": config.get("temperature", 0.7),
            "max_tokens": config.get("max_tokens", 2000),
            "tools_used": config.get("default_tools", [])
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
    config_path = args.config if args.config else "input.json"
    config = load_config(config_path)
    
    # Set up logging level
    log_level = config.get("error_handling", {}).get("log_level", "INFO")
    logging.getLogger().setLevel(getattr(logging, log_level))
    
    try:
        # Initialize LLM
        llm = initialize_llm(config)
        logger.info("LLM initialized successfully")
        
        # Initialize tools
        tools = initialize_tools(config, llm)
        logger.info(f"Initialized {len(tools)} tools")
        
        # Create agent
        agent_executor = create_agent(llm, tools, config)
        logger.info("Agent created successfully")
        
        # Get input
        if args.input:
            input_text = load_input(args.input)
        else:
            input_text = config.get("default_input", "Hello, how can you help me?")
        
        logger.info(f"Processing input: {input_text[:100]}...")
        
        # Execute agent
        result = agent_executor.invoke({"input": input_text})
        
        # Extract the output
        if isinstance(result, dict) and "output" in result:
            final_result = result["output"]
        else:
            final_result = str(result)
        
        # Save output
        save_output(final_result, args.output, config)
        
        logger.info("Agent execution completed successfully")
        
    except Exception as e:
        logger.error(f"Error during execution: {e}")
        save_output(None, args.output, config, error=str(e))
        raise

if __name__ == "__main__":
    main()