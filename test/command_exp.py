from typing import Literal, TypedDict
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command

class OrderState(TypedDict):
    order_amount: int
    discount_applied: bool
    final_price: int
    message: str

def check_order_node(state: OrderState) -> Command[Literal["apply_discount"]]:
    """
    
    """

    amount = state['order_amount']

    if amount >= 100_000:
        print("고액 주문자입니다. 할인 적용 노드로 이동하겠습니다.")
        
        return Command(
            update={
                "message": "할인 대상입니다."
            },
            goto="apply_discount"
        )
    

    else:
        print("일반 주문자입니다. 할인 대상이 아닙니다.")

        return Command(
            update={
                "message": "할인 대상자가 아닙니다."
            },
            goto="no_discount"
        )
    


def apply_discount(state: OrderState) -> TypedDict:
    print("할인 적용 노드 실행!")

    discount_price = int(state['order_amount'] * 0.9)
    
    return {
        "discount_applied": True,
        "final_price": discount_price,
        "message": "10%할인 적용 완료",
    }


def no_discount(state: OrderState):

    print("할인 없음 노드 실행")

    return {
        "discount_applied": False,
        "final_price": state['order_amount'],
        "message": "정가 결제",
    }

builder = StateGraph(OrderState)

builder.add_node(check_order_node)
builder.add_node(apply_discount)
builder.add_node(no_discount)
    
builder.add_edge(START, "check_order_node")
builder.add_edge("apply_discount", END)
builder.add_edge("no_discount", END)

graph = builder.compile()

result1 = graph.invoke({
    "order_amount": 100_000
})
print(result1)

result2 = graph.invoke({
    "order_amount": 50_000
})
print(result2)