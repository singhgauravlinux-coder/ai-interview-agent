from app.providers.factory import get_ai_provider

DEFAULT_QUESTIONS = {
 "technical": [
  ("Explain the difference between a list and a tuple in Python.", "Python fundamentals", "easy", ["Mutability", "Use cases"]),
  ("How would you investigate a slow SQL query in production?", "Database optimization", "medium", ["Query plan", "Indexes", "Measurement"]),
  ("Design an API endpoint for creating and retrieving customer orders.", "API design", "medium", ["Resource modeling", "Validation", "Error handling"]),
  ("Describe how you would make a service resilient to transient failures.", "Reliability", "hard", ["Timeouts", "Retries", "Idempotency", "Observability"])
 ],
 "hr": [
  ("What interests you about this role and organization?", "Motivation", "easy", ["Role alignment", "Specific motivation"]),
  ("Tell me about a time you received difficult feedback. What did you do?", "Self-awareness", "medium", ["Situation", "Action", "Learning"]),
  ("Describe a disagreement at work and how you handled it.", "Conflict resolution", "medium", ["Listening", "Resolution", "Outcome"])
 ],
 "managerial": [
  ("How do you set priorities when several projects compete for the same resources?", "Prioritization", "medium", ["Trade-offs", "Alignment", "Communication"]),
  ("Tell me about a time you helped a team member improve performance.", "People leadership", "medium", ["Specific example", "Support", "Outcome"]),
  ("How would you handle a critical delivery that is at risk?", "Execution", "hard", ["Risk assessment", "Options", "Stakeholder communication"])
 ],
 "mixed": [
  ("Walk me through a project relevant to this role.", "Relevant experience", "easy", ["Personal contribution", "Impact"]),
  ("Describe a difficult problem you solved and your approach.", "Problem solving", "medium", ["Decomposition", "Options", "Validation"]),
  ("Tell me about a time you had to influence a stakeholder.", "Communication", "medium", ["Context", "Approach", "Outcome"])
 ]
}

ROLE_QUESTIONS = {
 "devops engineer": [
  ("Walk through how you would design a CI/CD pipeline with quality gates, artifact promotion and rollback.", "CI/CD engineering", "medium", ["Pipeline stages", "Quality gates", "Immutable artifacts", "Rollback strategy"]),
  ("A Kubernetes deployment is stuck in CrashLoopBackOff. Describe your investigation sequence.", "Kubernetes operations", "medium", ["Events and logs", "Probes", "Configuration and dependencies", "Root cause"]),
  ("How would you manage Terraform state and prevent unsafe concurrent infrastructure changes?", "Infrastructure as code", "hard", ["Remote state", "Locking", "Plan review", "Drift detection"]),
  ("A production release causes elevated latency. How do you mitigate impact and establish the cause?", "Release reliability", "hard", ["Rollback or roll-forward", "Telemetry", "Communication", "Post-incident actions"]),
 ],
 "site reliability engineer": [
  ("How would you define an SLI and SLO for a customer-facing API, and use an error budget?", "SLO engineering", "medium", ["User-centric indicators", "Target and window", "Error budget policy"]),
  ("Describe your response to a high-severity incident affecting multiple services.", "Incident management", "hard", ["Triage", "Mitigation", "Roles and communication", "Learning review"]),
  ("How would you reduce alert fatigue while ensuring actionable detection?", "Observability", "medium", ["Symptom-based alerts", "SLO burn rates", "Ownership", "Runbooks"]),
  ("A service is approaching capacity during a traffic spike. What options do you evaluate?", "Capacity and resilience", "hard", ["Load shedding", "Autoscaling", "Bottleneck analysis", "Cost and risk trade-offs"]),
 ],
 "production support engineer": [
  ("A customer reports intermittent transaction failures. Explain how you triage the issue from first report to resolution.", "Production troubleshooting", "medium", ["Scope and impact", "Logs and metrics", "Reproduction", "Communication"]),
  ("How do you investigate a slow SQL query without creating additional production risk?", "Database diagnostics", "medium", ["Query plan", "Indexes", "Locking", "Safe measurement"]),
  ("Describe how you perform root-cause analysis after a recurring production incident.", "Problem management", "medium", ["Timeline", "Contributing factors", "Corrective actions", "Verification"]),
  ("A critical issue is outside your team's ownership. How do you manage escalation and keep stakeholders informed?", "Escalation management", "medium", ["Evidence package", "Ownership", "Impact updates", "Follow-through"]),
 ],
 "cloud engineer": [
  ("Design a secure network layout for a multi-tier application in a public cloud.", "Cloud networking", "medium", ["Network segmentation", "Private endpoints", "Ingress and egress", "Security groups"]),
  ("How would you structure IAM permissions for an application running in Kubernetes?", "Cloud identity", "hard", ["Least privilege", "Workload identity", "Secret handling", "Rotation"]),
  ("Describe how you would provision repeatable cloud infrastructure across environments.", "Cloud automation", "medium", ["IaC modules", "State", "Environment separation", "Policy checks"]),
  ("Cloud spend increased by 35% in a month. How do you identify the drivers and reduce cost safely?", "FinOps", "medium", ["Cost allocation", "Usage analysis", "Rightsizing", "Guardrails"]),
 ],
 "backend engineer": [
  ("Design an idempotent API for processing payment requests under retry conditions.", "API design", "hard", ["Idempotency keys", "Transactions", "Concurrency", "Failure semantics"]),
  ("How would you diagnose and improve a slow endpoint backed by PostgreSQL?", "Performance engineering", "medium", ["Profiling", "Query plans", "Indexes", "Caching trade-offs"]),
  ("Describe how you would evolve an API without breaking existing clients.", "API lifecycle", "medium", ["Compatibility", "Versioning", "Deprecation", "Contract tests"]),
  ("How do you test a distributed workflow that can partially fail?", "Reliability testing", "hard", ["Unit and integration tests", "Fault injection", "Retries", "Observability"]),
 ],
 "technical support engineer": [
  ("A customer cannot connect to your service. Walk through a structured network troubleshooting approach.", "Network diagnostics", "medium", ["DNS", "Connectivity", "TLS", "Client-side versus server-side isolation"]),
  ("How do you turn an unclear customer problem into a reproducible technical issue?", "Customer troubleshooting", "medium", ["Clarifying questions", "Environment details", "Reproduction", "Evidence"]),
  ("Describe how you prioritize several customer-impacting tickets with different severities.", "Support operations", "medium", ["Impact and urgency", "SLA", "Communication", "Escalation"]),
  ("How would you explain a complex technical workaround to a non-technical customer?", "Technical communication", "easy", ["Plain language", "Steps", "Validation", "Expectation setting"]),
 ],
}

def generate_questions(category: str, job_title: str, skills: list[str], experience: str):
    system = (
        "You design structured, fair, job-related interviews. "
        "Do not use protected characteristics. Return valid JSON only."
    )
    prompt = f"""
Create 4 to 6 concise, job-relevant interview questions.
Interview category: {category}
Job title: {job_title}
Experience level: {experience}
Required skills: {skills}
Return JSON: {{"questions":[{{"question":"string","competency":"string",
"difficulty":"easy|medium|hard","expected_evidence":["string"]}}]}}.
Avoid duplicate questions.
"""
    try:
        data = get_ai_provider().generate_json(system_prompt=system, user_prompt=prompt, temperature=0.4)
        questions = data.get("questions", [])
        if questions:
            return questions[:8]
    except Exception:
        # A configured provider failure falls back to the deterministic local question bank.
        # Production should additionally log provider errors and surface degraded-mode status.
        pass
    role_rows = ROLE_QUESTIONS.get(job_title.strip().lower()) if category in ("technical", "mixed") else None
    rows = role_rows or DEFAULT_QUESTIONS.get(category, DEFAULT_QUESTIONS["mixed"])
    return [{"question": q, "competency": c, "difficulty": d, "expected_evidence": e}
            for q, c, d, e in rows]

def evaluate_answer(question: str, answer: str, competency: str):
    system = (
        "You are an evidence-based interview evaluator. "
        "Do not assess accent, appearance, emotion, gender, age, disability or personality."
    )
    prompt = f"""
Evaluate only job-related evidence.
Competency: {competency}
Question: {question}
Candidate answer: {answer}

Use a 1-5 scale:
1 incorrect/no relevant understanding; 2 limited with major gaps;
3 basic/partial; 4 strong and relevant; 5 excellent with depth/application.

Return JSON:
{{"score":1,"strengths":["specific observed strength"],
"gaps":["specific gap"],"evidence":["answer evidence"],
"rationale":"brief explanation","confidence":"low|medium|high"}}.

Do not reward length alone. Accept valid alternative approaches.
Do not infer knowledge not demonstrated. If evidence is insufficient,
say so and use low confidence.
"""
    try:
        result = get_ai_provider().generate_json(system_prompt=system, user_prompt=prompt, temperature=0)
        result["score"] = max(1, min(5, float(result.get("score", 3))))
        result["evaluation_status"] = "ai"
        return result
    except Exception as exc:
        return {
            "score": 3, "strengths": [],
            "gaps": ["AI evaluation unavailable; human review required."],
            "evidence": [answer[:500]],
            "rationale": f"Fallback placeholder, not an AI assessment ({type(exc).__name__}).",
            "confidence": "low", "evaluation_status": "fallback"
        }
