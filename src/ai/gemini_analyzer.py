#!/usr/bin/env python3
"""
Google Gemini AI Analyzer module.

This module provides the GeminiAnalyzer class, which uses the Google Gemini API
to analyze research papers. It implements the BaseAnalyzer interface.
"""

import logging
import time
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions # For specific exception handling
import arxiv # For arxiv.Result type hinting
from typing import Dict, Any, List

from .base_analyzer import BaseAnalyzer
from .prompts import PromptManager

logger = logging.getLogger(__name__)

class GeminiAnalyzer(BaseAnalyzer):
    """
    GeminiAnalyzer uses the Google Gemini API to analyze research papers.
    """

    def __init__(self, api_key: str, model: str = "gemini-pro", timeout: int = 60, retry_times: int = 3, delay: int = 2):
        """
        Initializes the GeminiAnalyzer.

        Args:
            api_key: The Google Gemini API key.
            model: The Gemini model to use (e.g., "gemini-pro").
            timeout: Timeout for API calls in seconds.
            retry_times: Number of times to retry an API call if it fails.
            delay: Delay between retries in seconds.
        """
        super().__init__(api_key, model, timeout, retry_times, delay)
        
        try:
            genai.configure(api_key=self.api_key)
        except Exception as e:
            logger.error(f"Failed to configure Gemini API: {e}")
            raise ValueError(f"Gemini API key configuration failed: {e}")

        self.genai_model = genai.GenerativeModel(self.model)

        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]

        self.generation_config = genai.types.GenerationConfig(
            temperature=0.7, 
            max_output_tokens=1500 
            # candidate_count can be set if needed, default is 1
        )
        logger.info(f"GeminiAnalyzer initialized with model: {self.model}")

    def analyze_paper(self, paper: arxiv.Result, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Analyzes a single paper using the Gemini API.
        """
        system_prompt = PromptManager.get_system_prompt(analysis_type)
        user_prompt = PromptManager.get_user_prompt(paper, analysis_type)
        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        request_options = {"timeout": self.timeout}

        for attempt in range(self.retry_times):
            try:
                logger.info(f"Gemini analyzing paper: {paper.title[:50]}... (Attempt {attempt + 1}/{self.retry_times}) Model: {self.model}")
                
                response = self.genai_model.generate_content(
                    full_prompt,
                    generation_config=self.generation_config,
                    safety_settings=self.safety_settings,
                    request_options=request_options
                )

                # Check for content blocking
                if response.prompt_feedback and response.prompt_feedback.block_reason:
                    block_reason = response.prompt_feedback.block_reason
                    logger.warning(f"❌ Gemini content blocked for paper {paper.title[:50]} (Attempt {attempt + 1}). Reason: {block_reason}")
                    # If blocked, treat as an error for retry purposes
                    if attempt < self.retry_times - 1:
                        time.sleep(self.delay * (attempt + 1))
                        continue # Go to next attempt
                    else: # Last attempt failed due to blocking
                        raise Exception(f"Gemini content generation blocked after {self.retry_times} attempts. Reason: {block_reason}")
                
                # Ensure text is available (it might not be if candidates list is empty)
                if not response.candidates or not response.candidates[0].content.parts:
                    logger.warning(f"❌ Gemini response for {paper.title[:50]} had no content/candidates (Attempt {attempt + 1}).")
                    if attempt < self.retry_times - 1:
                        time.sleep(self.delay * (attempt+1))
                        continue
                    else:
                        raise Exception(f"Gemini response had no content after {self.retry_times} attempts.")

                analysis_text = response.text # Convenience accessor, same as response.candidates[0].content.parts[0].text

                logger.info(f"✅ Gemini analysis successful for: {paper.title[:50]}...")
                time.sleep(self.delay)
                
                return {
                    'analysis': analysis_text,
                    'provider': 'gemini',
                    'model': self.model,
                    'timestamp': time.time(),
                    'html_analysis': PromptManager.format_analysis_for_html(analysis_text)
                }

            except (google_exceptions.DeadlineExceeded, google_exceptions.RetryError, google_exceptions.ServiceUnavailable, google_exceptions.ResourceExhausted) as e:
                error_msg = str(e)
                logger.warning(f"❌ Gemini API error (Attempt {attempt + 1}) for {paper.title[:50]}: {error_msg}")
                if attempt < self.retry_times - 1:
                    wait_time = self.delay * (2 ** attempt) # Exponential backoff
                    logger.info(f"Retryable API error. Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Final attempt failed for paper {paper.title[:50]} due to API error: {error_msg}")
                    raise e
            except Exception as e: # Catch any other unexpected errors
                error_msg = str(e)
                logger.warning(f"❌ Gemini analysis unexpected error (Attempt {attempt + 1}) for {paper.title[:50]}: {error_msg}")
                if attempt < self.retry_times - 1:
                    time.sleep(self.delay * (attempt + 1))
                else:
                    logger.error(f"Gemini analysis ultimately failed for paper: {paper.title[:50]} after {self.retry_times} attempts.")
                    raise e
        
        # Fallback if loop finishes without returning or raising (should not happen)
        logger.error(f"Gemini analysis failed for {paper.title[:50]} after all retries without specific exception.")
        return {
            'analysis': "Error: Analysis failed after multiple retries.",
            'provider': 'gemini',
            'model': self.model,
            'timestamp': time.time(),
            'html_analysis': "<p>Error: Analysis failed after multiple retries.</p>"
        }

    def analyze_papers_batch(self, papers: List[arxiv.Result], batch_size: int = 4) -> Dict[str, Any]:
        """
        Analyzes a batch of papers using the Gemini API for comparison.
        """
        if not papers or len(papers) < 2:
            logger.warning(f"Gemini: Paper count ({len(papers)}) is less than 2. Skipping batch comparison.")
            return None

        actual_batch_papers = papers[:batch_size]
        if len(actual_batch_papers) < 2:
            logger.warning(f"Gemini: Effective paper count for batch ({len(actual_batch_papers)}) is less than 2. Skipping.")
            return None

        papers_info = []
        for paper in actual_batch_papers:
            authors_str = 'Unknown Authors'
            if paper.authors:
                try:
                    author_names = [author.name for author in paper.authors]
                    authors_str = ', '.join(author_names[:3])
                    if len(author_names) > 3: authors_str += f" et al. ({len(author_names)} total)"
                except AttributeError: authors_str = ', '.join(str(a) for a in paper.authors[:3])

            published_date = 'Unknown Date'
            if paper.published:
                try:
                    if hasattr(paper.published, 'strftime'): published_date = paper.published.strftime('%Y-%m-%d')
                    else: published_date = str(paper.published)
                except Exception as e_date:
                    logger.debug(f"Could not format date for {paper.entry_id}: {e_date}")
                    published_date = str(paper.published)
            
            summary = paper.summary.strip() if paper.summary else "Summary not available."
            if len(summary) > 800: summary = summary[:797] + "..."

            papers_info.append({
                'title': paper.title if paper.title else "Title not available.",
                'authors': authors_str,
                'categories': ', '.join(paper.categories) if paper.categories else "N/A",
                'published': published_date,
                'summary': summary,
                'url': paper.entry_id
            })
        
        if len(papers_info) < 2:
             logger.warning(f"Gemini: Not enough valid paper info entries ({len(papers_info)}) for batch. Skipping.")
             return None

        system_prompt = PromptManager.get_batch_comparison_system_prompt()
        user_prompt = PromptManager.get_batch_comparison_user_prompt(papers_info)
        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        batch_generation_config = genai.types.GenerationConfig(
            temperature=0.3, 
            max_output_tokens=3000
        )
        request_options = {"timeout": self.timeout * 2} # Longer timeout for batch

        for attempt in range(self.retry_times):
            try:
                logger.info(f"Gemini batch analyzing {len(papers_info)} papers... (Attempt {attempt + 1}/{self.retry_times}) Model: {self.model}")
                
                response = self.genai_model.generate_content(
                    full_prompt,
                    generation_config=batch_generation_config,
                    safety_settings=self.safety_settings,
                    request_options=request_options
                )

                if response.prompt_feedback and response.prompt_feedback.block_reason:
                    block_reason = response.prompt_feedback.block_reason
                    logger.warning(f"❌ Gemini content blocked for batch analysis (Attempt {attempt + 1}). Reason: {block_reason}")
                    if attempt < self.retry_times - 1:
                        time.sleep(self.delay * (attempt + 1) * 2) # Longer delay
                        continue
                    else:
                        logger.error(f"Final batch attempt failed due to content blocking. Reason: {block_reason}")
                        return None 
                
                if not response.candidates or not response.candidates[0].content.parts:
                    logger.warning(f"❌ Gemini batch response had no content/candidates (Attempt {attempt + 1}).")
                    if attempt < self.retry_times - 1:
                        time.sleep(self.delay * (attempt+1) * 2)
                        continue
                    else:
                        logger.error(f"Gemini batch response had no content after {self.retry_times} attempts.")
                        return None


                batch_analysis_text = response.text
                logger.info(f"✅ Gemini batch analysis successful for {len(papers_info)} papers.")
                time.sleep(self.delay * 2)

                return {
                    'batch_analysis': batch_analysis_text,
                    'papers_count': len(papers_info),
                    'provider': 'gemini',
                    'model': self.model,
                    'timestamp': time.time(),
                    'analysis_type': 'batch_comparison'
                }

            except (google_exceptions.DeadlineExceeded, google_exceptions.RetryError, google_exceptions.ServiceUnavailable, google_exceptions.ResourceExhausted) as e:
                error_msg = str(e)
                logger.warning(f"❌ Gemini API error during batch analysis (Attempt {attempt + 1}): {error_msg}")
                if attempt < self.retry_times - 1:
                    wait_time = self.delay * (2 ** attempt) * 2 # Longer exponential backoff
                    logger.info(f"Retryable API error for batch. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Final batch attempt failed due to API error: {error_msg}")
                    return None
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"❌ Gemini batch analysis unexpected error (Attempt {attempt + 1}): {error_msg}")
                if attempt < self.retry_times - 1:
                    time.sleep(self.delay * (attempt + 1) * 2)
                else:
                    logger.error(f"Gemini batch analysis ultimately failed after {self.retry_times} attempts.")
                    return None
        
        logger.error(f"Gemini batch analysis failed for {len(papers_info)} papers after all retries.")
        return None

    def get_info(self) -> Dict[str, str]:
        """
        Returns information about the Gemini analyzer.
        """
        return {
            "provider_name": "Gemini",
            "model_name": self.model,
            "description": "Gemini - Google's Next-Generation AI Models"
        }

if __name__ == '__main__':
    # Basic commented-out test structure
    # logger.setLevel(logging.INFO)
    # logging.basicConfig(level=logging.INFO)
    
    # class MockArxivResult: # Same as in openai_analyzer for consistency
    #     def __init__(self, title, summary, entry_id="http://arxiv.org/abs/test/123", authors=None, categories=None, published=None):
    #         self.title = title
    #         self.summary = summary
    #         self.entry_id = entry_id
    #         self.authors = authors if authors else [type('Author', (), {'name': 'Dr. Test'})()]
    #         self.categories = categories if categories else ["cs.AI"]
    #         self.published = published if published else time.gmtime() 

    # IMPORTANT: Set your Google Gemini API Key in environment variables or directly
    # test_api_key = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
    # if test_api_key == "YOUR_GEMINI_API_KEY_HERE":
    #     logger.error("Please set your GEMINI_API_KEY for testing.")
    #     exit()

    # analyzer = GeminiAnalyzer(api_key=test_api_key, model="gemini-pro") # or "gemini-1.5-flash" etc.

    # Test single paper
    # paper1 = MockArxivResult(title="Exploring Gemini Pro", summary="A comprehensive study of the Gemini Pro model capabilities.")
    # try:
    #     analysis_result = analyzer.analyze_paper(paper1)
    #     logger.info(f"Single Analysis (Gemini): {analysis_result['analysis'][:100]}...")
    # except Exception as e:
    #     logger.error(f"Error during Gemini single paper analysis test: {e}")

    # Test batch paper
    # paper2 = MockArxivResult(title="Future of Generative AI", summary="Predictions and analysis of future generative AI trends.")
    # paper3 = MockArxivResult(title="Multimodal Models", summary="Understanding the architecture of multimodal AI systems.")
    # try:
    #     batch_result = analyzer.analyze_papers_batch([paper1, paper2, paper3])
    #     if batch_result:
    #         logger.info(f"Batch Analysis (Gemini): {batch_result['batch_analysis'][:100]}...")
    #     else:
    #         logger.warning("Gemini batch analysis returned None.")
    # except Exception as e:
    #     logger.error(f"Error during Gemini batch paper analysis test: {e}")
    
    # logger.info(f"Analyzer Info: {analyzer.get_info()}")
    pass
