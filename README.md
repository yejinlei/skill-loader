# Skill Loader

A model-agnostic skill loading and execution framework following the [Claude Skill specification](https://docs.anthropic.com/en/docs/agents-and-tools/skills).

## Features

- **Model & Platform Agnostic**: Works with any LLM (OpenAI, Anthropic, local models, etc.)
- **Dynamic Loading**: Automatically discovers and loads skills from directories
- **Keyword Matching**: Fast skill selection using keyword matching
- **LLM Semantic Matching**: Optional semantic matching using any LLM
- **Project & Global Skills**: Supports both project-level and global skill directories
- **Auto-configuration**: Automatically detects skill execution configuration
- **Dependency Management**: Automatically installs skill dependencies

## Installation

```bash
pip install skill-loader
```

## Quick Start

### Basic Usage

```python
from skill_loader import get_skill_loader

# Get skill loader with default global skills
loader = get_skill_loader(verbose=True)

# List available skills
print(loader.get_skills())
# ['excel-parser', 'pdf-ocr', 'web-search']

# Execute a skill
result = loader.execute_skill('excel-parser', {
    'action': 'read',
    'file_path': 'data.xlsx'
})
```

### Natural Language Matching

```python
# Find skill by natural language (keyword matching)
skill_name = loader.find_skill_by_natural_language("parse this Excel file")
# Returns: 'excel-parser' or list of candidates

# Use LLM for semantic matching
def my_llm_predict(prompt: str) -> str:
    # Your LLM implementation here
    return "excel-parser"

skill_name = loader.find_skill_with_llm(
    "help me read this spreadsheet",
    llm_predict_func=my_llm_predict
)
```

### Project & Global Skills

```python
from skill_loader import SkillLoader

# Use only global skills
loader = SkillLoader()

# Use project-level skills (global included automatically)
loader = SkillLoader('/path/to/project/skills')

# Explicitly specify multiple directories
loader = SkillLoader([
    '/global/skills',      # Global skills (loaded first)
    '/project/skills'      # Project skills (overrides global)
])
```

## Creating a Skill

### Directory Structure

```
skills/
└── my-skill/                 # Skill directory (kebab-case)
    ├── SKILL.md              # Skill metadata (required)
    ├── scripts/              # Scripts directory
    │   ├── __init__.py
    │   └── main.py           # Main script
    └── README.md             # Documentation (optional)
```

### SKILL.md Template

```markdown
# My Skill

## Description
A brief description of what this skill does.

## Keywords
keyword1, keyword2, keyword3

## Execution

**type**: script

**script_path**: scripts/main.py

**main_class**: MySkillProcessor

**dependencies**: package1, package2

## Inputs
- param1: Description of parameter 1
- param2: Description of parameter 2

## Outputs
- result: Description of output
```

### Skill Implementation

```python
# scripts/main.py

class MySkillProcessor:
    """Skill processor class."""
    
    def process(self, input_data: dict) -> dict:
        """Process the input data.
        
        Args:
            input_data: Input data dictionary
            
        Returns:
            Result dictionary with 'success' key
        """
        try:
            # Your processing logic here
            result = do_something(input_data)
            
            return {
                'success': True,
                'data': result,
                'message': 'Processing completed'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Processing failed: {e}'
            }
```

## API Reference

### SkillLoader

```python
class SkillLoader:
    def __init__(self, skills_dir: Union[str, List[str]] = None, verbose: bool = False):
        """Initialize skill loader.
        
        Args:
            skills_dir: Skill directory path(s). Project-level takes priority.
            verbose: Enable verbose logging.
        """
    
    def get_skills(self) -> List[str]:
        """Get list of available skill names."""
    
    def get_skill(self, skill_name: str) -> Optional[Skill]:
        """Get a specific skill by name."""
    
    def execute_skill(self, skill_name: str, input_data: dict) -> dict:
        """Execute a skill with the given input data."""
    
    def find_skill_by_natural_language(self, query: str) -> Union[str, List[tuple]]:
        """Find skill using keyword matching."""
    
    def find_skill_with_llm(self, query: str, llm_predict_func: Callable, candidates: List[tuple] = None) -> Optional[str]:
        """Find skill using LLM semantic matching."""
```

### get_skill_loader

```python
def get_skill_loader(skills_dir: Union[str, List[str]] = None, verbose: bool = False) -> SkillLoader:
    """Get skill loader instance (singleton pattern)."""
```

## Why Skill Loader?

### Model Agnostic

Unlike other skill frameworks, Skill Loader doesn't tie you to any specific LLM or platform:

```python
# Works with OpenAI
import openai
def openai_predict(prompt):
    return openai.ChatCompletion.create(...)

# Works with Anthropic
import anthropic
def anthropic_predict(prompt):
    return anthropic.messages.create(...)

# Works with local models
def local_predict(prompt):
    return my_local_llm.generate(prompt)

# All work with Skill Loader
loader.find_skill_with_llm("query", openai_predict)
loader.find_skill_with_llm("query", anthropic_predict)
loader.find_skill_with_llm("query", local_predict)
```

### No External Dependencies

Skill Loader uses only Python standard library, making it:
- Easy to install and deploy
- Compatible with any environment
- Lightweight and fast

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Links

- [Documentation](https://github.com/yejinlei/skill-loader#readme)
- [GitHub Repository](https://github.com/yejinlei/skill-loader)
- [Issue Tracker](https://github.com/yejinlei/skill-loader/issues)
