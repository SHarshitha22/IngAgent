import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration management for the PR Review Orchestrator"""
    
    # GitHub Configuration
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    GITHUB_REPO = os.getenv('GITHUB_REPO')
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///review.db')
    
    # LLM Configuration
    LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'openai')  # openai, llama, mistral
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    
    # Model Settings
    MODEL_NAME = os.getenv('MODEL_NAME', 'gpt-4')
    TEMPERATURE = float(os.getenv('TEMPERATURE', '0.1'))
    
    # Agent Configuration
    MAX_POLL_ATTEMPTS = int(os.getenv('MAX_POLL_ATTEMPTS', '50'))
    POLL_INTERVAL_SECONDS = int(os.getenv('POLL_INTERVAL_SECONDS', '30'))
    
    @classmethod
    def get_llm_config(cls) -> Dict[str, Any]:
        """Get LLM configuration based on provider"""
        if cls.LLM_PROVIDER == 'openai':
            return {
                'model': cls.MODEL_NAME,
                'api_key': cls.OPENAI_API_KEY,
                'temperature': cls.TEMPERATURE
            }
        elif cls.LLM_PROVIDER == 'llama':
            return {
                'model': 'llama3-70b-8192',
                'api_key': cls.GROQ_API_KEY,
                'base_url': 'https://api.groq.com/openai/v1',
                'temperature': cls.TEMPERATURE
            }
        elif cls.LLM_PROVIDER == 'mistral':
            return {
                'model': 'mistral-large-latest',
                'api_key': cls.OPENAI_API_KEY,  # Using OpenAI-compatible endpoint
                'base_url': 'https://api.mistral.ai/v1',
                'temperature': cls.TEMPERATURE
            }
        else:
            raise ValueError(f"Unsupported LLM provider: {cls.LLM_PROVIDER}")