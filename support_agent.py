from typing import TypedDict
from langgraph.graph import StateGraph, END


# ==========================================
# STATE
# ==========================================

class SupportState(TypedDict):
    user_query: str
    intent: str
    tool_result: str
    final_response: str


# ==========================================
# NODE 1 - ANALYZE INTENT
# ==========================================

def analyze_intent(state: SupportState):

    query = state["user_query"].lower()

    print("\n[Analyze Intent Node]")
    print(f"Query Received : {query}")

    if "account" in query:
        intent = "account"
    else:
        intent = "faq"

    print(f"Intent Detected: {intent}")

    return {
        "intent": intent
    }


# ==========================================
# NODE 2A - FAQ SERVICE
# ==========================================

def faq_tool(state: SupportState):

    print("\n[FAQ Tool Node]")

    return {
        "tool_result":
        "You can reset your password using the Forgot Password option."
    }


# ==========================================
# NODE 2B - ACCOUNT SERVICE
# ==========================================

def account_tool(state: SupportState):

    print("\n[Account Tool Node]")

    return {
        "tool_result":
        "Account Status = Active"
    }


# ==========================================
# NODE 3 - GENERATE RESPONSE
# ==========================================

def generate_response(state: SupportState):

    print("\n[Generate Response Node]")

    return {
        "final_response":
        f"Support Response: {state['tool_result']}"
    }


# ==========================================
# ROUTING FUNCTION
# ==========================================

def route_intent(state: SupportState):

    print("\n[Routing Decision]")

    return state["intent"]


# ==========================================
# BUILD GRAPH
# ==========================================

builder = StateGraph(SupportState)

# Add Nodes

builder.add_node("analyze", analyze_intent)
builder.add_node("faq_tool", faq_tool)
builder.add_node("account_tool", account_tool)
builder.add_node("generate_response", generate_response)


# Entry Point

builder.set_entry_point("analyze")

# Conditional Routing

builder.add_conditional_edges(
    "analyze",
    route_intent,
    {
        "faq": "faq_tool",
        "account": "account_tool"
    }
)

# Remaining Edges

builder.add_edge("faq_tool","generate_response")

builder.add_edge("account_tool","generate_response")

builder.add_edge("generate_response",END)

# Compile

graph = builder.compile()

# ==========================================
# EXECUTION
# ==========================================

initial_state = {

    "user_query": "Show my account details",

    "intent": "",

    "tool_result": "",

    "final_response": ""
}

print("\nInitial State")
print(initial_state)

result = graph.invoke(initial_state)

print("\nFinal State")
print(result)

print("\nFinal Response")
print(result["final_response"])