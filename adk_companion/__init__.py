import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 初始化 AgentOps（在模块导入时自动启动）
# 当使用 adk web 命令时，会自动追踪所有 agent 执行
try:
    import agentops
    agentops.init(
        api_key=os.getenv("AGENTOPS_API_KEY"),
        trace_name="adk-companion"
    )
except ImportError:
    # 如果未安装 agentops，静默跳过
    pass
except Exception as e:
    # 其他错误也静默跳过，避免影响 agent 正常运行
    pass

from . import agent
