from typing import TypedDict
from langgraph.graph import StateGraph, END
import time


# ==================================================
# STATE
# ==================================================

class ExpenseState(TypedDict):
    employee_name: str
    amount: int
    status: str


# ==================================================
# MIDDLEWARE
# ==================================================
#
# This middleware executes:
#
# Before Node Execution
# After Node Execution
#
# It logs:
# - Node Name
# - Start Time
# - End Time
# - Execution Duration
#
# ==================================================

def logging_middleware(node_function):

    def wrapper(state):

        print("\n" + "=" * 50)

        print(
            f"[MIDDLEWARE] Node Started -> {node_function.__name__}"
        )

        start_time = time.time()

        result = node_function(state)

        end_time = time.time()

        print(
            f"[MIDDLEWARE] Node Completed -> {node_function.__name__}"
        )

        print(
            f"[MIDDLEWARE] Duration -> {(end_time-start_time):.4f} seconds"
        )

        print("=" * 50)

        return result

    return wrapper


# ==================================================
# NODE 1
# VALIDATE EXPENSE
# ==================================================

def validate_expense(state: ExpenseState):

    print(
        f"Validating expense amount ₹{state['amount']}"
    )

    return {
        "status": "validated"
    }


# ==================================================
# NODE 2
# MANAGER APPROVAL
# ==================================================

def manager_approval(state: ExpenseState):

    print(
        "Manager approved expense request"
    )

    return {
        "status": "approved"
    }


# ==================================================
# NODE 3
# PROCESS PAYMENT
# ==================================================

def process_payment(state: ExpenseState):

    print(
        f"Processing payment for {state['employee_name']}"
    )

    return {
        "status": "payment_completed"
    }


# ==================================================
# GRAPH
# ==================================================

builder = StateGraph(ExpenseState)


# ==================================================
# APPLY MIDDLEWARE TO NODES
# ==================================================
#
# Instead of registering node directly,
# we wrap it with middleware.
#
# ==================================================

builder.add_node(
    "validate_expense",
    logging_middleware(validate_expense)
)

builder.add_node(
    "manager_approval",
    logging_middleware(manager_approval)
)

builder.add_node(
    "process_payment",
    logging_middleware(process_payment)
)


# ==================================================
# ENTRY POINT
# ==================================================

builder.set_entry_point(
    "validate_expense"
)


# ==================================================
# EDGES
# ==================================================

builder.add_edge(
    "validate_expense",
    "manager_approval"
)

builder.add_edge(
    "manager_approval",
    "process_payment"
)

builder.add_edge(
    "process_payment",
    END
)


# ==================================================
# COMPILE
# ==================================================

graph = builder.compile()


# ==================================================
# EXECUTE
# ==================================================

result = graph.invoke(
    {
        "employee_name": "Kedar",
        "amount": 75000,
        "status": ""
    }
)

print("\nFINAL STATE")
print(result)