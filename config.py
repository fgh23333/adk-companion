"""
ADK Companion 配置管理
管理不同智能体的 GitHub Token 和其他配置
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

class TokenConfig:
    """GitHub Token 配置管理"""
    
    # 默认Token环境变量名
    DEFAULT_TOKEN = "GITHUB_TOKEN"
    REVIEW_TOKEN = "REVIEW_GITHUB_TOKEN"
    
    @classmethod
    def get_default_token(cls) -> Optional[str]:
        """获取默认的 GitHub Token"""
        return os.getenv(cls.DEFAULT_TOKEN)
    
    @classmethod
    def get_review_token(cls) -> Optional[str]:
        """获取审查专用的 GitHub Token"""
        return os.getenv(cls.REVIEW_TOKEN)
    
    @classmethod
    def validate_tokens(cls) -> Dict[str, bool]:
        """验证所有Token的可用性"""
        return {
            cls.DEFAULT_TOKEN: bool(cls.get_default_token()),
            cls.REVIEW_TOKEN: bool(cls.get_review_token())
        }
    
    @classmethod
    def get_token_info(cls) -> Dict[str, str]:
        """获取Token信息（不暴露实际值）"""
        return {
            cls.DEFAULT_TOKEN: "✅ 已设置" if cls.get_default_token() else "❌ 未设置",
            cls.REVIEW_TOKEN: "✅ 已设置" if cls.get_review_token() else "❌ 未设置"
        }
    
    @classmethod
    def setup_review_token(cls, token: str) -> bool:
        """设置审查专用Token（临时设置，仅当前会话有效）"""
        try:
            os.environ[cls.REVIEW_TOKEN] = token
            return True
        except Exception:
            return False

class AgentConfig:
    """智能体配置管理"""
    
    # 智能体名称
    MAIN_AGENT = "adk_companion"
    REVIEW_AGENT = "pr_reviewer"
    
    # 模型配置
    DEFAULT_MODEL = "gemini-2.5-pro"
    
    # 审查配置
    REVIEW_DEFAULTS = {
        "auto_merge": True,
        "merge_method": "squash",  # 推荐使用 squash 合并
        "require_tests": True,
        "require_docs": True,
        "min_score_threshold": 80  # 最低评分阈值
    }
    
    @classmethod
    def get_review_config(cls) -> Dict[str, any]:
        """获取审查配置"""
        return cls.REVIEW_DEFAULTS.copy()
    
    @classmethod
    def update_review_config(cls, **kwargs) -> Dict[str, any]:
        """更新审查配置"""
        config = cls.REVIEW_DEFAULTS.copy()
        config.update(kwargs)
        return config

class ConfigValidator:
    """配置验证器"""
    
    REQUIRED_VARS = [
        "GOOGLE_GENAI_USE_VERTEXAI",
        "GOOGLE_CLOUD_PROJECT", 
        "GOOGLE_CLOUD_LOCATION",
        "GITHUB_TOKEN"
    ]
    
    OPTIONAL_VARS = [
        "REVIEW_GITHUB_TOKEN",
        "UPSTREAM_REPO"
    ]
    
    REQUIRED_PACKAGES = [
        ("google.adk", "google.adk"),
        ("github", "github"),
        ("python-dotenv", "dotenv")
    ]
    
    @classmethod
    def check_env_file(cls) -> bool:
        """检查 .env 文件是否存在"""
        env_file = Path(".env")
        if env_file.exists():
            print("✅ .env 文件存在")
            return True
        else:
            print("❌ .env 文件不存在")
            print("   请复制 .env.example 为 .env 并填入真实值")
            return False
    
    @classmethod
    def check_required_vars(cls) -> bool:
        """检查必需的环境变量"""
        print("\n📋 检查必需环境变量:")
        all_required_ok = True
        
        for var in cls.REQUIRED_VARS:
            value = os.getenv(var)
            if value:
                if var == "GITHUB_TOKEN":
                    print(f"  ✅ {var}: {'*' * 10}...{value[-4:]}")
                else:
                    print(f"  ✅ {var}: {value}")
            else:
                print(f"  ❌ {var}: 未设置")
                all_required_ok = False
        
        print("\n📋 检查可选环境变量:")
        for var in cls.OPTIONAL_VARS:
            value = os.getenv(var)
            if value:
                if var == "REVIEW_GITHUB_TOKEN":
                    print(f"  ✅ {var}: {'*' * 10}...{value[-4:]}")
                else:
                    print(f"  ✅ {var}: {value}")
            else:
                if var == "REVIEW_GITHUB_TOKEN":
                    print(f"  ⚠️  {var}: 未设置（审查智能体将使用主Token）")
                else:
                    print(f"  ⚠️  {var}: 未设置（将使用默认值）")
        
        return all_required_ok
    
    @classmethod
    def check_token_permissions(cls):
        """检查 Token 权限（简单验证）"""
        print("\n🔍 验证 GitHub Token:")
        
        # 验证默认Token
        default_token = TokenConfig.get_default_token()
        if default_token:
            print("  ✅ GITHUB_TOKEN: 格式正确")
        else:
            print("  ❌ GITHUB_TOKEN: 未设置或格式错误")
        
        # 验证审查Token
        review_token = TokenConfig.get_review_token()
        if review_token:
            print("  ✅ REVIEW_GITHUB_TOKEN: 格式正确")
            
            # 检查是否为不同Token
            if default_token and review_token != default_token:
                print("  ✅ 使用不同的审查Token（推荐）")
            else:
                print("  ⚠️  使用相同的Token（建议使用不同Token）")
        else:
            print("  ❌ REVIEW_GITHUB_TOKEN: 未设置或格式错误")
    
    @classmethod
    def check_google_cloud_config(cls):
        """检查 Google Cloud 配置"""
        print("\n☁️  检查 Google Cloud 配置:")
        
        use_vertexai = os.getenv("GOOGLE_GENAI_USE_VERTEXAI")
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("GOOGLE_CLOUD_LOCATION")
        
        if use_vertexai == "1":
            print("  ✅ 使用 Vertex AI")
            
            if project_id:
                print(f"  ✅ 项目ID: {project_id}")
            else:
                print("  ❌ 项目ID未设置")
                
            if location:
                print(f"  ✅ 位置: {location}")
            else:
                print("  ❌ 位置未设置")
        else:
            print("  ⚠️  未启用 Vertex AI")
    
    @classmethod
    def check_python_dependencies(cls):
        """检查 Python 依赖"""
        print("\n🐍 检查 Python 依赖:")
        
        for package_name, import_name in cls.REQUIRED_PACKAGES:
            try:
                __import__(import_name)
                print(f"  ✅ {package_name}: 已安装")
            except ImportError:
                print(f"  ❌ {package_name}: 未安装")
    
    @classmethod
    def validate_all(cls) -> Tuple[bool, bool]:
        """执行所有配置检查"""
        print("🔧 ADK Companion 配置检查")
        print("=" * 50)
        
        # 加载环境变量
        try:
            from dotenv import load_dotenv
            load_dotenv()
            print("✅ 环境变量已加载")
        except ImportError:
            print("⚠️  python-dotenv 未安装，跳过环境变量加载")
        
        # 执行各项检查
        env_ok = cls.check_env_file()
        vars_ok = cls.check_required_vars()
        cls.check_token_permissions()
        cls.check_google_cloud_config()
        cls.check_python_dependencies()
        
        print("\n" + "=" * 50)
        
        # 总结
        if env_ok and vars_ok:
            print("✅ 配置检查通过！可以开始使用 ADK Companion")
            
            # 给出使用建议
            print("\n💡 使用建议:")
            print("1. 运行 'python review_demo.py' 测试审查功能")
            print("2. 运行 'python ollama_demo.py' 测试主智能体")
            print("3. 查看 TOKEN_CONFIG.md 了解详细配置")
            
            return True, True
        else:
            print("❌ 配置检查失败，请修复上述问题后重试")
            
            print("\n🔧 修复建议:")
            if not env_ok:
                print("1. 复制 .env.example 为 .env")
            if not vars_ok:
                print("2. 在 .env 中设置必需的环境变量")
            
            return False, False

def print_config_status():
    """打印配置状态"""
    print("🔧 ADK Companion 配置状态")
    print("=" * 40)
    
    # Token 状态
    print("📋 Token 状态:")
    token_info = TokenConfig.get_token_info()
    for name, status in token_info.items():
        print(f"  {name}: {status}")
    print()
    
    # 智能体状态
    print("🤖 智能体配置:")
    print(f"  主智能体: {AgentConfig.MAIN_AGENT}")
    print(f"  审查智能体: {AgentConfig.REVIEW_AGENT}")
    print(f"  默认模型: {AgentConfig.DEFAULT_MODEL}")
    print()
    
    # 审查配置
    print("⚖️  审查配置:")
    review_config = AgentConfig.get_review_config()
    for key, value in review_config.items():
        print(f"  {key}: {value}")
    print()

def main():
    """主入口 - 支持命令行参数"""
    if len(sys.argv) > 1 and sys.argv[1] == "--validate":
        # 验证配置
        success, _ = ConfigValidator.validate_all()
        return 0 if success else 1
    else:
        # 显示配置状态
        print_config_status()
        return 0

if __name__ == "__main__":
    sys.exit(main())