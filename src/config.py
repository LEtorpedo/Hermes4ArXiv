#!/usr/bin/env python3
"""
配置管理模块
集中管理所有配置项，便于维护和扩展
"""

import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """配置类，管理所有配置项"""

    def _clean_string(self, value: str) -> str:
        """清理字符串中的特殊字符"""
        if not value:
            return value
        # 移除不间断空格和其他不可见字符
        return value.replace('\xa0', ' ').strip()

    def __init__(self):
        """初始化配置，从环境变量读取"""
        # AI API配置
        self.DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
        self.DEEPSEEK_API_BASE = "https://api.deepseek.com/v1"
        self.DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-r1")
        
        # 多AI支持
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.OPENAI_MODEL = os.getenv("OPENAI_MODEL", "o3-2025-04-16")
        
        self.CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
        self.CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-opus-4-20250514")
        
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        self.GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-pro-preview-05-06")
        
        # AI分析策略配置
        self.ANALYSIS_STRATEGY = os.getenv("ANALYSIS_STRATEGY", "fallback")
        self.AI_FALLBACK_ORDER = os.getenv("AI_FALLBACK_ORDER", "deepseek,openai,claude,gemini")
        self.ANALYSIS_TYPE = os.getenv("ANALYSIS_TYPE", "comprehensive")

        # 邮件配置
        self.SMTP_SERVER = os.getenv("SMTP_SERVER")
        smtp_port = os.getenv("SMTP_PORT", "587").strip()
        self.SMTP_PORT = int(smtp_port) if smtp_port else 587
        self.SMTP_USERNAME = self._clean_string(os.getenv("SMTP_USERNAME"))
        self.SMTP_PASSWORD = self._clean_string(os.getenv("SMTP_PASSWORD"))
        self.EMAIL_FROM = os.getenv("EMAIL_FROM")
        self.EMAIL_TO = [
            email.strip() for email in os.getenv("EMAIL_TO", "").split(",") if email.strip()
        ]

        # 文件路径配置
        self.BASE_DIR = Path(__file__).parent
        self.PAPERS_DIR = self.BASE_DIR / "storage" / "papers"
        self.CONCLUSION_FILE = self.BASE_DIR / "storage" / "conclusion.md"
        self.TEMPLATES_DIR = self.BASE_DIR / "output" / "templates"

        # ArXiv搜索配置
        categories_str = os.getenv("CATEGORIES", "cs.AI,cs.LG,cs.CL")
        self.CATEGORIES = [cat.strip() for cat in categories_str.split(",") if cat.strip()]
        self.MAX_PAPERS = int(os.getenv("MAX_PAPERS", "50"))
        self.SEARCH_DAYS = int(os.getenv("SEARCH_DAYS", "2"))
        
        # 📊 论文质量筛选配置
        self.ENABLE_QUALITY_FILTER = os.getenv("ENABLE_QUALITY_FILTER", "true").lower() == "true"
        self.QUALITY_THRESHOLD = float(os.getenv("QUALITY_THRESHOLD", "65.0"))

        # AI分析配置
        self.AI_MODEL = "deepseek-chat"
        self.API_RETRY_TIMES = 3  # API重试次数
        self.API_DELAY = 2  # API调用间隔（秒）

        # 并行处理配置
        self.ENABLE_PARALLEL = os.getenv("ENABLE_PARALLEL", "true").lower() == "true"
        self.MAX_WORKERS = int(os.getenv("MAX_WORKERS", "0"))  # 0表示自动计算
        self.BATCH_SIZE = int(os.getenv("BATCH_SIZE", "20"))

        # 并行处理配置
        self.ENABLE_PARALLEL = os.getenv("ENABLE_PARALLEL", "true").lower() == "true"
        self.MAX_WORKERS = int(os.getenv("MAX_WORKERS", "0"))  # 0表示自动计算
        self.BATCH_SIZE = int(os.getenv("BATCH_SIZE", "20"))

        # 输出配置
        self.OUTPUT_FORMAT = "markdown"  # 输出格式：markdown, html
        self.EMAIL_FORMAT = "html"  # 邮件格式：html, text
        
        # GitHub仓库配置
        self.GITHUB_REPO_URL = os.getenv("GITHUB_REPO_URL", "https://github.com/your-username/hermes4arxiv")

    def validate(self) -> bool:
        """验证配置是否完整"""
        required_configs = [
            self.DEEPSEEK_API_KEY,
            self.SMTP_SERVER,
            self.SMTP_USERNAME,
            self.SMTP_PASSWORD,
            self.EMAIL_FROM,
        ]

        missing_configs = [config for config in required_configs if not config]

        if missing_configs:
            print(f"缺少必要配置: {missing_configs}")
            return False

        if not self.EMAIL_TO:
            print("缺少收件人邮箱配置")
            return False

        return True

    def create_directories(self):
        """创建必要的目录"""
        self.PAPERS_DIR.mkdir(parents=True, exist_ok=True)
        self.TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
        # 创建日志目录
        (self.BASE_DIR / "storage" / "logs").mkdir(parents=True, exist_ok=True)
