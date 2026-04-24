from state import GraphState
from utils.llm import get_llm
from prompts import CONSISTENCY_CHECK
from config import CONSISTENCY_TEMPERATURE, CONSISTENCY_SAMPLES


def run(state: GraphState) -> dict:
    query = state["query"]
    llm = get_llm(temperature=CONSISTENCY_TEMPERATURE)
    answers = []
    for _ in range(CONSISTENCY_SAMPLES):
        response = llm.invoke(CONSISTENCY_CHECK.format(query=query))
        answers.append(response.content)
    return {"consistency_answers": answers}
