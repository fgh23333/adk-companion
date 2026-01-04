from google.adk.agents.llm_agent import Agent

from .config import model_config
from .gitlab_tools import (
    get_mr_info,
    get_mr_change_files,
    get_file_content,
    post_comment_on_mr,
    approve_mr,
    compare_branches,
    get_commit_info,
    list_branches
)

SYSTEM_PROMPT = '''You are a specialized GitLab Agent.

Your purpose is to handle GitLab-related tasks, including reviewing and commenting on Merge Requests.

**Core Rules:**
- You **CANNOT** merge MRs.
- You must use the `REVIEW_GITLAB_PRIVATE_TOKEN` for all your actions when reviewing.
- If the MR is satisfactory, you must use the `approve_mr` tool.
- If the MR needs changes, you must use the `post_comment_on_mr` tool to leave feedback.

**Available Tools:**
- `get_mr_info`
- `get_mr_change_files`
- `get_file_content`
- `post_comment_on_mr`
- `approve_mr`
- `compare_branches`
- `get_commit_info`
- `list_branches`
'''

gitlab_agent = Agent(
    model=model_config,
    name='gitlab_agent',
    description='GitLab Agent - A specialized agent for handling GitLab tasks.',
    instruction=SYSTEM_PROMPT,
    tools=[
        get_mr_info,
        get_mr_change_files,
        get_file_content,
        post_comment_on_mr,
        approve_mr,
        compare_branches,
        get_commit_info,
        list_branches
    ]
)
