#!/usr/bin/env python3
"""
ArXiv论文追踪与分析器
使用模块化架构，支持更好的扩展性和维护性
"""

import sys
import traceback
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from data.arxiv_client import ArxivClient
# from config import Config # Config is already imported via src.config
from src.config import Config # Ensure Config is imported if not already
from src.ai.factory import get_analyzer # Import the factory
from output.email_sender import EmailSender
from output.formatter import OutputFormatter
from ai.parallel import ParallelPaperAnalyzer # This seems to be an old path or structure
# from src.ai.parallel import ParallelPaperAnalyzer # Corrected path if parallel is under src.ai
# Based on current file structure, ai.parallel seems to be sibling to main.py's dir if main is in src
# Let's assume ai.parallel is found as `from ai.parallel import ParallelPaperAnalyzer` if main.py is in `src`
# and `ai` is also in `src`. If `ai` is a sub-package of `src`, then `from .ai.parallel` or `from src.ai.parallel`
# The provided file structure has main.py in src/ and ai/ in src/ai/.
# The original code had `from ai.parallel import ParallelPaperAnalyzer` which implies `ai` is in python path
# or `src` is added to path and `ai` is a top-level dir in `src`.
# Given `sys.path.insert(0, str(Path(__file__).parent))` and main.py in `src/`,
# and `ai` is `src/ai/`, then `from ai.parallel...` should work.

from src.utils.logger import logger
# Removed: from ai.analyzer import DeepSeekAnalyzer


class ArxivPaperTracker:
    """ArXiv论文追踪器主类"""

    def __init__(self):
        """初始化追踪器"""
        self.config = Config()
        self.arxiv_client = None
        self.ai_analyzer = None
        self.output_formatter = None
        self.email_sender = None

        # 验证配置
        if not self.config.validate():
            raise ValueError("配置验证失败，请检查环境变量设置")

        # 创建必要目录
        self.config.create_directories()

        # 初始化组件
        self._initialize_components()

    def _initialize_components(self):
        """初始化各个组件"""
        try:
            # 初始化AI分析器 (using the factory)
            logger.info(f"Initializing AI Analyzer using provider: {self.config.AI_PROVIDER}")
            self.ai_analyzer = get_analyzer(self.config)
            logger.info(f"Successfully initialized AI Analyzer: {type(self.ai_analyzer).__name__}")
            
            # 初始化ArXiv客户端
            self.arxiv_client = ArxivClient(
                categories=self.config.CATEGORIES,
                max_papers=self.config.MAX_PAPERS,
                search_days=self.config.SEARCH_DAYS,
            )

            # 初始化输出格式化器
            self.output_formatter = OutputFormatter(self.config.TEMPLATES_DIR, self.config.GITHUB_REPO_URL)

            # 初始化邮件发送器
            self.email_sender = EmailSender.create_from_config(self.config)

            logger.info("所有组件初始化完成")

        except Exception as e:
            logger.error(f"组件初始化失败: {e}")
            raise

    def run(self):
        """运行论文追踪和分析流程"""
        try:
            logger.info("开始ArXiv论文追踪和分析")

            # 1. 获取最近的论文
            papers = self.arxiv_client.get_recent_papers()

            if not papers:
                logger.info("没有找到符合条件的论文")
                return

            logger.info(f"找到 {len(papers)} 篇论文，开始分析")

            # 2. 分析论文（支持并行和串行两种模式）
            if self.config.ENABLE_PARALLEL and len(papers) > 1:
                # 并行分析模式
                logger.info("使用并行分析模式")
                
                # 计算最优工作线程数
                if self.config.MAX_WORKERS > 0:
                    optimal_workers = self.config.MAX_WORKERS
                else:
                    optimal_workers = ParallelPaperAnalyzer.calculate_optimal_workers(
                        len(papers), self.config.API_DELAY
                    )
                
                # 创建并行分析器
                parallel_analyzer = ParallelPaperAnalyzer(
                    ai_analyzer=self.ai_analyzer,
                    arxiv_client=self.arxiv_client,
                    papers_dir=self.config.PAPERS_DIR,
                    max_workers=optimal_workers,
                    batch_size=min(len(papers), self.config.BATCH_SIZE),
                    analysis_type=self.config.ANALYSIS_TYPE
                )
                
                # 执行并行分析
                papers_analyses = parallel_analyzer.analyze_papers_parallel(papers)
                
                # 记录性能统计
                stats = parallel_analyzer.get_performance_stats()
                logger.info(f"并行分析统计: {stats}")
                
                # 检查并行分析的失败情况
                failed_count = len(papers) - len(papers_analyses)
                if failed_count > 0:
                    logger.warning(f"并行分析中有 {failed_count} 篇论文分析失败")
                    
                    # 如果所有论文都失败了
                    if not papers_analyses:
                        logger.error("所有论文的AI分析都失败了，发送通知邮件")
                        if self.email_sender and self.config.EMAIL_TO:
                            self.email_sender.send_ai_analysis_failure_notification(
                                self.config.EMAIL_TO, len(papers)
                            )
                        return
                    
                    # 如果失败比例超过50%
                    failure_rate = failed_count / len(papers)
                    if failure_rate >= 0.5:
                        logger.warning(f"AI分析失败率过高 ({failure_rate*100:.1f}%)，发送通知邮件")
                        if self.email_sender and self.config.EMAIL_TO:
                            error_msg = f"并行AI分析失败率过高：{failed_count}/{len(papers)} 篇论文分析失败 ({failure_rate*100:.1f}%)"
                            self.email_sender.send_error_notification(self.config.EMAIL_TO, error_msg)

            else:
                # 串行分析模式（原有逻辑）
                logger.info("使用串行分析模式")
                papers_analyses = []
                failed_papers = []

                for i, paper in enumerate(papers, 1):
                    logger.info(f"正在处理论文 {i}/{len(papers)}: {paper.title}")

                    try:
                        # 下载论文（如果需要）
                        pdf_path = self.arxiv_client.download_paper(
                            paper, self.config.PAPERS_DIR
                        )

                        # 分析论文
                        analysis = self.ai_analyzer.analyze_paper(paper, self.config.ANALYSIS_TYPE)
                        
                        # 检查AI分析是否成功
                        if analysis is not None:
                            papers_analyses.append((paper, analysis))
                        else:
                            logger.warning(f"AI分析失败，所有模型都无法处理: {paper.title}")
                            failed_papers.append(paper)

                        # 清理PDF文件
                        if pdf_path:
                            self.arxiv_client.delete_pdf(pdf_path)

                    except Exception as e:
                        logger.error(f"处理论文失败 {paper.title}: {e}")
                        failed_papers.append(paper)
                        # 继续处理下一篇论文
                        continue

            # 检查是否所有论文都分析失败了
            if not papers_analyses and len(papers) > 0:
                logger.error("所有论文的AI分析都失败了，发送通知邮件")
                # 发送AI分析失败通知邮件
                if self.email_sender and self.config.EMAIL_TO:
                    self.email_sender.send_ai_analysis_failure_notification(
                        self.config.EMAIL_TO, len(papers)
                    )
                return

            # 如果有部分论文分析失败，记录信息
            if hasattr(locals(), 'failed_papers') and failed_papers:
                logger.warning(f"有 {len(failed_papers)} 篇论文AI分析失败，成功分析 {len(papers_analyses)} 篇")
                # 如果失败比例超过50%，也发送通知
                failure_rate = len(failed_papers) / len(papers)
                if failure_rate >= 0.5:
                    logger.warning(f"AI分析失败率过高 ({failure_rate*100:.1f}%)，发送通知邮件")
                    if self.email_sender and self.config.EMAIL_TO:
                        # 使用send_error_notification发送高失败率警告
                        error_msg = f"AI分析失败率过高：{len(failed_papers)}/{len(papers)} 篇论文分析失败 ({failure_rate*100:.1f}%)\n\n失败论文列表：\n" + "\n".join([f"- {paper.title}" for paper in failed_papers[:10]])
                        if len(failed_papers) > 10:
                            error_msg += f"\n... 以及其他 {len(failed_papers) - 10} 篇论文"
                        self.email_sender.send_error_notification(self.config.EMAIL_TO, error_msg)

            if not papers_analyses:
                logger.warning("没有成功分析任何论文")
                return

            # 3. 生成输出
            self._generate_outputs(papers_analyses)

            # 4. 发送邮件
            self._send_email_report(papers_analyses)

            logger.info("ArXiv论文追踪和分析完成")

        except Exception as e:
            error_msg = f"运行过程中发生错误: {e}\n{traceback.format_exc()}"
            logger.error(error_msg)

            # 发送错误通知邮件
            if self.email_sender and self.config.EMAIL_TO:
                self.email_sender.send_error_notification(
                    self.config.EMAIL_TO, error_msg
                )

            raise

    def _generate_outputs(self, papers_analyses):
        """生成各种格式的输出"""
        try:
            # 生成Markdown格式并保存到文件
            markdown_content = self.output_formatter.format_markdown(papers_analyses)

            # 追加到conclusion.md文件
            self.output_formatter.save_to_file(
                f"\n\n{markdown_content}", self.config.CONCLUSION_FILE, mode="a"
            )

            # 生成统计信息
            stats = self.output_formatter.create_summary_stats(papers_analyses)
            logger.info(f"生成统计信息: {stats}")

        except Exception as e:
            logger.error(f"生成输出失败: {e}")
            raise

    def _send_email_report(self, papers_analyses):
        """发送邮件报告"""
        if not self.email_sender or not self.config.EMAIL_TO:
            logger.info("邮件配置不完整，跳过发送邮件")
            return

        try:
            # 生成HTML邮件内容
            html_content = self.output_formatter.format_html_email(papers_analyses)

            # 发送邮件
            success = self.email_sender.send_paper_analysis_report(
                self.config.EMAIL_TO, html_content, len(papers_analyses)
            )

            if success:
                logger.info("邮件报告发送成功")
            else:
                logger.error("邮件报告发送失败")

        except Exception as e:
            logger.error(f"发送邮件报告失败: {e}")

    def test_components(self):
        """测试各个组件的连接"""
        logger.info("开始测试组件连接")

        # 测试邮件连接
        if self.email_sender:
            self.email_sender.test_connection()

        # 测试ArXiv连接
        try:
            test_papers = self.arxiv_client.get_recent_papers()
            logger.info(f"ArXiv连接测试成功，找到 {len(test_papers)} 篇论文")
        except Exception as e:
            logger.error(f"ArXiv连接测试失败: {e}")

        logger.info("组件测试完成")


def main():
    """主函数"""
    try:
        # 创建追踪器实例
        tracker = ArxivPaperTracker()

        # 运行追踪和分析
        tracker.run()

    except Exception as e:
        logger.error(f"程序运行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()