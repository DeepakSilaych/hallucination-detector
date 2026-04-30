from state import GraphState
from utils.llm import get_llm
from prompts import EXPERT_PERSONA, EXPERT_ANSWER

EXPERT_COUNT = 3


def run(state: GraphState) -> dict:
    query = state["query"]
    llm = get_llm(temperature=0.0)
    creative_llm = get_llm(temperature=0.7)

    experts: list[dict] = []
    previous_personas: list[str] = []

    for i in range(EXPERT_COUNT):
        persona_response = creative_llm.invoke(
            EXPERT_PERSONA.format(
                query=query,
                index=i + 1,
                previous=", ".join(previous_personas) if previous_personas else "none",
            )
        )
        persona = persona_response.content.strip()
        previous_personas.append(persona)

        answer_response = llm.invoke(
            EXPERT_ANSWER.format(persona=persona, query=query)
        )

        experts.append({
            "persona": persona,
            "answer": answer_response.content.strip(),
        })

    return {"expert_analyses": experts}
