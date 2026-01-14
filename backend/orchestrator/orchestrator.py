from backend.agents.vision_agent import VisionAgent
from backend.agents.nlp_agent import NLPAgent
from backend.agents.fraud_agent import FraudAgent
from backend.agents.policy_agent import PolicyAgent
from backend.agents.decision_agent import DecisionAgent
from typing import Optional


class Orchestrator:
    def __init__(self):
        self.vision_agent = VisionAgent()
        self.nlp_agent = NLPAgent()
        self.fraud_agent = FraudAgent()
        self.policy_agent = PolicyAgent()
        self.decision_agent = DecisionAgent()

    async def run_pipeline(self, file_path: str, progress_tracker=None):
        """
        Run the complete processing pipeline with optional progress tracking
        
        Args:
            file_path: Path to invoice file
            progress_tracker: Optional ProgressTracker for real-time updates
        """
        print(f"Starting pipeline for {file_path}")
        
        # Step 1: Vision Agent (OCR)
        if progress_tracker:
            await progress_tracker.start_step(0)
        
        vision_result = await self.vision_agent.process(file_path)
        
        if progress_tracker:
            await progress_tracker.complete_step(0, {
                "text_length": len(vision_result.get("raw_text", "")),
                "confidence": vision_result.get("confidence", 0)
            })
        
        # Step 2: NLP Agent (Extraction)
        if progress_tracker:
            await progress_tracker.start_step(1)
        
        extraction_result = await self.nlp_agent.extract(vision_result["raw_text"])
        
        if progress_tracker:
            await progress_tracker.complete_step(1, {
                "invoice_number": extraction_result.get("invoice_number"),
                "vendor": extraction_result.get("vendor"),
                "amount": extraction_result.get("total_amount"),
                "confidence": extraction_result.get("confidence", 0)
            })
        
        # Step 3: Fraud Agent
        if progress_tracker:
            await progress_tracker.start_step(2)
        
        fraud_result = await self.fraud_agent.detect(extraction_result)
        
        if progress_tracker:
            await progress_tracker.complete_step(2, {
                "risk_level": fraud_result.get("risk_level"),
                "risk_score": fraud_result.get("risk_score"),
                "is_suspicious": fraud_result.get("is_suspicious"),
                "flags_count": len(fraud_result.get("flags", []))
            })
        
        # Step 4: Policy Agent
        if progress_tracker:
            await progress_tracker.start_step(3)
        
        policy_result = await self.policy_agent.check_compliance(extraction_result)
        
        if progress_tracker:
            await progress_tracker.complete_step(3, {
                "compliant": policy_result.get("compliant"),
                "approval_level": policy_result.get("approval_level"),
                "violations_count": len(policy_result.get("violations", [])),
                "warnings_count": len(policy_result.get("warnings", []))
            })
        
        # Step 5: Decision Agent
        if progress_tracker:
            await progress_tracker.start_step(4)
        
        final_decision = await self.decision_agent.decide(extraction_result, fraud_result, policy_result)
        
        if progress_tracker:
            await progress_tracker.complete_step(4, {
                "decision": final_decision.get("decision"),
                "confidence": final_decision.get("confidence"),
                "reason": final_decision.get("reason")
            })
        
        return {
            "ocr_text": vision_result.get("raw_text"),
            "extraction": extraction_result,
            "fraud": fraud_result,
            "policy": policy_result,
            "decision": final_decision
        }
