````markdown
# File Commander AI

基于 Google ADK (Agent Development Kit) 框架开发的智能本地文件管理与扫描 Agent。

## 历史成果总结 (截至最新迭代)

本项目近期已成功实现以下核心技术特性：

### 1. Google ADK Agent 基础架构搭建
*   **标准化技能划分**：在项目根目录构建了遵循 ADK 规范的项目结构，建立了专属的 `file_scanner` Skill。
*   **元数据配置**：规范化编写了 `SKILL.md`，定义了文件遍历、本地数据库交互（PostgreSQL）及安全边界的指令边界（Instruction）。
*   **开发环境支撑**：全量集成与部署了 `google-adk[extensions]` 工具链及所有相关依附组件。

### 2. 深度本地文件扫描能力 (`src/files_scan.py`)
经过多轮迭代与优化，实现了一个强健兼具容错能力的本地（如 `J:\` 盘）文件扫描脚本，核心特性包括：
*   **SHA-256 哈希计算**：引入原生 `hashlib` 模块对文件计算 SHA-256 唯一指纹，为去重和高级归档奠定数据基础。
*   **异常捕获与中断保护机制**：能够在极其冗长的磁盘扫描过程中，随时响应 `Ctrl+C` (KeyboardInterrupt) 并即时将内存中已扫描完毕的文件数据落盘至 `scan_results.json`，确保进度不丢失。
*   **热加载断点续传**：每次启动扫描时智能解析上次运行的 `.json` 缓存，在遇到已存在且未被修改过的文件时，直接从本地缓存热加载其数据与哈希值，极大降低了对 CPU 的算力消耗，提升了复用效率。

## 快速开始

1. **依赖安装**
   建议在支持的虚拟环境 (Python 3.12+) 中安装包含全部扩展的 ADK 工具套件以驱动大语言模型后端：
   ```bash
   uv pip install "google-adk[extensions]"
   ```
2. **执行扫描**
   通过终端进行独立扫描测试，支持直接传递具体盘符（例如扫描整块 J 盘并开启哈希计算去重能力）：
   ```bash
   python skills/file_scanner/tools.py J:\ --hash
   ```

## 项目文件组织结构 (Project Structure)

当前项目由以下主要文件夹和核心文件组成：

*   **`skills/`**: ADK Agent 技能定义目录，包含不同能力模块。
    *   `file_scanner/`: 负责文件扫描和哈希计算的技能指令与执行逻辑。
    *   `file_organizer/`: 文件归档管理相关技能。
    *   `file_renamer/`: 文件重命名处理技能。
*   **`src/`**: 核心源代码主目录。包含数据库连接 (`database.py`)、实体模型 (`models.py`)、AI分类代理 (`ai_classifier.py`) 以及多种底层扫描、备份等执行脚本。
*   **`scripts/`**: 独立实用的业务流处理脚本，如智能图纸组织 (`smart_organizer.py`)、规范标准整理 (`standard_organizer.py`) 及其配置文件。
*   **`models/`**: 本地大模型文件存放或模型参数相关配置目录。
*   **`test_openai_env/`**: 测试与调试脚本目录，专门用于测试验证语言模型 API 端点 (如兼容 OpenAI 格式的接口测试 JS/MJS 脚本)。
*   **`tests/`**: 一般性单元测试与集成测试代码目录。
*   **`frontend.html`**: 项目自带的简易前端可视化交互界面。
*   **`file_query.sql`**: 用于快速直接从本地 PostgreSQL 数据库中提取、测试或分析数据的 SQL 脚本。
*   **`start_llm_server.ps1`**: 用于一键启动本地 LLM 推理服务的 PowerShell 脚本。
*   **`requirements.txt` / `environment.yml`**: Python 项目及 Conda 环境的核心依赖声明文件。

## 如何使用

下面说明如何在本地环境快速运行与使用该应用：

1. 环境准备
   - 建议使用 Python 3.10+，并在项目根目录创建虚拟环境：
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - 安装依赖：
     ```powershell
     pip install -r requirements.txt
     # 或者使用 conda
     conda env create -f environment.yml
     conda activate <env-name>
     ```

2. 配置模型与数据目录
   - 将本地模型文件放入 `models/` 目录（如已有 gguf 模型文件）。
   - 如需连接数据库，请根据 `src/database.py` 中的配置修改环境变量或 `environment.yml` 中的连接信息（Postgres）。

3. 启动本地 LLM 推理服务（可选）
   - 若使用项目中的推理脚本或本地服务，运行：
     ```powershell
     .\start_llm_server.ps1
     ```

4. 运行核心脚本
   - 扫描文件并生成哈希/索引（示例）：
     ```powershell
     python src/files_scan.py --path "J:\" --hash
     ```
   - 使用技能脚本：
     ```powershell
     python skills/file_scanner/tools.py J:\ --hash
     ```
   - 运行主程序（示例）：
     ```powershell
     python src/main.py
     ```

5. 常见操作
   - 查看可用脚本：检查 `scripts/` 与 `skills/` 下的各子模块
   - 测试模型兼容性：参见 `test_openai_env/` 中的测试脚本

6. 日志与调试
   - 运行时日志会输出到控制台，同时可查看 `debug_log.txt` 以获取历史调试信息。

7. 贡献与开发
   - 新增功能或修复请在 feature 分支完成后提交 PR；确保现有单元测试通过并补充必要测试。

````
