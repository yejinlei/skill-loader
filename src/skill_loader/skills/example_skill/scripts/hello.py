#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Example skill implementation."""


class HelloProcessor:
    """Example skill processor that generates greetings."""
    
    def process(self, input_data: dict) -> dict:
        """Process the input and generate a greeting.
        
        Args:
            input_data: Input data containing optional 'name' field
            
        Returns:
            Result dictionary with greeting message
        """
        name = input_data.get('name', 'World')
        
        return {
            'success': True,
            'message': f'Hello, {name}!',
            'data': {
                'name': name,
                'greeting': f'Hello, {name}!'
            }
        }
    
    def greet(self, input_data: dict) -> dict:
        """Alternative method for greeting.
        
        Args:
            input_data: Input data containing 'name' field
            
        Returns:
            Result dictionary with greeting
        """
        return self.process(input_data)


def main(input_data: dict) -> dict:
    """Main entry point for the skill.
    
    Args:
        input_data: Input data dictionary
        
    Returns:
        Result dictionary
    """
    processor = HelloProcessor()
    return processor.process(input_data)


if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) > 1:
        input_data = json.loads(sys.argv[1])
    else:
        input_data = {}
    
    result = main(input_data)
    print(json.dumps(result, indent=2))
