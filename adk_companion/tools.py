"""
ADK Companion - 工具集
"""

import os
from pathlib import Path
from typing import Optional
from github import Github
from dotenv import load_dotenv
load_dotenv()

def find_adk_site_packages() -> Optional[Path]:
    """查找当前 Python 环境下 ADK 库的 site-packages 路径"""
    try:
        import google.adk
        adk_path = Path(google.adk.__file__).parent
        return adk_path
    except ImportError:
        return None

def read_adk_codebase(keyword: str, max_results: int = 10) -> list[str]:
    """在 ADK 源码中搜索关键词并返回匹配的文件内容片段"""
    adk_path = find_adk_site_packages()
    if not adk_path:
        return ["ADK 未安装在当前环境中"]
    
    results = []
    try:
        # 简单实现：遍历 .py 文件并搜索关键词
        for py_file in adk_path.rglob("*.py"):
            if len(results) >= max_results:
                break
            try:
                content = py_file.read_text(encoding="utf-8")
                if keyword.lower() in content.lower():
                    results.append(f"文件: {py_file.relative_to(adk_path)}\n{content[:500]}...")
            except Exception:
                continue
    except Exception as e:
        results.append(f"搜索出错: {e}")
    
    return results[:max_results]

def check_upstream_release() -> dict:
    """检查上游 ADK 仓库的最新发布版本"""
    try:
        # 使用 GitHub API 获取最新发布
        token = os.getenv("GITHUB_TOKEN")
        g = Github(token) if token else Github()
        repo = g.get_repo("google/adk-python")
        latest_release = repo.get_latest_release()
        
        return {
            "tag_name": latest_release.tag_name,
            "published_at": latest_release.published_at.isoformat(),
            "body": latest_release.body[:1000] + "..." if len(latest_release.body) > 1000 else latest_release.body
        }
    except Exception as e:
        return {"error": str(e)}

def generate_pr(
    title: str,
    description: str,
    files_to_modify: dict = None,
    files_to_create: dict = None,
    base_branch: str = "main",
    branch_prefix: str = "feature"
) -> dict:
    """
    通用 PR 生成器 - 创建分支、修改/创建文件、提交并创建 PR
    
    Args:
        title: PR 标题
        description: PR 描述
        files_to_modify: 要修改的文件字典 {文件路径: 新内容}
        files_to_create: 要创建的文件字典 {文件路径: 文件内容}
        base_branch: 目标分支（默认 main）
        branch_prefix: 分支前缀（默认 feature）
    
    Returns:
        dict: 包含 PR 信息或错误信息
    """
    try:
        import git
        from datetime import datetime
        
        # 获取当前仓库路径 - 使用更可靠的方法
        current_file = Path(__file__).resolve()
        repo_path = current_file.parent.parent.parent
        
        # 验证仓库路径
        if not repo_path.exists():
            return {"error": f"仓库路径不存在: {repo_path}"}
        
        # 检查是否是 git 仓库
        if not (repo_path / '.git').exists():
            return {"error": f"路径不是 Git 仓库: {repo_path}"}
        
        # 初始化仓库对象
        try:
            repo = git.Repo(str(repo_path))
        except Exception as e:
            return {"error": f"无法初始化 Git 仓库: {str(e)}"}
        
        # 检查仓库状态
        if repo.is_dirty():
            return {"error": "工作目录有未提交的更改，请先提交或暂存更改"}
        
        # 获取当前分支
        try:
            current_branch = repo.active_branch.name
        except Exception as e:
            return {"error": f"无法获取当前分支: {str(e)}"}
        
        # 生成分支名（基于标题，简化处理）
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        if not safe_title:
            safe_title = "update"
        branch_name = f"{branch_prefix}/{'-'.join(safe_title.lower().split()[:5])}"
        
        # 确保在正确的分支上
        try:
            # 先获取最新代码
            origin = repo.remote(name='origin')
            origin.fetch()
        except Exception as e:
            return {"error": f"无法获取远程更新: {str(e)}"}
        
        # 切换到新分支
        try:
            if branch_name in [ref.name for ref in repo.refs]:
                # 分支已存在，删除并重新创建
                repo.delete_head(branch_name, force=True)
            new_branch = repo.create_head(branch_name)
            new_branch.checkout()
        except Exception as e:
            return {"error": f"无法创建分支 {branch_name}: {str(e)}"}
        
        # 修改文件
        files_added = []
        if files_to_modify:
            for file_path, new_content in files_to_modify.items():
                try:
                    full_path = repo_path / file_path
                    # 确保路径是相对路径且在仓库内
                    if not str(full_path).startswith(str(repo_path)):
                        return {"error": f"文件路径超出仓库范围: {file_path}"}
                    
                    if full_path.exists():
                        with open(full_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        files_added.append(file_path)
                    else:
                        return {"error": f"要修改的文件不存在: {file_path}"}
                except Exception as e:
                    return {"error": f"修改文件 {file_path} 失败: {str(e)}"}
        
        # 创建新文件
        if files_to_create:
            for file_path, content in files_to_create.items():
                try:
                    full_path = repo_path / file_path
                    # 确保路径是相对路径且在仓库内
                    if not str(full_path).startswith(str(repo_path)):
                        return {"error": f"文件路径超出仓库范围: {file_path}"}
                    
                    # 确保目录存在
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    files_added.append(file_path)
                except Exception as e:
                    return {"error": f"创建文件 {file_path} 失败: {str(e)}"}
        
        # 提交更改
        if files_added:
            try:
                repo.index.add(files_added)
                
                commit_message = f"""{title}

{description}

---
Generated by ADK Companion at {datetime.now().isoformat()}
"""
                repo.index.commit(commit_message)
            except Exception as e:
                return {"error": f"提交更改失败: {str(e)}"}
        else:
            # 没有文件更改，切换回原分支并返回
            try:
                repo.branches[current_branch].checkout()
                return {"error": "没有文件被修改或创建"}
            except Exception as e:
                return {"error": f"切换回原分支失败: {str(e)}"}
        
        # 推送到远程
        try:
            origin = repo.remote(name='origin')
            origin.push(branch_name)
        except Exception as e:
            return {"error": f"推送分支 {branch_name} 到远程失败: {str(e)}"}
        
        # 创建 PR（需要 GitHub Token）
        token = os.getenv("GITHUB_TOKEN")
        if token:
            try:
                g = Github(token)
                
                # 获取仓库信息
                try:
                    remote_url = repo.remotes.origin.url
                    if 'github.com' in remote_url:
                        # 处理 HTTPS 和 SSH 两种格式
                        if remote_url.startswith('git@'):
                            # SSH 格式: git@github.com:owner/repo.git
                            repo_path_part = remote_url.split('github.com:')[1].replace('.git', '')
                        else:
                            # HTTPS 格式: https://github.com/owner/repo.git
                            repo_path_part = remote_url.split('github.com/')[1].replace('.git', '')
                        
                        if '/' in repo_path_part:
                            owner, name = repo_path_part.split('/')
                        else:
                            return {"error": f"无法解析仓库名称: {repo_path_part}"}
                    else:
                        return {"error": f"不支持的远程 URL 格式: {remote_url}"}
                except Exception as e:
                    return {"error": f"获取远程仓库信息失败: {str(e)}"}
                
                github_repo = g.get_repo(f"{owner}/{name}")
                pr = github_repo.create_pull(
                    title=title,
                    body=commit_message,
                    head=branch_name,
                    base=base_branch
                )
                
                # 切换回原分支
                try:
                    repo.branches[current_branch].checkout()
                except Exception as e:
                    # 即使切换分支失败，PR 已经创建成功
                    pass
                
                return {
                    "status": "success",
                    "pr_url": pr.html_url,
                    "pr_number": pr.number,
                    "branch_name": branch_name,
                    "message": f"Created PR #{pr.number}: {title}"
                }
            except Exception as e:
                # 切换回原分支
                try:
                    repo.branches[current_branch].checkout()
                except:
                    pass
                return {"error": f"创建 PR 失败: {str(e)}"}
        else:
            # 切换回原分支
            try:
                repo.branches[current_branch].checkout()
            except Exception as e:
                return {"error": f"切换回原分支失败: {str(e)}"}
            return {
                "status": "partial_success",
                "pr_url": None,
                "branch_name": branch_name,
                "message": f"Branch {branch_name} created and pushed, but no GitHub token to create PR"
            }
            
    except ImportError as e:
        return {"error": f"缺少依赖库: {str(e)}. 请安装 GitPython: pip install GitPython"}
    except Exception as e:
        # 尝试切换回原分支
        try:
            if 'repo' in locals():
                repo.branches[current_branch].checkout()
        except:
            pass
        return {"error": f"创建 PR 失败: {str(e)}"}

def read_github_repo(
    repo_path: str = None,
    file_path: str = None,
    branch: str = "main",
    max_files: int = 50
) -> dict:
    """
    读取 GitHub 仓库的项目结构或指定文件内容
    
    Args:
        repo_path: 仓库路径，格式为 "owner/repo"，默认使用当前项目仓库
        file_path: 指定文件路径（相对于仓库根目录），如果为空则返回目录结构
        branch: 分支名，默认为 main
        max_files: 最大文件数量限制（仅在读取目录结构时生效）
    
    Returns:
        dict: 包含文件结构或文件内容的字典
    """
    try:
        token = os.getenv("GITHUB_TOKEN")
        g = Github(token) if token else Github()
        
        # 如果没有指定仓库，尝试从当前 git remote 获取
        if not repo_path:
            try:
                import git
                repo_path_obj = Path(__file__).parent.parent.parent
                repo = git.Repo(repo_path_obj)
                remote_url = repo.remotes.origin.url
                
                if 'github.com' in remote_url:
                    repo_path = remote_url.split('github.com/')[1].replace('.git', '')
                else:
                    return {"error": "无法确定仓库路径，请手动指定 repo_path 参数"}
            except Exception:
                return {"error": "无法自动获取仓库信息，请手动指定 repo_path 参数"}
        
        # 获取仓库对象
        repo = g.get_repo(repo_path)
        
        if file_path:
            # 读取指定文件内容
            try:
                file_content = repo.get_contents(file_path, ref=branch)
                if file_content.type == "file":
                    return {
                        "file_path": file_path,
                        "content": file_content.decoded_content.decode('utf-8'),
                        "size": file_content.size,
                        "sha": file_content.sha
                    }
                else:
                    return {"error": f"'{file_path}' 是一个目录，不是文件"}
            except Exception as e:
                return {"error": f"读取文件 '{file_path}' 失败: {str(e)}"}
        else:
            # 获取目录结构
            try:
                file_tree = []
                contents = repo.get_contents("", ref=branch)
                
                def process_directory(contents, prefix="", depth=0):
                    if depth > 3 or len(file_tree) >= max_files:  # 限制深度和数量
                        return
                    
                    for content in contents:
                        if len(file_tree) >= max_files:
                            break
                            
                        if content.type == "dir":
                            file_tree.append({
                                "type": "dir",
                                "path": f"{prefix}{content.name}/",
                                "size": 0
                            })
                            
                            # 递归获取子目录内容（限制深度）
                            if depth < 2:
                                try:
                                    sub_contents = repo.get_contents(content.path, ref=branch)
                                    process_directory(sub_contents, f"{prefix}{content.name}/", depth + 1)
                                except:
                                    continue
                        else:
                            file_tree.append({
                                "type": "file",
                                "path": f"{prefix}{content.name}",
                                "size": content.size,
                                "sha": content.sha
                            })
                
                process_directory(contents)
                
                return {
                    "repo": repo_path,
                    "branch": branch,
                    "total_files": len([f for f in file_tree if f["type"] == "file"]),
                    "total_dirs": len([f for f in file_tree if f["type"] == "dir"]),
                    "file_tree": file_tree[:max_files]
                }
                
            except Exception as e:
                return {"error": f"获取目录结构失败: {str(e)}"}
                
    except Exception as e:
        return {"error": f"GitHub API 调用失败: {str(e)}"}

def generate_evolution_pr(target_version: str, sample_code: str, dependency_changes: str) -> dict:
    """
    生成 ADK 升级 PR - 使用通用 PR 生成器的特化版本
    """
    from datetime import datetime
    
    title = f"feat: upgrade to ADK {target_version}"
    description = f"""Upgrade google-adk to version {target_version}

Changes:
- Update google-adk to version {target_version}
- Add new feature sample: new_feature_{target_version}.py

{dependency_changes}"""
    
    # 修改 requirements.txt
    files_to_modify = {}
    requirements_path = "requirements.txt"
    if (Path(__file__).parent.parent.parent / requirements_path).exists():
        with open(Path(__file__).parent.parent.parent / requirements_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        updated_lines = []
        for line in lines:
            if line.startswith('google-adk'):
                updated_lines.append(f'google-adk=={target_version}')
            else:
                updated_lines.append(line)
        
        files_to_modify[requirements_path] = '\n'.join(updated_lines)
    
    # 创建示例文件
    files_to_create = {
        f"samples/new_feature_{target_version}.py": f'''"""
新功能示例 - 版本 {target_version}
生成时间: {datetime.now().isoformat()}
"""

{sample_code}

if __name__ == "__main__":
    # 示例用法
    print("新功能示例运行完成")
'''
    }
    
    return generate_pr(
        title=title,
        description=description,
        files_to_modify=files_to_modify,
        files_to_create=files_to_create,
        branch_prefix="chore"
    )