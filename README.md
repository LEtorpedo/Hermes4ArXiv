# Hermes4ArXiv - ArXiv论文自动追踪器
基于 GitHub Actions 的自动化工具，每日追踪和分析 ArXiv 最新论文，通过邮件发送分析报告。
推荐使用9b0efd5636d0c6aaff1a5873e8ccd049de4ec08c分支。新版过几周维护。

## 🚀 快速开始

1. **Fork 本仓库** 到您的GitHub账号

2. **设置必需密钥**：进入 Settings → Secrets and variables → Actions，添加（一条条添加）：
   ```
   # AI 模型配置（三选一，推荐Qwen）
   QWEN_API_KEY=your-qwen-api-key            # 推荐：阿里云通义千问API密钥
   QWEN_MODEL=qwen3-max                      # 可选：模型名称，默认为qwen3-max
   # 或者
   GLM_API_KEY=your-glm-api-key            # 推荐：智谱GLM API密钥
   # 或者
   DEEPSEEK_API_KEY=sk-your-api-key        # 备选：DeepSeek API密钥

   # 邮件配置
   SMTP_USERNAME=your-email@gmail.com      # 必需：发送邮箱
   SMTP_PASSWORD=your-app-password         # 必需：邮箱授权码
   EMAIL_TO=recipient@gmail.com            # 必需：接收邮箱(支持多人，用","隔开)
   
   # 🎛️ 可选：总开关控制（控制每日自动运行）
   ENABLE_DAILY_RUN=true                   # 可选：设置为false可暂停每日运行，默认为true
   ```

3. **启用Actions**：GitHub Actions 将每周一到周五北京时间7:00自动运行（周末自动跳过）

就是这么简单！系统将每日自动分析最新的AI/ML/NLP论文并发送邮件报告。

📖 **需要自定义配置？** 参见：[高级配置指南](ADVANCED_CONFIG.md)
🔑 **获取API密钥？**
- [Qwen配置指南](https://www.aliyun.com/product/dashscope) - 推荐，阿里云通义千问，成本低，性能好
- [智谱GLM配置指南](https://open.bigmodel.cn/) - 推荐，200K上下文窗口，128K输出tokens
- [DeepSeek配置指南](docs/setup/DEEPSEEK_SETUP_GUIDE.md) - 备选方案

📧 **邮箱设置问题？** 参见：[Gmail设置指南](docs/setup/GMAIL_SETUP_GUIDE.md)

## 🔧 主要功能

- **自动论文获取**：每日从 ArXiv 获取AI/ML/NLP领域最新论文
- **AI 智能分析**：支持阿里云通义千问、智谱GLM-4、DeepSeek等多种AI模型进行深度分析
- **邮件自动推送**：发送包含分析结果的简洁美观HTML邮件报告
- **GitHub Actions部署**：完全基于云端，无需本地环境

## 📊 AI 分析维度

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
| **搜索范围** | `今天发布` | 只查询当天论文，避免重复 |
| **分析详细度** | `全面分析` | 400-600字，平衡详细度和可读性 |
| **运行时间** | `周一至五 7:00` | 北京时间，周末自动跳过，可手动触发 |
| **总开关** | `ENABLE_DAILY_RUN` | 通过GitHub Secret控制，默认启用 |

**需要调整这些配置？** 参见 [高级配置指南](ADVANCED_CONFIG.md)

## 🕒 使用方式

- **自动运行**：每周一至五北京时间 7:00（GitHub Actions自动触发，周末休息）
- **手动运行**：Actions → Daily Paper Analysis → Run workflow  
- **暂停运行**：Settings → Secrets → 设置 `ENABLE_DAILY_RUN=false`
- **查看结果**：检查邮箱或仓库的运行日志

📖 **详细开关使用指南**：参见 [SWITCH_GUIDE.md](SWITCH_GUIDE.md)

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
- 检查AI API密钥是否正确设置（QWEN_API_KEY、GLM_API_KEY 或 DEEPSEEK_API_KEY）
- 确认AI服务账户有足够余额
- Qwen: https://www.aliyun.com/product/dashscope
- 智谱GLM: https://open.bigmodel.cn/
- DeepSeek: https://platform.deepseek.com/
- 查看Actions运行日志了解具体错误

**想要更多自定义？**
- 调整论文数量和分析详细度：[高级配置指南](ADVANCED_CONFIG.md)
- 添加更多研究领域：参见ArXiv分类说明
- 修改运行时间：编辑`.github/workflows/`文件

## 📚 详细文档

- [开关控制指南](SWITCH_GUIDE.md) - 如何暂停/启用每日运行，成本控制
- [评分优化分析](SCORING_ANALYSIS.md) - 评分虚高问题分析与解决方案
- [高级配置指南](ADVANCED_CONFIG.md) - 自定义分析类型、论文数量等
- [Qwen API配置](docs/setup/QWEN_SETUP_GUIDE.md) - 通义千问API密钥申请和配置
- [DeepSeek API配置](docs/setup/DEEPSEEK_SETUP_GUIDE.md) - API密钥申请和配置
- [Gmail邮箱设置](docs/setup/GMAIL_SETUP_GUIDE.md) - 邮箱授权码设置

## 🤝 贡献期待

欢迎提交Issue和Pull Request来改进项目！特别期待：

- 📧 **邮件模板优化** - 更美观的设计和移动端适配
- 🔧 **功能增强** - 支持更多邮箱服务商、可视化图表
- 📖 **文档完善** - 使用经验分享和故障排除案例，可以尝试更多邮箱和AI模型
- 💰 **节约成本** - 如果有进一步节约成本，或者在现有成本下优化结果的方法就更好了

## 📄 许可证

MIT License
