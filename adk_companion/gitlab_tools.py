# -*- coding: utf-8 -*-

"""
@author: gitlab_tools.py
@software: Gautomator
@time: 2024/5/21 16:21
"""

import os
import json
import re
import gitlab
import json_repair
from dotenv import load_dotenv

load_dotenv()

def get_gitlab_instance(use_review_token: bool = False):
    """获取 GitLab 实例"""
    gitlab_url = os.getenv("GITLAB_URL")
    if use_review_token:
        token_name = "REVIEW_GITLAB_PRIVATE_TOKEN"
        private_token = os.getenv(token_name)
    else:
        token_name = "GITLAB_PRIVATE_TOKEN"
        private_token = os.getenv(token_name)

    if not gitlab_url or not private_token:
        error_message = (
            f"请在 .env 文件中设置 GITLAB_URL 和 {token_name}。"
            f" {token_name} 是审查代理所必需的，以确保遵循多代理审查工作流程。"
        )
        raise ValueError(error_message)
    return gitlab.Gitlab(gitlab_url, private_token=private_token)

def _get_project(gl, repo_path: str):
    """Helper function to get a project by its path."""
    return gl.projects.get(repo_path)

def check_mr_author(repo_path: str, mr_id: int) -> dict:
    """检查 MR 的创建者信息"""
    try:
        gl_main = get_gitlab_instance(use_review_token=False)
        gl_main.auth()  # Force authentication to populate user object
        main_user = gl_main.user.username
        
        project = _get_project(gl_main, repo_path)
        mr = project.mergerequests.get(mr_id)
        author = mr.author['username']
        
        is_own_mr = author == main_user
        
        return {
            "status": "success",
            "mr_author": author,
            "current_user": main_user,
            "is_own_mr": is_own_mr
        }
    except Exception as e:
        return {"error": f"检查 MR 作者失败: {e}"}

def get_mr_info(repo_path: str, mr_id: int) -> dict:
    """获取 GitLab MR 信息"""
    try:
        gl = get_gitlab_instance()
        project = _get_project(gl, repo_path)
        mr = project.mergerequests.get(mr_id)
        return mr.attributes
    except Exception as e:
        return {"error": f"获取 MR 信息失败: {e}"}

def get_mr_change_files(repo_path: str, mr_id: int) -> dict:
    """获取 GitLab MR 涉及文件"""
    try:
        gl = get_gitlab_instance()
        project = _get_project(gl, repo_path)
        mr = project.mergerequests.get(mr_id)
        changes = mr.changes()
        return changes
    except Exception as e:
        return {"error": f"获取 MR 变更文件失败: {e}"}

def get_file_content(repo_path: str, file_path: str, ref: str) -> dict:
    """获取 GitLab 文件内容"""
    try:
        gl = get_gitlab_instance()
        project = _get_project(gl, repo_path)
        file_content = project.files.get(file_path=file_path, ref=ref)
        return file_content.decode()
    except Exception as e:
        return {"error": f"获取文件内容失败: {e}"}

def post_comment_on_mr(repo_path: str, mr_id: int, comment: str, use_review_token: bool = False) -> dict:
    """在 GitLab MR 下发表评论"""
    try:
        gl = get_gitlab_instance(use_review_token=use_review_token)
        project = _get_project(gl, repo_path)
        mr = project.mergerequests.get(mr_id)
        mr.notes.create({'body': comment})
        return {"status": "success", "message": "评论已发布"}
    except Exception as e:
        return {"error": f"发表评论失败: {e}"}

def create_branch(repo_path: str, branch_name: str, ref: str = "main") -> dict:
    """
    创建 GitLab 分支
    """
    try:
        gl = get_gitlab_instance()
        project = _get_project(gl, repo_path)
        
        # 检查分支是否存在
        try:
            project.branches.get(branch_name)
            return {"status": "exists", "message": f"分支 {branch_name} 已存在"}
        except gitlab.exceptions.GitlabGetError:
            pass

        branch = project.branches.create({'branch': branch_name, 'ref': ref})
        return {"status": "success", "branch_name": branch.name, "message": f"已基于 {ref} 创建分支 {branch_name}"}
    except Exception as e:
        return {"error": f"创建分支失败: {e}"}

def create_commit(
    repo_path: str,
    branch_name: str,
    commit_message: str,
    actions: str,
    author_name: str,
    author_email: str
) -> dict:
    """
    提交文件到 GitLab 分支
    
    Args:
        repo_path: 仓库路径 (e.g., 'namespace/project-name')
        branch_name: 分支名称
        commit_message: 提交信息，必须以 '#' 开头，后跟六位数字 (例如 #123456)
        actions: 操作列表 (JSON 字符串)，格式为 [{"action": "create", "file_path": "path", "content": "content"}]
        author_name: 提交者姓名 (必需)
        author_email: 提交者邮箱 (必需)
    """
    try:
        # 验证提交信息格式
        if not re.match(r'^#\d+', commit_message):
            return {"error": "无效的提交信息格式。它必须以 '#' 开头，后跟六位数字 (例如 #123456)。"}
        
        # 验证作者信息
        if not author_name or not author_email:
            return {"error": "提交者姓名和邮箱是必需的。"}

        gl = get_gitlab_instance()
        project = _get_project(gl, repo_path)
        
        actions_list = []
        if isinstance(actions, list):
            actions_list = actions
        elif isinstance(actions, str):
            try:
                # First try standard load
                actions_list = json.loads(actions)
            except json.JSONDecodeError:
                try:
                    # If standard load fails, try json_repair which is robust against common LLM JSON errors
                    # like unescaped control characters, missing quotes, etc.
                    actions_list = json_repair.repair_json(actions, return_objects=True)
                except Exception as e:
                    return {"error": f"actions 参数解析失败: 无效的 JSON 字符串，尝试修复也失败. Error: {e}"}
            
            # Validate structure
            if not isinstance(actions_list, list):
                 return {"error": "actions 参数解析后必须是列表 (List)"}
        else:
             return {"error": f"actions 参数类型错误: 必须是 JSON 字符串或列表，但在收到的是 {type(actions)}"}

        commit_data = {
            'branch': branch_name,
            'commit_message': commit_message,
            'actions': actions_list,
            'author_name': author_name,
            'author_email': author_email
        }
        
        print(f"[DEBUG] create_commit payload preview: branch={branch_name}, message={commit_message}, author={author_name}")
        print(f"[DEBUG] Actions count: {len(actions_list)}")
        # Log first action summary for debugging (avoid printing full content if huge)
        if actions_list:
            first_action = actions_list[0].copy()
            if 'content' in first_action and len(first_action['content']) > 100:
                first_action['content'] = first_action['content'][:100] + "..."
            print(f"[DEBUG] First action preview: {first_action}")

        commit = project.commits.create(commit_data)
        return {"status": "success", "commit_id": commit.id, "message": "提交成功"}
    except gitlab.exceptions.GitlabCreateError as e:
        print(f"[ERROR] GitlabCreateError: {e.response_code}, Body: {e.response_body}, Error: {e.error_message}")
        return {"error": f"提交失败: {e.response_code}", "details": e.error_message}
    except Exception as e:
        print(f"[ERROR] create_commit failed with unexpected error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return {"error": f"提交失败: {e}"}

def create_mr(
    repo_path: str,
    title: str,
    description: str,
    source_branch: str,
    target_branch: str = "main"
) -> dict:
    """
    创建 GitLab Merge Request
    """
    try:
        gl = get_gitlab_instance()
        project = _get_project(gl, repo_path)
        
        mr = project.mergerequests.create({
            'source_branch': source_branch,
            'target_branch': target_branch,
            'title': title,
            'description': description
        })
        
        return {
            "status": "success",
            "mr_id": mr.iid,
            "mr_url": mr.web_url,
            "message": f"MR !{mr.iid} 创建成功"
        }
    except Exception as e:
        return {"error": f"创建 MR 失败: {e}"}

def review_mr(repo_path: str, mr_id: int, review_comment: str, use_review_token: bool = False) -> dict:
    """
    提交 GitLab MR 审查意见 (不执行正式 approve 动作)
    
    Args:
        repo_path: 仓库路径
        mr_id: MR ID
        review_comment: 审查意见（必需，应明确是否通过）
        use_review_token: 是否使用审查 Token
    """
    token_in_use = "REVIEW_GITLAB_PRIVATE_TOKEN" if use_review_token else "GITLAB_PRIVATE_TOKEN"
    print(f"[DEBUG] Attempting to review MR !{mr_id} in project {repo_path} using {token_in_use}")

    try:
        gl = get_gitlab_instance(use_review_token=use_review_token)
        print("[DEBUG] GitLab instance created.")

        project = _get_project(gl, repo_path)
        print(f"[DEBUG] Fetched project: {project.name_with_namespace}")

        mr = project.mergerequests.get(mr_id)
        print(f"[DEBUG] Fetched MR: '{mr.title}'")
        print(f"[DEBUG] MR Author: {mr.author['username']}")
        print(f"[DEBUG] MR State: {mr.state}")

        # Post review comment
        print("[DEBUG] Posting review comment...")
        try:
            mr.notes.create({'body': review_comment})
            print("[DEBUG] Review comment posted successfully.")
            return {"status": "success", "message": f"已成功发表审查意见到 MR !{mr_id}"}
        except Exception as note_e:
            print(f"[ERROR] Failed to post review comment: {note_e}")
            return {"error": f"发表审查意见失败: {note_e}"}

    except Exception as e:
        print(f"[ERROR] An unexpected error occurred in review_mr: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return {"error": f"审查 MR 失败: {e}"}

def merge_mr(repo_path: str, mr_id: int) -> dict:
    """合并 GitLab MR"""
    try:
        gl = get_gitlab_instance()
        project = _get_project(gl, repo_path)
        mr = project.mergerequests.get(mr_id)
        if not mr.mergeable:
            return {"error": "MR 不可合并", "merge_status": mr.merge_status}
        mr.merge()
        return {"status": "success", "message": f"MR !{mr_id} 已合并"}
    except Exception as e:
        return {"error": f"合并 MR 失败: {e}"}

def compare_branches(repo_path: str, source: str, target: str) -> dict:
    """
    对比两个分支或提交之间的差异
    
    Args:
        repo_path: 仓库路径 (e.g., 'namespace/project-name')
        source: 源分支或提交 hash (from)
        target: 目标分支或提交 hash (to)
    """
    try:
        gl = get_gitlab_instance()
        project = _get_project(gl, repo_path)
        
        comparison = project.repository_compare(target, source)
        
        diffs = []
        for diff in comparison['diffs']:
            diffs.append({
                'new_path': diff['new_path'],
                'old_path': diff['old_path'],
                'new_file': diff['new_file'],
                'renamed_file': diff['renamed_file'],
                'deleted_file': diff['deleted_file'],
                'diff': diff['diff'][:1000] + "..." if len(diff['diff']) > 1000 else diff['diff']
            })
            
        return {
            "status": "success",
            "commit": comparison['commit'],
            "diffs": diffs,
            "compare_timeout": comparison['compare_timeout'],
            "compare_error": comparison['compare_error']
        }
    except Exception as e:
        return {"error": f"对比分支失败: {e}"}

def get_commit_info(repo_path: str, commit_sha: str) -> dict:
    """
    获取指定提交的详细信息
    
    Args:
        repo_path: 仓库路径 (e.g., 'namespace/project-name')
        commit_sha: 提交的 SHA 哈希值
    """
    try:
        gl = get_gitlab_instance()
        project = _get_project(gl, repo_path)
        commit = project.commits.get(commit_sha)
        
        diff = commit.diff()
        
        return {
            "status": "success",
            "id": commit.id,
            "short_id": commit.short_id,
            "title": commit.title,
            "message": commit.message,
            "author_name": commit.author_name,
            "author_email": commit.author_email,
            "authored_date": commit.authored_date,
            "committer_name": commit.committer_name,
            "committer_email": commit.committer_email,
            "committed_date": commit.committed_date,
            "stats": commit.stats,
            "web_url": commit.web_url,
            "diffs": diff[:10]
        }
    except Exception as e:
        return {"error": f"获取提交信息失败: {e}"}

def list_commits(repo_path: str, ref_name: str = None, max_commits: int = 20) -> dict:
    """
    列出 GitLab 仓库的提交记录
    
    Args:
        repo_path: 仓库路径 (e.g., 'namespace/project-name')
        ref_name: 分支、标签或提交 SHA (可选, 默认为默认分支)
        max_commits: 返回的最大提交数量 (可选, 默认 20)
    """
    try:
        gl = get_gitlab_instance()
        project = _get_project(gl, repo_path)
        
        # Build options for the list call
        options = {'per_page': max_commits}
        if ref_name:
            options['ref_name'] = ref_name
            
        commits = project.commits.list(iterator=True, **options)
        
        commit_list = []
        for commit in commits:
            commit_list.append({
                "id": commit.id,
                "short_id": commit.short_id,
                "title": commit.title,
                "author_name": commit.author_name,
                "committed_date": commit.committed_date,
                "web_url": commit.web_url
            })
            if len(commit_list) >= max_commits:
                break
        
        return {
            "status": "success",
            "repo_path": repo_path,
            "ref_name": ref_name or project.default_branch,
            "commit_count": len(commit_list),
            "commits": commit_list
        }
    except Exception as e:
        return {"error": f"获取提交列表失败: {e}"}

def list_branches(repo_path: str, search: str = None) -> dict:
    """
    列出 GitLab 仓库的分支
    
    Args:
        repo_path: 仓库路径 (e.g., 'namespace/project-name')
        search: 搜索关键词（可选）
    """
    try:
        gl = get_gitlab_instance()
        project = _get_project(gl, repo_path)
        
        branches = project.branches.list(search=search, iterator=True)
        branch_list = []
        for branch in branches:
            branch_list.append({
                "name": branch.name,
                "merged": branch.merged,
                "protected": branch.protected,
                "default": branch.default,
                "commit": {
                    "id": branch.commit['id'],
                    "message": branch.commit['message'],
                    "committed_date": branch.commit['committed_date']
                }
            })
            if len(branch_list) >= 50:
                break
                
        return {
            "status": "success",
            "project_name": project.name,
            "total_count": len(branch_list),
            "branches": branch_list
        }
    except Exception as e:
        return {"error": f"获取分支列表失败: {e}"}

def read_gitlab_repo(repo_path: str, file_path: str = None, ref: str = None, max_files: int = 50) -> dict:
    """
    读取 GitLab 仓库的项目结构或指定文件内容
    
    Args:
        repo_path: 仓库路径 (e.g., 'namespace/project-name')
        file_path: 文件路径（可选，若提供则读取文件内容）
        ref: 分支名或 commit SHA（可选，若不提供则使用项目默认分支）
        max_files: 最大返回文件数（仅在读取目录结构时生效）
    """
    try:
        gl = get_gitlab_instance()
        project = _get_project(gl, repo_path)
        
        if not ref:
            if hasattr(project, 'default_branch') and project.default_branch:
                ref = project.default_branch
            else:
                ref = 'main'
        
        try:
            project.branches.list(iterator=True).next()
        except StopIteration:
             return {"error": "仓库为空，没有任何分支或提交", "project_name": project.name}
        except Exception:
            pass

        if file_path:
            try:
                file_content = project.files.get(file_path=file_path, ref=ref)
                return {
                    "file_path": file_path,
                    "content": file_content.decode().decode('utf-8'),
                    "size": file_content.size,
                    "commit_id": file_content.commit_id,
                    "ref": ref
                }
            except gitlab.exceptions.GitlabGetError as e:
                if e.response_code == 404:
                    return {"error": f"文件 '{file_path}' 在分支 '{ref}' 上不存在"}
                return {"error": f"读取文件失败: {e}"}
        else:
            try:
                items = project.repository_tree(ref=ref, recursive=True, all=True)
                file_tree = []
                for item in items:
                    if len(file_tree) >= max_files:
                        break
                    file_tree.append({
                        "type": item['type'],
                        "path": item['path'],
                    })
                return {
                    "repo_path": repo_path,
                    "ref": ref,
                    "total_files": len(file_tree),
                    "file_tree": file_tree[:max_files]
                }
            except gitlab.exceptions.GitlabGetError as e:
                if e.response_code == 404:
                    try:
                        branches = [b.name for b in project.branches.list(iterator=True)]
                        return {
                            "error": f"分支 '{ref}' 不存在或无法访问", 
                            "available_branches": branches[:10]
                        }
                    except:
                        pass
                return {"error": f"获取目录结构失败: {e}"}
    except Exception as e:
        return {"error": f"GitLab API 调用失败: {str(e)}"}
