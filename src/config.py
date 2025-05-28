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

    def _safe_int(self, value: str, default: str) -> int:
        """安全的整数转换，处理空字符串和None"""
        if not value or not value.strip():
            return int(default)
        return int(value.strip())

    def __init__(self):
        """初始化配置，从环境变量读取"""
        # AI Provider Configuration
        self.AI_PROVIDER = os.getenv("AI_PROVIDER", "deepseek").lower()

        # DeepSeek AI配置
        self.DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
        self.DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

        # OpenAI AI配置
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

        # Gemini AI配置
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        self.GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-pro")
        
        # API调用配置
        self.API_RETRY_TIMES = self._safe_int(os.getenv("API_RETRY_TIMES"), "3")
        self.API_DELAY = self._safe_int(os.getenv("API_DELAY"), "2")
        self.API_TIMEOUT = self._safe_int(os.getenv("API_TIMEOUT"), "60")
        
        # 分析配置
        self.ANALYSIS_TYPE = os.getenv("ANALYSIS_TYPE", "comprehensive")

        # 邮件配置
        self.SMTP_SERVER = os.getenv("SMTP_SERVER")
        self.SMTP_PORT = self._safe_int(os.getenv("SMTP_PORT"), "587")
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
        self.MAX_PAPERS = self._safe_int(os.getenv("MAX_PAPERS"), "50")
        self.SEARCH_DAYS = self._safe_int(os.getenv("SEARCH_DAYS"), "2")

        # 并行处理配置
        self.ENABLE_PARALLEL = os.getenv("ENABLE_PARALLEL", "true").lower() == "true"
        self.MAX_WORKERS = self._safe_int(os.getenv("MAX_WORKERS"), "0")  # 0表示自动计算
        self.BATCH_SIZE = self._safe_int(os.getenv("BATCH_SIZE"), "20")

        # 输出配置
        self.OUTPUT_FORMAT = "markdown"  # 输出格式：markdown, html
        self.EMAIL_FORMAT = "html"  # 邮件格式：html, text
        
        # GitHub仓库配置
        self.GITHUB_REPO_URL = os.getenv("GITHUB_REPO_URL", "https://github.com/your-username/hermes4arxiv")

    def validate(self) -> bool:
        """验证配置是否完整"""
        # 检查AI Provider特定配置
        if self.AI_PROVIDER == "deepseek":
            if not self.DEEPSEEK_API_KEY:
                print("❌ AI_PROVIDER设置为deepseek，但未配置DEEPSEEK_API_KEY，无法进行论文分析")
                return False
            print(f"✅ 配置验证通过！使用DeepSeek模型: {self.DEEPSEEK_MODEL}")
        elif self.AI_PROVIDER == "openai":
            if not self.OPENAI_API_KEY:
                print("❌ AI_PROVIDER设置为openai，但未配置OPENAI_API_KEY，无法进行论文分析")
                return False
            print(f"✅ 配置验证通过！使用OpenAI模型: {self.OPENAI_MODEL}")
        elif self.AI_PROVIDER == "gemini":
            if not self.GEMINI_API_KEY:
                print("❌ AI_PROVIDER设置为gemini，但未配置GEMINI_API_KEY，无法进行论文分析")
                return False
            print(f"✅ 配置验证通过！使用Gemini模型: {self.GEMINI_MODEL}")
        else:
            print(f"❌ 不支持的AI_PROVIDER: {self.AI_PROVIDER}。请选择 'deepseek', 'openai', 或 'gemini'")
            return False
        
        # 检查邮件配置
        required_email_configs = [
            self.SMTP_SERVER,
            self.SMTP_USERNAME,
            self.SMTP_PASSWORD,
            self.EMAIL_FROM,
        ]

        missing_email_configs = [config for config in required_email_configs if not config]

        if missing_email_configs:
            print(f"❌ 缺少必要的邮件配置: {missing_email_configs}")
            return False

        if not self.EMAIL_TO:
            print("❌ 缺少收件人邮箱配置 (EMAIL_TO)")
            return False

        # 移除原先DeepSeek特定的成功消息，因为它现在由AI_PROVIDER逻辑处理
        return True

    def create_directories(self):
        """创建必要的目录"""
        self.PAPERS_DIR.mkdir(parents=True, exist_ok=True)
        self.TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
        # 创建日志目录
        (self.BASE_DIR / "storage" / "logs").mkdir(parents=True, exist_ok=True)
