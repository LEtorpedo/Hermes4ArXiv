# Hermes4ArXiv - ArXiv论文自动追踪器
基于 GitHub Actions 的自动化工具，每日追踪和分析 ArXiv 最新论文，通过邮件发送分析报告。

## 🚀 快速开始

1. **Fork 本仓库** 到您的GitHub账号

2. **设置环境变量和密钥**：进入仓库的 Settings → Secrets and variables → Actions，添加以下配置：

   **核心配置:**
   ```
   AI_PROVIDER=deepseek                       # AI服务提供商: "deepseek", "openai", "gemini" (默认为 "deepseek")
   # 根据选择的 AI_PROVIDER，配置对应的 API Key:
   DEEPSEEK_API_KEY=YOUR_DEEPSEEK_API_KEY     # (若使用 DeepSeek) 您的 DeepSeek API 密钥
   OPENAI_API_KEY=YOUR_OPENAI_API_KEY         # (若使用 OpenAI) 您的 OpenAI API 密钥
   GEMINI_API_KEY=YOUR_GEMINI_API_KEY         # (若使用 Gemini) 您的 Gemini API 密钥

   EMAIL_TO=recipient@example.com             # 必需：接收报告的邮箱 (支持多个, 用 "," 分隔)
   SMTP_USERNAME=your-email@example.com       # 必需：发送报告的邮箱地址
   SMTP_PASSWORD=your-email-app-password      # 必需：发送邮箱的授权码 (例如Gmail的App Password)
   ```
   > **注意**: 您只需要配置所选 `AI_PROVIDER` 对应的 `API_KEY`。

3. **启用Actions**：GitHub Actions 将每日北京时间8:00自动运行。

就是这么简单！系统将每日自动分析最新的AI/ML/NLP论文并发送邮件报告。

📖 **需要自定义配置？** 运行 `python scripts/configure_analysis.py` 生成推荐配置，或手动参考 [高级配置指南](ADVANCED_CONFIG.md)。  
🔑 **获取API密钥？** 参考 [高级配置指南](ADVANCED_CONFIG.md) 中各AI服务商的说明。  
📧 **邮箱设置问题？** 参见：[Gmail设置指南](docs/setup/GMAIL_SETUP_GUIDE.md)。

## 🌟 主要功能

- **自动论文获取**：每日从 ArXiv 获取用户指定领域的最新论文。
- **多AI模型支持**：可选择 DeepSeek, OpenAI (GPT系列), Google Gemini进行论文分析。
- **智能分析**：对论文进行多维度分析和质量评估。
- **邮件自动推送**：发送包含分析结果的精美HTML邮件报告。
- **GitHub Actions部署**：完全基于云端，无需本地环境。
- **高度可配置**：支持自定义论文领域、数量、分析深度、AI模型等。
- **AI 智能分析**：使用 DeepSeek 对论文进行深度分析和质量评估 (注: 分析维度和评分标准可能因选用AI模型而异)
- **邮件自动推送**：发送包含分析结果的精美HTML邮件报告
- **GitHub Actions部署**：完全基于云端，无需本地环境

## 📊 AI 分析维度 (以DeepSeek为例, 其他模型可能有所不同)

- **质量评分**：5星评分系统（严格学术标准，避免虚高评分）
- **创新程度**：突破性/渐进性/跟随性
- **技术严谨性**：严谨/良好/一般
- **实用价值**：高/中/低
- **研究意义**：全面技术和应用价值分析
- **方法总结**：核心方法和技术路线解读

> 💡 **评分说明**：系统采用严格学术标准，5星极其稀少，4星以上需明确技术突破，大多数论文在2-3星之间

## ⚙️ 默认配置

| 配置项 | 默认值 | 说明 |
|-------|--------|------|
| **分析领域** | `cs.AI,cs.LG,cs.CL` | AI、机器学习、自然语言处理 |
| **论文数量** | `50篇` | 每次分析的论文数量 |
| **搜索范围** | `最近2天` | 获取最新论文 |
| **分析详细度** | `全面分析` | 400-600字，平衡详细度和可读性 |
| **运行时间** | `每日8:00` | 北京时间，可手动触发 |

**需要调整这些配置？** 参见 [高级配置指南](ADVANCED_CONFIG.md)

## 🕒 使用方式

- **自动运行**：每日北京时间 8:00（GitHub Actions自动触发）
- **手动运行**：Actions → Daily Paper Analysis → Run workflow  
- **查看结果**：检查邮箱或仓库的运行日志

## 🔐 安全说明

- API密钥通过 GitHub Secrets 加密存储
- 分析结果仅保存在您的Fork仓库中
- 所有敏感信息在日志中自动脱敏

## 🛠️ 常见问题

**没收到邮件？**
- 检查垃圾邮件文件夹
- 确认Gmail启用两步验证并使用应用专用密码
- 验证接收邮箱地址正确

**Actions运行失败？**
- 检查API密钥是否正确设置 (对应您选择的 `AI_PROVIDER`)
- 确认AI服务商账户有足够余额/额度
- 查看Actions运行日志了解具体错误

**想要更多自定义？**
- 调整论文数量和分析详细度：[高级配置指南](ADVANCED_CONFIG.md)
- 添加更多研究领域：参见ArXiv分类说明
- 修改运行时间：编辑`.github/workflows/`文件

## 📚 详细文档

- [高级配置指南](ADVANCED_CONFIG.md) - 自定义AI提供商、模型、分析类型、论文数量等
- [Gmail邮箱设置](docs/setup/GMAIL_SETUP_GUIDE.md) - 邮箱授权码设置

## 🤝 贡献期待

欢迎提交Issue和Pull Request来改进项目！特别期待：

- 📧 **邮件模板优化** - 更美观的设计和移动端适配
- 🔧 **功能增强** - 支持更多邮箱服务商、可视化图表
- 📖 **文档完善** - 使用经验分享和故障排除案例，可以尝试更多邮箱和AI模型
- 💰 **节约成本** - 如果有进一步节约成本，或者在现有成本下优化结果的方法就更好了

## 📄 许可证

MIT License