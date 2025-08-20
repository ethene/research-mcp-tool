"""Routing logic for mapping tasks to OpenRouter models."""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class TaskRouter:
    """Routes tasks to appropriate models based on configuration."""
    
    def __init__(self, config_path: str = "routing.yaml"):
        """Initialize router with configuration file."""
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load routing configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Routing config not found: {self.config_path}")
        
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            if not isinstance(config, dict):
                raise ValueError("Routing config must be a dictionary")
                
            return config
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in routing config: {e}")
    
    def _validate_config(self):
        """Validate routing configuration structure."""
        if 'tasks' not in self.config:
            raise ValueError("Routing config must have 'tasks' section")
        
        if 'fallbacks' not in self.config:
            raise ValueError("Routing config must have 'fallbacks' section")
        
        tasks = self.config['tasks']
        if not isinstance(tasks, dict) or not tasks:
            raise ValueError("'tasks' must be a non-empty dictionary")
        
        fallbacks = self.config['fallbacks']
        if not isinstance(fallbacks, list) or not fallbacks:
            raise ValueError("'fallbacks' must be a non-empty list")
        
        logger.info(f"Loaded routing config with {len(tasks)} tasks and {len(fallbacks)} fallbacks")
        logger.info(f"Available tasks: {', '.join(tasks.keys())}")
        logger.info(f"Fallback models: {', '.join(fallbacks)}")
    
    def get_model_for_task(self, task: str) -> Optional[str]:
        """Get the appropriate model for a given task."""
        return self.config['tasks'].get(task)
    
    def get_fallbacks(self) -> List[str]:
        """Get list of fallback models."""
        return self.config['fallbacks'].copy()
    
    def get_available_tasks(self) -> List[str]:
        """Get list of available task types."""
        return list(self.config['tasks'].keys())
    
    def validate_or_fallback(self, model_name: str, available_models: List[str]) -> str:
        """Validate model exists, or return first working fallback."""
        model_names = {m.lower() for m in available_models}
        
        # Check if requested model exists
        if model_name.lower() in model_names:
            return model_name
        
        # Try fallbacks
        for fallback in self.get_fallbacks():
            if fallback.lower() in model_names:
                logger.warning(f"Model '{model_name}' not found, using fallback '{fallback}'")
                return fallback
        
        raise ValueError(f"Neither model '{model_name}' nor any fallbacks are available")
    
    def route_task(self, task: str, available_models: List[str]) -> str:
        """Route task to appropriate model, with fallback handling."""
        # Get model for task
        model = self.get_model_for_task(task)
        if not model:
            raise ValueError(
                f"Unknown task '{task}'. Available tasks: {', '.join(self.get_available_tasks())}"
            )
        
        # Validate and potentially fallback
        return self.validate_or_fallback(model, available_models)