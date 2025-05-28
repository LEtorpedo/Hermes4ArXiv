#!/usr/bin/env python3
"""
OpenAI AI Analyzer module.

This module provides the OpenAIAnalyzer class, which uses the OpenAI API
to analyze research papers. It implements the BaseAnalyzer interface.
"""

import logging
import time
import openai # OpenAI Python library
import arxiv # For arxiv.Result type hinting
from typing import Dict, Any, List

from .base_analyzer import BaseAnalyzer
from .prompts import PromptManager

logger = logging.getLogger(__name__)

class OpenAIAnalyzer(BaseAnalyzer):
    """
    OpenAIAnalyzer uses the OpenAI API to analyze research papers.
    It provides methods for analyzing single papers and batches of papers.
    """

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", timeout: int = 60, retry_times: int = 3, delay: int = 2):
        """
        Initializes the OpenAIAnalyzer.

        Args:
            api_key: The OpenAI API key.
            model: The OpenAI model to use (e.g., "gpt-3.5-turbo", "gpt-4").
            timeout: Timeout for API calls in seconds.
            retry_times: Number of times to retry an API call if it fails.
            delay: Delay between retries in seconds.
        """
        super().__init__(api_key, model, timeout, retry_times, delay)
        # The OpenAI client is initialized with the API key and timeout.
        # The base_url defaults to "https://api.openai.com/v1" which is what we want.
        self.client = openai.OpenAI(
            api_key=self.api_key,
            timeout=self.timeout
        )
        logger.info(f"OpenAIAnalyzer initialized with model: {self.model}")

    def analyze_paper(self, paper: arxiv.Result, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Analyzes a single paper using the OpenAI API.

        Args:
            paper: An arxiv.Result object representing the paper to analyze.
            analysis_type: The type of analysis to perform (e.g., "comprehensive", "summary").

        Returns:
            A dictionary containing the analysis results, provider information, and model details.
        
        Raises:
            Exception: If the analysis fails after multiple retries.
        """
        system_prompt = PromptManager.get_system_prompt(analysis_type)
        user_prompt = PromptManager.get_user_prompt(paper, analysis_type)

        for attempt in range(self.retry_times):
            try:
                logger.info(f"OpenAI analyzing paper: {paper.title[:50]}... (Attempt {attempt + 1}/{self.retry_times}) Model: {self.model}")
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1500,
                    timeout=self.timeout # Can be specified here again or rely on client's default
                )
                
                analysis = response.choices[0].message.content
                logger.info(f"✅ OpenAI analysis successful for: {paper.title[:50]}...")
                
                time.sleep(self.delay) # Delay to avoid hitting rate limits
                
                return {
                    'analysis': analysis,
                    'provider': 'openai',
                    'model': self.model,
                    'timestamp': time.time(),
                    'html_analysis': PromptManager.format_analysis_for_html(analysis)
                }
            
            except openai.APIError as e: # More specific exception handling for OpenAI
                error_msg = str(e)
                logger.warning(f"❌ OpenAI API error during analysis (Attempt {attempt + 1}): {error_msg}")
                # Check for common retryable errors
                if e.status_code in [429, 500, 502, 503, 504]: # Rate limit, server errors
                    wait_time = self.delay * (2 ** attempt) # Exponential backoff
                    logger.info(f"Retryable API error ({e.status_code}). Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                elif attempt < self.retry_times - 1:
                    time.sleep(self.delay * (attempt + 1)) # Standard delay for other errors
                else: # Last attempt
                    logger.error(f"Final attempt failed for paper {paper.title[:50]}. Error: {error_msg}")
                    raise e 
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"❌ OpenAI analysis failed (Attempt {attempt + 1}) for {paper.title[:50]}: {error_msg}")
                
                if attempt < self.retry_times - 1:
                    # Apply exponential backoff for network-related issues
                    if "timeout" in error_msg.lower() or "connection" in error_msg.lower() or "network" in error_msg.lower():
                        wait_time = self.delay * (2 ** attempt) # Exponential backoff
                        logger.info(f"Network-related error. Waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
                    else:
                        time.sleep(self.delay * (attempt + 1)) # Standard delay
                
                if attempt == self.retry_times - 1:
                    logger.error(f"OpenAI analysis ultimately failed for paper: {paper.title[:50]} after {self.retry_times} attempts.")
                    raise e
        
        # Should not be reached if retries are handled correctly, but as a fallback:
        logger.error(f"OpenAI analysis failed for {paper.title[:50]} after all retries without raising an exception.")
        return {
            'analysis': "Error: Analysis failed after multiple retries.",
            'provider': 'openai',
            'model': self.model,
            'timestamp': time.time(),
            'html_analysis': "<p>Error: Analysis failed after multiple retries.</p>"
        }

    def analyze_papers_batch(self, papers: List[arxiv.Result], batch_size: int = 4) -> Dict[str, Any]:
        """
        Analyzes a batch of papers using the OpenAI API for comparison.

        Args:
            papers: A list of arxiv.Result objects representing the papers to analyze.
            batch_size: The number of papers to process in this batch (actual OpenAI call).
                        The method will take the first `batch_size` papers from the `papers` list.

        Returns:
            A dictionary containing the batch analysis results or None if analysis is skipped/fails.
        """
        if not papers or len(papers) < 2:
            logger.warning(f"OpenAI: Paper count ({len(papers)}) is less than 2. Skipping batch comparison.")
            return None

        actual_batch_papers = papers[:batch_size]
        if len(actual_batch_papers) < 2:
            logger.warning(f"OpenAI: Effective paper count for batch ({len(actual_batch_papers)}) is less than 2. Skipping.")
            return None

        papers_info = []
        for paper in actual_batch_papers:
            authors_str = 'Unknown Authors'
            if paper.authors:
                try:
                    author_names = [author.name for author in paper.authors]
                    authors_str = ', '.join(author_names[:3])
                    if len(author_names) > 3:
                        authors_str += f" et al. ({len(author_names)} total)"
                except AttributeError: # Handle cases where authors might not be full Author objects
                    authors_str = ', '.join(str(a) for a in paper.authors[:3])


            published_date = 'Unknown Date'
            if paper.published:
                try:
                    if hasattr(paper.published, 'strftime'):
                        published_date = paper.published.strftime('%Y-%m-%d')
                    else:
                        published_date = str(paper.published)
                except Exception as e_date:
                    logger.debug(f"Could not format date for {paper.entry_id}: {e_date}")
                    published_date = str(paper.published)
            
            summary = paper.summary.strip() if paper.summary else "Summary not available."
            if len(summary) > 800: # Keep summary concise for batch prompt
                summary = summary[:797] + "..."

            papers_info.append({
                'title': paper.title if paper.title else "Title not available.",
                'authors': authors_str,
                'categories': ', '.join(paper.categories) if paper.categories else "N/A",
                'published': published_date,
                'summary': summary,
                'url': paper.entry_id
            })
        
        if len(papers_info) < 2: # Double check after formatting
             logger.warning(f"OpenAI: Not enough valid paper info entries ({len(papers_info)}) for batch. Skipping.")
             return None

        system_prompt = PromptManager.get_batch_comparison_system_prompt()
        user_prompt = PromptManager.get_batch_comparison_user_prompt(papers_info)

        for attempt in range(self.retry_times):
            try:
                logger.info(f"OpenAI batch analyzing {len(papers_info)} papers... (Attempt {attempt + 1}/{self.retry_times}) Model: {self.model}")
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3, # Lower temperature for factual comparison
                    max_tokens=3000, # Allow more tokens for batch analysis
                    timeout=self.timeout * 2 # Longer timeout for batch potentially
                )
                
                batch_analysis_content = response.choices[0].message.content
                logger.info(f"✅ OpenAI batch analysis successful for {len(papers_info)} papers.")
                
                time.sleep(self.delay * 2) # Longer delay after a heavier batch call

                return {
                    'batch_analysis': batch_analysis_content,
                    'papers_count': len(papers_info),
                    'provider': 'openai',
                    'model': self.model,
                    'timestamp': time.time(),
                    'analysis_type': 'batch_comparison'
                }

            except openai.APIError as e:
                error_msg = str(e)
                logger.warning(f"❌ OpenAI API error during batch analysis (Attempt {attempt + 1}): {error_msg}")
                if e.status_code in [429, 500, 502, 503, 504]:
                    wait_time = self.delay * (2 ** attempt) * 2 # Longer exponential backoff for batch
                    logger.info(f"Retryable API error ({e.status_code}). Waiting {wait_time} seconds before batch retry...")
                    time.sleep(wait_time)
                elif attempt < self.retry_times - 1:
                    time.sleep(self.delay * (attempt + 1) * 2)
                else:
                    logger.error(f"Final batch attempt failed. Error: {error_msg}")
                    # Unlike single analysis, might not re-raise to allow other operations to continue
                    return None 
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"❌ OpenAI batch analysis failed (Attempt {attempt + 1}): {error_msg}")
                
                if attempt < self.retry_times - 1:
                    if "timeout" in error_msg.lower() or "connection" in error_msg.lower() or "network" in error_msg.lower():
                        wait_time = self.delay * (2 ** attempt) * 2 # Longer exponential backoff
                        logger.info(f"Network-related error during batch. Waiting {wait_time} seconds...")
                        time.sleep(wait_time)
                    else:
                        time.sleep(self.delay * (attempt + 1) * 2) # Longer standard delay
                
                if attempt == self.retry_times - 1:
                    logger.error(f"OpenAI batch analysis ultimately failed after {self.retry_times} attempts.")
                    return None # Return None if batch fails after all retries
        
        logger.error(f"OpenAI batch analysis failed for {len(papers_info)} papers after all retries without specific error catch.")
        return None


    def get_info(self) -> Dict[str, str]:
        """
        Returns information about the OpenAI analyzer.

        Returns:
            A dictionary containing the provider name, model name, and a description.
        """
        return {
            "provider_name": "OpenAI",
            "model_name": self.model,
            "description": "OpenAI - Advanced AI Models"
        }

if __name__ == '__main__':
    # Example usage (requires dummy arxiv.Result and API key)
    # This part is for quick testing and would not be part of the final application logic
    logger.setLevel(logging.INFO)
    logging.basicConfig(level=logging.INFO)
    
    class MockArxivResult:
        def __init__(self, title, summary, entry_id="http://arxiv.org/abs/test/123", authors=None, categories=None, published=None):
            self.title = title
            self.summary = summary
            self.entry_id = entry_id
            self.authors = authors if authors else [type('Author', (), {'name': 'Dr. Test'})()]
            self.categories = categories if categories else ["cs.AI"]
            self.published = published if published else time.gmtime() # Using time.struct_time

    # IMPORTANT: Set your OpenAI API Key in environment variables or directly for testing
    # test_api_key = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY_HERE")
    # if test_api_key == "YOUR_OPENAI_API_KEY_HERE":
    #     logger.error("Please set your OPENAI_API_KEY for testing.")
    #     exit()

    # analyzer = OpenAIAnalyzer(api_key=test_api_key, model="gpt-3.5-turbo")

    # Test single paper analysis
    # paper1 = MockArxivResult(title="Paper about LLMs", summary="This paper discusses Large Language Models...")
    # try:
    #     analysis_result = analyzer.analyze_paper(paper1)
    #     logger.info(f"Single Analysis Result: {analysis_result['analysis'][:100]}...")
    # except Exception as e:
    #     logger.error(f"Error during single paper analysis test: {e}")

    # Test batch paper analysis
    # paper2 = MockArxivResult(title="Advancements in AI", summary="Exploring new advancements in AI research.")
    # paper3 = MockArxivResult(title="Reinforcement Learning", summary="A study on reinforcement learning techniques.")
    # try:
    #     batch_result = analyzer.analyze_papers_batch([paper1, paper2, paper3])
    #     if batch_result:
    #         logger.info(f"Batch Analysis Result: {batch_result['batch_analysis'][:100]}...")
    #     else:
    #         logger.warning("Batch analysis returned None.")
    # except Exception as e:
    #     logger.error(f"Error during batch paper analysis test: {e}")
    
    # logger.info(f"Analyzer Info: {analyzer.get_info()}")
    pass # End of example usage
