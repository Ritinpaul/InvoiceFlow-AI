class DecisionAgent:
    def __init__(self):
        self.name = "Decision Agent"

    async def decide(self, extraction_data: dict, fraud_results: dict, policy_results: dict):
        """
        Make the final approval decision based on all agent outputs.
        
        Decision Logic:
        - REJECT: If high-risk fraud OR critical policy violations
        - HOLD: If medium fraud risk OR policy warnings OR requires high-level approval
        - APPROVE: If low/minimal fraud risk AND policy compliant AND within auto-approve limits
        """
        print(f"[{self.name}] Making final decision...")
        
        # Extract key metrics
        fraud_risk = fraud_results.get("risk_score", 0)
        fraud_level = fraud_results.get("risk_level", "MINIMAL")
        is_suspicious = fraud_results.get("is_suspicious", False)
        
        policy_compliant = policy_results.get("compliant", False)
        policy_violations = policy_results.get("violations", [])
        policy_warnings = policy_results.get("warnings", [])
        approval_level = policy_results.get("approval_level", "auto_approve")
        
        amount = extraction_data.get("total_amount", 0)
        vendor = extraction_data.get("vendor", "Unknown")
        confidence = extraction_data.get("confidence", 0)
        
        # Decision logic
        decision = "APPROVE"
        reason = "All checks passed"
        confidence_score = 0.95
        
        # Critical rejections (highest priority)
        if fraud_level == "HIGH" or fraud_risk >= 0.7:
            decision = "REJECT"
            reason = f"High fraud risk detected (score: {fraud_risk:.2f})"
            confidence_score = 0.95
            
        elif len(policy_violations) > 0:
            decision = "REJECT"
            reason = f"Policy violations: {'; '.join(policy_violations[:2])}"  # Show first 2
            confidence_score = 0.90
            
        # Hold for review (medium priority)
        elif fraud_level == "MEDIUM" or fraud_risk >= 0.4:
            decision = "HOLD"
            reason = f"Medium fraud risk ({fraud_risk:.2f}) - requires manual review"
            confidence_score = 0.80
            
        elif approval_level in ["requires_cfo", "requires_board"]:
            decision = "HOLD"
            approver = policy_results.get("approver_required", "senior management")
            reason = f"Amount ${amount:,.2f} requires {approver} approval"
            confidence_score = 0.85
            
        elif len(policy_warnings) > 2:
            decision = "HOLD"
            reason = f"Multiple policy warnings ({len(policy_warnings)}) - verify before approval"
            confidence_score = 0.75
            
        elif confidence < 0.75:
            decision = "HOLD"
            reason = f"Low extraction confidence ({confidence:.0%}) - verify invoice details"
            confidence_score = 0.70
            
        # Approve with conditions
        elif approval_level == "requires_director":
            decision = "HOLD"
            reason = f"Amount ${amount:,.2f} requires director approval"
            confidence_score = 0.85
            
        elif approval_level == "requires_manager":
            decision = "APPROVE"
            reason = f"Approved pending manager confirmation (amount: ${amount:,.2f})"
            confidence_score = 0.80
            
        elif fraud_level == "LOW" or (is_suspicious and fraud_risk < 0.3):
            decision = "APPROVE"
            reason = f"Approved with minor fraud flags - monitor {vendor}"
            confidence_score = 0.75
            
        else:
            # Clean approval
            decision = "APPROVE"
            reason = f"All checks passed - invoice from {vendor} for ${amount:,.2f}"
            confidence_score = 0.95
        
        # Build detailed recommendation
        recommendation = self._build_recommendation(
            decision, fraud_results, policy_results, extraction_data
        )
        
        result = {
            "decision": decision,
            "reason": reason,
            "confidence": confidence_score,
            "recommendation": recommendation,
            "summary": {
                "fraud_risk": fraud_level,
                "policy_status": "Compliant" if policy_compliant else "Non-compliant",
                "approval_required": policy_results.get("approver_required", "None"),
                "amount": amount,
                "vendor": vendor
            }
        }
        
        emoji = "✓" if decision == "APPROVE" else "⚠" if decision == "HOLD" else "✗"
        print(f"[{self.name}] {emoji} Decision: {decision} | Confidence: {confidence_score:.0%}")
        
        return result
    
    def _build_recommendation(self, decision: str, fraud: dict, policy: dict, extraction: dict) -> str:
        """Build detailed recommendation text"""
        parts = []
        
        if decision == "APPROVE":
            parts.append("✓ Recommended for approval.")
        elif decision == "HOLD":
            parts.append("⚠ Recommended to HOLD for manual review.")
        else:
            parts.append("✗ Recommended to REJECT.")
        
        # Add fraud context
        if fraud.get("is_suspicious"):
            flags = fraud.get("flags", [])
            parts.append(f"Fraud concerns: {', '.join(flags[:2])}")
        
        # Add policy context
        if not policy.get("compliant"):
            violations = policy.get("violations", [])
            parts.append(f"Policy issues: {', '.join(violations[:2])}")
        
        if policy.get("warnings"):
            parts.append(f"Note: {len(policy.get('warnings', []))} warnings flagged")
        
        return " ".join(parts)
