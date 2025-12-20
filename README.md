# ADK Companion

ADK 伴随智能体 - 基于 Google ADK 框架的元智能体，提供专家指导与自动进化能力。

## 项目愿景

构建一个基于 ADK (Agent Development Kit) 框架自身的"元智能体"，具备双重身份：

1. **领域专家 (The Expert)**：通过读取自身源码和文档，为开发者提供 ADK 框架的使用指导和代码解析
2. **进化工程师 (The Evolver)**：通过自动化工作流，实时追踪上游框架更新，自动升级依赖，并生成新特性的演示代码

## 功能特性

### 🧠 智能体能力

- **read_adk_codebase**: 在 ADK 源码中搜索关键词，提供代码解析
- **check_upstream_release**: 检查上游 ADK 仓库的最新发布版本
- **generate_evolution_pr**: 自动创建升级分支、更新依赖、生成示例代码并提交 PR

### 🚀 运行模式

- **交互态 (Interactive Mode)**: 通过 Web UI 与开发者对话，解答 ADK 使用问题
- **自动态 (Autonomous Mode)**: 通过 GitHub Actions 定时检查更新并自动进化

## 快速开始

### 环境要求

- Python 3.12+
- Google Cloud 项目（用于 Vertex AI）
- GitHub Token（用于 API 访问）

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/fgh23333/adk-companion.git
   cd adk-companion
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv .venv
   # Windows
   .\.venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置环境变量**
   ```bash
   cp .env.template .env
   # 编辑 .env 文件，填入你的配置
   ```

5. **启动服务**
   ```bash
   adk web
   ```

   访问 http://localhost:8000 使用 Web UI

### 环境变量配置

在 `.env` 文件中配置以下变量：

```env
# Google Cloud / Vertex AI 配置
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=us-central1

# GitHub API Token
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 可选配置
UPSTREAM_REPO=google/adk-python
```

### 获取配置值

- **Google Cloud Project ID**: 在 [GCP 控制台](https://console.cloud.google.com/) 顶部查看
- **GitHub Token**: 在 [GitHub Settings](https://github.com/settings/tokens) 生成 Personal Access Token
- **GCP 服务账号**: 在 IAM & Admin → Service Accounts 创建并下载 JSON 密钥

## 使用指南

### 作为专家助手

启动 Web UI 后，你可以询问：
- "如何在 ADK 中创建自定义工具？"
- "Agent 类的构造参数有哪些？"
- "给我看一个 ADK 的示例代码"

智能体会调用 `read_adk_codebase` 工具搜索相关源码并给出准确答案。

### 自动进化流程

1. **定时检查**: GitHub Actions 每日自动运行 `check_upstream_release`
2. **版本比对**: 检测到新版本时触发升级流程
3. **代码生成**: 使用 Vertex AI 生成新特性示例代码
4. **自动 PR**: 调用 `generate_evolution_pr` 创建升级 PR
5. **测试验证**: 自动运行测试，通过后合并

## 项目结构

```
adk-companion/
├── adk-companion/          # ADK 应用目录
│   ├── agent.py           # 主智能体定义
│   ├── tools.py           # 工具函数
│   └── .env              # 环境变量配置
├── samples/               # 示例代码
├── .github/workflows/     # CI/CD 配置
├── requirements.txt       # Python 依赖
├── .env.template         # 环境变量模板
└── README.md            # 项目文档
```

## 开发指南

### 本地开发

```bash
# 激活虚拟环境
.\.venv\Scripts\activate

# 安装开发依赖
pip install -r requirements.txt

# 运行开发服务器
adk web

# 或使用命令行模式
adk run
```

### 添加新工具

1. 在 `tools.py` 中定义新函数
2. 在 `agent.py` 中注册工具
3. 更新文档和测试

### 部署到生产环境

项目支持部署到 Google Cloud Run：

```bash
# 构建 Docker 镜像
docker build -t adk-companion .

# 推送到 Artifact Registry
gcloud builds submit --tag gcr.io/your-project/adk-companion

# 部署到 Cloud Run
gcloud run deploy adk-companion --image gcr.io/your-project/adk-companion
```

## 依赖清单

### 核心依赖
- `google-adk>=1.21.0` - ADK 框架
- `fastapi>=0.115.0,<0.124.0` - Web 框架
- `uvicorn>=0.22.0` - ASGI 服务器

### 工具依赖
- `requests>=2.31.0` - HTTP 请求
- `PyGithub>=2.8.0` - GitHub API 客户端
- `GitPython>=3.1.0` - Git 操作
- `python-dotenv>=1.0.0` - 环境变量管理
- `PyYAML>=6.0.0,<7.0.0` - YAML 配置解析

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 许可证

本项目采用 Apache 2.0 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 相关链接

- [ADK 官方文档](https://google.github.io/adk-docs/)
- [Google Cloud Vertex AI](https://cloud.google.com/vertex-ai)
- [GitHub Actions](https://github.com/features/actions)

## 支持

如有问题或建议，请：
- 创建 [Issue](https://github.com/fgh23333/adk-companion/issues)
- 发送邮件到 [your-email@example.com]
- 加入我们的 [Discord 社区](https://discord.gg/your-invite)