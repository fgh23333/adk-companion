import os
from dotenv import load_dotenv
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# 基础读取工具集：专注于获取仓库内容和结构
github_repo_reader_toolset = McpToolset(
    connection_params=StreamableHTTPServerParams(
        url="https://api.githubcopilot.com/mcp/",
        headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "X-MCP-Toolsets": "repos,users",
            "X-MCP-Readonly": "true"
        },
    ),
)

# 安全与依赖工具集：专注于依赖安全、扫描和警报
github_security_toolset = McpToolset(
    connection_params=StreamableHTTPServerParams(
        url="https://api.githubcopilot.com/mcp/",
        headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "X-MCP-Toolsets": "code_security,dependabot",
            "X-MCP-Readonly": "true"
        },
    ),
)

# PR 与问题管理工具集：具备写权限，用于创建和管理内容
github_full_access_toolset = McpToolset(
    connection_params=StreamableHTTPServerParams(
        url="https://api.githubcopilot.com/mcp/",
        headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "X-MCP-Toolsets": "repos,pull_requests,issues,actions",
            "X-MCP-Readonly": "false"
        },
    ),
)

REVIEW_GITHUB_TOKEN = os.getenv("REVIEW_GITHUB_TOKEN")

# 专用审查工具集：使用独立 Token，专注于 PR 审查和合并
github_review_toolset = McpToolset(
    connection_params=StreamableHTTPServerParams(
        url="https://api.githubcopilot.com/mcp/",
        headers={
            "Authorization": f"Bearer {REVIEW_GITHUB_TOKEN}",
            "X-MCP-Toolsets": "repos,pull_requests",
            "X-MCP-Readonly": "false"
        },
    ),
)
