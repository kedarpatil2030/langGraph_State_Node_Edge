from typing import TypedDict
from langgraph.graph import StateGraph, END

# -------------------
# 1. Define State
# -------------------
class MyState(TypedDict):
    name: str
    message: str


# -------------------
# 2. Create Nodes
# -------------------
def greet_node(state: MyState):
    print("Running Greeting Node")
    return {
        "message": f"Hello {state['name']}"
    }


def farewell_node(state: MyState):
    print("Running Farewell Node")
    return {
        "message": state["message"] + " | Goodbye!"
    }

def uppercase_node(state):
    return {
        "message": state["message"].upper()
    }

# -------------------
# 3. Build Graph
# -------------------
builder = StateGraph(MyState)

# Add nodes
builder.add_node("greet", greet_node)
builder.add_node("farewell", farewell_node)
builder.add_node("uppercase", uppercase_node)


# Define flow
builder.set_entry_point("greet")
builder.add_edge("greet", "uppercase")
builder.add_edge("uppercase", "farewell")
builder.add_edge("farewell", END)

# Compile graph
graph = builder.compile()


# -------------------
# 4. Execute Graph
# -------------------
result = graph.invoke({
    "name": "Kedar",
    "message": ""
})

print("\nFinal State:")
print(result)