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
from langchain.agents import AgentExecutor

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config(config_path: str = "input.json") -> Dict[str, Any]:
    """Load configuration from JSON file."""
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Could not load config from {config_path}: {e}")
    
    # Return default configuration
    return {
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
            if tool_config.get("warn_on_missing_tools", True):
                logger.warning(f"Could not initialize tool '{tool_name}': {e}")
            if tool_config.get("handle_import_errors", True):
                continue
            else:
                raise
    
    return tools

def get_input_text(input_arg: str) -> str:
    """Get input text from argument (either direct text or file path)."""
    if os.path.isfile(input_arg):
        with open(input_arg, 'r') as f:
            return f.read().strip()
    return input_arg

def save_output(result: Any, output_path: str, config: Dict[str, Any], error: Optional[str] = None) -> None:
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
            "model": config.get("llm_model"),
            "temperature": config.get("temperature"),
            "max_tokens": config.get("max_tokens"),
            "tools_used": config.get("default_tools", [])
        }
    
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    logger.info(f"Output saved to {output_path}")

def main():
    """Main function to run the LangChain agent."""
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
    
    try:
        # Initialize LLM
        llm = initialize_llm(config)
        logger.info("LLM initialized successfully")
        
        # Initialize tools
        tools = initialize_tools(config, llm)
        logger.info(f"Initialized {len(tools)} tools")
        
        # Create the ChatAgent
        agent = ChatAgent.from_llm_and_tools(llm=llm, tools=tools)
        logger.info("ChatAgent created successfully")
        
        # Create AgentExecutor
        agent_config = config.get("agent_config", {})
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=agent_config.get("verbose", True),
            max_iterations=agent_config.get("max_iterations", 10),
            early_stopping_method=agent_config.get("early_stopping_method", "generate")
        )
        logger.info("AgentExecutor created successfully")
        
        # Get input
        if args.input:
            input_text = get_input_text(args.input)
        else:
            input_text = config.get("default_input", "Hello, how can you help me?")
        
        logger.info(f"Processing input: {input_text[:100]}...")
        
        # Execute the agent
        result = agent_executor.invoke({"input": input_text})
        
        # Extract the output
        if isinstance(result, dict) and "output" in result:
            output = result["output"]
        else:
            output = str(result)
        
        logger.info("Agent execution completed successfully")
        
        # Save output
        save_output(output, args.output, config)
        
    except Exception as e:
        logger.error(f"Error during execution: {e}")
        save_output(None, args.output, config, error=str(e))
        raise

if __name__ == "__main__":
    main()