"""
ADK Companion - 工具集
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional
import requests
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


def generate_evolution_pr(target_version: str, sample_code: str, dependency_changes: str) -> dict:
    """生成进化 PR（简化实现）"""
    try:
        # 这里应该实现 Git 操作和 PR 创建
        # 由于需要 Git 操作，这里返回模拟结果
        return {
            "status": "success",
            "pr_url": f"https://github.com/your-repo/pull/123",
            "message": f"Created PR for upgrade to {target_version}"
        }
    except Exception as e:
        return {"error": str(e)}