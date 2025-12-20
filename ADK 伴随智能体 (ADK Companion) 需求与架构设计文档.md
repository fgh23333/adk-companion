# **ADK 伴随智能体 (ADK Companion) 需求与架构设计文档**

版本: v1.2  
日期: 2025-05-20  
目标环境: Python 3.12, GitHub Actions, Google ADK Framework, Google Cloud Run

## **1\. 项目愿景**

构建一个基于 ADK (Agent Development Kit) 框架自身的“元智能体”。它具备双重身份：

1. **领域专家 (The Expert)**：通过读取自身源码和文档，为开发者提供 ADK 框架的使用指导和代码解析。  
2. **进化工程师 (The Evolver)**：通过自动化工作流，实时追踪上游框架更新，自动升级依赖，并生成新特性的演示代码，实现“自我迭代”。

## **2\. 核心架构设计**

系统采用 **“双模态”** 运行机制，分别应对交互需求和运维需求。

### **2.1 交互态 (Interactive Mode) \- 专家模式**

此模式用于与开发者进行日常对话，解答问题。

* **本地开发 (Development)**：  
  * **启动方式**：利用 ADK 原生命令 adk web 启动，快速调试 Prompt 和 Tools。  
  * **运行环境**：Localhost。  
* **生产部署 (Production)**：  
  * **启动方式**：基于 Docker 容器运行，通过 GitHub Actions 自动构建并发布。  
  * **运行环境**：**Google Cloud Run** (Serverless, Auto-scaling)。  
  * **部署机制**：GitOps 流程，代码推送到 main 分支自动触发构建与部署。  
* **核心逻辑**：  
  * 用户在 Web UI 提问。  
  * 智能体调用 **read\_local\_source** 工具，扫描项目内的 site-packages/google/adk 源码或 samples/ 目录。  
  * 智能体基于最新源码回答问题，避免幻觉。

### **2.2 自动态 (Autonomous Mode) \- 进化模式**

此模式用于后台自动维护和升级。

* **启动方式**：由 **GitHub Actions** 定时触发 (Cron Job)。  
* **运行环境**：GitHub Runner (Ubuntu-latest)。  
* **核心逻辑**：  
  * **监听**：轮询上游仓库状态。  
  * **决策**：判断是否需要升级。  
  * **执行**：生成代码 \-\> 提交 PR \-\> (可选) 自动合并。

## **3\. 详细功能需求**

### **3.1 智能体能力定义 (Agent Capabilities)**

智能体需挂载以下工具 (Tools) 以具备感知和行动能力：

#### **A. 感知类工具**

1. **check\_upstream\_release**  
   * **输入**：无（目标仓库硬编码为 google/adk-python）。  
   * **输出**：最新版本号 (Tag)、发布时间、Release Body (更新日志)。  
   * **逻辑**：调用 GitHub API 获取 Latest Release 信息。  
2. **read\_adk\_codebase**  
   * **输入**：搜索关键词或文件路径。  
   * **输出**：文件内容片段。  
   * **逻辑**：提供对本地安装的 ADK 库文件的读取权限，赋予 Agent “白盒”视角。

#### **B. 行动类工具**

3. **generate\_evolution\_pr**  
   * **输入**：目标版本号、新生成的 Sample 代码内容、依赖变更说明。  
   * **输出**：PR 链接。  
   * **逻辑**：  
     1. 创建新分支 chore/upgrade-to-{version}。  
     2. 更新 requirements.txt 或 pyproject.toml。  
     3. 将 Sample 代码写入 samples/new\_feature\_{version}.py。  
     4. 提交更改并推送。  
     5. 创建 Pull Request。

### **3.2 自动化工作流 (CI/CD Pipeline)**

#### **A. 进化流水线 (auto-evolve.yml)**

负责检测更新并提交代码变更。

* **触发**：定时 (Cron) 或 手动 (Workflow Dispatch)。  
* **逻辑**：比对版本 \-\> 生成代码 (Vertex AI) \-\> 提交 PR。

#### **B. 部署流水线 (deploy-cloud-run.yml)**

负责将最新的智能体部署到生产环境。

* **触发**：main 分支的代码推送 (Push) 或 PR 合并。  
* **逻辑**：  
  1. **Build**：构建 Docker 镜像 (包含最新的 ADK 依赖和 Sample 代码)。  
  2. **Push**：推送到 Google Artifact Registry。  
  3. **Deploy**：部署到 Cloud Run 服务，更新对外服务的版本。

#### **C. 自动合并策略**

* **前提**：仓库设置中需开启 "Allow auto-merge"。  
* **安全网**：PR 创建后，立即触发 **Test Workflow**，尝试运行新生成的 Sample 代码。  
* **合并动作**：只有当 Test 成功 (exit code 0\) 且 Cloud Run 预构建通过时，才执行自动合并。

## **4\. 基础设施与配置清单**

### **4.1 必须拥有的账号与凭证**

| 资源名称 | 用途 | 权限要求 | 配置位置 |
| :---- | :---- | :---- | :---- |
| **GCP Project** | 运行 Gemini 模型 & Cloud Run | 启用 Vertex AI API, Cloud Run API, Artifact Registry API | 环境变量 |
| **GCP Service Account** | CI/CD 部署 & 运行时身份 | 角色：Vertex AI User, Cloud Run Developer, Service Account User | GitHub Secrets (GCP\_CREDENTIALS) |
| **GitHub Repo** | 托管代码 | Admin (用于开启 PR 相关设置) | \- |
| **GitHub PAT** | 机器人操作 GitHub | Scopes: repo, workflow | GitHub Secrets (PAT\_TOKEN) |

### **4.2 本地开发环境规范**

* **Language**: Python **3.12** (严格匹配需求)。  
* **Package Manager**: pip 或 poetry。  
* **Framework**: google-adk (最新版)。  
* **CLI**: gcloud sdk (用于本地鉴权)。

## **5\. 实施路线图 (Step-by-Step)**

### **阶段一：搭建“专家” (Day 1\)**

1. **项目初始化**：创建符合 ADK 规范的目录结构 (agent.py, tools.py)。  
2. **工具实现**：编写 read\_adk\_codebase 工具，确保它能正确找到 Python 3.12 环境下的 site-packages 目录。  
3. **本地验证**：使用 adk web . 启动，询问 Agent 源码细节，确认回答准确。

### **阶段二：配置生产部署 (Day 2\)**

1. **Dockerfile 编写**：创建一个轻量级 Dockerfile，基于 python:3.12-slim，安装依赖并设置启动命令（例如 uvicorn 或 ADK 推荐的生产启动方式）。  
2. **GCP 基础设施**：在 GCP 上创建 Artifact Registry 仓库和 Cloud Run 服务占位。  
3. **CI/CD 配置**：编写 GitHub Action (deploy.yml)，实现 git push \-\> Cloud Run 的自动部署。

### **阶段三：实现“进化”逻辑 (Day 3\)**

1. **脚本编写**：编写 scripts/check\_update.py，实现版本比对、Gemini 代码生成和 Git 操作。  
2. **进化流水线**：配置 GitHub Action (auto-evolve.yml) 定时运行该脚本。  
3. **闭环测试**：手动触发进化流水线，观察是否生成了 PR；合并 PR，观察是否触发了部署流水线更新 Cloud Run。

## **6\. 风险控制与兜底方案**

1. **代码生成失败**：  
   * *现象*：Gemini 生成的代码有语法错误。  
   * *对策*：在自动化流程中加入 ast.parse(code) 检查。如果语法解析失败，放弃本次自动合并，转为 Draft PR 等待人工修复。  
2. **部署失败**：  
   * *现象*：新版本导致 Cloud Run 启动失败。  
   * *对策*：Cloud Run 原生支持版本回滚。CI/CD 脚本中可配置健康检查，若新版本 Unhealthy 则自动回滚到上一个 Revision。