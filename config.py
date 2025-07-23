#!/usr/bin/env python3
"""
Configuration module for FP-Growth Federated Learning System
Manages global settings and parameters
"""

import json
import os
from typing import Dict, Any

class Config:
    """Global configuration manager"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.default_config = {
            "min_utility_threshold": 100,
            "max_itemsets": 1000,
            "enable_privacy": True,
            "differential_privacy_epsilon": 1.0,
            "federated_learning": {
                "server_port": 50051,
                "client_timeout": 30,
                "max_clients": 10
            },
            "mining": {
                "max_depth": 5,
                "max_items_per_iteration": 50,
                "enable_parallel": False
            },
            "ui": {
                "dashboard_port": 8050,
                "simple_ui_port": 5000,
                "auto_refresh_interval": 5000
            }
        }
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults to ensure all keys exist
                return self._merge_configs(self.default_config, config)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
                return self.default_config.copy()
        else:
            # Create default config file
            self.save_config(self.default_config)
            return self.default_config.copy()
    
    def save_config(self, config: Dict[str, Any] = None) -> bool:
        """Save configuration to file"""
        if config is None:
            config_to_save = self.config
        else:
            config_to_save = config
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config_to_save, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def _merge_configs(self, default: Dict, user: Dict) -> Dict:
        """Merge user config with defaults"""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """Set configuration value"""
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        
        # Save to file
        return self.save_config()
    
    def get_min_utility_threshold(self) -> float:
        """Get minimum utility threshold"""
        return self.get("min_utility_threshold", 100)
    
    def set_min_utility_threshold(self, threshold: float) -> bool:
        """Set minimum utility threshold"""
        return self.set("min_utility_threshold", threshold)
    
    def reset_min_utility_threshold(self) -> bool:
        """Reset minimum utility threshold to default"""
        return self.set("min_utility_threshold", 100)

# Global configuration instance
config = Config()

# Convenience functions
def get_min_utility_threshold() -> float:
    """Get minimum utility threshold"""
    return config.get_min_utility_threshold()

def set_min_utility_threshold(threshold: float) -> bool:
    """Set minimum utility threshold"""
    return config.set_min_utility_threshold(threshold)

def reset_min_utility_threshold() -> bool:
    """Reset minimum utility threshold to default"""
    return config.reset_min_utility_threshold() 