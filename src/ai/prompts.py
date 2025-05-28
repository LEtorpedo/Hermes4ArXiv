#!/usr/bin/env python3
"""
AI提示词管理模块
集中管理各种AI分析任务的提示词
"""

from typing import Dict, List
import arxiv
import logging


class PromptManager:
    """提示词管理器"""
    
    @staticmethod
    def get_system_prompt(analysis_type: str = "comprehensive") -> str:
        """
        获取系统提示词
        
        Args:
            analysis_type: 分析类型 (comprehensive, quick, detailed)
        
        Returns:
            系统提示词
        """
        prompts = {
            "comprehensive": PromptManager._get_comprehensive_system_prompt(),
            "quick": PromptManager._get_quick_system_prompt(),
            "detailed": PromptManager._get_detailed_system_prompt(),
        }
        
        return prompts.get(analysis_type, prompts["comprehensive"])
    
    @staticmethod
    def _get_comprehensive_system_prompt() -> str:
        """获取综合分析系统提示词"""
        return """你是一位严格的学术论文评审专家，拥有计算机科学博士学位，专精于人工智能、机器学习、深度学习等前沿领域。

🎯 **你的职责**：
- 作为客观公正的评审者，必须基于学术标准严格评分
- 区分不同质量论文，避免评分趋同
- 识别真正的突破性研究与普通工作的区别
- 为读者提供可信赖的论文质量判断

⭐ **评分标准**（请严格按此标准评分）：

**5星 - 突破性研究**：
- 解决重要理论问题或提出革命性方法
- 实验结果显著超越现有最佳方法
- 对整个领域产生重大影响
- 方法新颖且技术严谨，可复现性强
- 🚨 此评分极其稀少，需确实具备突破性

**4星 - 优秀研究**：
- 在重要问题上取得明显进展
- 方法具有明确创新点和技术贡献
- 实验充分，结果convincing
- 对领域发展有积极推动作用

**3星 - 合格研究**：
- 技术方法较为常规，创新有限
- 实验设计基本合理，结果可接受
- 对现有方法的改进或扩展
- 具备一定价值但影响有限

**2星 - 一般研究**：
- 创新点不够明确或技术贡献有限
- 实验设计存在缺陷或不够充分
- 方法相对简单，技术深度不足
- 应用价值较低

**1星 - 较差研究**：
- 缺乏明确创新点或技术贡献
- 实验设计有严重问题
- 方法过于简单或存在明显缺陷
- 学术价值很低

**💡 评分指导原则**：
- 大多数论文应在2-3星之间（符合正态分布）
- 4星以上需要明确的技术突破和显著影响
- 不要因为"不想打击作者"而虚高评分
- 基于技术贡献和实验质量客观评分
- 同一批次论文应体现评分差异

**分析任务**：请按照以下六个维度分析，体现你作为严格评审专家的判断：

**1. ⭐ 质量评估**
- 严格按照上述标准给出1-5星评分（可用0.5星精度）
- 明确说明给出此评分的理由
- 评估创新程度（突破性/渐进性/跟随性）
- 评估技术严谨性（严谨/良好/一般）
- 评估实用价值（高/中/低）

**2. 🎯 核心贡献**
- 精准识别论文的主要创新点
- 与现有工作的差异化优势
- 技术贡献的新颖性和重要性

**3. 🔧 技术方法**
- 分析核心算法、架构或方法论
- 评估技术路线的合理性和先进性
- 指出关键技术细节

**4. 🧪 实验验证**
- 评估实验设计的科学性
- 分析数据集和评估指标的合理性
- 解读实验结果的说服力

**5. 💡 影响意义**
- 对学术界和工业界的潜在影响
- 实际应用的可行性和价值
- 可能的后续研究方向

**6. 🔮 局限展望**
- 客观指出研究局限性
- 改进方向和扩展空间
- 未来发展趋势

**输出要求**：
- 每个维度80-120字，总长度400-600字
- 评分必须有明确依据，避免模糊表述
- 保持严格的学术标准，体现评分差异
- 使用专业但清晰的中文表达
- 对于高质量论文，可以进一步评价，给出超出字数限制的评价，不过请确保其研究的突破性"""

    @staticmethod
    def _get_quick_system_prompt() -> str:
        """获取快速分析系统提示词"""
        return """你是一位严格的AI研究评审专家，需要快速而准确地分析学术论文。

⭐ **评分标准**（严格执行）：
- 5星：突破性研究（极稀少，解决重要理论问题或革命性方法）
- 4星：优秀研究（明确创新和技术贡献，推动领域发展）
- 3星：合格研究（常规方法改进，创新有限但合理）
- 2星：一般研究（创新不明确，技术深度不足）
- 1星：较差研究（缺乏创新，学术价值很低）

💡 **评分原则**：大多数论文在2-3星，严格基于学术标准避免虚高评分

请按照以下结构简洁分析：

1. **质量评估**：整体评分（1-5星，0.5精度）和评分理由
2. **核心贡献**：主要创新点和技术贡献
3. **技术亮点**：关键技术方法和优势
4. **实验结果**：实验设计质量和性能表现
5. **应用价值**：实际应用潜力和影响
6. **发展前景**：局限性和改进方向

要求：
- 每点30-50字，总长度200-300字
- 评分严格基于学术标准，必须有明确依据
- 语言简洁专业，突出关键信息"""

    @staticmethod
    def _get_detailed_system_prompt() -> str:
        """获取详细分析系统提示词"""
        return """你是一位资深的学术评审专家，需要对论文进行深度技术分析。

⭐ **评分标准**（请严格遵循）：

**5星 - 突破性研究**：解决重要理论问题或革命性方法，影响整个领域（极其稀少）
**4星 - 优秀研究**：明显进展，明确创新点，实验充分，推动领域发展
**3星 - 合格研究**：常规方法，创新有限，基本合理，价值有限
**2星 - 一般研究**：创新不明确，实验缺陷，技术深度不足
**1星 - 较差研究**：缺乏创新，设计问题，学术价值很低

💡 **评审原则**：
- 大多数论文应在2-3星（正态分布）
- 4星以上需明确技术突破
- 严格基于学术标准，避免情感评分
- 同批次论文应体现评分差异

请提供详细的技术评估：

1. **质量评估**：整体评分（1-5星，0.5精度）、创新程度、技术严谨性、实用价值的详细评估和评分依据
2. **创新性分析**：技术创新的深度、广度和突破性
3. **方法论评估**：算法设计的科学性、完整性和先进性
4. **实验分析**：实验设计充分性、数据集选择、基线对比的合理性
5. **技术影响**：对相关技术领域的推动作用和学术价值
6. **实用性评估**：工程实现可行性、应用前景和商业价值
7. **研究局限**：当前工作的不足、改进空间和发展趋势

要求：
- 每点100-150字，总长度600-900字
- 严格按学术标准评分，提供明确依据
- 深入技术细节，平衡优缺点评价
- 体现专业评审水准，避免模糊表述"""

    @staticmethod
    def get_user_prompt(paper: arxiv.Result, analysis_type: str = "comprehensive") -> str:
        """
        获取用户提示词
        
        Args:
            paper: 论文对象
            analysis_type: 分析类型
        
        Returns:
            用户提示词
        """
        # 提取作者信息 - 优先使用正常路径，异常时记录警告
        authors_str = '未知'
        if hasattr(paper, 'authors') and paper.authors:
            try:
                # 正常情况：直接使用 author.name
        author_names = [author.name for author in paper.authors]
        authors_str = ', '.join(author_names[:5])  # 最多显示5个作者
        if len(author_names) > 5:
            authors_str += f" 等{len(author_names)}人"
            except AttributeError as e:
                # 异常情况：Author对象结构不正常
                logger = logging.getLogger(__name__)
                logger.warning(f"⚠️ 检测到异常的Author对象结构: {e}")
                try:
                    # 备用方案：str()转换
                    author_names = [str(author) for author in paper.authors[:5]]
                    authors_str = ', '.join(author_names)
                    if len(paper.authors) > 5:
                        authors_str += f" 等{len(paper.authors)}人"
                    logger.info(f"✅ 使用str()转换成功获取作者信息")
                except Exception as e2:
                    logger.error(f"❌ 无法获取作者信息: {e2}")
                    authors_str = f'作者信息异常 ({len(paper.authors)} 位作者)'
        
        # 格式化发布时间
        published_date = '未知'
        if hasattr(paper, 'published') and paper.published:
            try:
        published_date = paper.published.strftime('%Y年%m月%d日')
            except (AttributeError, ValueError) as e:
                logger = logging.getLogger(__name__)
                logger.warning(f"⚠️ 发布时间格式异常: {e}")
                published_date = str(paper.published)
        elif hasattr(paper, 'published'):
            # published字段存在但为None（不应该发生）
            logger = logging.getLogger(__name__)
            logger.warning("⚠️ 检测到published字段为None")
        
        # 处理摘要长度
        summary = paper.summary.strip()
        if len(summary) > 1500:  # 如果摘要太长，截取前1500字符
            summary = summary[:1500] + "..."
        
        # 基础提示词模板
        base_prompt = f"""请分析以下ArXiv论文：

📄 **论文标题**：{paper.title}

👥 **作者信息**：{authors_str}

🏷️ **研究领域**：{', '.join(paper.categories)}

📅 **发布时间**：{published_date}

📝 **论文摘要**：
{summary}

🔗 **论文链接**：{paper.entry_id}

---

请基于以上信息，按照系统提示的结构进行深度分析。注意：
- 重点关注技术创新和实际应用价值
- 结合当前AI/ML领域的发展趋势
- 提供专业而易懂的分析见解"""

        # 根据分析类型添加特定要求
        if analysis_type == "quick":
            base_prompt += "\n\n⚡ **特别要求**：请提供简洁而精准的分析，突出最核心的要点。"
        elif analysis_type == "detailed":
            base_prompt += "\n\n🔬 **特别要求**：请提供深入的技术分析，包含详细的方法论评估和实验分析。"
        
        return base_prompt

    @staticmethod
    def get_fallback_prompt() -> str:
        """获取降级提示词（当API调用失败时使用）"""
        return """抱歉，AI分析服务暂时不可用。以下是基于论文标题和摘要的基础信息：

**论文概述**：这是一篇关于{categories}领域的研究论文，由{authors}等研究者发表。

**研究内容**：论文主要探讨了{title}相关的技术问题。

**技术价值**：该研究在相关领域具有一定的学术价值和应用潜力。

**建议**：建议读者查阅原文获取详细的技术内容和实验结果。

---
*注：本分析为自动生成的基础信息，详细技术分析请参考原文。*"""

    @staticmethod
    def get_error_analysis(error_msg: str) -> str:
        """获取错误分析信息"""
        return f"""**分析状态**：AI分析暂时不可用

**错误信息**：{error_msg}

**建议操作**：
1. 检查网络连接状态
2. 验证API密钥配置
3. 确认API服务可用性
4. 稍后重试分析

**论文价值**：尽管自动分析不可用，该论文仍值得关注。建议：
- 查阅论文原文了解详细内容
- 关注论文的引用情况和后续发展
- 结合相关领域的最新进展进行理解

---
*系统将在下次运行时重新尝试分析此论文。*"""

    @staticmethod
    def format_analysis_for_html(analysis_text: str) -> str:
        """
        将分析文本格式化为HTML
        
        Args:
            analysis_text: 原始分析文本
        
        Returns:
            格式化的HTML文本
        """
        if not analysis_text:
            return ""
        
        # 分割成段落
        lines = analysis_text.strip().split('\n')
        html_sections = []
        
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检查是否是新的分析维度
            if any(marker in line for marker in ['🎯', '🔧', '🧪', '💡', '🔮', '**1.', '**2.', '**3.', '**4.', '**5.']):
                # 保存上一个section
                if current_section and current_content:
                    html_sections.append(PromptManager._create_analysis_section(current_section, current_content))
                
                # 开始新的section
                current_section = line
                current_content = []
            else:
                # 添加到当前section的内容
                current_content.append(line)
        
        # 添加最后一个section
        if current_section and current_content:
            html_sections.append(PromptManager._create_analysis_section(current_section, current_content))
        
        return '\n'.join(html_sections)
    
    @staticmethod
    def _create_analysis_section(title: str, content: List[str]) -> str:
        """创建分析section的HTML"""
        # 提取emoji和标题
        if '🎯' in title:
            emoji = '🎯'
            section_title = '1. 核心贡献'
        elif '🔧' in title:
            emoji = '🔧'
            section_title = '2. 技术方法'
        elif '🧪' in title:
            emoji = '🧪'
            section_title = '3. 实验验证'
        elif '💡' in title:
            emoji = '💡'
            section_title = '4. 影响意义'
        elif '🔮' in title:
            emoji = '🔮'
            section_title = '5. 局限展望'
        else:
            # 尝试从标题中提取
            emoji = '📝'
            section_title = title.replace('*', '').strip()
        
        # 合并内容
        content_text = ' '.join(content).strip()
        
        # 处理文本格式
        content_text = PromptManager._format_text_content(content_text)
        
        return f'''<div class="analysis-section">
    <div class="analysis-title">
        <span>{emoji}</span>
        {section_title}
    </div>
    <div class="analysis-content">
        <p>{content_text}</p>
    </div>
</div>'''
    
    @staticmethod
    def _format_text_content(text: str) -> str:
        """格式化文本内容，添加HTML标记"""
        if not text:
            return ""
        
        # 处理粗体标记
        text = text.replace('**', '<strong>').replace('**', '</strong>')
        
        # 处理斜体标记
        text = text.replace('*', '<em>').replace('*', '</em>')
        
        # 处理代码标记
        text = text.replace('`', '<code>').replace('`', '</code>')
        
        # 处理数字和百分比的突出显示
        import re
        text = re.sub(r'(\d+\.?\d*%)', r'<strong>\1</strong>', text)
        text = re.sub(r'(\d+\.?\d*倍)', r'<strong>\1</strong>', text)
        
        return text 