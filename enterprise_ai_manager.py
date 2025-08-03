"""
Enhanced GenAI Provider Manager for Enterprise ADF Monitoring
Supports multiple AI providers with fallback, ensemble methods, and cost tracking
"""
import asyncio
import time
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
from abc import ABC, abstractmethod

# Provider-specific imports (with graceful fallbacks)
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

@dataclass
class AnalysisResult:
    """Result from AI analysis"""
    success: bool
    provider_id: str
    error_type: str
    confidence_score: int
    should_retry: bool
    analysis_summary: str
    recommended_actions: List[str]
    reasoning: str
    processing_time: float
    token_usage: int
    cost_estimate: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "provider_id": self.provider_id,
            "error_type": self.error_type,
            "confidence_score": self.confidence_score,
            "should_retry": self.should_retry,
            "analysis_summary": self.analysis_summary,
            "recommended_actions": self.recommended_actions,
            "reasoning": self.reasoning,
            "processing_time": self.processing_time,
            "token_usage": self.token_usage,
            "cost_estimate": self.cost_estimate
        }

class BaseAIProvider(ABC):
    """Base class for AI providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider_id = config.get("provider_id")
        self.provider_name = config.get("provider_name")
        self.model_name = config.get("model_name")
        self.api_key = config.get("api_key")
        self.cost_per_1k_tokens = config.get("cost_per_1k_tokens", 0.03)
        
        # Model parameters
        self.temperature = config.get("temperature", 0.3)
        self.max_tokens = config.get("max_tokens", 1000)
        self.top_p = config.get("top_p", 0.9)
        
        # Performance tracking
        self.total_requests = 0
        self.successful_requests = 0
        self.total_cost = 0.0
        self.avg_response_time = 0.0
    
    @abstractmethod
    async def analyze_error(self, pipeline_name: str, error_message: str, 
                          run_id: str, context: Dict[str, Any] = None) -> AnalysisResult:
        """Analyze a pipeline error using this AI provider"""
        pass
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for error analysis"""
        return """You are an expert Azure Data Factory (ADF) pipeline failure analyst. 
        
Your task is to analyze pipeline errors and provide:
1. Error classification (transient, data_quality, configuration, resource, unknown)
2. Confidence score (0-100)
3. Retry recommendation (true/false)
4. Clear analysis summary
5. Specific recommended actions
6. Detailed reasoning

Classification Guidelines:
- TRANSIENT: Network timeouts, temporary service unavailability, rate limiting
- DATA_QUALITY: Schema mismatches, data validation failures, missing data
- CONFIGURATION: Authentication issues, permission errors, incorrect settings
- RESOURCE: Memory limits, storage issues, compute constraints
- UNKNOWN: Unclear or insufficient error information

Response format: JSON with keys: error_type, confidence_score, should_retry, analysis_summary, recommended_actions, reasoning"""
    
    def calculate_cost(self, token_count: int) -> float:
        """Calculate cost based on token usage"""
        return (token_count / 1000) * self.cost_per_1k_tokens
    
    def update_metrics(self, success: bool, response_time: float, token_count: int):
        """Update provider performance metrics"""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        
        # Update average response time
        if self.total_requests == 1:
            self.avg_response_time = response_time
        else:
            self.avg_response_time = (
                (self.avg_response_time * (self.total_requests - 1) + response_time) 
                / self.total_requests
            )
        
        # Update total cost
        self.total_cost += self.calculate_cost(token_count)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get provider performance metrics"""
        success_rate = (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0
        
        return {
            "provider_id": self.provider_id,
            "provider_name": self.provider_name,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "success_rate": round(success_rate, 2),
            "avg_response_time": round(self.avg_response_time, 2),
            "total_cost": round(self.total_cost, 4)
        }

class OpenAIProvider(BaseAIProvider):
    """OpenAI GPT provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        if OPENAI_AVAILABLE:
            openai.api_key = self.api_key
            self.client = openai.OpenAI(api_key=self.api_key)
        else:
            self.client = None
    
    async def analyze_error(self, pipeline_name: str, error_message: str, 
                          run_id: str, context: Dict[str, Any] = None) -> AnalysisResult:
        """Analyze error using OpenAI GPT"""
        start_time = time.time()
        
        if not OPENAI_AVAILABLE or not self.client:
            return self._create_mock_result(pipeline_name, error_message, start_time)
        
        try:
            user_prompt = f"""
            Pipeline: {pipeline_name}
            Run ID: {run_id}
            Error: {error_message}
            
            Additional Context: {json.dumps(context or {})}
            
            Please analyze this ADF pipeline failure and provide a JSON response.
            """
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.get_system_prompt()},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p
            )
            
            processing_time = time.time() - start_time
            
            # Parse response
            content = response.choices[0].message.content
            token_usage = response.usage.total_tokens
            
            try:
                analysis = json.loads(content)
            except json.JSONDecodeError:
                # Fallback parsing
                analysis = self._parse_fallback_response(content)
            
            # Update metrics
            self.update_metrics(True, processing_time, token_usage)
            
            return AnalysisResult(
                success=True,
                provider_id=self.provider_id,
                error_type=analysis.get("error_type", "unknown"),
                confidence_score=analysis.get("confidence_score", 50),
                should_retry=analysis.get("should_retry", False),
                analysis_summary=analysis.get("analysis_summary", "Analysis completed"),
                recommended_actions=analysis.get("recommended_actions", []),
                reasoning=analysis.get("reasoning", "Analysis performed"),
                processing_time=processing_time,
                token_usage=token_usage,
                cost_estimate=self.calculate_cost(token_usage)
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.update_metrics(False, processing_time, 0)
            
            return AnalysisResult(
                success=False,
                provider_id=self.provider_id,
                error_type="unknown",
                confidence_score=0,
                should_retry=False,
                analysis_summary=f"Analysis failed: {str(e)}",
                recommended_actions=["Check API configuration", "Retry analysis"],
                reasoning=f"Provider error: {str(e)}",
                processing_time=processing_time,
                token_usage=0,
                cost_estimate=0.0
            )
    
    def _create_mock_result(self, pipeline_name: str, error_message: str, start_time: float) -> AnalysisResult:
        """Create mock result when OpenAI is not available"""
        processing_time = time.time() - start_time
        
        # Simple rule-based analysis for demo
        error_type = "unknown"
        should_retry = False
        confidence = 60
        
        if any(keyword in error_message.lower() for keyword in ["timeout", "connection", "network"]):
            error_type = "transient"
            should_retry = True
            confidence = 85
        elif any(keyword in error_message.lower() for keyword in ["schema", "column", "data"]):
            error_type = "data_quality"
            should_retry = False
            confidence = 80
        elif any(keyword in error_message.lower() for keyword in ["access", "permission", "denied"]):
            error_type = "configuration"
            should_retry = False
            confidence = 90
        
        return AnalysisResult(
            success=True,
            provider_id=self.provider_id,
            error_type=error_type,
            confidence_score=confidence,
            should_retry=should_retry,
            analysis_summary=f"Mock analysis: {error_type} error detected",
            recommended_actions=["Review error details", "Check configuration"],
            reasoning="Mock analysis based on keyword matching",
            processing_time=processing_time,
            token_usage=100,  # Mock token usage
            cost_estimate=self.calculate_cost(100)
        )
    
    def _parse_fallback_response(self, content: str) -> Dict[str, Any]:
        """Parse response when JSON parsing fails"""
        return {
            "error_type": "unknown",
            "confidence_score": 50,
            "should_retry": False,
            "analysis_summary": "Response parsing failed",
            "recommended_actions": ["Manual review required"],
            "reasoning": "Unable to parse AI response"
        }

class AnthropicProvider(BaseAIProvider):
    """Anthropic Claude provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        if ANTHROPIC_AVAILABLE:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            self.client = None
    
    async def analyze_error(self, pipeline_name: str, error_message: str, 
                          run_id: str, context: Dict[str, Any] = None) -> AnalysisResult:
        """Analyze error using Anthropic Claude"""
        start_time = time.time()
        
        if not ANTHROPIC_AVAILABLE or not self.client:
            return self._create_mock_result(pipeline_name, error_message, start_time)
        
        try:
            user_prompt = f"""
            Pipeline: {pipeline_name}
            Run ID: {run_id}
            Error: {error_message}
            
            {self.get_system_prompt()}
            
            Please analyze this ADF pipeline failure.
            """
            
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            processing_time = time.time() - start_time
            content = response.content[0].text
            token_usage = response.usage.input_tokens + response.usage.output_tokens
            
            # Parse response (similar to OpenAI)
            try:
                analysis = json.loads(content)
            except json.JSONDecodeError:
                analysis = self._parse_fallback_response(content)
            
            self.update_metrics(True, processing_time, token_usage)
            
            return AnalysisResult(
                success=True,
                provider_id=self.provider_id,
                error_type=analysis.get("error_type", "unknown"),
                confidence_score=analysis.get("confidence_score", 50),
                should_retry=analysis.get("should_retry", False),
                analysis_summary=analysis.get("analysis_summary", "Analysis completed"),
                recommended_actions=analysis.get("recommended_actions", []),
                reasoning=analysis.get("reasoning", "Analysis performed"),
                processing_time=processing_time,
                token_usage=token_usage,
                cost_estimate=self.calculate_cost(token_usage)
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.update_metrics(False, processing_time, 0)
            
            return AnalysisResult(
                success=False,
                provider_id=self.provider_id,
                error_type="unknown",
                confidence_score=0,
                should_retry=False,
                analysis_summary=f"Analysis failed: {str(e)}",
                recommended_actions=["Check API configuration"],
                reasoning=f"Provider error: {str(e)}",
                processing_time=processing_time,
                token_usage=0,
                cost_estimate=0.0
            )
    
    def _create_mock_result(self, pipeline_name: str, error_message: str, start_time: float) -> AnalysisResult:
        """Create mock result when Anthropic is not available"""
        # Similar mock implementation as OpenAI
        processing_time = time.time() - start_time
        
        return AnalysisResult(
            success=True,
            provider_id=self.provider_id,
            error_type="unknown",
            confidence_score=60,
            should_retry=False,
            analysis_summary="Mock Anthropic analysis",
            recommended_actions=["Manual review"],
            reasoning="Mock analysis - Anthropic not available",
            processing_time=processing_time,
            token_usage=100,
            cost_estimate=self.calculate_cost(100)
        )

class GoogleProvider(BaseAIProvider):
    """Google Gemini provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        if GOOGLE_AVAILABLE:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        else:
            self.model = None
    
    async def analyze_error(self, pipeline_name: str, error_message: str, 
                          run_id: str, context: Dict[str, Any] = None) -> AnalysisResult:
        """Analyze error using Google Gemini"""
        start_time = time.time()
        
        if not GOOGLE_AVAILABLE or not self.model:
            return self._create_mock_result(pipeline_name, error_message, start_time)
        
        try:
            prompt = f"""
            {self.get_system_prompt()}
            
            Pipeline: {pipeline_name}
            Run ID: {run_id}
            Error: {error_message}
            
            Please analyze this ADF pipeline failure.
            """
            
            response = self.model.generate_content(prompt)
            processing_time = time.time() - start_time
            
            # Parse response
            content = response.text
            token_usage = 100  # Google doesn't provide token count easily
            
            try:
                analysis = json.loads(content)
            except json.JSONDecodeError:
                analysis = self._parse_fallback_response(content)
            
            self.update_metrics(True, processing_time, token_usage)
            
            return AnalysisResult(
                success=True,
                provider_id=self.provider_id,
                error_type=analysis.get("error_type", "unknown"),
                confidence_score=analysis.get("confidence_score", 50),
                should_retry=analysis.get("should_retry", False),
                analysis_summary=analysis.get("analysis_summary", "Analysis completed"),
                recommended_actions=analysis.get("recommended_actions", []),
                reasoning=analysis.get("reasoning", "Analysis performed"),
                processing_time=processing_time,
                token_usage=token_usage,
                cost_estimate=self.calculate_cost(token_usage)
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.update_metrics(False, processing_time, 0)
            
            return AnalysisResult(
                success=False,
                provider_id=self.provider_id,
                error_type="unknown",
                confidence_score=0,
                should_retry=False,
                analysis_summary=f"Analysis failed: {str(e)}",
                recommended_actions=["Check API configuration"],
                reasoning=f"Provider error: {str(e)}",
                processing_time=processing_time,
                token_usage=0,
                cost_estimate=0.0
            )
    
    def _create_mock_result(self, pipeline_name: str, error_message: str, start_time: float) -> AnalysisResult:
        """Create mock result when Google is not available"""
        processing_time = time.time() - start_time
        
        return AnalysisResult(
            success=True,
            provider_id=self.provider_id,
            error_type="unknown",
            confidence_score=60,
            should_retry=False,
            analysis_summary="Mock Google analysis",
            recommended_actions=["Manual review"],
            reasoning="Mock analysis - Google not available",
            processing_time=processing_time,
            token_usage=100,
            cost_estimate=self.calculate_cost(100)
        )

class EnterpriseAIManager:
    """Enterprise AI manager with multi-provider support"""
    
    def __init__(self):
        self.providers: Dict[str, BaseAIProvider] = {}
        self.provider_configs: List[Dict[str, Any]] = []
        self.primary_provider_id: Optional[str] = None
        self.fallback_enabled: bool = True
        self.ensemble_enabled: bool = False
        
        # Load configurations
        self._load_provider_configs()
        self._initialize_providers()
    
    def _load_provider_configs(self):
        """Load AI provider configurations"""
        # This would typically load from the enterprise config
        # For now, using default configurations
        self.provider_configs = [
            {
                "provider_id": "openai-gpt4",
                "provider_name": "OpenAI GPT-4",
                "provider_class": "OpenAIProvider",
                "model_name": "gpt-4",
                "api_key": "your-openai-api-key",
                "temperature": 0.3,
                "max_tokens": 1000,
                "top_p": 0.9,
                "cost_per_1k_tokens": 0.03,
                "active": True
            },
            {
                "provider_id": "anthropic-claude",
                "provider_name": "Anthropic Claude",
                "provider_class": "AnthropicProvider",
                "model_name": "claude-3-sonnet-20240229",
                "api_key": "your-anthropic-api-key",
                "temperature": 0.3,
                "max_tokens": 1000,
                "cost_per_1k_tokens": 0.015,
                "active": False
            },
            {
                "provider_id": "google-gemini",
                "provider_name": "Google Gemini",
                "provider_class": "GoogleProvider",
                "model_name": "gemini-pro",
                "api_key": "your-google-api-key",
                "temperature": 0.3,
                "max_tokens": 1000,
                "cost_per_1k_tokens": 0.025,
                "active": False
            }
        ]
        
        # Set primary provider
        active_providers = [p for p in self.provider_configs if p.get("active", False)]
        if active_providers:
            self.primary_provider_id = active_providers[0]["provider_id"]
    
    def _initialize_providers(self):
        """Initialize AI provider instances"""
        provider_classes = {
            "OpenAIProvider": OpenAIProvider,
            "AnthropicProvider": AnthropicProvider,
            "GoogleProvider": GoogleProvider
        }
        
        for config in self.provider_configs:
            if config.get("active", False):
                provider_class_name = config.get("provider_class")
                provider_class = provider_classes.get(provider_class_name)
                
                if provider_class:
                    try:
                        provider = provider_class(config)
                        self.providers[config["provider_id"]] = provider
                    except Exception as e:
                        logging.error(f"Failed to initialize provider {config['provider_id']}: {e}")
    
    async def analyze_error(self, pipeline_name: str, error_message: str, 
                          run_id: str, context: Dict[str, Any] = None) -> AnalysisResult:
        """Analyze error using the configured AI strategy"""
        
        if self.ensemble_enabled:
            return await self._ensemble_analysis(pipeline_name, error_message, run_id, context)
        else:
            return await self._single_provider_analysis(pipeline_name, error_message, run_id, context)
    
    async def _single_provider_analysis(self, pipeline_name: str, error_message: str, 
                                       run_id: str, context: Dict[str, Any] = None) -> AnalysisResult:
        """Analyze using single provider with fallback"""
        
        # Try primary provider first
        if self.primary_provider_id and self.primary_provider_id in self.providers:
            provider = self.providers[self.primary_provider_id]
            result = await provider.analyze_error(pipeline_name, error_message, run_id, context)
            
            if result.success:
                return result
        
        # Try fallback providers if primary fails
        if self.fallback_enabled:
            for provider_id, provider in self.providers.items():
                if provider_id != self.primary_provider_id:
                    result = await provider.analyze_error(pipeline_name, error_message, run_id, context)
                    if result.success:
                        return result
        
        # Return failure result if all providers fail
        return AnalysisResult(
            success=False,
            provider_id="none",
            error_type="unknown",
            confidence_score=0,
            should_retry=False,
            analysis_summary="All AI providers failed",
            recommended_actions=["Manual review required"],
            reasoning="No AI providers available",
            processing_time=0.0,
            token_usage=0,
            cost_estimate=0.0
        )
    
    async def _ensemble_analysis(self, pipeline_name: str, error_message: str, 
                                run_id: str, context: Dict[str, Any] = None) -> AnalysisResult:
        """Analyze using ensemble of multiple providers"""
        
        results = []
        
        # Get analysis from all available providers
        tasks = []
        for provider in self.providers.values():
            task = provider.analyze_error(pipeline_name, error_message, run_id, context)
            tasks.append(task)
        
        if tasks:
            provider_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in provider_results:
                if isinstance(result, AnalysisResult) and result.success:
                    results.append(result)
        
        if not results:
            return AnalysisResult(
                success=False,
                provider_id="ensemble",
                error_type="unknown",
                confidence_score=0,
                should_retry=False,
                analysis_summary="Ensemble analysis failed",
                recommended_actions=["Manual review required"],
                reasoning="No successful provider results",
                processing_time=0.0,
                token_usage=0,
                cost_estimate=0.0
            )
        
        # Aggregate results
        return self._aggregate_ensemble_results(results)
    
    def _aggregate_ensemble_results(self, results: List[AnalysisResult]) -> AnalysisResult:
        """Aggregate multiple AI provider results into a single result"""
        
        if not results:
            return AnalysisResult(
                success=False,
                provider_id="ensemble",
                error_type="unknown",
                confidence_score=0,
                should_retry=False,
                analysis_summary="No results to aggregate",
                recommended_actions=[],
                reasoning="No provider results",
                processing_time=0.0,
                token_usage=0,
                cost_estimate=0.0
            )
        
        # Count error types
        error_types = [r.error_type for r in results]
        error_type_counts = {et: error_types.count(et) for et in set(error_types)}
        consensus_error_type = max(error_type_counts, key=error_type_counts.get)
        
        # Average confidence
        avg_confidence = sum(r.confidence_score for r in results) / len(results)
        
        # Majority vote on retry recommendation
        retry_votes = sum(1 for r in results if r.should_retry)
        should_retry = retry_votes > len(results) / 2
        
        # Combine recommended actions
        all_actions = []
        for r in results:
            all_actions.extend(r.recommended_actions)
        unique_actions = list(set(all_actions))
        
        # Aggregate other metrics
        total_processing_time = sum(r.processing_time for r in results)
        total_token_usage = sum(r.token_usage for r in results)
        total_cost = sum(r.cost_estimate for r in results)
        
        return AnalysisResult(
            success=True,
            provider_id="ensemble",
            error_type=consensus_error_type,
            confidence_score=int(avg_confidence),
            should_retry=should_retry,
            analysis_summary=f"Ensemble analysis from {len(results)} providers",
            recommended_actions=unique_actions,
            reasoning=f"Consensus from {len(results)} AI providers",
            processing_time=total_processing_time,
            token_usage=total_token_usage,
            cost_estimate=total_cost
        )
    
    def get_provider_metrics(self) -> List[Dict[str, Any]]:
        """Get performance metrics for all providers"""
        return [provider.get_metrics() for provider in self.providers.values()]
    
    def add_provider(self, config: Dict[str, Any]) -> bool:
        """Add a new AI provider"""
        try:
            provider_classes = {
                "OpenAIProvider": OpenAIProvider,
                "AnthropicProvider": AnthropicProvider,
                "GoogleProvider": GoogleProvider
            }
            
            provider_class_name = config.get("provider_class")
            provider_class = provider_classes.get(provider_class_name)
            
            if provider_class:
                provider = provider_class(config)
                self.providers[config["provider_id"]] = provider
                self.provider_configs.append(config)
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"Failed to add provider: {e}")
            return False
    
    def remove_provider(self, provider_id: str) -> bool:
        """Remove an AI provider"""
        if provider_id in self.providers:
            del self.providers[provider_id]
            self.provider_configs = [c for c in self.provider_configs if c["provider_id"] != provider_id]
            
            # Update primary provider if needed
            if self.primary_provider_id == provider_id:
                active_providers = [p for p in self.provider_configs if p.get("active", False)]
                self.primary_provider_id = active_providers[0]["provider_id"] if active_providers else None
            
            return True
        
        return False
    
    def set_primary_provider(self, provider_id: str) -> bool:
        """Set the primary AI provider"""
        if provider_id in self.providers:
            self.primary_provider_id = provider_id
            return True
        return False
    
    def enable_ensemble(self, enabled: bool = True):
        """Enable or disable ensemble analysis"""
        self.ensemble_enabled = enabled
    
    def enable_fallback(self, enabled: bool = True):
        """Enable or disable fallback to other providers"""
        self.fallback_enabled = enabled

# Global AI manager instance
ai_manager = EnterpriseAIManager()

def get_ai_manager() -> EnterpriseAIManager:
    """Get the global AI manager instance"""
    return ai_manager
