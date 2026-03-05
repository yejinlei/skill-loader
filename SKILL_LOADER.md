# SKILL加载器与选择算法文档

## 概述

本文档详细介绍SKILL加载器的架构、选择算法和使用方法。该模块实现了完整的SKILL管理功能，包括动态加载、关键词匹配和LLM语义匹配，符合Claude Skill规范。

---

## 一、SKILL加载器架构

### 1.1 核心组件

```
┌─────────────────────────────────────────────────────────────┐
│                     SKILL加载器系统                          │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    Skill     │  │ DynamicSkill │  │ SkillLoader  │      │
│  │   技能基类    │  │   动态技能    │  │   加载器     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                 │                 │               │
│         └─────────────────┴─────────────────┘               │
│                           │                                 │
│                    ┌──────┴──────┐                         │
│                    │  SKILL注册表  │                         │
│                    │  (内存存储)   │                         │
│                    └─────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 类设计

#### Skill - 技能基类

```python
class Skill:
    """技能基类"""
    
    def __init__(self, skill_name: str, skill_path: str):
        self.skill_name = skill_name      # 技能名称
        self.skill_path = skill_path      # 技能目录路径
        self.metadata = self._load_metadata()  # 从SKILL.md加载元数据
    
    def _load_metadata(self) -> Dict[str, Any]:
        """加载技能元数据"""
        # 从SKILL.md文件读取元数据
        pass
    
    def _check_and_install_dependencies(self, dependencies: List[str]) -> bool:
        """检查并安装依赖"""
        # 自动安装缺失的依赖包
        pass
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行技能，子类需要重写此方法"""
        return {
            'skill': self.skill_name,
            'status': 'error',
            'message': f'Skill {self.skill_name} is not implemented'
        }
```

#### DynamicSkill - 动态技能类

```python
class DynamicSkill(Skill):
    """动态技能 - 基于SKILL.md配置执行"""
    
    def __init__(self, skill_name: str, skill_path: str, execution_config: Dict[str, Any]):
        super().__init__(skill_name, skill_path)
        self.execution_config = execution_config  # SKILL.md中的执行配置
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """根据配置动态执行脚本/模块/命令"""
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
    
    def _execute_script(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行脚本类型的技能"""
        # 动态加载脚本并执行
        pass
    
    def _execute_command(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行命令类型的技能"""
        # 执行外部命令
        pass
    
    def _auto_detect_main_class(self, module) -> Optional[str]:
        """自动检测脚本中的主类"""
        # 智能检测主类
        pass
```

#### SkillLoader - 技能加载器类

```python
class SkillLoader:
    """技能加载器"""
    
    def __init__(self, skills_dir: Optional[Union[str, List[str]]] = None, verbose: bool = False):
        self.verbose = verbose
        self.skills_dirs = self._normalize_skills_dir(skills_dir)
        self.skills = self._load_skills()  # 加载所有技能
    
    def get_skills(self) -> List[str]:
        """获取可用技能列表"""
        return list(self.skills.keys())
    
    def get_skill(self, skill_name: str) -> Optional[Skill]:
        """获取指定技能"""
        return self.skills.get(skill_name)
    
    def execute_skill(self, skill_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行指定技能"""
        skill = self.get_skill(skill_name)
        if skill:
            return skill.execute(input_data)
        return {
            'skill': skill_name,
            'status': 'error',
            'message': f'Skill {skill_name} not found'
        }
    
    def find_skill_by_natural_language(self, natural_language: str) -> Optional[Union[str, List[tuple]]]:
        """通过自然语言查找技能"""
        # 关键词匹配算法
        pass
    
    def find_skill_with_llm(self, natural_language: str, llm_predict_func: Callable, candidates: Optional[List[tuple]] = None) -> Optional[str]:
        """使用LLM语义匹配查找技能"""
        # LLM语义理解
        pass
    
    def execute_skill_by_natural_language(self, natural_language: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """通过自然语言执行技能"""
        # 自动匹配并执行技能
        pass
```

---

## 二、SKILL选择算法

### 2.1 分层匹配策略

SKILL选择采用三层匹配策略，兼顾速度和准确性：

```
┌─────────────────────────────────────────────────────────────┐
│                    SKILL选择流程                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  用户输入: "帮我解析这个Excel文件"                            │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────────┐                                        │
│  │ 第一层: 关键词匹配 │ ◄── 快速筛选，计算相关性分数           │
│  │                 │                                        │
│  │ 分数 >= 3       │ ──► 直接返回最佳匹配                    │
│  │ 单个强候选       │                                        │
│  └─────────────────┘                                        │
│         │                                                   │
│         │ 多个候选或弱候选                                    │
│         ▼                                                   │
│  ┌─────────────────┐                                        │
│  │ 第二层: LLM语义匹配│ ◄── 使用大模型理解意图                │
│  │                 │                                        │
│  │ 从候选中选择     │ ──► 返回LLM选择的技能                   │
│  └─────────────────┘                                        │
│         │                                                   │
│         │ LLM失败                                           │
│         ▼                                                   │
│  ┌─────────────────┐                                        │
│  │ 第三层: 回退机制  │ ◄── 返回关键词分数最高的候选            │
│  └─────────────────┘                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 关键词匹配算法

#### 2.2.1 关键词索引构建

从每个技能的SKILL.md动态提取关键词：

1. **提取Keywords部分**
   ```python
   ## Keywords
   excel, spreadsheet, xlsx, 表格, 数据
   ```

2. **添加技能名称**
   - 将技能名称本身也作为关键词
   - 支持大小写不敏感匹配

#### 2.2.2 相关性评分

```python
def find_skill_by_natural_language(self, natural_language: str) -> Optional[Union[str, List[tuple]]]:
    skill_mappings = self._build_skill_keyword_index()
    query = natural_language.lower()
    scores = {}
    
    for skill_name, keywords in skill_mappings.items():
        score = 0
        # 关键词匹配 +1分
        for keyword in keywords:
            if keyword.lower() in query:
                score += 1
        # 精确匹配（技能名称在查询中）+2分
        if skill_name in query:
            score += 2
        # 模糊匹配（相似度>0.7）+0.5分
        for word in re.findall(r'\b\w+\b', query):
            if difflib.get_close_matches(word, keywords, n=1, cutoff=0.7):
                score += 0.5
        scores[skill_name] = score
    
    # 处理结果
    candidates = {skill: score for skill, score in scores.items() if score > 0}
    if not candidates:
        return None
    
    sorted_candidates = sorted(candidates.items(), key=lambda x: x[1], reverse=True)
    
    if len(sorted_candidates) == 1 and sorted_candidates[0][1] >= 3:
        return sorted_candidates[0][0]
    
    return sorted_candidates[:5]
```

#### 2.2.3 决策逻辑

- **强匹配**：单个候选且分数≥3，直接返回
- **弱匹配**：多个候选或分数<3，返回候选列表
- **无匹配**：返回None

### 2.3 LLM语义匹配

当关键词匹配无法确定最佳技能时，使用LLM进行语义理解。

#### 2.3.1 Prompt设计

```
You are an AI assistant helping users find the right tool/skill.

Available skills:
- excel-parser: 解析和写入Excel文件，支持.xlsx格式
- pdf-ocr: 从PDF和图片中提取文字，使用OCR技术
- web-search: 搜索网络信息，查询企业公开信息

User request: "帮我解析这个Excel文件"

Select the most appropriate skill from the available skills list based on the user request.

Rules:
1. Return only the skill name (e.g., "pdf-ocr", "excel-parser")
2. If no skill matches, return "NONE"
3. Do not guess if unsure

Your answer (skill name only):
```

#### 2.3.2 响应处理

```python
def find_skill_with_llm(self, natural_language: str, llm_predict_func: Callable, candidates: Optional[List[tuple]] = None) -> Optional[str]:
    # 构建技能描述列表
    skill_descriptions = []
    for skill_name in skill_names:
        skill = self.skills[skill_name]
        content = skill.metadata.get('content', '')
        description = self._extract_skill_description(content)
        short_desc = description[:150] if description else "No description"
        skill_descriptions.append(f"- {skill_name}: {short_desc}")
    
    # 构建Prompt
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
    
    # 调用LLM
    response = llm_predict_func(prompt).strip()
    response = response.strip('"\'`- ')
    
    # 验证响应
    if response and response != "NONE" and response in self.skills:
        return response
    return None
```

---

## 三、SKILL动态加载

### 3.1 加载流程

```
┌─────────────────────────────────────────────────────────────┐
│                    SKILL加载流程                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  扫描技能目录列表                                            │
│         │                                                   │
│         ▼                                                   │
│  对每个子目录（技能名称）                                     │
│         │                                                   │
│         ├──► 读取 SKILL.md                                  │
│         │         │                                         │
│         │         ├──► 解析 Execution 配置                   │
│         │         │           │                             │
│         │         │           ├──► 有配置 ──► DynamicSkill   │
│         │         │           │                             │
│         │         │           └──► 无配置 ──► 自动检测       │
│         │         │                       │                 │
│         │         │                       ├──► 找到脚本      │
│         │         │                       │       │         │
│         │         │                       │       ▼         │
│         │         │                       │   DynamicSkill   │
│         │         │                       │                 │
│         │         │                       └──► 未找到        │
│         │         │                               │         │
│         │         │                               ▼         │
│         │         │                           Skill(基础)    │
│         │         │                                         │
│         │         └──► 无SKILL.md ──► Skill(基础)            │
│         │                                                   │
│         ▼                                                   │
│  注册到 skills 字典（项目级覆盖全局）                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 SKILL.md配置

#### 3.2.1 基本结构

```markdown
# Excel Parser Skill

## Description
解析和写入Excel文件，支持.xlsx格式。

## Keywords
excel, spreadsheet, xlsx, 表格, 数据, 解析, 读取, 写入

## Execution

**type**: script

**script_path**: scripts/excel_parser.py

**main_class**: ExcelParser

**dependencies**: openpyxl, pandas

## Inputs
- action: 操作类型 (read/write/update)
- file_path: 文件路径
- data: 数据内容

## Outputs
- success: 是否成功
- data: 返回数据
- message: 提示信息
```

#### 3.2.2 Execution配置项

| 配置项 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| type | string | 执行类型 | script / module / command |
| script_path | string | 脚本路径（相对技能目录） | scripts/main.py |
| main_class | string | 主类名称（可选） | ExcelParser |
| dependencies | list | 依赖包列表 | openpyxl, pandas |
| command | string | 命令（type=command时使用） | python script.py |

### 3.3 自动检测机制

当SKILL.md中没有Execution配置时，自动检测脚本：

```python
def _auto_detect_execution_config(self, skill_name: str, skill_path: str) -> Optional[Dict[str, Any]]:
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
    
    # 查找任意Python文件
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
```

---

## 四、使用方法

### 4.1 基础使用

```python
from skill_loader import get_skill_loader

# 获取技能加载器（自动包含全局和项目级技能目录）
skill_loader = get_skill_loader(skills_dir='./project-skills', verbose=True)

# 查看可用技能
print(skill_loader.get_skills())
# ['excel-parser', 'pdf-ocr', 'web-search']

# 执行技能
result = skill_loader.execute_skill('excel-parser', {
    'action': 'read',
    'file_path': 'data.xlsx'
})
```

### 4.2 项目级与全局技能目录

技能加载器支持项目级和全局技能目录，项目级优先，同名自动去重：

```python
from skill_loader import SkillLoader, get_skill_loader

# 方式1: 只使用默认全局技能目录
loader = SkillLoader()

# 方式2: 使用指定的项目级技能目录（会自动包含全局目录）
loader = get_skill_loader('/path/to/project/skills')

# 方式3: 显式指定多个目录（全局先，项目级后）
loader = SkillLoader([
    '/global/skills',      # 全局技能目录
    '/project/skills'      # 项目级技能目录（同名会覆盖全局）
], verbose=True)
```

**优先级规则：**
1. 项目级技能优先于全局技能
2. 同名技能自动去重，保留先加载的（项目级）
3. 使用 `get_skill_loader()` 时会自动合并全局和项目目录

### 4.3 自然语言匹配

```python
# 关键词匹配
skill_name = skill_loader.find_skill_by_natural_language("解析Excel文件")
# 返回: 'excel-parser' 或 [('excel-parser', 3.5), ('pdf-ocr', 1.0)]

# LLM语义匹配（需要LLM函数）
# 假设我们有一个LLM预测函数

def llm_predict(prompt):
    # 这里应该调用实际的LLM
    return "excel-parser"

skill_name = skill_loader.find_skill_with_llm(
    "帮我读取这个表格",
    llm_predict_func=llm_predict,
    candidates=[('excel-parser', 2.0), ('pdf-ocr', 0.5)]
)
# 返回: 'excel-parser'

# 直接通过自然语言执行技能
result = skill_loader.execute_skill_by_natural_language(
    "帮我解析Excel文件",
    {'file_path': 'data.xlsx'}
)
```

### 4.4 单例模式

`get_skill_loader()` 函数实现了单例模式，确保全局只有一个技能加载器实例：

```python
# 第一次调用创建实例
loader1 = get_skill_loader('./skills')

# 第二次调用返回相同实例
loader2 = get_skill_loader('./skills')

print(loader1 is loader2)  # True
```

---

## 五、技能开发规范

### 5.1 目录结构

```
skills/
└── excel-parser/              # 技能目录（使用kebab-case命名）
    ├── SKILL.md               # 技能元数据（必需）
    ├── scripts/               # 脚本目录
    │   ├── __init__.py
    │   └── excel_parser.py    # 主脚本
    ├── tests/                 # 测试目录（可选）
    │   └── test_excel_parser.py
    └── README.md              # 说明文档（可选）
```

### 5.2 SKILL.md模板

```markdown
# {技能名称}

## Description
{技能的详细描述，包括功能、使用场景等}

## Keywords
{关键词列表，用逗号分隔，用于匹配}

## Execution

**type**: script

**script_path**: scripts/{main_script}.py

**main_class**: {MainClass}

**dependencies**: {dependency1}, {dependency2}

## Inputs
- {param1}: {描述}
- {param2}: {描述}

## Outputs
- {field1}: {描述}
- {field2}: {描述}

## Examples

### 示例1: {场景}
```python
input_data = {
    "{param1}": "{value1}",
    "{param2}": "{value2}"
}
```
```

### 5.3 脚本编写规范

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict, Any

class MySkillProcessor:
    """技能处理器类"""
    
    def __init__(self):
        """初始化"""
        pass
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理入口
        
        Args:
            input_data: 输入数据
            
        Returns:
            处理结果，必须包含'success'字段
        """
        try:
            # 处理逻辑
            result = self._do_something(input_data)
            
            return {
                'success': True,
                'data': result,
                'message': '处理成功'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'处理失败: {e}'
            }
    
    def _do_something(self, input_data: Dict[str, Any]) -> Any:
        """具体处理逻辑"""
        pass


# 可选：main函数入口
def main(input_data: Dict[str, Any]) -> Dict[str, Any]:
    processor = MySkillProcessor()
    return processor.process(input_data)
```

---

## 六、核心文件

### 6.1 文件位置

- **核心文件**: `src/skill_loader/loader.py`
- **模块初始化**: `src/skill_loader/__init__.py`
- **技能目录**: `src/skill_loader/skills/`
- **本文档**: `SKILL_LOADER.md`

### 6.2 兼容性说明

为了保持向后兼容，保留了以下别名：

```python
# 旧名称别名
SkillManager = SkillLoader
get_skill_manager = get_skill_loader
```

### 6.3 导入方式

```python
# 推荐方式
from skill_loader import SkillLoader, get_skill_loader

# 兼容旧代码
from skill_loader import SkillManager, get_skill_manager
```

---

## 七、Agent框架集成案例

Skill Loader 是模型无关的，可以与各种主流Agent框架集成使用。以下是常见框架的集成案例：

### 7.1 LangChain 集成

```python
from langchain.agents import AgentExecutor, Tool
from langchain_openai import ChatOpenAI
from skill_loader import get_skill_loader

# 初始化 skill loader
loader = get_skill_loader('./skills')

# 将技能转换为 LangChain Tool
def create_langchain_tool(skill_name: str):
    skill = loader.get_skill(skill_name)
    
    def tool_func(input_data: str):
        import json
        try:
            data = json.loads(input_data) if input_data else {}
        except:
            data = {"input": input_data}
        result = skill.execute(data)
        return result.get('output', result)
    
    return Tool(
        name=skill_name,
        description=f"执行 {skill_name} 技能",
        func=tool_func
    )

# 创建工具列表
tools = [create_langchain_tool(name) for name in loader.get_skills()]

# 创建 Agent
llm = ChatOpenAI(model="gpt-4")
agent = create_json_agent(llm, tools, prompt=...)
agent_executor = AgentExecutor(agent=agent, tools=tools)

# 执行
result = agent_executor.invoke({
    "input": "帮我解析 data.xlsx 文件"
})
```

### 7.2 AutoGen 集成

```python
from autogen import ConversableAgent, AssistantAgent
from skill_loader import get_skill_loader

# 初始化 skill loader
loader = get_skill_loader('./skills')

# 创建技能执行函数
def execute_skill(skill_name: str, input_data: dict):
    skill = loader.get_skill(skill_name)
    return skill.execute(input_data)

# 使用示例：创建带技能的AutoGen Agent
# 方法1：使用register_for_execution装饰器
skill_executor = ConversableAgent(
    name="skill_executor",
    llm_config={"model": "gpt-4"}
)

# 注册技能函数
for skill_name in loader.get_skills():
    def make_wrapper(name):
        def wrapper(**kwargs):
            return execute_skill(name, kwargs)
        return wrapper
    skill_executor.register_for_execution(skill_name)(make_wrapper(skill_name))

# 方法2：作为工具函数直接调用
result = execute_skill("excel-parser", {"file_path": "data.xlsx"})
print(result)
```

### 7.3 CrewAI 集成

```python
from crewai import Agent, Task, Crew
from skill_loader import get_skill_loader

# 初始化 skill loader
loader = get_skill_loader('./skills')

# 创建 CrewAI 工具
def create_crew_tool(skill_name: str):
    from crewai.tools import BaseTool
    from pydantic import BaseModel
    
    skill = loader.get_skill(skill_name)
    
    class SkillInput(BaseModel):
        input_data: str
    
    class SkillTool(BaseTool):
        name: str = skill_name
        description: str = f"执行 {skill_name} 技能"
        args_schema: type = SkillInput
        
        def _run(self, input_data: str):
            import json
            try:
                data = json.loads(input_data)
            except:
                data = {"input": input_data}
            result = skill.execute(data)
            return result
    
    return SkillTool()

# 创建 Agent
tools = [create_crew_tool(name) for name in loader.get_skills()]

data_agent = Agent(
    role="数据处理专家",
    goal="帮助用户处理各种数据文件",
    backstory="你擅长使用各种工具处理Excel、PDF等文件",
    tools=tools
)

# 执行任务
task = Task(
    description="解析 data.xlsx 文件并提取数据",
    agent=data_agent
)

crew = Crew(agents=[data_agent], tasks=[task])
result = crew.kickoff()
```

### 7.4 独立 Agent 系统

```python
from skill_loader import get_skill_loader

class SimpleAgent:
    """简单的Skill Agent"""
    
    def __init__(self, skills_dir: str = None):
        self.loader = get_skill_loader(skills_dir)
        self.llm_predict = None
    
    def set_llm(self, predict_func):
        """设置LLM预测函数"""
        self.llm_predict = predict_func
    
    def run(self, user_input: str):
        """运行Agent"""
        # 1. 使用关键词匹配查找技能
        skill_name = self.loader.find_skill_by_natural_language(user_input)
        
        # 2. 如果有多个候选，使用LLM确定
        if isinstance(skill_name, list) and self.llm_predict:
            skill_name = self.loader.find_skill_with_llm(
                user_input,
                self.llm_predict,
                skill_name
            )
        
        # 3. 如果仍未确定，返回错误
        if not skill_name:
            return {"status": "error", "message": "未找到合适的技能"}
        
        # 4. 执行技能
        result = self.loader.execute_skill(skill_name, {"input": user_input})
        return result

# 使用示例
agent = SimpleAgent('./skills')

# 设置LLM
def my_llm(prompt):
    import openai
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

agent.set_llm(my_llm)

# 运行
result = agent.run("帮我解析这个Excel文件")
```

### 7.5 消息队列集成（异步场景）

```python
import asyncio
from skill_loader import get_skill_loader

class AsyncSkillAgent:
    """异步Skill Agent"""
    
    def __init__(self, skills_dir: str = None):
        self.loader = get_skill_loader(skills_dir)
    
    async def execute_skill_async(self, skill_name: str, input_data: dict):
        """异步执行技能"""
        skill = self.loader.get_skill(skill_name)
        
        # 在线程池中执行同步代码
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            skill.execute,
            input_data
        )
        return result
    
    async def handle_message(self, message: dict):
        """处理消息"""
        user_input = message.get('input', '')
        skill_name = self.loader.find_skill_by_natural_language(user_input)
        
        if isinstance(skill_name, list):
            skill_name = skill_name[0][0]  # 取最高分的
        
        return await self.execute_skill_async(skill_name, message)

# 使用示例
async def main():
    agent = AsyncSkillAgent('./skills')
    
    result = await agent.handle_message({
        "input": "解析Excel",
        "file_path": "data.xlsx"
    })
    print(result)

asyncio.run(main())
```

### 7.6 FastAPI Web服务集成

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from skill_loader import get_skill_loader

app = FastAPI(title="Skill Loader API")
loader = get_skill_loader('./skills')

class SkillRequest(BaseModel):
    skill_name: str
    input_data: dict

class NLRequest(BaseModel):
    query: str
    input_data: dict
    use_llm: bool = False

@app.get("/skills")
def list_skills():
    """列出所有可用技能"""
    return {"skills": loader.get_skills()}

@app.post("/execute")
def execute_skill(request: SkillRequest):
    """直接执行指定技能"""
    result = loader.execute_skill(request.skill_name, request.input_data)
    return result

@app.post("/execute-by-query")
def execute_by_query(request: NLRequest):
    """通过自然语言执行技能"""
    # 查找技能
    skill_name = loader.find_skill_by_natural_language(request.query)
    
    if isinstance(skill_name, list):
        skill_name = skill_name[0][0]
    
    if not skill_name:
        raise HTTPException(status_code=404, detail="未找到匹配技能")
    
    # 执行
    result = loader.execute_skill(skill_name, request.input_data)
    return result

# 启动服务
# uvicorn main:app --reload
```

---

## 八、常见问题

### Q1: 如何添加新的技能？

创建技能目录并添加 `SKILL.md` 文件即可，详见第五章。

### Q2: 如何处理技能依赖？

在 `SKILL.md` 的 `dependencies` 字段中添加依赖包，框架会自动安装。

### Q3: 支持哪些执行类型？

支持 `script`（脚本）、`module`（模块）、`command`（命令）三种类型。

### Q4: 如何选择使用关键词匹配还是LLM匹配？

- **关键词匹配**：快速、无需额外API调用，适合明确意图
- **LLM匹配**：更准确、适合模糊意图，需要提供LLM函数

### Q5: 项目级和全局技能如何选择？

项目级技能会覆盖全局技能同名项，建议全局放置通用技能，项目级放置业务相关技能。

---

## 九、总结

SKILL加载器实现了以下核心功能：

1. **动态加载**: 自动发现并加载技能，支持SKILL.md配置和自动检测
2. **分层匹配**: 关键词匹配（快速）+ LLM语义匹配（准确）
3. **灵活执行**: 支持脚本、模块、命令三种执行方式
4. **依赖管理**: 自动检查和安装依赖
5. **单例模式**: 全局唯一实例，避免重复加载
6. **优先级管理**: 项目级技能优先于全局技能
7. **框架无关**: 可与LangChain、AutoGen、CrewAI等主流Agent框架集成

该模块与大模型和框架无关，可以独立使用或集成到Agent系统中。