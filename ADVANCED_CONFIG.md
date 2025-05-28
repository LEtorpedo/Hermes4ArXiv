# 📚 高级配置指南

本文档提供详细的配置说明和自定义选项，适合需要个性化设置的用户。

> 💡 **快速部署**: 如果您只想快速开始，请参考 [README.md](README.md) 的快速入门指南，或运行 `python scripts/configure_analysis.py` 脚本生成推荐配置。

## ⚙️ 核心配置选项 (GitHub Secrets)

在您的仓库 `Settings → Secrets and variables → Actions` 中配置以下环境变量：

| 变量名             | 描述                                                                 | 选项 / 示例值                                    | 默认值           | 必需 |
|--------------------|----------------------------------------------------------------------|----------------------------------------------------|--------------------|------|
| `AI_PROVIDER`      | 选择AI服务提供商。                                                       | `"deepseek"`, `"openai"`, `"gemini"`               | `"deepseek"`       | 是   |
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 (若 `AI_PROVIDER="deepseek"`)。                       | `sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx`                  | -                  | 视情况 |
| `OPENAI_API_KEY`   | OpenAI API密钥 (若 `AI_PROVIDER="openai"`)。                         | `sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`      | -                  | 视情况 |
| `GEMINI_API_KEY`   | Gemini API密钥 (若 `AI_PROVIDER="gemini"`)。                         | `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`          | -                  | 视情况 |
| `EMAIL_TO`         | 接收分析报告的邮箱地址。支持多个邮箱，用逗号 `,` 分隔。                   | `user1@example.com,user2@example.com`              | -                  | 是   |
| `SMTP_USERNAME`    | 发送邮件报告的邮箱账户。                                                   | `your-email@gmail.com`                             | -                  | 是   |
| `SMTP_PASSWORD`    | 发送邮件报告的邮箱授权码 (例如Gmail的App Password)。                       | `yourapppassword`                                  | -                  | 是   |
| `DEEPSEEK_MODEL`   | DeepSeek 模型名称 (若 `AI_PROVIDER="deepseek"`)。                      | `"deepseek-chat"`, `"deepseek-coder"`              | `"deepseek-chat"`  | 否   |
| `OPENAI_MODEL`     | OpenAI 模型名称 (若 `AI_PROVIDER="openai"`)。                        | `"gpt-4"`, `"gpt-3.5-turbo"`                       | `"gpt-3.5-turbo"`| 否   |
| `GEMINI_MODEL`     | Gemini 模型名称 (若 `AI_PROVIDER="gemini"`)。                        | `"gemini-pro"`, `"gemini-1.5-pro-latest"`          | `"gemini-pro"`   | 否   |
| `ANALYSIS_TYPE`    | 分析报告的详细程度。                                                     | `"quick"`, `"comprehensive"`, `"detailed"`         | `"comprehensive"`| 否   |
| `MAX_PAPERS`       | 每次分析的最大论文数量。                                                   | `50`                                               | `50`               | 否   |
| `SEARCH_DAYS`      | 搜索最近N天的论文。                                                      | `2`                                                | `2`                | 否   |
| `CATEGORIES`       | ArXiv论文分类，用逗号分隔。                                                | `"cs.AI,cs.LG,cs.CL"`                              | `"cs.AI,cs.LG,cs.CL"` | 否   |
| `API_RETRY_TIMES`  | API请求失败时的重试次数。                                                  | `3`                                                | `3`                | 否   |
| `API_DELAY`        | API请求之间的延迟时间（秒），有助于避免频率限制。                             | `2`                                                | `2`                | 否   |
| `API_TIMEOUT`      | API请求的超时时间（秒）。                                                  | `60`                                               | `60`               | 否   |
| `ENABLE_PARALLEL`  | 是否启用并行处理以加快分析速度。                                             | `"true"`, `"false"`                                | `"true"`           | 否   |
| `MAX_WORKERS`      | 并行处理时使用的最大线程数。`0` 表示自动计算。                               | `4`                                                | `4`                | 否   |
| `BATCH_SIZE`       | （当前主要用于并行处理逻辑）并行分析时每个批次处理的论文数量。                   | `20`                                               | `20`               | 否   |
| `SMTP_SERVER`      | SMTP服务器地址。                                                         | `"smtp.gmail.com"`                                 | `"smtp.gmail.com"` | 否   |
| `SMTP_PORT`        | SMTP服务器端口。                                                         | `587`                                              | `587`              | 否   |
| `GITHUB_REPO_URL`  | 您的GitHub仓库URL，用于生成报告中的链接。                                  | `https://github.com/your-username/your-repo`     | (自动检测尝试)      | 否   |

**注意**:
*   根据您选择的 `AI_PROVIDER`，您**只需要配置对应的API密钥** (例如，如果 `AI_PROVIDER="openai"`，则只需配置 `OPENAI_API_KEY`)。
*   `必需`列指示该配置是否为系统运行的核心条件。`视情况`表示根据`AI_PROVIDER`的选择而定。

## 🤖 AI 服务提供商特定配置

### DeepSeek (`AI_PROVIDER="deepseek"`)
*   **`DEEPSEEK_API_KEY`**: 从 [DeepSeek Platform](https://platform.deepseek.com/) 获取。
*   **`DEEPSEEK_MODEL`**: 可选模型如 `"deepseek-chat"` (默认), `"deepseek-coder"`。
*   **文档**: [DeepSeek API 文档](https://platform.deepseek.com/docs)
*   **定价**: 通常性价比较高，具体请参考其官网。

### OpenAI (`AI_PROVIDER="openai"`)
*   **`OPENAI_API_KEY`**: 从 [OpenAI Platform](https://platform.openai.com/api-keys) 获取。
*   **`OPENAI_MODEL`**: 可选模型如 `"gpt-4"`, `"gpt-4-turbo-preview"`, `"gpt-3.5-turbo"` (默认)。
*   **文档**: [OpenAI Models Documentation](https://platform.openai.com/docs/models)
*   **定价**: [OpenAI Pricing](https://openai.com/pricing)

### Gemini (`AI_PROVIDER="gemini"`)
*   **`GEMINI_API_KEY`**: 从 [Google AI Studio](https://aistudio.google.com/app/apikey) 获取。
*   **`GEMINI_MODEL`**: 可选模型如 `"gemini-pro"` (默认), `"gemini-1.5-pro-latest"`.
*   **文档**: [Gemini API Documentation](https://ai.google.dev/docs/gemini_api_overview)
*   **定价**: [Gemini Pricing on Google Cloud](https://cloud.google.com/vertex-ai/pricing) (通常通过Vertex AI提供) 或 Google AI Studio 的免费额度。

## 🔬 分析类型详细配置

系统提供三种分析类型，您可以根据需求选择：

| 分析类型        | 字数范围  | 适用场景                                  | 优势                               | 适合用户                                     |
|-----------------|-----------|-------------------------------------------|------------------------------------|----------------------------------------------|
| `quick`         | 200-300字 | • 每日大量论文筛选<br>• 快速了解研究趋势<br>• 初步评估论文价值 | • 节省时间和成本<br>• 突出核心要点<br>• 便于快速决策 | • 需要处理大量论文的研究者<br>• 预算有限的用户<br>• 初级筛选需求 |
| `comprehensive` | 400-600字 | • 日常论文跟踪<br>• 周报和月报<br>• 平衡的分析需求       | • 信息全面均衡<br>• 可读性良好<br>• 性价比最优     | • 大多数研究者（推荐）<br>• 日常学术跟踪<br>• 平衡需求的团队 |
| `detailed`      | 600-900字 | • 重要论文深度分析<br>• 学术调研项目<br>• 决策支持分析     | • 技术细节丰富<br>• 深度洞察<br>• 专业评估       | • 资深研究者<br>• 深度技术分析<br>• 投资决策支持     |

### 🎯 推荐配置组合

**🔥 快速筛选模式**（大量论文初筛）：
```bash
AI_PROVIDER=deepseek # 或 openai/gemini
ANALYSIS_TYPE=quick
MAX_PAPERS=100
CATEGORIES=cs.AI,cs.LG,cs.CL,cs.CV
ENABLE_PARALLEL=true
MAX_WORKERS=8
```

**⭐ 日常跟踪模式**（推荐）：
```bash
AI_PROVIDER=deepseek # 或 openai/gemini
ANALYSIS_TYPE=comprehensive
MAX_PAPERS=50
CATEGORIES=cs.AI,cs.LG,cs.CL
ENABLE_PARALLEL=true
MAX_WORKERS=4
```

**🎓 深度研究模式**（精选论文）：
```bash
AI_PROVIDER=openai # 或 gemini/deepseek，可能选用更强模型
# OPENAI_MODEL=gpt-4 # 示例
ANALYSIS_TYPE=detailed
MAX_PAPERS=20
CATEGORIES=cs.AI,cs.LG
ENABLE_PARALLEL=true
MAX_WORKERS=2
```

### 💰 成本对比

| 分析类型        | 相对成本 (以DeepSeek为基准) | 10篇论文预估 (DeepSeek) | 50篇论文预估 (DeepSeek) |
|-----------------|---------------------------|-------------------------|-------------------------|
| `quick`         | 1x                        | ¥0.05-0.10              | ¥0.25-0.50              |
| `comprehensive` | 1.5x                      | ¥0.08-0.15              | ¥0.40-0.75              |
| `detailed`      | 2x                        | ¥0.10-0.20              | ¥0.50-1.00              |

**注意**: 使用OpenAI或Gemini的成本会根据所选模型有显著不同。请参考其官方定价页面。

### ⚙️ 如何配置分析类型
在GitHub Secrets中添加或修改 `ANALYSIS_TYPE` 变量。

## 📡 论文搜索配置

```bash
CATEGORIES=cs.AI,cs.LG,cs.CL       # ArXiv分类，支持多个，用逗号分隔
MAX_PAPERS=50                       # 每次分析论文数量
SEARCH_DAYS=2                       # 搜索最近N天的论文

# 常用分类组合示例:
# AI/ML核心: cs.AI,cs.LG,cs.CL
# AI扩展 (含CV, IR): cs.AI,cs.LG,cs.CL,cs.CV,cs.IR
# 计算机理论: cs.DS,cs.CC,cs.DM
# 计算机系统: cs.DC,cs.OS,cs.NI
```

## 🚀 性能优化

```bash
ENABLE_PARALLEL=true               
MAX_WORKERS=4                       # 并行线程数，0=自动计算
BATCH_SIZE=20                       # (当前主要用于并行处理逻辑) 批处理大小

# 性能建议：
# - 论文数量 < 10: ENABLE_PARALLEL=false 或 MAX_WORKERS=1
# - 论文数量 10-30: MAX_WORKERS=2-4
# - 论文数量 > 30: MAX_WORKERS=4-8 (取决于API提供商的速率限制)
```

## 📧 邮件配置

```bash
SMTP_SERVER=smtp.gmail.com          # Gmail示例
SMTP_PORT=587                       # Gmail示例
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=16-digit-app-password # Gmail应用专用密码

# Outlook示例
# SMTP_SERVER=smtp-mail.outlook.com
# SMTP_PORT=587
# SMTP_USERNAME=your-email@outlook.com
# SMTP_PASSWORD=your-password

# QQ邮箱示例
# SMTP_SERVER=smtp.qq.com
# SMTP_PORT=587 # 或 465 (SSL)
# SMTP_USERNAME=your-email@qq.com
# SMTP_PASSWORD=authorization-code    # QQ邮箱授权码
```
参考 [Gmail设置指南](docs/setup/GMAIL_SETUP_GUIDE.md) 获取详细帮助。

## 📊 成本和性能参考 (补充)

AI服务提供商的成本差异较大：
*   **DeepSeek**: 通常提供高性价比的选项。
*   **OpenAI**: 成本取决于模型 (e.g., GPT-3.5-Turbo vs GPT-4)。GPT-4成本显著高于GPT-3.5-Turbo。
*   **Gemini**: 成本也因模型而异 (e.g., Gemini Pro vs Gemini Ultra)。

建议查阅各服务商的最新定价页面，并从小规模测试开始，监控您的实际用量和费用。

## 🔍 结果查看

### 邮件报告
- HTML格式，支持移动端查看。
- 分析维度和评分标准可能因所选AI模型而略有不同。
- 自动发送到 `EMAIL_TO` 指定的邮箱。

### GitHub Actions日志
- **运行状态**: Actions页面查看每次运行结果。
- **详细日志**: 点击具体运行查看详细分析过程。
- **错误诊断**: 失败时查看具体错误信息。

## 🛠️ 详细故障排除

### AI 服务 API 问题

**API 密钥无效**
- 检查GitHub Secrets中对应 `AI_PROVIDER` 的API密钥是否正确复制。
- **DeepSeek**: 密钥通常以`sk-`开头。登录 [DeepSeek平台](https://platform.deepseek.com/) 验证。
- **OpenAI**: 密钥通常以`sk-`开头。登录 [OpenAI Platform](https://platform.openai.com/) 验证。
- **Gemini**: 检查API密钥是否在 [Google AI Studio](https://aistudio.google.com/app/apikey) 中有效。

**余额/额度不足**
- 登录相应AI服务提供商的平台查看账户余额和使用统计。
- 充值或检查免费额度。

**请求频率/速率限制**
API服务商通常有速率限制 (每分钟请求数, RPM; 每分钟token数, TPM)。如果遇到此类错误：
```bash
# 在GitHub Secrets中增加请求间隔
API_DELAY=5  # 增加到5秒或更高

# 减少并行数
MAX_WORKERS=2 # 或 1 (即串行)
```
查阅对应服务商的API文档了解具体的速率限制策略。

### 邮件发送问题
(内容与之前类似，保持不变)
...

### GitHub Actions 问题
(内容与之前类似，保持不变)
...

## 📝 GitHub Actions 最佳实践
(内容与之前类似，保持不变)
...

## 🔗 相关文档

- **AI服务商文档**:
  - [DeepSeek API 文档](https://platform.deepseek.com/docs)
  - [OpenAI API 文档](https://platform.openai.com/docs)
  - [Gemini API 文档](https://ai.google.dev/docs)
- [GitHub Actions 文档](https://docs.github.com/actions)
- [Gmail 应用密码设置](docs/setup/GMAIL_SETUP_GUIDE.md)