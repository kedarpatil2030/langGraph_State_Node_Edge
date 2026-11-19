# ==========================================================
# IMPORTS
# ==========================================================

from typing import TypedDict

# Core LangGraph components
from langgraph.graph import StateGraph, END

# Required for Human-in-the-Loop
from langgraph.types import interrupt, Command

# Required to save workflow state when interrupted
from langgraph.checkpoint.memory import MemorySaver


# ==========================================================
# STATE
# ==========================================================
#
# State is shared across all nodes.
# Every node can read and update this state.
#
# ==========================================================

class ExpenseState(TypedDict):
    employee_name: str
    amount: int
    approval_status: str
    result: str


# ==========================================================
# NODE 1 : VALIDATE EXPENSE
# ==========================================================
#
# Purpose:
# - Check expense amount
# - Small expenses are auto-approved
# - Large expenses require manager approval
#
# ==========================================================

def validate_expense(state: ExpenseState):

    print("\n[Node] validate_expense")

    # If amount exceeds business threshold
    # require manager approval.
    if state["amount"] > 50000:

        print(
            f"Expense ₹{state['amount']} requires manager approval"
        )

        return {
            "approval_status": "pending"
        }

    # Auto approve smaller expenses
    return {
        "approval_status": "approved"
    }


# ==========================================================
# NODE 2 : HUMAN-IN-THE-LOOP
# ==========================================================
#
# interrupt()
#
# This pauses the workflow.
#
# State is saved by MemorySaver.
#
# Workflow waits for human action.
#
# Once user approves/rejects,
# graph continues from here.
#
# ==========================================================

def manager_approval(state: ExpenseState):

    print("\n[Node] manager_approval")

    approval = interrupt(

        {
            "message":
                f"Approve expense claim of ₹{state['amount']} ?",

            "employee":
                state["employee_name"]
        }

    )

    # Execution resumes here after
    # Command(resume="approve")
    #
    # or
    #
    # Command(resume="reject")

    return {
        "approval_status": approval
    }


# ==========================================================
# NODE 3 : PROCESS PAYMENT
# ==========================================================
#
# Executes when expense is approved.
#
# In real projects this could:
# - Create payment record
# - Call ERP system
# - Update SQL Database
# - Trigger Power Automate Flow
#
# ==========================================================

def process_payment(state: ExpenseState):

    print("\n[Node] process_payment")

    return {
        "result":
        f"✅ Expense approved for {state['employee_name']}"
    }


# ==========================================================
# NODE 4 : REJECT CLAIM
# ==========================================================
#
# Executes when manager rejects.
#
# ==========================================================

def reject_claim(state: ExpenseState):

    print("\n[Node] reject_claim")

    return {
        "result":
        f"❌ Expense rejected for {state['employee_name']}"
    }


# ==========================================================
# ROUTER FUNCTION
# ==========================================================
#
# Conditional edges use this function.
#
# Returns:
# - pending
# - approved
# - approve
# - reject
#
# Based on return value LangGraph
# decides next node.
#
# ==========================================================

def route_approval(state: ExpenseState):

    return state["approval_status"]


# ==========================================================
# BUILD GRAPH
# ==========================================================

builder = StateGraph(ExpenseState)


# ==========================================================
# REGISTER NODES
# ==========================================================
#
# Format:
#
# builder.add_node(
#     "NodeName",
#     function_name
# )
#
# ==========================================================

builder.add_node(
    "validate_expense",
    validate_expense
)

builder.add_node(
    "manager_approval",
    manager_approval
)

builder.add_node(
    "process_payment",
    process_payment
)

builder.add_node(
    "reject_claim",
    reject_claim)


# ==========================================================
# ENTRY POINT
# ==========================================================
#
# Graph execution starts here.
#
# START
#   |
#   v
# validate_expense
#
# ==========================================================

builder.set_entry_point(
    "validate_expense"
)


# ==========================================================
# CONDITIONAL EDGE #1
# ==========================================================
#
# After validate_expense node:
#
# pending
#   |
#   v
# manager_approval
#
# approved
#   |
#   v
# process_payment
#
# ==========================================================

builder.add_conditional_edges(
    "validate_expense",
    route_approval,
    {
        "pending": "manager_approval",
        "approved": "process_payment"
    }
)


# ==========================================================
# CONDITIONAL EDGE #2
# ==========================================================
#
# After manager_approval:
#
# approve
#   |
#   v
# process_payment
#
# reject
#   |
#   v
# reject_claim
#
# ==========================================================

builder.add_conditional_edges(
    "manager_approval",
    route_approval,
    {
        "approve": "process_payment",
        "reject": "reject_claim"
    }
)


# ==========================================================
# FINAL EDGES
# ==========================================================
#
# Approved workflow ends.
#
# Rejected workflow ends.
#
# ==========================================================

builder.add_edge(
    "process_payment",
    END
)

builder.add_edge(
    "reject_claim",
    END
)


# ==========================================================
# CHECKPOINTER
# ==========================================================
#
# Required for interrupt().
#
# Stores graph state while workflow
# is paused.
#
# Enterprise environments often use:
# - PostgreSQL
# - Redis
# - SQL Server
#
# MemorySaver is good for learning.
#
# ==========================================================

memory = MemorySaver()


# ==========================================================
# COMPILE GRAPH
# ==========================================================
#
# Converts graph definition
# into executable workflow.
#
# ==========================================================

graph = builder.compile(
    checkpointer=memory
)


# ==========================================================
# THREAD CONFIGURATION
# ==========================================================
#
# thread_id uniquely identifies
# workflow instance.
#
# Required for pause/resume.
#
# ==========================================================

config = {
    "configurable": {
        "thread_id": "expense-001"
    }
}


# ==========================================================
# START WORKFLOW
# ==========================================================

result = graph.invoke(
    {
        "employee_name": "Kedar",
        "amount": 75000,
        "approval_status": "",
        "result": ""
    },
    config=config
)

print("\nWorkflow Paused")
print(result)


# ==========================================================
# MANAGER APPROVES
# ==========================================================
#
# Imagine user clicks Approve
# button in UI.
#
# ==========================================================

resume_result = graph.invoke(
    Command(
        resume="approve"
    ),
    config=config
)

print("\nWorkflow Completed")
print(resume_result)