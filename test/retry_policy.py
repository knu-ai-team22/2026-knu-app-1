from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import RetryPolicy
import random


class PaymentState(TypedDict):
    user_id: str
    amount: int
    payment_status: str
    error_message: str


class PaymentError(Exception):
    pass


def process_payment(state: PaymentState):
    print(f"결제 시도: {state['amount']}원")

    if random.random() < 0.7:
        print("결제 실패 발생")
        raise PaymentError("결제 서버 오류")

    print("결제 성공")

    return {
        "payment_status": "SUCCESS",
        "error_message": ""
    }


def success_handler(state: PaymentState):
    print("결제 성공 처리 완료")
    return {
        "payment_status": "SUCCESS"
    }


def failure_handler(state: PaymentState):
    print("결제 최종 실패 fallback 처리")
    return {
        "payment_status": "FAILED",
        "error_message": "모든 재시도 실패"
    }


builder = StateGraph(PaymentState)

builder.add_node(
    "process_payment",
    process_payment,
    retry_policy=RetryPolicy(
        max_attempts=4,
        initial_interval=1,
        backoff_factor=2,
        max_interval=8,
        jitter=True,
        retry_on=PaymentError
    )
)

builder.add_node("success_handler", success_handler)
builder.add_node("failure_handler", failure_handler)

builder.add_edge(START, "process_payment")

builder.add_edge("process_payment", "success_handler")

builder.add_edge("success_handler", END)
builder.add_edge("failure_handler", END)

graph = builder.compile()

try:
    result = graph.invoke({
        "user_id": "user_1",
        "amount": 50000,
        "payment_status": "",
        "error_message": ""
    })

except Exception as e:
    print(e)