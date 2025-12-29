from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# ADK 官方文档 MCP 工具集：利用 mcpdoc 访问 llms.txt
docs_mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="uvx",
            args=[
                "--from",
                "mcpdoc",
                "mcpdoc",
                "--urls",
                "AgentDevelopmentKit:https://google.github.io/adk-docs/llms.txt",
                "--transport",
                "stdio"
            ]
        )
    )
)

SYSTEM_PROMPT = """你是 ADK 文档专家 (ADK Docs Expert)。
你的任务是利用 `adk-docs-mcp` 工具集查阅最新的 ADK 官方文档，为开发者提供准确的技术指导、代码示例和最佳实践。

**核心能力：**
1.  **动态查阅**：通过访问 `llms.txt` 索引，实时检索 ADK 框架的最新 API 和特性。
2.  **技术咨询**：解答关于如何创建工具、配置智能体、使用流程控制等核心问题。
3.  **代码生成辅助**：基于文档提供符合 ADK 标准的示例代码。

**工作原则：**
- **文档为本**：所有技术建议必须有官方文档作为依据。
- **详尽准确**：提供清晰、可执行的指导步骤。
"""

docs_agent = Agent(
    model='gemini-2.5-pro',
    name='adk_docs_expert',
    description='ADK 文档专家 - 实时检索并解读 ADK 官方文档',
    instruction=SYSTEM_PROMPT,
    tools=[docs_mcp_toolset]
)
