from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool import StreamableHTTPConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset

minio_mcp_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="http://172.31.243.14:8090/mcp",
    )
)

SYSTEM_PROMPT = """你是 MinIO 专家，负责通过工具与 MinIO 服务进行交互。
你可以使用以下工具来管理文件、存储桶和执行其他 MinIO 相关操作。
请根据用户的请求，选择合适的工具并执行。"""

minio_agent = Agent(
    model='gemini-2.5-pro',
    name='minio_expert',
    description='MinIO 专家 - 负责通过工具与 MinIO 服务进行交互',
    instruction=SYSTEM_PROMPT,
    tools=[minio_mcp_toolset]
)