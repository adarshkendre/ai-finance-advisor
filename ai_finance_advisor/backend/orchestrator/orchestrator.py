"""
Orchestrator Agent
------------------
Central coordinator for the AI Money Mentor multi-agent system.
Responsibilities:
  - Route user input to appropriate specialist agents
  - Maintain a full audit trail of every decision
  - Retry failed agents (up to MAX_RETRIES)
  - Detect missing inputs and request clarification
  - Assemble final response from all agent outputs
"""

import time
import traceback
from typing import Any

from agents.input_agent import InputAgent
from agents.analysis_agent import AnalysisAgent
from agents.fire_agent import FireAgent
from agents.tax_agent import TaxAgent
from agents.life_event_agent import LifeEventAgent
from agents.advice_agent import AdviceSynthesisAgent
from agents.guardrail_agent import GuardrailAgent

MAX_RETRIES = 2


class Orchestrator:
    def __init__(self):
        self.input_agent = InputAgent()
        self.analysis_agent = AnalysisAgent()
        self.fire_agent = FireAgent()
        self.tax_agent = TaxAgent()
        self.life_event_agent = LifeEventAgent()
        self.advice_agent = AdviceSynthesisAgent()
        self.guardrail_agent = GuardrailAgent()

    def run(self, raw_input: dict) -> dict:
        audit_trail = []
        start_time = time.time()

        def log(agent: str, status: str, detail: Any = None):
            entry = {
                "agent": agent,
                "status": status,
                "timestamp": round(time.time() - start_time, 3),
            }
            if detail:
                entry["detail"] = detail
            audit_trail.append(entry)

        # ── STEP 1: Input validation & gap detection ──────────────────────────
        validated, missing_fields = self._run_with_retry(
            "InputAgent", log, self.input_agent.run, raw_input
        )
        if missing_fields:
            return {
                "status": "needs_clarification",
                "missing_fields": missing_fields,
                "message": self.input_agent.clarification_message(missing_fields),
                "audit_trail": audit_trail,
            }
        log("InputAgent", "success", {"validated_fields": list(validated.keys())})

        # ── STEP 2: Parallel specialist analysis ─────────────────────────────
        analysis = self._run_with_retry(
            "AnalysisAgent", log, self.analysis_agent.run, validated
        )
        log("AnalysisAgent", "success", {"score": analysis.get("overall_score")})

        fire_plan = self._run_with_retry(
            "FireAgent", log, self.fire_agent.run, validated
        )
        log("FireAgent", "success", {"sip_required": fire_plan.get("sip_required_monthly")})

        tax_result = self._run_with_retry(
            "TaxAgent", log, self.tax_agent.run, validated
        )
        log("TaxAgent", "success", {"recommended_regime": tax_result.get("recommended_regime")})

        # ── STEP 3: Life event (conditional – only if event provided) ─────────
        life_event_result = None
        if validated.get("life_event"):
            life_event_result = self._run_with_retry(
                "LifeEventAgent", log, self.life_event_agent.run, validated
            )
            log("LifeEventAgent", "success", {"event": validated["life_event"]})

        # ── STEP 4: Advice synthesis ──────────────────────────────────────────
        advice = self._run_with_retry(
            "AdviceAgent",
            log,
            self.advice_agent.run,
            analysis, fire_plan, tax_result, life_event_result
        )
        log("AdviceAgent", "success", {"priorities_count": len(advice.get("priorities", []))})

        # ── STEP 5: Guardrail enforcement ────────────────────────────────────
        final_output = self._run_with_retry(
            "GuardrailAgent", log, self.guardrail_agent.run, advice
        )
        log("GuardrailAgent", "success", {"guardrail_rules_applied": len(final_output.get("guardrail_audit", []))})

        log("Orchestrator", "complete", {"total_agents_run": len(audit_trail)})

        return {
            "status": "success",
            "user_profile": validated,
            "money_health_score": analysis,
            "fire_plan": fire_plan,
            "tax_analysis": tax_result,
            "life_event_advice": life_event_result,
            "final_advice": final_output,
            "audit_trail": audit_trail,
            "processing_time_sec": round(time.time() - start_time, 3),
        }

    def _run_with_retry(self, agent_name: str, log, fn, *args):
        """
        Run an agent function with retry logic.
        On failure: logs the error, waits briefly, retries up to MAX_RETRIES.
        On total failure: raises so the caller can return a graceful error.
        """
        last_error = None
        for attempt in range(1, MAX_RETRIES + 2):
            try:
                result = fn(*args)
                if attempt > 1:
                    log(agent_name, f"recovered_on_attempt_{attempt}", None)
                return result
            except Exception as e:
                last_error = e
                log(
                    agent_name,
                    f"error_attempt_{attempt}",
                    {"error": str(e), "trace": traceback.format_exc(limit=3)},
                )
                if attempt <= MAX_RETRIES:
                    time.sleep(0.1 * attempt)

        # All retries exhausted – raise with context
        raise RuntimeError(
            f"{agent_name} failed after {MAX_RETRIES + 1} attempts: {last_error}"
        )
