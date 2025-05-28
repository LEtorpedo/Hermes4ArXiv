"""
Base module for AI paper analyzers.

This module defines the abstract base class `BaseAnalyzer` which outlines the
common interface for all AI paper analyzers. Different AI providers (like OpenAI,
Gemini, Deepseek) will implement concrete versions of this analyzer.
"""

import abc
from typing import Any, Dict, List

import arxiv # arxiv.Result is used for type hinting

class BaseAnalyzer(abc.ABC):
    """
    Abstract Base Class for AI paper analyzers.

    This class defines the common interface that all specific AI paper
    analyzers must implement.
    """

    def __init__(self, api_key: str, model: str, timeout: int, retry_times: int, delay: int):
        """
        Initializes the BaseAnalyzer.

        Args:
            api_key: The API key for the AI provider.
            model: The specific model to be used for analysis.
            timeout: The timeout for API calls in seconds.
            retry_times: The number of times to retry an API call if it fails.
            delay: The delay between retries in seconds.
        """
        if not api_key:
            raise ValueError("API key cannot be empty.")
        
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.retry_times = retry_times
        self.delay = delay

    @abc.abstractmethod
    def analyze_paper(self, paper: arxiv.Result, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Analyzes a single paper.

        This method should be implemented by concrete subclasses to perform
        the actual analysis of a paper using the specific AI provider's API.

        Args:
            paper: An arxiv.Result object representing the paper to analyze.
            analysis_type: The type of analysis to perform (e.g., "comprehensive", "summary").
                           Defaults to "comprehensive".

        Returns:
            A dictionary containing the analysis results. The structure of this
            dictionary may vary depending on the implementation.
        """
        pass

    @abc.abstractmethod
    def analyze_papers_batch(self, papers: List[arxiv.Result], batch_size: int = 4) -> Dict[str, Any]:
        """
        Analyzes a batch of papers.

        This method should be implemented by concrete subclasses to perform
        batch analysis of papers. This can be more efficient than analyzing
        papers one by one.

        Args:
            papers: A list of arxiv.Result objects representing the papers to analyze.
            batch_size: The number of papers to process in each batch. Defaults to 4.

        Returns:
            A dictionary containing the analysis results for the batch. The structure
            may vary based on implementation, but it typically would map paper IDs
            or titles to their respective analyses.
        """
        pass

    @abc.abstractmethod
    def get_info(self) -> Dict[str, str]:
        """
        Returns information about the analyzer.

        This method should be implemented by concrete subclasses to provide
        details about the analyzer, such as its name, the model it uses, etc.

        Returns:
            A dictionary containing information about the analyzer.
            For example: {"provider_name": "OpenAI", "model_name": "gpt-3.5-turbo"}
        """
        pass
