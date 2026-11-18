from typing import TypedDict
from langgraph.graph import StateGraph, END


# ==================================================
# STATE
# ==================================================

class ExpenseState(TypedDict):
    employee_name: str
    amount: int
    receipt_available: bool
    approval_status: str
    result: str


# ==================================================
# NODE 1 - VALIDATE EXPENSE
# ==================================================

def validate_expense(state: ExpenseState):

    print("\n[Node] Validate Expense")

    amount = state["amount"]
    receipt = state["receipt_available"]

    if not receipt:

        return {
            "approval_status": "reject"
        }

    if amount > 50000:

        print(
            f"Expense amount ₹{amount} requires manager approval"
        )

        return {
            "approval_status": "pending"
        }

    print(
        f"Expense amount ₹{amount} is auto-approved"
    )

    return {
        "approval_status": "approved"
    }


# ==================================================
# NODE 2 - HUMAN APPROVAL
# ==================================================

def manager_approval(state: ExpenseState):

    print("\n[Node] Manager Approval")

    print(
        f"Employee: {state['employee_name']}"
    )

    print(
        f"Amount: ₹{state['amount']}"
    )

    decision = input(
        "\nManager Decision (approve/reject): "
    ).strip().lower()

    return {
        "approval_status": decision
    }


# ==================================================
# NODE 3 - REIMBURSE EMPLOYEE
# ==================================================

def reimburse_employee(state: ExpenseState):

    print("\n[Node] Reimburse Employee")

    return {
        "result":
        f"✅ Expense reimbursed to {state['employee_name']}"
    }


# ==================================================
# NODE 4 - REJECT EXPENSE
# ==================================================

def reject_expense(state: ExpenseState):

    print("\n[Node] Reject Expense")

    return {
        "result":
        f"❌ Expense claim rejected for {state['employee_name']}"
    }


# ==================================================
# ROUTER FUNCTION
# ==================================================

def route_status(state: ExpenseState):

    return state["approval_status"]


# ==================================================
# BUILD GRAPH
# ==================================================

builder = StateGraph(ExpenseState)


# Nodes

builder.add_node(
    "validate_expense",
    validate_expense
)

builder.add_node(
    "manager_approval",
    manager_approval
)

builder.add_node(
    "reimburse_employee",
    reimburse_employee
)

builder.add_node(
    "reject_expense",
    reject_expense
)


# ==================================================
# ENTRY POINT
# ==================================================

builder.set_entry_point(
    "validate_expense"
)


# ==================================================
# CONDITIONAL EDGE 1
# ==================================================
#
# pending  -> manager approval
# approved -> reimburse
# reject   -> reject expense
#
# ==================================================

builder.add_conditional_edges(
    "validate_expense",
    route_status,
    {
        "pending": "manager_approval",
        "approved": "reimburse_employee",
        "reject": "reject_expense"
    }
)

# ==================================================
# CONDITIONAL EDGE 2
# ==================================================
#
# approve -> reimburse
# reject  -> reject expense
#
# ==================================================

builder.add_conditional_edges(
    "manager_approval",
    route_status,
    {
        "approve": "reimburse_employee",
        "reject": "reject_expense"
    }
)

# ==================================================
# FINAL EDGES
# ==================================================

builder.add_edge(
    "reimburse_employee",
    END
)

builder.add_edge(
    "reject_expense",
    END
)


# ==================================================
# COMPILE GRAPH
# ==================================================

graph = builder.compile()


# ==================================================
# INPUT
# ==================================================

initial_state = {
    "employee_name": "Kedar",
    "amount": 75000,
    "receipt_available": True,
    "approval_status": "",
    "result": ""
}


# ==================================================
# EXECUTE GRAPH
# ==================================================

print("\n=== Expense Claim Workflow Started ===")

result = graph.invoke(initial_state)

print("\n=== Final State ===")
print(result)

print("\n=== Final Result ===")
print(result["result"])