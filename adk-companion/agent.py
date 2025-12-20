from google.adk.agents.llm_agent import Agent
from tools import read_adk_codebase, check_upstream_release, generate_evolution_pr

SYSTEM_PROMPT = """你是 ADK 伴随智能体，具备双重身份：

1. **领域专家 (The Expert)**：通过读取自身源码和文档，为开发者提供 ADK 框架的使用指导和代码解析。
2. **进化工程师 (The Evolver)**：通过自动化工作流，实时追踪上游框架更新，自动升级依赖，并生成新特性的演示代码。

你可以使用以下工具：
- read_adk_codebase: 在 ADK 源码中搜索关键词
- check_upstream_release: 检查上游 ADK 仓库的最新发布版本
- generate_evolution_pr: 生成进化 PR
"""

root_agent = Agent(
    model='gemini-2.5-flash',
    name='adk_companion',
    description='ADK 伴随智能体 - 基于 ADK 框架的元智能体，提供专家指导与自动进化能力',
    instruction=SYSTEM_PROMPT,
    tools=[read_adk_codebase, check_upstream_release, generate_evolution_pr]
)
