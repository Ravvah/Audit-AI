import os
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """API configuration settings class"""
    
    # Server settings
    HOST: str = Field("0.0.0.0", description="API host")
    PORT: int = Field(8000, description="API port")
    
    # LLM service settings
    OLLAMA_BASE_URL: str = Field(
        os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
        description="Base URL for Ollama API"
    )
    
    DEFAULT_MODEL: str = Field(
        os.environ.get("MODEL_NAME", "smollm2:360m"),
        description="Default LLM model to use"
    )
    
    # Metrics settings
    METRICS_STORAGE_PATH: str = Field(
        os.environ.get("METRICS_STORAGE_PATH", "./data/metrics"),
        description="Path to store metrics data"
    )
    
    METRICS_ENABLED: bool = Field(
        os.environ.get("METRICS_ENABLED", "true").lower() == "true",
        description="Enable metrics collection"
    )
    
    # Performance settings
    REQUEST_TIMEOUT: int = Field(60, description="Request timeout in seconds")
    MAX_TOKENS: int = Field(2048, description="Default max tokens for generation")
    
    class Config:
        """Pydantic config"""
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"
