# -*- coding: utf-8 -*-

"""
@author: gitlab_tools.py
@software: Gautomator
@time: 2024/5/21 16:21
"""

import os
import json
import gitlab
from dotenv import load_dotenv

load_dotenv()

def get_gitlab_instance():
    """获取 GitLab 实例"""
    gitlab_url = os.getenv("GITLAB_URL")
    private_token = os.getenv("GITLAB_PRIVATE_TOKEN")
    if not gitlab_url or not private_token:
        raise ValueError("请在 .env 文件中设置 GITLAB_URL 和 GITLAB_PRIVATE_TOKEN")
    return gitlab.Gitlab(gitlab_url, private_token=private_token)

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

def post_comment_on_mr(project_id: int, mr_id: int, comment: str) -> dict:
    """在 GitLab MR 下发表评论"""
    try:
        gl = get_gitlab_instance()
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
    actions: str,  # JSON string
    author_name: str = None,
    author_email: str = None
) -> dict:
    """
    提交文件到 GitLab 分支
    
    Args:
        project_id: 项目 ID
        branch_name: 分支名称
        commit_message: 提交信息
        actions: 操作列表 (JSON 字符串)，格式为 [{"action": "create", "file_path": "path", "content": "content"}]
        author_name: 提交者姓名 (可选)
        author_email: 提交者邮箱 (可选)
    """
    try:
        gl = get_gitlab_instance()
        project = gl.projects.get(project_id)
        
        actions_list = json.loads(actions)
        
        commit_data = {
            'branch': branch_name,
            'commit_message': commit_message,
            'actions': actions_list
        }
        
        if author_name:
            commit_data['author_name'] = author_name
        if author_email:
            commit_data['author_email'] = author_email
        
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

def approve_mr(project_id: int, mr_id: int) -> dict:
    """批准 GitLab MR"""
    try:
        print(f"[DEBUG] Approving MR !{mr_id} in project {project_id}")
        gl = get_gitlab_instance()
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

def read_gitlab_repo(project_id: int, file_path: str = None, ref: str = "main", max_files: int = 50) -> dict:
    """读取 GitLab 仓库的项目结构或指定文件内容"""
    try:
        gl = get_gitlab_instance()
        project = gl.projects.get(project_id)
        
        if file_path:
            # 读取指定文件内容
            try:
                file_content = project.files.get(file_path=file_path, ref=ref)
                return {
                    "file_path": file_path,
                    "content": file_content.decode().decode('utf-8'),
                    "size": file_content.size,
                    "commit_id": file_content.commit_id
                }
            except Exception as e:
                return {"error": f"读取文件 '{file_path}' 失败: {str(e)}"}
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
            except Exception as e:
                return {"error": f"获取目录结构失败: {str(e)}"}
    except Exception as e:
        return {"error": f"GitLab API 调用失败: {str(e)}"}
