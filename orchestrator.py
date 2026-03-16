# orchestrator.py
from agents import DataCollectorAgent, AnalysisAgent, InsightsAgent
from safety import SafetyValidator, ConfidenceScorer
from error_handling import RetryHandler, FailureHandler, ExecutionLogger
from datetime import datetime

class MultiAgentOrchestrator:
    """Production-ready orchestrator with safety and error handling"""
    
    def __init__(self):
        # Agents
        self.data_collector = DataCollectorAgent()
        self.analyzer = AnalysisAgent()
        self.insights_generator = InsightsAgent()
        
        # Safety and error handling
        self.safety = SafetyValidator()
        self.confidence_scorer = ConfidenceScorer()
        self.retry_handler = RetryHandler(max_retries=3)
        self.failure_handler = FailureHandler()
        self.logger = ExecutionLogger()
        
        self.execution_log = []
    
    def run(self, query: str) -> dict:
        """
        Execute multi-agent workflow with safety checks
        """
        start_time = datetime.now()
        
        # Step 1: Validate input
        self.logger.log_event("input_validation", "system", {"query": query})
        
        is_valid, sanitized_query, input_warnings = self.safety.validate_input(query)
        
        if not is_valid:
            return {
                "success": False,
                "error": "Input validation failed",
                "warnings": input_warnings,
                "requires_human_review": True
            }
        
        # Use sanitized query
        query = sanitized_query
        
        # Step 2: Execute agents with retry logic
        all_warnings = input_warnings.copy()
        error_count = 0
        
        # Data Collection with retry
        success, data_result, errors = self.retry_handler.execute_with_retry(
            self.data_collector.execute,
            query
        )
        
        if not success:
            error_count += 1
            data_result = self.failure_handler.get_fallback_response(
                "Data Collector",
                str(errors[-1]["error"]) if errors else "Unknown error"
            )
        
        self.logger.log_event("data_collection", "Data Collector", data_result, success)
        
        # Validate data collector output
        is_valid_output, sanitized_output, output_warnings = self.safety.validate_output(
            data_result["output"]
        )
        
        if output_warnings:
            all_warnings.extend(output_warnings)
        
        data_result["output"] = sanitized_output
        data_result["confidence"] = self.confidence_scorer.calculate_confidence(
            sanitized_output,
            "Data Collector"
        )
        
        self.execution_log.append(data_result)
        
        # Analysis with retry
        success, analysis_result, errors = self.retry_handler.execute_with_retry(
            self.analyzer.execute,
            query=query,
            data_collected=data_result["output"]
        )
        
        if not success:
            error_count += 1
            analysis_result = self.failure_handler.get_fallback_response(
                "Analysis Agent",
                str(errors[-1]["error"]) if errors else "Unknown error"
            )
        
        self.logger.log_event("analysis", "Analysis Agent", analysis_result, success)
        
        # Validate analysis output
        is_valid_output, sanitized_output, output_warnings = self.safety.validate_output(
            analysis_result["output"]
        )
        
        if output_warnings:
            all_warnings.extend(output_warnings)
        
        analysis_result["output"] = sanitized_output
        analysis_result["confidence"] = self.confidence_scorer.calculate_confidence(
            sanitized_output,
            "Analysis Agent"
        )
        
        self.execution_log.append(analysis_result)
        
        # Insights with retry
        success, insights_result, errors = self.retry_handler.execute_with_retry(
            self.insights_generator.execute,
            query=query,
            analysis=analysis_result["output"]
        )
        
        if not success:
            error_count += 1
            insights_result = self.failure_handler.get_fallback_response(
                "Insights Agent",
                str(errors[-1]["error"]) if errors else "Unknown error"
            )
        
        self.logger.log_event("insights", "Insights Agent", insights_result, success)
        
        # Validate insights output
        is_valid_output, sanitized_output, output_warnings = self.safety.validate_output(
            insights_result["output"]
        )
        
        if output_warnings:
            all_warnings.extend(output_warnings)
        
        insights_result["output"] = sanitized_output
        insights_result["confidence"] = self.confidence_scorer.calculate_confidence(
            sanitized_output,
            "Insights Agent"
        )
        
        self.execution_log.append(insights_result)
        
        # Step 3: Determine if human review needed
        avg_confidence = sum(
            r.get("confidence", 0.5) for r in self.execution_log
        ) / len(self.execution_log)
        
        needs_review, review_reason = self.failure_handler.should_trigger_human_review(
            confidence_score=avg_confidence,
            error_count=error_count,
            warnings=all_warnings
        )
        
        # Step 4: Consolidate results
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        report = {
            "success": True,
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "execution_time_seconds": round(execution_time, 2),
            "agents_executed": len(self.execution_log),
            "results": {
                "data_collection": data_result["output"],
                "analysis": analysis_result["output"],
                "insights": insights_result["output"]
            },
            "safety": {
                "input_sanitized": query != sanitized_query,
                "warnings": all_warnings,
                "confidence_scores": {
                    "data_collection": data_result.get("confidence", 0),
                    "analysis": analysis_result.get("confidence", 0),
                    "insights": insights_result.get("confidence", 0),
                    "average": round(avg_confidence, 2)
                }
            },
            "reliability": {
                "error_count": error_count,
                "retry_attempts": error_count * 3,  # rough estimate
                "fallbacks_used": sum(1 for r in self.execution_log if r.get("status") == "fallback")
            },
            "human_review": {
                "required": needs_review,
                "reason": review_reason if needs_review else "All checks passed"
            },
            "execution_log": self.execution_log,
            "detailed_logs": self.logger.get_execution_summary()
        }
        
        return report