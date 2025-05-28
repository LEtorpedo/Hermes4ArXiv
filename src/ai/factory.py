#!/usr/bin/env python3
"""
AI Analyzer Factory Module.

This module provides a factory function to create an instance of an AI analyzer
based on the application's configuration. It centralizes the logic for
selecting and initializing the appropriate analyzer (e.g., OpenAI, Gemini, DeepSeek).
"""

import logging

# Assuming this factory.py is in src/ai/, so config is one level up.
# If the project structure implies src.config, this would be:
# from src.config import Config
# However, for a package structure, relative imports are common.
from ..config import Config 
from .base_analyzer import BaseAnalyzer
from .analyzer import DeepSeekAnalyzer
from .openai_analyzer import OpenAIAnalyzer
from .gemini_analyzer import GeminiAnalyzer

logger = logging.getLogger(__name__)

def get_analyzer(config: Config) -> BaseAnalyzer:
    """
    Factory function to get an AI analyzer instance based on configuration.

    Args:
        config: The application configuration object (Config) containing
                AI provider settings, API keys, models, etc.

    Returns:
        An instance of a class that implements the BaseAnalyzer interface.

    Raises:
        ValueError: If the selected AI provider's API key is missing
                    (this is typically handled by the analyzer's __init__).
                    Or if an unknown AI_PROVIDER is specified and not handled.
    """
    ai_provider = config.AI_PROVIDER.lower() # Ensure consistent casing

    logger.info(f"Attempting to initialize AI analyzer for provider: '{ai_provider}'")

    if ai_provider == "openai":
        if not config.OPENAI_API_KEY:
            # This check is a bit redundant if OpenAIAnalyzer's __init__ validates,
            # but can provide a clearer error source from the factory.
            logger.error("OpenAI provider selected, but OPENAI_API_KEY is not configured.")
            raise ValueError("OPENAI_API_KEY is required for OpenAI provider but not set.")
        logger.info(f"Initializing OpenAIAnalyzer with model: {config.OPENAI_MODEL}")
        return OpenAIAnalyzer(
            api_key=config.OPENAI_API_KEY,
            model=config.OPENAI_MODEL,
            timeout=config.API_TIMEOUT,
            retry_times=config.API_RETRY_TIMES,
            delay=config.API_DELAY
        )
    elif ai_provider == "gemini":
        if not config.GEMINI_API_KEY:
            logger.error("Gemini provider selected, but GEMINI_API_KEY is not configured.")
            raise ValueError("GEMINI_API_KEY is required for Gemini provider but not set.")
        logger.info(f"Initializing GeminiAnalyzer with model: {config.GEMINI_MODEL}")
        return GeminiAnalyzer(
            api_key=config.GEMINI_API_KEY,
            model=config.GEMINI_MODEL,
            timeout=config.API_TIMEOUT,
            retry_times=config.API_RETRY_TIMES,
            delay=config.API_DELAY
        )
    elif ai_provider == "deepseek":
        if not config.DEEPSEEK_API_KEY:
            logger.error("DeepSeek provider selected, but DEEPSEEK_API_KEY is not configured.")
            raise ValueError("DEEPSEEK_API_KEY is required for DeepSeek provider but not set.")
        logger.info(f"Initializing DeepSeekAnalyzer with model: {config.DEEPSEEK_MODEL}")
        return DeepSeekAnalyzer(
            api_key=config.DEEPSEEK_API_KEY,
            model=config.DEEPSEEK_MODEL,
            timeout=config.API_TIMEOUT,
            retry_times=config.API_RETRY_TIMES,
            delay=config.API_DELAY
        )
    else:
        # Default behavior or error for unknown provider
        # The config.validate() should ideally catch unknown AI_PROVIDER values first.
        # If it reaches here, it implies AI_PROVIDER might be an unexpected value
        # not covered by config.validate() or the default was intended to be DeepSeek
        # but the value was something else entirely.
        logger.warning(
            f"AI_PROVIDER '{config.AI_PROVIDER}' is not explicitly supported or is misconfigured. "
            f"The Config.validate() method should ensure AI_PROVIDER is one of the supported values. "
            f"This factory does not have a fallback for unknown providers."
        )
        # Raising an error for an unknown provider is safer than falling back to a default
        # if the config validation is expected to handle this.
        raise ValueError(f"Unsupported AI_PROVIDER: '{config.AI_PROVIDER}'. Please check configuration.")

if __name__ == '__main__':
    # This section is for illustrative purposes and basic testing.
    # It requires a valid Config object setup, which might involve .env files.
    
    # Setup basic logging for testing
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.info("Testing AI Analyzer Factory (requires .env configuration for keys)")

    # Mock Config class for standalone testing if needed, or use actual Config
    # For actual Config, ensure .env is loaded or environment variables are set.
    # Example: Create a dummy .env file with necessary keys for one provider.
    
    # try:
    #     # Create a dummy .env for testing
    #     with open(".env", "w") as f:
    #         f.write("AI_PROVIDER=openai\n")
    #         f.write("OPENAI_API_KEY=sk-yourkeyhere\n") # Replace with a real or mock key for testing
    #         f.write("OPENAI_MODEL=gpt-3.5-turbo\n")
    #         f.write("API_TIMEOUT=60\n")
    #         f.write("API_RETRY_TIMES=3\n")
    #         f.write("API_DELAY=2\n")
        
    #     test_config = Config() # Reloads .env due to load_dotenv() in Config
        
    #     # Check if validate() passes; it might fail if other settings are missing
    #     # if not test_config.validate():
    #     #     logger.error("Test configuration is invalid. Aborting factory test.")
    #     # else:
    #     #     analyzer_instance = get_analyzer(test_config)
    #     #     logger.info(f"Successfully obtained analyzer: {type(analyzer_instance).__name__}")
    #     #     analyzer_info = analyzer_instance.get_info()
    #     #     logger.info(f"Analyzer info: {analyzer_info}")

    # except ImportError:
    #     logger.error("Could not import Config. Ensure 'src' is in PYTHONPATH or adjust import paths.")
    # except ValueError as ve:
    #     logger.error(f"Configuration error during test: {ve}")
    # except Exception as e:
    #     logger.error(f"An unexpected error occurred during factory test: {e}")
    # finally:
    #     # Clean up dummy .env if created
    #     import os
    #     if os.path.exists(".env"):
    #         # os.remove(".env") # Be careful with this in a real environment
    #         pass
    
    logger.info("Factory test section complete. Note: Actual analyzer instantiation requires valid API keys.")
    pass
