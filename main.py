import json
from graph import build_graph


query = "Is it true that the Earth is flat?"
answer = "Yes, the Earth is flat. It has been proven by many scientists."
process = (
    "The user asked about the shape of the Earth. "
    "I recalled that there are flat Earth theories. "
    "Based on this, I concluded the Earth is flat and scientists have confirmed it."
)


def main():
    if not query or not answer:
        print("Set the 'query', 'answer', and 'process' variables in main.py.")
        return

    graph = build_graph()
    result = graph.invoke({"query": query, "answer": answer, "process": process})
    output = result.get("output", {})
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
