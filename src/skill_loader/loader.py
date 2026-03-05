#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skill Loader - Core module for skill discovery, execution and management.

This module provides skill discovery, execution, and management functionality
following the Claude Skill specification. Supports dynamic loading, keyword
matching, and LLM semantic matching.
"""

import os
import json
import sys
import importlib
import re
import difflib
import glob
from typing import Dict, Optional, Any, List, Callable, Union


class Skill:
    """Base class for skills."""
    
    def __init__(self, skill_name: str, skill_path: str):
        """Initialize a skill.
        
        Args:
            skill_name: Name of the skill
            skill_path: Path to the skill directory
        """
        self.skill_name = skill_name
        self.skill_path = skill_path
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load skill metadata from SKILL.md file.
        
        Returns:
            Skill metadata as a dictionary
        """
        skill_md_path = os.path.join(self.skill_path, 'SKILL.md')
        metadata = {
            'name': self.skill_name,
            'path': self.skill_path,
            'content': ''
        }
        
        if os.path.exists(skill_md_path):
            try:
                with open(skill_md_path, 'r', encoding='utf-8') as f:
                    metadata['content'] = f.read()
            except Exception as e:
                print(f"[WARN] Failed to load skill metadata: {e}")
        
        return metadata
    
    def _check_and_install_dependencies(self, dependencies: List[str]) -> bool:
        """Check and install dependencies.
        
        Args:
            dependencies: List of dependencies to check and install
            
        Returns:
            True if all dependencies are installed successfully
        """
        import subprocess
        
        all_installed = True
        for dep in dependencies:
            try:
                __import__(dep)
            except ImportError:
                print(f"   Installing dependency {dep}...")
                try:
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep, '-q'])
                    print(f"   [OK] {dep} installed successfully")
                except subprocess.CalledProcessError:
                    print(f"   [ERROR] Failed to install {dep}")
                    all_installed = False
        
        return all_installed
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the skill.
        
        Args:
            input_data: Input data for the skill
            
        Returns:
            Execution result
        """
        return {
            'skill': self.skill_name,
            'status': 'error',
            'message': f'Skill {self.skill_name} is not implemented'
        }


class DynamicSkill(Skill):
    """Dynamic skill that executes based on SKILL.md configuration."""
    
    def __init__(self, skill_name: str, skill_path: str, execution_config: Dict[str, Any]):
        """Initialize a dynamic skill.
        
        Args:
            skill_name: Name of the skill
            skill_path: Path to the skill directory
            execution_config: Execution configuration from SKILL.md
        """
        super().__init__(skill_name, skill_path)
        self.execution_config = execution_config
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the dynamic skill.
        
        Args:
            input_data: Input data for the skill
            
        Returns:
            Execution result
        """
        try:
            exec_type = self.execution_config.get('type', 'script')
            
            if exec_type == 'script':
                return self._execute_script(input_data)
            elif exec_type == 'module':
                return self._execute_module(input_data)
            elif exec_type == 'command':
                return self._execute_command(input_data)
            else:
                return {
                    'skill': self.skill_name,
                    'status': 'error',
                    'message': f"Unsupported execution type: {exec_type}"
                }
        except Exception as e:
            return {
                'skill': self.skill_name,
                'status': 'error',
                'message': str(e)
            }
    
    def _execute_script(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a script-based skill."""
        import importlib.util
        
        script_path = self.execution_config.get('script_path')
        if not script_path:
            return {
                'skill': self.skill_name,
                'status': 'error',
                'message': 'script_path not specified in execution config'
            }
        
        full_script_path = os.path.join(self.skill_path, script_path)
        if not os.path.exists(full_script_path):
            return {
                'skill': self.skill_name,
                'status': 'error',
                'message': f'Script not found: {full_script_path}'
            }
        
        dependencies = self.execution_config.get('dependencies', [])
        if dependencies and not self._check_and_install_dependencies(dependencies):
            return {
                'skill': self.skill_name,
                'status': 'error',
                'message': 'Failed to install dependencies'
            }
        
        scripts_dir = os.path.dirname(full_script_path)
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        
        try:
            spec = importlib.util.spec_from_file_location(
                f"{self.skill_name}_module", 
                full_script_path
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                main_class_name = self.execution_config.get('main_class')
                if not main_class_name:
                    main_class_name = self._auto_detect_main_class(module)
                
                if main_class_name and hasattr(module, main_class_name):
                    processor_class = getattr(module, main_class_name)
                    processor = processor_class()
                    
                    action = input_data.get('action', 'process')
                    if hasattr(processor, action):
                        method = getattr(processor, action)
                        result = method(input_data)
                    elif hasattr(processor, 'process'):
                        result = processor.process(input_data)
                    elif hasattr(processor, 'execute'):
                        result = processor.execute(input_data)
                    else:
                        return {
                            'skill': self.skill_name,
                            'status': 'error',
                            'message': f'No suitable method found in {main_class_name}'
                        }
                    
                    return {
                        'skill': self.skill_name,
                        'status': 'success' if result.get('success', False) else 'error',
                        'output': result
                    }
                else:
                    if hasattr(module, 'main'):
                        result = module.main(input_data)
                        return {
                            'skill': self.skill_name,
                            'status': 'success' if result.get('success', False) else 'error',
                            'output': result
                        }
                    else:
                        return {
                            'skill': self.skill_name,
                            'status': 'error',
                            'message': 'No main class or main function found in script'
                        }
            else:
                return {
                    'skill': self.skill_name,
                    'status': 'error',
                    'message': f'Failed to load script: {full_script_path}'
                }
        finally:
            if scripts_dir in sys.path:
                sys.path.remove(scripts_dir)
    
    def _execute_module(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a module-based skill."""
        return self._execute_script(input_data)
    
    def _execute_command(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a command-based skill."""
        import subprocess
        
        command = self.execution_config.get('command')
        if not command:
            return {
                'skill': self.skill_name,
                'status': 'error',
                'message': 'command not specified in execution config'
            }
        
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate(input=json.dumps(input_data))
            
            if process.returncode == 0:
                try:
                    result = json.loads(stdout)
                    return {
                        'skill': self.skill_name,
                        'status': 'success',
                        'output': result
                    }
                except json.JSONDecodeError:
                    return {
                        'skill': self.skill_name,
                        'status': 'success',
                        'output': {'text': stdout}
                    }
            else:
                return {
                    'skill': self.skill_name,
                    'status': 'error',
                    'message': stderr or f'Command failed with return code: {process.returncode}'
                }
        except Exception as e:
            return {
                'skill': self.skill_name,
                'status': 'error',
                'message': str(e)
            }
    
    def _auto_detect_main_class(self, module) -> Optional[str]:
        """Auto-detect the main class in a module.
        
        Args:
            module: Loaded Python module
            
        Returns:
            Main class name or None
        """
        import inspect
        
        classes = [name for name, obj in inspect.getmembers(module, inspect.isclass) 
                   if obj.__module__ == module.__name__]
        
        if not classes:
            return None
        
        priority_patterns = [
            self.skill_name.replace('-', '').replace('_', '').title(),
            self.skill_name.replace('-', ' ').replace('_', ' ').title().replace(' ', ''),
            'Main', 'Processor', 'Handler', 'Skill',
        ]
        
        for pattern in priority_patterns:
            for class_name in classes:
                if class_name.lower() == pattern.lower():
                    return class_name
        
        for class_name in classes:
            if class_name not in ['object', 'BaseModel', 'BaseSkill']:
                return class_name
        
        return None


class SkillLoader:
    """Skill loader that manages skill discovery, loading and execution.
    
    Supports dynamic loading, keyword matching, and LLM semantic matching.
    Supports project-level and global skill directories with project-level priority
    and duplicate name deduplication.
    """
    
    def __init__(self, skills_dir: Optional[Union[str, List[str]]] = None, verbose: bool = False):
        """Initialize the skill loader.
        
        Args:
            skills_dir: Skill directory path or list of paths. Project-level directories
                       take priority over global directories. If None, uses default
                       global skill directory.
            verbose: Whether to enable verbose logging
        """
        self.verbose = verbose
        
        if skills_dir is None:
            self.skills_dirs = [os.path.join(os.path.dirname(__file__), 'skills')]
        elif isinstance(skills_dir, str):
            self.skills_dirs = [skills_dir]
        else:
            self.skills_dirs = skills_dir
        
        self.skills = self._load_skills()
    
    def _load_skills(self) -> Dict[str, Skill]:
        """Load all available skills.
        
        Skills are loaded in directory order, with later directories (project-level)
        overriding earlier directories (global) for skills with the same name.
        
        Returns:
            Dictionary mapping skill names to Skill instances
        """
        skills = {}
        
        for skills_dir in self.skills_dirs:
            if not os.path.exists(skills_dir):
                if self.verbose:
                    print(f"[WARN] Skill directory not found: {skills_dir}")
                continue
            
            if self.verbose:
                print(f"[INFO] Scanning skill directory: {skills_dir}")
            
            for skill_name in os.listdir(skills_dir):
                skill_path = os.path.join(skills_dir, skill_name)
                
                if os.path.isdir(skill_path):
                    if skill_name in skills:
                        if self.verbose:
                            print(f"   [Skip] Skill '{skill_name}' already exists, skipping duplicate from {skills_dir}")
                        continue
                    
                    skill = self._create_skill_instance(skill_name, skill_path)
                    if skill:
                        skills[skill_name] = skill
                        if self.verbose:
                            source_type = "project-level" if skills_dir == self.skills_dirs[-1] else "global"
                            print(f"   [OK] Loaded {source_type} skill: {skill_name}")
        
        return skills
    
    def _create_skill_instance(self, skill_name: str, skill_path: str) -> Optional[Skill]:
        """Create a skill instance.
        
        Args:
            skill_name: Name of the skill
            skill_path: Path to the skill directory
            
        Returns:
            Skill instance or None
        """
        execution_config = self._parse_skill_execution_config(skill_path)
        
        if execution_config:
            return DynamicSkill(skill_name, skill_path, execution_config)
        
        auto_config = self._auto_detect_execution_config(skill_name, skill_path)
        if auto_config:
            if self.verbose:
                print(f"   [Auto-detect] Auto-detected execution config for skill '{skill_name}'")
            return DynamicSkill(skill_name, skill_path, auto_config)
        
        return Skill(skill_name, skill_path)
    
    def _auto_detect_execution_config(self, skill_name: str, skill_path: str) -> Optional[Dict[str, Any]]:
        """Auto-detect execution configuration.
        
        Args:
            skill_name: Name of the skill
            skill_path: Path to the skill directory
            
        Returns:
            Execution configuration dictionary or None
        """
        scripts_dir = os.path.join(skill_path, 'scripts')
        if not os.path.exists(scripts_dir):
            return None
        
        common_patterns = [
            'main.py', 'index.py', 'run.py',
            f'{skill_name}.py',
            f'{skill_name.replace("-", "_")}.py',
        ]
        
        for pattern in common_patterns:
            script_path = os.path.join('scripts', pattern)
            full_path = os.path.join(skill_path, script_path)
            if os.path.exists(full_path):
                return {
                    'type': 'script',
                    'script_path': script_path,
                    'main_class': None,
                    'dependencies': []
                }
        
        py_files = glob.glob(os.path.join(scripts_dir, '*.py'))
        if py_files:
            first_py = py_files[0]
            script_path = os.path.join('scripts', os.path.basename(first_py))
            return {
                'type': 'script',
                'script_path': script_path,
                'main_class': None,
                'dependencies': []
            }
        
        return None
    
    def _parse_skill_execution_config(self, skill_path: str) -> Optional[Dict[str, Any]]:
        """Parse execution configuration from SKILL.md.
        
        Args:
            skill_path: Path to the skill directory
            
        Returns:
            Execution configuration dictionary or None
        """
        skill_md_path = os.path.join(skill_path, 'SKILL.md')
        if not os.path.exists(skill_md_path):
            return None
        
        try:
            with open(skill_md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            execution_match = re.search(r'##\s*Execution\s*\n(.*?)(?=\n##|\Z)', content, re.IGNORECASE | re.DOTALL)
            if not execution_match:
                return None
            
            exec_section = execution_match.group(1)
            config = {}
            
            type_match = re.search(r'\*\*type\*\*[:\s]+(\w+)', exec_section)
            if type_match:
                config['type'] = type_match.group(1).lower()
            
            script_match = re.search(r'\*\*script_path\*\*[:\s]+([^\n]+)', exec_section)
            if script_match:
                config['script_path'] = script_match.group(1).strip()
            
            class_match = re.search(r'\*\*main_class\*\*[:\s]+([^\n]+)', exec_section)
            if class_match:
                config['main_class'] = class_match.group(1).strip()
            
            deps_match = re.search(r'\*\*dependencies\*\*[:\s]+([^\n]+)', exec_section)
            if deps_match:
                deps_str = deps_match.group(1).strip()
                config['dependencies'] = [d.strip() for d in deps_str.split(',')]
            
            return config if config else None
            
        except Exception as e:
            if self.verbose:
                print(f"[WARN] Failed to parse execution config: {e}")
            return None
    
    def get_skills(self) -> List[str]:
        """Get list of available skills.
        
        Returns:
            List of skill names
        """
        return list(self.skills.keys())
    
    def get_skill(self, skill_name: str) -> Optional[Skill]:
        """Get a specific skill.
        
        Args:
            skill_name: Name of the skill
            
        Returns:
            Skill instance or None
        """
        return self.skills.get(skill_name)
    
    def execute_skill(self, skill_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a skill.
        
        Args:
            skill_name: Name of the skill
            input_data: Input data for the skill
            
        Returns:
            Execution result
        """
        skill = self.get_skill(skill_name)
        if not skill:
            return {
                'skill': skill_name,
                'status': 'error',
                'message': f'Skill {skill_name} not found'
            }
        
        try:
            return skill.execute(input_data)
        except Exception as e:
            return {
                'skill': skill_name,
                'status': 'error',
                'message': str(e)
            }
    
    def _extract_skill_description(self, skill_content: str) -> str:
        """Extract description from SKILL.md content.
        
        Args:
            skill_content: SKILL.md content
            
        Returns:
            Description text
        """
        description = ""
        
        desc_match = re.search(r'##\s*Description\s*\n(.*?)(?=\n##|\Z)', skill_content, re.IGNORECASE | re.DOTALL)
        if desc_match:
            description = desc_match.group(1).strip()
        
        if not description:
            first_para = re.search(r'^#.*?\n\n(.*?)(?=\n\n|\Z)', skill_content, re.DOTALL)
            if first_para:
                description = first_para.group(1).strip()
        
        return description
    
    def _extract_skill_keywords(self, skill_content: str) -> List[str]:
        """Extract keywords from SKILL.md content.
        
        Args:
            skill_content: SKILL.md content
            
        Returns:
            List of keywords
        """
        keywords = []
        
        keywords_match = re.search(r'##\s*Keywords\s*\n(.*?)(?=\n##|\Z)', skill_content, re.IGNORECASE | re.DOTALL)
        if keywords_match:
            keywords_text = keywords_match.group(1).strip()
            keywords = [k.strip().lower() for k in re.split(r'[,;\n]', keywords_text) if k.strip()]
        
        return keywords
    
    def _build_skill_keyword_index(self) -> Dict[str, List[str]]:
        """Build skill keyword index.
        
        Returns:
            Mapping from skill names to keyword lists
        """
        keyword_index = {}
        
        for skill_name, skill in self.skills.items():
            if skill.metadata and 'content' in skill.metadata:
                content = skill.metadata['content']
                keywords = self._extract_skill_keywords(content)
                
                keywords.append(skill_name.lower())
                
                keyword_index[skill_name] = list(set(keywords))
        
        return keyword_index
    
    def find_skill_by_natural_language(self, natural_language: str) -> Optional[Union[str, List[tuple]]]:
        """Find skill by natural language using keyword matching.
        
        Uses a layered matching strategy:
        1. Exact match (skill name in query)
        2. Keyword match (from SKILL.md Keywords section)
        3. Fuzzy match (similarity matching)
        
        Args:
            natural_language: Natural language description
            
        Returns:
            Best matching skill name, or list of (skill_name, score) tuples for candidates
        """
        skill_mappings = self._build_skill_keyword_index()
        
        query = natural_language.lower()
        
        scores = {}
        for skill_name, keywords in skill_mappings.items():
            if skill_name in self.skills:
                score = 0
                for keyword in keywords:
                    if keyword.lower() in query:
                        score += 1
                if skill_name in query:
                    score += 2
                for word in re.findall(r'\b\w+\b', query):
                    if difflib.get_close_matches(word, keywords, n=1, cutoff=0.7):
                        score += 0.5
                scores[skill_name] = score
        
        candidates = {skill: score for skill, score in scores.items() if score > 0}
        
        if not candidates:
            return None
        
        sorted_candidates = sorted(candidates.items(), key=lambda x: x[1], reverse=True)
        
        if len(sorted_candidates) == 1 and sorted_candidates[0][1] >= 3:
            return sorted_candidates[0][0]
        
        return sorted_candidates[:5]
    
    def find_skill_with_llm(self, natural_language: str, llm_predict_func: Callable, candidates: Optional[List[tuple]] = None) -> Optional[str]:
        """Find skill using LLM semantic matching.
        
        Uses the provided LLM function to understand user intent and select
        the most appropriate skill.
        
        Args:
            natural_language: Natural language description
            llm_predict_func: LLM prediction function that takes a prompt string and returns a response string
            candidates: List of candidate skills to limit LLM selection scope
            
        Returns:
            Best matching skill name or None
        """
        try:
            if candidates:
                skill_names = [skill for skill, score in candidates]
                if self.verbose:
                    print(f"   [LLM] Considering {len(skill_names)} candidate skills: {skill_names}")
            else:
                skill_names = sorted(self.skills.keys())
            
            skill_descriptions = []
            for skill_name in skill_names:
                skill = self.skills[skill_name]
                content = skill.metadata.get('content', '')
                description = self._extract_skill_description(content)
                short_desc = description[:150] if description else "No description"
                skill_descriptions.append(f"- {skill_name}: {short_desc}")
            
            prompt = f"""You are an AI assistant helping users find the right tool/skill.

Available skills:
{chr(10).join(skill_descriptions)}

User request: "{natural_language}"

Select the most appropriate skill from the available skills list based on the user request.

Rules:
1. Return only the skill name (e.g., "pdf-ocr", "excel-parser")
2. If no skill matches, return "NONE"
3. Do not guess if unsure

Your answer (skill name only):"""
            
            response = llm_predict_func(prompt).strip()
            
            response = response.strip('"\'`- ')
            
            if response and response != "NONE" and response in self.skills:
                return response
            
            return None
            
        except Exception as e:
            if self.verbose:
                print(f"   [LLM] Semantic matching failed: {e}")
            return None
    
    def execute_skill_by_natural_language(self, natural_language: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute skill by natural language description.
        
        Args:
            natural_language: Natural language description
            input_data: Input data
            
        Returns:
            Execution result
        """
        skill_name = self.find_skill_by_natural_language(natural_language)
        
        if not skill_name:
            return {
                'status': 'error',
                'message': f'No matching skill found: {natural_language}'
            }
        
        if isinstance(skill_name, list):
            skill_name = skill_name[0][0]
        
        return self.execute_skill(skill_name, input_data)


_skill_loader_instance = None


def get_skill_loader(skills_dir: Optional[Union[str, List[str]]] = None, verbose: bool = False) -> SkillLoader:
    """Get skill loader instance (factory function).
    
    Supports project-level and global skill directories with project-level priority
    and duplicate name deduplication.
    
    Args:
        skills_dir: Skill directory path or list of paths. Multiple directories can be
                   specified as [global_dir, project_dir]. Project-level skills will
                   override global skills with the same name.
        verbose: Whether to enable verbose logging
        
    Returns:
        SkillLoader instance
        
    Examples:
        # Use default global skill directory only
        loader = get_skill_loader()
        
        # Use specified project-level skill directory (global directory included automatically)
        loader = get_skill_loader('/path/to/project/skills')
        
        # Explicitly specify multiple directories (global first, project-level second)
        loader = get_skill_loader(['/global/skills', '/project/skills'])
    """
    global _skill_loader_instance
    
    if _skill_loader_instance is None:
        if skills_dir is not None and isinstance(skills_dir, str):
            global_dir = os.path.join(os.path.dirname(__file__), 'skills')
            if skills_dir != global_dir:
                skills_dir = [global_dir, skills_dir]
        
        _skill_loader_instance = SkillLoader(skills_dir, verbose=verbose)
    
    return _skill_loader_instance


SkillManager = SkillLoader
get_skill_manager = get_skill_loader
