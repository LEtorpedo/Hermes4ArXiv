#!/usr/bin/env python3
"""
批量分析协调器
管理论文批次处理和评分分配
"""

import logging
from typing import Dict, List, Any, Tuple
import re
import arxiv

# from .analyzer import DeepSeekAnalyzer # No longer specific to DeepSeek
from .base_analyzer import BaseAnalyzer # Import BaseAnalyzer for type hinting

logger = logging.getLogger(__name__)


class BatchAnalysisCoordinator:
    """批量分析协调器"""
    
    def __init__(self, analyzer: BaseAnalyzer, batch_size: int = 4): # Changed type hint
        self.analyzer = analyzer
        self.batch_size = batch_size
    
    def analyze_papers_with_comparison(self, papers: List[arxiv.Result]) -> List[Tuple[arxiv.Result, Dict[str, Any]]]:
        """
        使用批量比较方式分析论文
        
        Args:
            papers: 论文列表
            
        Returns:
            (论文, 分析结果) 元组列表
        """
        if len(papers) < 2:
            logger.warning("论文数量不足，使用单独分析模式")
            return self._analyze_individual_papers(papers)
        
        results = []
        
        # 按批次处理论文
        for i in range(0, len(papers), self.batch_size):
            batch_papers = papers[i:i + self.batch_size]
            
            if len(batch_papers) == 1:
                # 最后一篇论文单独分析
                logger.info(f"剩余1篇论文，单独分析")
                individual_result = self._analyze_individual_papers(batch_papers)
                results.extend(individual_result)
            else:
                # 批量比较分析
                logger.info(f"批次 {i//self.batch_size + 1}: 分析 {len(batch_papers)} 篇论文")
                batch_results = self._analyze_batch_with_comparison(batch_papers)
                results.extend(batch_results)
        
        return results
    
    def _analyze_batch_with_comparison(self, batch_papers: List[arxiv.Result]) -> List[Tuple[arxiv.Result, Dict[str, Any]]]:
        """对一个批次的论文进行比较分析"""
        try:
            # 获取批量分析结果
            batch_analysis = self.analyzer.analyze_papers_batch(batch_papers, len(batch_papers))
            
            if batch_analysis is None:
                logger.warning("批量分析失败，回退到单独分析")
                return self._analyze_individual_papers(batch_papers)
            
            # 解析批量分析结果，提取每篇论文的评分和分析
            individual_analyses = self._parse_batch_analysis(
                batch_analysis['batch_analysis'], 
                batch_papers
            )
            
            # 组合结果
            results = []
            for i, paper in enumerate(batch_papers):
                if i < len(individual_analyses):
                    analyzer_info = self.analyzer.get_info()
                    analysis_result = {
                        'analysis': individual_analyses[i]['analysis'],
                        'provider': analyzer_info.get('provider_name', 'unknown_provider'),
                        'model': analyzer_info.get('model_name', self.analyzer.model), # Fallback to self.analyzer.model if new key not present
                        'timestamp': batch_analysis['timestamp'],
                        'batch_analysis': True,
                        'batch_size': len(batch_papers),
                        'paper_rank': individual_analyses[i].get('rank', i + 1),
                        'relative_score': individual_analyses[i].get('score', 3.0)
                    }
                    results.append((paper, analysis_result))
                else:
                    # 解析失败时的回退
                    logger.warning(f"解析论文 {i+1} 失败，使用单独分析")
                    individual_result = self._analyze_individual_papers([paper])
                    results.extend(individual_result)
            
            return results
            
        except Exception as e:
            logger.error(f"批量分析处理失败: {e}")
            return self._analyze_individual_papers(batch_papers)
    
    def _parse_batch_analysis(self, batch_text: str, papers: List[arxiv.Result]) -> List[Dict[str, Any]]:
        """
        解析批量分析结果，提取每篇论文的个人分析
        
        Args:
            batch_text: 批量分析文本
            papers: 论文列表
            
        Returns:
            每篇论文的分析结果列表
        """
        results = []
        
        try:
            # 按论文分割文本
            sections = re.split(r'## 论文 \d+[:：]|### 论文 \d+[:：]|论文\d+[:：]', batch_text)
            
            if len(sections) < len(papers):
                # 尝试其他分割方式
                sections = re.split(r'(?=\*\*论文|(?=第\d+名)|(?=排名第\d+))', batch_text)
            
            # 提取评分信息
            scores = self._extract_scores_from_text(batch_text)
            ranks = self._extract_ranks_from_text(batch_text)
            
            for i, paper in enumerate(papers):
                analysis_text = ""
                score = 3.0
                rank = i + 1
                
                # 提取对应论文的分析文本
                if i + 1 < len(sections):
                    analysis_text = sections[i + 1].strip()
                elif i < len(sections):
                    analysis_text = sections[i].strip()
                else:
                    analysis_text = f"论文{i+1}的分析暂时无法解析"
                
                # 从分析文本中提取评分
                if i < len(scores):
                    score = scores[i]
                else:
                    # 尝试从文本中提取评分
                    score_match = re.search(r'(\d+\.?\d*)\s*星', analysis_text)
                    if score_match:
                        score = float(score_match.group(1))
                
                # 提取排名
                if i < len(ranks):
                    rank = ranks[i]
                else:
                    # 尝试从文本中提取排名
                    rank_match = re.search(r'第\s*(\d+)\s*名|排名\s*(\d+)', analysis_text)
                    if rank_match:
                        rank = int(rank_match.group(1) or rank_match.group(2))
                
                results.append({
                    'analysis': analysis_text,
                    'score': score,
                    'rank': rank
                })
            
            # 确保有足够的结果
            while len(results) < len(papers):
                results.append({
                    'analysis': f"论文{len(results)+1}的分析暂时无法解析",
                    'score': 3.0,
                    'rank': len(results) + 1
                })
            
            return results[:len(papers)]
            
        except Exception as e:
            logger.error(f"解析批量分析失败: {e}")
            # 回退方案：平均分配
            return [
                {
                    'analysis': f"批量分析解析失败，论文{i+1}需要重新分析",
                    'score': 3.0,
                    'rank': i + 1
                }
                for i in range(len(papers))
            ]
    
    def _extract_scores_from_text(self, text: str) -> List[float]:
        """从文本中提取评分"""
        scores = []
        
        # 匹配各种评分格式
        score_patterns = [
            r'(\d+\.?\d*)\s*星',
            r'评分[:：]\s*(\d+\.?\d*)',
            r'得分[:：]\s*(\d+\.?\d*)',
            r'分数[:：]\s*(\d+\.?\d*)'
        ]
        
        for pattern in score_patterns:
            matches = re.findall(pattern, text)
            if matches:
                try:
                    scores = [float(score) for score in matches]
                    break
                except ValueError:
                    continue
        
        return scores
    
    def _extract_ranks_from_text(self, text: str) -> List[int]:
        """从文本中提取排名"""
        ranks = []
        
        # 匹配排名格式
        rank_patterns = [
            r'第\s*(\d+)\s*名',
            r'排名\s*(\d+)',
            r'位次\s*(\d+)'
        ]
        
        for pattern in rank_patterns:
            matches = re.findall(pattern, text)
            if matches:
                try:
                    ranks = [int(rank) for rank in matches]
                    break
                except ValueError:
                    continue
        
        return ranks
    
    def _analyze_individual_papers(self, papers: List[arxiv.Result]) -> List[Tuple[arxiv.Result, Dict[str, Any]]]:
        """单独分析论文（回退方案）"""
        results = []
        
        for paper in papers:
            try:
                analysis_result = self.analyzer.analyze_paper(paper, "comprehensive")
                results.append((paper, analysis_result))
            except Exception as e:
                logger.error(f"单独分析论文失败: {paper.title[:50]}... - {e}")
                # 使用错误分析
                from .prompts import PromptManager
                error_analysis = PromptManager.get_error_analysis(str(e))
                error_result = {
                    'analysis': error_analysis,
                    'provider': 'error',
                    'model': 'fallback',
                    'timestamp': 0,
                    'error': True
                }
                results.append((paper, error_result))
        
        return results 