# GitHub Token 配置指南

ADK Companion 支持使用多个 GitHub Token 来实现不同智能体的独立操作。

## 🎯 设计目标

- **独立性**：PR审查智能体使用独立的Token，确保审查的客观性
- **安全性**：不同智能体使用不同权限的Token，降低安全风险
- **灵活性**：支持根据需要配置不同的Token策略

## 🔧 Token 配置

### 1. 默认Token (GITHUB_TOKEN)

用于主智能体的常规操作：
- 创建PR
- 读取仓库信息
- 基本的GitHub API操作

```bash
export GITHUB_TOKEN="your_main_github_token"
```

### 2. 审查专用Token (REVIEW_GITHUB_TOKEN)

用于PR审查智能体的专门操作：
- 审查PR
- 合并PR
- 请求审查
- 批准PR

```bash
export REVIEW_GITHUB_TOKEN="your_review_github_token"
```

## 🏗️ 架构设计

```
主智能体 (adk_companion)
├── 使用 GITHUB_TOKEN
├── 负责：创建PR、读取信息等
└── 工具：通用版本 (支持 token_env 参数)

审查智能体 (pr_reviewer)  
├── 使用 REVIEW_GITHUB_TOKEN
├── 负责：审查PR、合并决策等
└── 工具：专用版本 (_with_review_token 后缀)
```

## 📋 工具对比

| 功能 | 通用工具 | 审查专用工具 | 默认Token |
|------|----------|--------------|-----------|
| 检查PR作者 | `check_pr_author()` | `check_pr_author_with_review_token()` | GITHUB_TOKEN |
| 审查PR | `review_pr()` | `review_pr_with_review_token()` | GITHUB_TOKEN |
| 合并PR | `merge_pr()` | `merge_pr_with_review_token()` | GITHUB_TOKEN |
| 请求审查 | `request_pr_review()` | `request_pr_review_with_review_token()` | GITHUB_TOKEN |
| 列出PR | `list_prs()` | `list_prs_with_review_token()` | GITHUB_TOKEN |
| 智能审查 | `smart_review_pr()` | `smart_review_pr_with_review_token()` | GITHUB_TOKEN |

## 🚀 使用方式

### 方式1：使用通用工具（指定Token）

```python
from adk_companion.tools import smart_review_pr

# 使用默认Token
result = smart_review_pr("owner/repo", 123)

# 使用审查专用Token
result = smart_review_pr("owner/repo", 123, token_env="REVIEW_GITHUB_TOKEN")
```

### 方式2：使用专用工具（自动使用审查Token）

```python
from adk_companion.tools import smart_review_pr_with_review_token

# 自动使用 REVIEW_GITHUB_TOKEN
result = smart_review_pr_with_review_token("owner/repo", 123)
```

### 方式3：使用审查智能体

```python
from adk_companion.review_agent import review_agent

# 智能体自动使用专用工具和Token
# 所有操作都使用 REVIEW_GITHUB_TOKEN
```

## ⚙️ 配置管理

使用 `config.py` 模块管理配置：

```python
from config import TokenConfig, AgentConfig, print_config_status

# 检查Token状态
print_config_status()

# 验证Token
tokens = TokenConfig.validate_tokens()
print(tokens)

# 获取审查配置
review_config = AgentConfig.get_review_config()
```

## 🔍 最佳实践

### 1. Token权限分离

- **主Token**：需要 `repo` 权限用于创建PR
- **审查Token**：需要 `repo` + `pull_request:write` 权限用于审查和合并

### 2. 用户身份分离

建议使用不同GitHub账户的Token：
- 主Token：项目维护者账户
- 审查Token：另一位维护者或专门的审查账户

这样可以：
- 避免自己批准自己的PR
- 提供更客观的审查视角
- 分散权限风险

### 3. 权限最小化

根据实际需求分配最小必要权限：
- 只需要读取：使用 `public_repo` 权限
- 需要创建PR：使用 `repo` 权限
- 需要合并PR：使用 `repo` + `pull_request:write` 权限

## 🛠️ 故障排除

### 常见问题

1. **Token未设置**
   ```
   错误: 需要设置 REVIEW_GITHUB_TOKEN 环境变量
   解决: export REVIEW_GITHUB_TOKEN="your_token"
   ```

2. **权限不足**
   ```
   错误: 403 Forbidden
   解决: 检查Token权限设置
   ```

3. **自己批准自己PR**
   ```
   错误: Review Can not approve your own pull request
   解决: 使用不同用户的Token
   ```

### 调试方法

```python
# 检查Token信息
from config import TokenConfig
print(TokenConfig.get_token_info())

# 检查当前用户
from adk_companion.tools import check_pr_author_with_review_token
result = check_pr_author_with_review_token("owner/repo", 123)
print(f"当前用户: {result.get('current_user')}")
```

## 📝 示例配置

### 开发环境

```bash
# ~/.bashrc 或 ~/.zshrc
export GITHUB_TOKEN="ghp_xxx_main_token"
export REVIEW_GITHUB_TOKEN="ghp_xxx_review_token"
```

### 生产环境

```bash
# 环境变量或密钥管理服务
GITHUB_TOKEN=ghp_xxx_main_token
REVIEW_GITHUB_TOKEN=ghp_xxx_review_token
```

### Docker环境

```dockerfile
ENV GITHUB_TOKEN=ghp_xxx_main_token
ENV REVIEW_GITHUB_TOKEN=ghp_xxx_review_token
```

## 🔐 安全建议

1. **定期轮换Token**：建议每3-6个月更换一次
2. **使用IP限制**：在GitHub设置中限制Token的IP访问范围
3. **监控使用情况**：定期检查Token的使用日志
4. **最小权限原则**：只授予必要的权限
5. **安全存储**：使用安全的密钥管理服务存储Token

## 📚 相关文档

- [GitHub Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [GitHub Permissions](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps)
- [ADK Companion 使用指南](README.md)