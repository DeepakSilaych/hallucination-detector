CLAIM_DECOMPOSE = (
    "You are analyzing an LLM's response for hallucination detection.\n\n"
    "Given the original question, the LLM's reasoning/tool calls, and its final answer, "
    "break down the ENTIRE decision-making chain into independent, atomic factual claims.\n\n"
    "Extract claims from BOTH the reasoning process AND the final answer. "
    "This helps identify WHERE a hallucination was introduced.\n\n"
    "Each claim must be a single verifiable statement. "
    "Do not include opinions or compound claims.\n\n"
    "Question: {query}\n\n"
    "Reasoning/Process:\n{process}\n\n"
    "Final Answer: {answer}\n\n"
    'Return ONLY a JSON array of strings. Example: ["claim one", "claim two"]\n\n'
    "Claims:"
)

EXPERT_PERSONA = (
    "Given the following question, identify the most relevant expert who would be "
    "best qualified to answer it. Return ONLY a short description of the expert "
    "(e.g. 'Astrophysicist specializing in planetary science').\n\n"
    "Question: {query}\n\n"
    "Expert #{index} (choose a different specialty than: {previous}):\n"
    "Expert:"
)

EXPERT_ANSWER = (
    "You are {persona}.\n\n"
    "Answer the following question using your domain expertise. "
    "Be accurate, concise, and cite specific facts where possible.\n\n"
    "Question: {query}\n\n"
    "Answer:"
)

VERIFY_CLAIM = (
    "You are a fact-checking judge. Classify the claim based on the provided evidence.\n\n"
    "Claim: {claim}\n\n"
    "Retrieval Evidence:\n{retrieval_evidence}\n\n"
    "Expert Analysis (answers from domain experts):\n{consistency_evidence}\n\n"
    "Tool Validation Evidence:\n{tool_evidence}\n\n"
    "Classify as exactly one of: Supported, Contradicted, Not Enough Info\n\n"
    "Respond with ONLY the classification.\n\n"
    "Classification:"
)
