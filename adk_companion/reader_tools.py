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

def inspect_installed_package(package_name: str) -> dict:
    """
    检查已安装的 Python 包信息（版本、依赖、元数据）
    
    Args:
        package_name: 包名
    
    Returns:
        dict: 包信息
    """
    try:
        import importlib.metadata
        
        try:
            dist = importlib.metadata.distribution(package_name)
            metadata = dist.metadata
            
            return {
                "name": metadata.get("Name"),
                "version": metadata.get("Version"),
                "summary": metadata.get("Summary"),
                "home_page": metadata.get("Home-page"),
                "author": metadata.get("Author"),
                "license": metadata.get("License"),
                "requires_dist": dist.requires if dist.requires else [],
                "files_count": len(dist.files) if dist.files else 0,
                "location": str(dist.locate_file(""))
            }
        except importlib.metadata.PackageNotFoundError:
            return {"error": f"包 '{package_name}' 未安装"}
            
    except Exception as e:
        return {"error": f"检查包信息失败: {str(e)}"}

def analyze_file_imports(file_path: str, content: str = None) -> dict:
    """
    分析 Python 文件中的导入依赖
    
    Args:
        file_path: 文件路径（用于显示）
        content: 文件内容（如果未提供，尝试从 file_path 读取，但这需要本地文件访问，通常配合 read_github_repo 使用）
    
    Returns:
        dict: 导入列表和分析结果
    """
    import ast
    
    try:
        if content is None:
            # 尝试本地读取，如果失败则返回错误
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                return {"error": "需要提供 content 参数或本地文件不存在"}
        
        tree = ast.parse(content)
        
        imports = []
        from_imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append({
                        "name": name.name,
                        "asname": name.asname
                    })
            elif isinstance(node, ast.ImportFrom):
                module = node.module if node.module else ""
                for name in node.names:
                    from_imports.append({
                        "module": module,
                        "name": name.name,
                        "asname": name.asname,
                        "level": node.level
                    })
                    
        # 提取顶级依赖
        dependencies = set()
        for imp in imports:
            dependencies.add(imp["name"].split('.')[0])
        for imp in from_imports:
            if imp["module"]:
                dependencies.add(imp["module"].split('.')[0])
        
        return {
            "file": file_path,
            "imports": imports,
            "from_imports": from_imports,
            "detected_dependencies": list(dependencies)
        }
        
    except Exception as e:
        return {"error": f"分析导入失败: {str(e)}"}
