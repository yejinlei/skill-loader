#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for skill_loader package."""

import os
import sys
import pytest

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from skill_loader import SkillLoader, Skill, DynamicSkill, get_skill_loader


class TestSkillLoader:
    """Tests for SkillLoader class."""
    
    def test_initialization(self):
        """Test SkillLoader initialization."""
        loader = SkillLoader(verbose=True)
        assert loader is not None
        assert isinstance(loader.skills, dict)
    
    def test_get_skills(self):
        """Test get_skills method."""
        loader = SkillLoader(verbose=True)
        skills = loader.get_skills()
        assert isinstance(skills, list)
    
    def test_get_skill(self):
        """Test get_skill method."""
        loader = SkillLoader(verbose=True)
        skills = loader.get_skills()
        
        if skills:
            skill = loader.get_skill(skills[0])
            assert skill is not None
            assert isinstance(skill, (Skill, DynamicSkill))
    
    def test_execute_skill_not_found(self):
        """Test execute_skill with non-existent skill."""
        loader = SkillLoader()
        result = loader.execute_skill('non-existent-skill', {})
        
        assert result['status'] == 'error'
        assert 'not found' in result['message'].lower()
    
    def test_find_skill_by_natural_language(self):
        """Test find_skill_by_natural_language method."""
        loader = SkillLoader(verbose=True)
        
        # Test with example skill
        result = loader.find_skill_by_natural_language("hello example")
        # Result can be None, a string, or a list of tuples
        assert result is None or isinstance(result, (str, list))


class TestGetSkillLoader:
    """Tests for get_skill_loader factory function."""
    
    def test_singleton(self):
        """Test that get_skill_loader returns singleton."""
        loader1 = get_skill_loader()
        loader2 = get_skill_loader()
        
        assert loader1 is loader2
    
    def test_with_skills_dir(self):
        """Test get_skill_loader with custom skills directory."""
        import skill_loader.loader as loader_module
        loader_module._skill_loader_instance = None
        
        skills_dir = os.path.join(os.path.dirname(__file__), '..', 'src', 'skill_loader', 'skills')
        loader = get_skill_loader(skills_dir, verbose=True)
        
        assert loader is not None


class TestExampleSkill:
    """Tests for the example skill."""
    
    def test_example_skill_execution(self):
        """Test executing the example skill."""
        skills_dir = os.path.join(os.path.dirname(__file__), '..', 'src', 'skill_loader', 'skills')
        loader = SkillLoader(skills_dir, verbose=True)
        
        if 'example-skill' in loader.get_skills():
            result = loader.execute_skill('example-skill', {'name': 'Test'})
            assert result['status'] == 'success'
            assert 'Hello' in result['output']['message']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
