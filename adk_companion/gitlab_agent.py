from google.adk.agents.llm_agent import Agent

from .config import model_config
from .gitlab_tools import (
    get_mr_info,
    get_mr_change_files,
    get_file_content,
    post_comment_on_mr,
    review_mr,
    compare_branches,
    get_commit_info,
    list_branches,
    list_commits
)

SYSTEM_PROMPT = '''You are a specialized GitLab Agent.

Your purpose is to handle GitLab-related tasks, including reviewing and commenting on Merge Requests.

**Core Rules:**
- You **CANNOT** merge MRs.
- You must use the `REVIEW_GITLAB_PRIVATE_TOKEN` for all your actions when reviewing.
- If the MR is satisfactory, you must use the `review_mr` tool and provide a clear review comment (e.g., "Approved: Looks good", "LGTM") explaining why it is approved. Note that this tool only posts a comment and does not perform a formal approval action.
- If the MR needs changes, you must use the `post_comment_on_mr` tool to leave feedback.

**Available Tools:**
- `get_mr_info(repo_path, mr_id)`
- `get_mr_change_files(repo_path, mr_id)`
- `get_file_content(repo_path, file_path, ref)`
- `post_comment_on_mr(repo_path, mr_id, comment)`
- `review_mr(repo_path, mr_id, review_comment)`
- `compare_branches(repo_path, source, target)`
- `get_commit_info(repo_path, commit_sha)`
- `list_commits(repo_path, ref_name, max_commits)`
- `list_branches(repo_path, search)`
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
        review_mr,
        compare_branches,
        get_commit_info,
        list_branches,
        list_commits
    ]
)
