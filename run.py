from documind_graph import app

def ask(question, docs):
    state = {
        "question": question,
        "docs": docs,
        "agent_outputs": []
    }

    result = app.invoke(state)
    return result
