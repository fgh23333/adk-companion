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
        raise ValueError(f"请在 .env 文件中设置 GITLAB_URL 和 {token_name}")
    return gitlab.Gitlab(gitlab_url, private_token=private_token)

def check_mr_author(project_id: int, mr_id: int) -> dict:
    """检查 MR 的创建者信息"""
    try:
        gl_main = get_gitlab_instance(use_review_token=False)
        main_user = gl_main.user.username
        
        project = gl_main.projects.get(project_id)
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

def get_mr_info(project_id: int, mr_id: int) -> dict:
    """获取 GitLab MR 信息"""
    try:
        gl = get_gitlab_instance()
        project = gl.projects.get(project_id)
        mr = project.mergerequests.get(mr_id)
        return mr.attributes
    except Exception as e:
        return {"error": f"获取 MR 信息失败: {e}"}

def get_mr_change_files(project_id: int, mr_id: int) -> dict:
    """获取 GitLab MR 涉及文件"""
    try:
        gl = get_gitlab_instance()
        project = gl.projects.get(project_id)
        mr = project.mergerequests.get(mr_id)
        changes = mr.changes()
        return changes
    except Exception as e:
        return {"error": f"获取 MR 变更文件失败: {e}"}

def get_file_content(project_id: int, file_path: str, ref: str) -> dict:
    """获取 GitLab 文件内容"""
    try:
        gl = get_gitlab_instance()
        project = gl.projects.get(project_id)
        file_content = project.files.get(file_path=file_path, ref=ref)
        return file_content.decode()
    except Exception as e:
        return {"error": f"获取文件内容失败: {e}"}

def post_comment_on_mr(project_id: int, mr_id: int, comment: str, use_review_token: bool = False) -> dict:
    """在 GitLab MR 下发表评论"""
    try:
        gl = get_gitlab_instance(use_review_token=use_review_token)
        project = gl.projects.get(project_id)
        mr = project.mergerequests.get(mr_id)
        mr.notes.create({'body': comment})
        return {"status": "success", "message": "评论已发布"}
    except Exception as e:
        return {"error": f"发表评论失败: {e}"}

def create_branch(project_id: int, branch_name: str, ref: str = "main") -> dict:
    """
    创建 GitLab 分支
    """
    try:
        gl = get_gitlab_instance()
        project = gl.projects.get(project_id)
        
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
    project_id: int,
    branch_name: str,
    commit_message: str,
    actions: str,
    author_name: str,
    author_email: str
) -> dict:
    """
    提交文件到 GitLab 分支
    
    Args:
        project_id: 项目 ID
        branch_name: 分支名称
        commit_message: 提交信息，必须以 '#' 开头，后跟数字 (例如 #12345)
        actions: 操作列表 (JSON 字符串)，格式为 [{"action": "create", "file_path": "path", "content": "content"}]
        author_name: 提交者姓名 (必需)
        author_email: 提交者邮箱 (必需)
    """
    try:
        # 验证提交信息格式
        if not re.match(r'^#\d+', commit_message):
            return {"error": "无效的提交信息格式。它必须以 '#' 开头，后跟数字 (例如 #12345)。"}
        
        # 验证作者信息
        if not author_name or not author_email:
            return {"error": "提交者姓名和邮箱是必需的。"}

        gl = get_gitlab_instance()
        project = gl.projects.get(project_id)
        
        try:
            actions_list = json.loads(actions)
        except json.JSONDecodeError:
            return {"error": "actions 参数必须是有效的 JSON 字符串"}
        
        commit_data = {
            'branch': branch_name,
            'commit_message': commit_message,
            'actions': actions_list,
            'author_name': author_name,
            'author_email': author_email
        }
        
        commit = project.commits.create(commit_data)
        return {"status": "success", "commit_id": commit.id, "message": "提交成功"}
    except Exception as e:
        return {"error": f"提交失败: {e}"}

def create_mr(
    project_id: int,
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
        project = gl.projects.get(project_id)
        
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

def approve_mr(project_id: int, mr_id: int, use_review_token: bool = False) -> dict:
    """批准 GitLab MR"""
    try:
        print(f"[DEBUG] Approving MR !{mr_id} in project {project_id}")
        gl = get_gitlab_instance(use_review_token=use_review_token)
        project = gl.projects.get(project_id)
        mr = project.mergerequests.get(mr_id)
        
        # 尝试进行批准
        try:
            mr.approve()
            return {"status": "success", "message": f"MR !{mr_id} 已批准"}
        except gitlab.exceptions.GitlabUpdateError as e:
            if e.response_code == 404:
                return {
                    "error": f"批准失败 (404): 可能是因为没有权限批准（例如不能批准自己的MR），或者该 GitLab 实例未启用批准功能。",
                    "detail": str(e)
                }
            elif e.response_code == 401:
                 return {"error": "批准失败 (401): 认证失败，请检查 Token 权限", "detail": str(e)}
            else:
                raise e

    except Exception as e:
        print(f"[ERROR] approve_mr failed: {e}")
        return {"error": f"批准 MR 失败: {e}"}

def merge_mr(project_id: int, mr_id: int) -> dict:
    """合并 GitLab MR"""
    try:
        gl = get_gitlab_instance()
        project = gl.projects.get(project_id)
        mr = project.mergerequests.get(mr_id)
        if not mr.mergeable:
            return {"error": "MR 不可合并", "merge_status": mr.merge_status}
        mr.merge()
        return {"status": "success", "message": f"MR !{mr_id} 已合并"}
    except Exception as e:
        return {"error": f"合并 MR 失败: {e}"}

def compare_branches(project_id: int, source: str, target: str) -> dict:
    """
    对比两个分支或提交之间的差异
    
    Args:
        project_id: 项目 ID
        source: 源分支或提交 hash (from)
        target: 目标分支或提交 hash (to)
    """
    try:
        gl = get_gitlab_instance()
        project = gl.projects.get(project_id)
        
        # 注意：GitLab API 的 compare 参数顺序是 from=source, to=target
        # 但通常我们要看 source 相对于 target 改了什么，所以 API 里 from 是 target (base), to 是 source (head)
        comparison = project.repository_compare(target, source)
        
        diffs = []
        for diff in comparison['diffs']:
            diffs.append({
                'new_path': diff['new_path'],
                'old_path': diff['old_path'],
                'new_file': diff['new_file'],
                'renamed_file': diff['renamed_file'],
                'deleted_file': diff['deleted_file'],
                'diff': diff['diff'][:1000] + "..." if len(diff['diff']) > 1000 else diff['diff'] # 截断过长的 diff
            })
            
        return {
            "status": "success",
            "commit": comparison['commit'], # The latest commit on source
            "diffs": diffs,
            "compare_timeout": comparison['compare_timeout'],
            "compare_error": comparison['compare_error']
        }
    except Exception as e:
        return {"error": f"对比分支失败: {e}"}

def get_commit_info(project_id: int, commit_sha: str) -> dict:
    """
    获取指定提交的详细信息
    
    Args:
        project_id: 项目 ID
        commit_sha: 提交的 SHA 哈希值
    """
    try:
        gl = get_gitlab_instance()
        project = gl.projects.get(project_id)
        commit = project.commits.get(commit_sha)
        
        # 获取提交的变更内容 (diff)
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
            "diffs": diff[:10] # 限制返回的 diff 数量，避免内容过大
        }
    except Exception as e:
        return {"error": f"获取提交信息失败: {e}"}

def list_branches(project_id: int, search: str = None) -> dict:
    """
    列出 GitLab 仓库的分支
    
    Args:
        project_id: 项目 ID
        search: 搜索关键词（可选）
    """
    try:
        gl = get_gitlab_instance()
        project = gl.projects.get(project_id)
        
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
            if len(branch_list) >= 50: # 限制返回数量
                break
                
        return {
            "status": "success",
            "project_name": project.name,
            "total_count": len(branch_list), # 注意：iterator 模式下这里只是已获取的数量
            "branches": branch_list
        }
    except Exception as e:
        return {"error": f"获取分支列表失败: {e}"}

def read_gitlab_repo(project_id: int, file_path: str = None, ref: str = None, max_files: int = 50) -> dict:
    """
    读取 GitLab 仓库的项目结构或指定文件内容
    
    Args:
        project_id: 项目 ID
        file_path: 文件路径（可选，若提供则读取文件内容）
        ref: 分支名或 commit SHA（可选，若不提供则使用项目默认分支）
        max_files: 最大返回文件数（仅在读取目录结构时生效）
    """
    try:
        gl = get_gitlab_instance()
        project = gl.projects.get(project_id)
        
        # 自动检测默认分支
        if not ref:
            if hasattr(project, 'default_branch') and project.default_branch:
                ref = project.default_branch
            else:
                ref = 'main' # Fallback
        
        # 检查仓库是否为空
        try:
            project.branches.list(iterator=True).next()
        except StopIteration:
             return {"error": "仓库为空，没有任何分支或提交", "project_name": project.name}
        except Exception:
            pass # 忽略其他错误，继续尝试

        if file_path:
            # 读取指定文件内容
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
            # 获取目录结构
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
                    "project_id": project_id,
                    "ref": ref,
                    "total_files": len(file_tree),
                    "file_tree": file_tree[:max_files]
                }
            except gitlab.exceptions.GitlabGetError as e:
                if e.response_code == 404:
                     # 尝试列出可用分支
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
