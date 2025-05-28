#!/usr/bin/env python3
"""
输出格式化模块
支持多种输出格式和美化显示
"""

import datetime
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

import arxiv
from jinja2 import Environment, FileSystemLoader, Template

from utils.logger import logger


class OutputFormatter:
    """输出格式化器"""

    def __init__(self, templates_dir: Path, github_repo_url: str = None):
        """
        初始化格式化器

        Args:
            templates_dir: 模板目录路径
            github_repo_url: GitHub仓库URL
        """
        self.templates_dir = templates_dir
        self.github_repo_url = github_repo_url or "https://github.com/your-username/hermes4arxiv"
        self.env = Environment(loader=FileSystemLoader(str(templates_dir)))

    def format_markdown(
        self, papers_analyses: List[Tuple[arxiv.Result, Dict[str, Any]]], title: str = None
    ) -> str:
        """
        格式化为Markdown格式

        Args:
            papers_analyses: 论文分析结果列表，每个元素为(paper, analysis_dict)
            title: 标题

        Returns:
            Markdown格式的内容
        """
        today = datetime.datetime.now().strftime("%Y-%m-%d")

        if title is None:
            title = f"Hermes4ArXiv 学术精华 ({today})"

        content = f"# {title}\n\n"
        content += f"**生成时间**: {today}\n"
        content += f"**论文数量**: {len(papers_analyses)}\n\n"

        for i, (paper, analysis_result) in enumerate(papers_analyses, 1):
            author_names = [author.name for author in paper.authors]
            
            # 处理分析内容 - 从字典中提取实际分析文本
            if isinstance(analysis_result, dict):
                analysis_text = analysis_result.get('analysis', '分析暂时不可用')
            else:
                analysis_text = analysis_result or '分析暂时不可用'

            content += f"## {i}. {paper.title}\n\n"
            content += f"**👥 作者**: {', '.join(author_names)}\n\n"
            content += f"**🏷️ 类别**: {', '.join(paper.categories)}\n\n"
            content += f"**📅 发布日期**: {paper.published.strftime('%Y-%m-%d')}\n\n"
            content += f"**🔗 链接**: [{paper.entry_id}]({paper.entry_id})\n\n"
            content += f"### 📝 分析结果\n\n{analysis_text}\n\n"
            content += "---\n\n"

        return content

    def format_html_email(self, papers_analyses: List[Tuple[arxiv.Result, Dict[str, Any]]]) -> str:
        """
        格式化为HTML邮件格式

        Args:
            papers_analyses: 论文分析结果列表，每个元素为(paper, analysis_dict)

        Returns:
            HTML格式的邮件内容
        """
        try:
            template = self.env.get_template("email_template.html")
        except Exception as e:
            logger.error(f"加载邮件模板失败: {e}")
            return self._fallback_html_format(papers_analyses)

        today = datetime.datetime.now().strftime("%Y年%m月%d日")

        # 准备模板数据
        papers_data = []
        categories_set = set()

        for paper, analysis_result in papers_analyses:
            author_names = [author.name for author in paper.authors]
            categories_set.update(paper.categories)

            # 处理分析内容 - 从字典中提取实际分析文本
            if isinstance(analysis_result, dict):
                # 优先使用html_analysis，如果不存在则使用analysis
                if 'html_analysis' in analysis_result and analysis_result['html_analysis']:
                    analysis_html = analysis_result['html_analysis']
                else:
                    analysis_text = analysis_result.get('analysis', '分析暂时不可用')
                    analysis_html = self._convert_analysis_to_html(analysis_text)
            else:
                # 兼容旧格式，直接是字符串
                analysis_html = self._convert_analysis_to_html(analysis_result)

            # 生成PDF链接
            pdf_url = paper.pdf_url if hasattr(paper, 'pdf_url') else paper.entry_id.replace('/abs/', '/pdf/') + '.pdf'

            papers_data.append(
                {
                    "title": paper.title,
                    "authors": ", ".join(author_names),
                    "published": paper.published.strftime("%Y年%m月%d日"),
                    "categories": paper.categories,
                    "url": paper.entry_id,
                    "pdf_url": pdf_url,
                    "analysis": analysis_html,
                }
            )

        template_data = {
            "date": today,
            "paper_count": len(papers_analyses),
            "categories": ", ".join(sorted(categories_set)),
            "papers": papers_data,
            "github_repo_url": self.github_repo_url,
        }

        return template.render(**template_data)

    def _convert_analysis_to_html(self, analysis: str) -> str:
        """
        将分析内容转换为HTML格式，支持五维分析结构

        Args:
            analysis: 分析内容

        Returns:
            HTML格式的分析内容
        """
        # 定义分析维度的图标映射
        dimension_icons = {
            "核心贡献": "🎯",
            "技术方法": "🔧", 
            "实验验证": "🧪",
            "影响与意义": "💡",
            "局限与展望": "🔮",
            "Core Contribution": "🎯",
            "Technical Methods": "🔧",
            "Experimental Validation": "🧪", 
            "Impact & Significance": "💡",
            "Limitations & Future Work": "🔮"
        }

        # 分割段落
        paragraphs = analysis.split("\n\n")
        html_sections = []

        current_section = None
        current_content = []

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # 检查是否是新的分析维度标题
            is_dimension_title = False
            dimension_icon = "📝"
            
            # 匹配数字开头的标题 (如 "1. 核心贡献")
            title_match = re.match(r'^(\d+)\.\s*(.+?)[:：]?\s*$', para)
            if title_match:
                dimension_title = title_match.group(2).strip()
                dimension_icon = dimension_icons.get(dimension_title, "📝")
                is_dimension_title = True
            else:
                # 检查是否直接是维度名称
                for dim_name, icon in dimension_icons.items():
                    if para.startswith(dim_name):
                        dimension_icon = icon
                        is_dimension_title = True
                        break

            if is_dimension_title:
                # 保存之前的section
                if current_section and current_content:
                    html_sections.append(self._create_analysis_section(current_section, current_content))
                
                # 开始新的section
                current_section = {
                    "title": para,
                    "icon": dimension_icon
                }
                current_content = []
            else:
                # 添加到当前section的内容
                if para:
                    current_content.append(para)

        # 添加最后一个section
        if current_section and current_content:
            html_sections.append(self._create_analysis_section(current_section, current_content))

        # 如果没有找到结构化的分析，使用简单格式
        if not html_sections:
            return f'<div class="analysis-section"><div class="analysis-content">{self._format_simple_text(analysis)}</div></div>'

        return "\n".join(html_sections)

    def _create_analysis_section(self, section_info: Dict, content_list: List[str]) -> str:
        """
        创建分析section的HTML

        Args:
            section_info: section信息，包含title和icon
            content_list: 内容列表

        Returns:
            HTML section
        """
        title = section_info["title"]
        icon = section_info["icon"]
        
        # 处理内容
        content_html = []
        for content in content_list:
            formatted_content = self._format_simple_text(content)
            content_html.append(f"<p>{formatted_content}</p>")

        content_str = "\n".join(content_html)

        return f'''<div class="analysis-section">
    <div class="analysis-title">
        <span>{icon}</span>
        {title}
    </div>
    <div class="analysis-content">
        {content_str}
    </div>
</div>'''

    def _format_simple_text(self, text: str) -> str:
        """
        格式化简单文本，处理粗体、斜体等

        Args:
            text: 原始文本

        Returns:
            格式化后的HTML文本
        """
        # 处理粗体
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        
        # 处理斜体
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        
        # 处理代码
        text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
        
        # 处理换行
        text = text.replace('\n', '<br>')
        
        return text

    def _fallback_html_format(
        self, papers_analyses: List[Tuple[arxiv.Result, Dict[str, Any]]]
    ) -> str:
        """
        备用HTML格式化方法

        Args:
            papers_analyses: 论文分析结果列表

        Returns:
            简单的HTML格式内容
        """
        today = datetime.datetime.now().strftime("%Y年%m月%d日")

        html = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Hermes4ArXiv - 今日学术精华</title>
            <style>
                body {{ 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                    line-height: 1.6; 
                    max-width: 800px; 
                    margin: 0 auto; 
                    padding: 20px; 
                    background: #f5f7fa;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 12px;
                    margin-bottom: 30px;
                }}
                .paper {{ 
                    background: white;
                    border: 1px solid #e9ecef; 
                    margin-bottom: 25px; 
                    padding: 25px; 
                    border-radius: 12px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
                }}
                .paper-title {{ 
                    color: #2c3e50; 
                    font-size: 20px; 
                    font-weight: 600; 
                    margin-bottom: 15px; 
                    line-height: 1.4;
                }}
                .paper-meta {{ 
                    color: #6c757d; 
                    margin-bottom: 20px; 
                    font-size: 14px;
                }}
                .analysis {{ 
                    margin-top: 20px; 
                    line-height: 1.6;
                }}
                .paper-link {{
                    display: inline-block;
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    color: white;
                    padding: 8px 16px;
                    border-radius: 6px;
                    text-decoration: none;
                    margin-top: 15px;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🏛️ Hermes4ArXiv</h1>
                <p>赫尔墨斯为您送达今日学术精华</p>
                <p>{today}</p>
            </div>
            <div style="text-align: center; margin-bottom: 30px;">
                <p><strong>今日共分析 {len(papers_analyses)} 篇论文</strong></p>
            </div>
        """

        for i, (paper, analysis_result) in enumerate(papers_analyses, 1):
            author_names = [author.name for author in paper.authors]
            pdf_url = paper.entry_id.replace('/abs/', '/pdf/') + '.pdf'
            
            # 处理分析内容 - 从字典中提取实际分析文本
            if isinstance(analysis_result, dict):
                analysis_text = analysis_result.get('analysis', '分析暂时不可用')
            else:
                analysis_text = analysis_result or '分析暂时不可用'

            html += f"""
            <div class="paper">
                <div class="paper-title">{i}. {paper.title}</div>
                <div class="paper-meta">
                    <strong>👥 作者</strong>: {', '.join(author_names)}<br>
                    <strong>🏷️ 类别</strong>: {', '.join(paper.categories)}<br>
                    <strong>📅 发布日期</strong>: {paper.published.strftime('%Y年%m月%d日')}<br>
                </div>
                <div class="analysis">{analysis_text.replace(chr(10), '<br>')}</div>
                <div>
                    <a href="{paper.entry_id}" class="paper-link">🔗 查看原文</a>
                    <a href="{pdf_url}" class="paper-link" style="margin-left: 10px;">📄 下载PDF</a>
                </div>
            </div>
            """

        html += """
            <div style="text-align: center; margin-top: 40px; color: #6c757d; font-size: 14px;">
                <p>🏛️ Hermes4ArXiv - 智慧信使赫尔墨斯，每日为您传递学术前沿</p>
            </div>
        </body>
        </html>
        """

        return html

    def save_to_file(self, content: str, file_path: Path, mode: str = "a") -> None:
        """
        保存内容到文件

        Args:
            content: 要保存的内容
            file_path: 文件路径
            mode: 文件打开模式
        """
        try:
            with open(file_path, mode, encoding="utf-8") as f:
                f.write(content)
            logger.info(f"内容已保存到 {file_path}")
        except Exception as e:
            logger.error(f"保存文件失败 {file_path}: {e}")

    def create_summary_stats(
        self, papers_analyses: List[Tuple[arxiv.Result, Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        创建统计摘要

        Args:
            papers_analyses: 论文分析结果列表

        Returns:
            统计信息字典
        """
        if not papers_analyses:
            return {}

        categories = {}
        authors = set()
        dates = []

        for paper, analysis_result in papers_analyses:
            # 统计类别
            for cat in paper.categories:
                categories[cat] = categories.get(cat, 0) + 1

            # 统计作者
            for author in paper.authors:
                authors.add(author.name)

            # 统计日期
            dates.append(paper.published.date())

        return {
            "total_papers": len(papers_analyses),
            "categories": categories,
            "unique_authors": len(authors),
            "date_range": {
                "earliest": min(dates) if dates else None,
                "latest": max(dates) if dates else None,
            },
        }
