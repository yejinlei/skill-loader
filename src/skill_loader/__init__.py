#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skill Loader - A model-agnostic skill loading and execution framework.

This module provides skill discovery, execution, and management functionality
following the Claude Skill specification. Supports dynamic loading, keyword
matching, and LLM semantic matching.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .loader import Skill, DynamicSkill, SkillLoader, get_skill_loader

__all__ = [
    "Skill",
    "DynamicSkill", 
    "SkillLoader",
    "get_skill_loader",
]
