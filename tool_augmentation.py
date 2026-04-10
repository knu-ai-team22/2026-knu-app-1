from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """도시에 해당하는 날씨를 구합니다.
    
    Args:
         city: 목표가 되는 도시의 이름

    Returns:
        str: 목표 도시에 대한 날씨
    """

    weather_data = {
        "Seoul" "맑음, 25도",
        "Daejeon" "맑음, 22도",
        "Tokyo" "흐림, 28도",
    }


    return weather_data.get(city, "도시 이름이 정확하지 않습니다. 다시 시도해주시기 바랍니다.")

@tool

def calculate_tax(total_amount: int, tax_rate: int):
    """전체 계산 금액과 해당 금액의 백분율에 해당하는 세금이 얼마인지를 계산하는 도구
    
    Args:
        total_amount: 전체 계산금액(영수증금액)
        target_rate: 전체 계산 금액에서의 세금의 백분율
    
    Returns:
        계산된 세금 금액

    """
    return round(total_amount * (tax_rate / 100))


from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-20b"
)

llm_with_tools = llm.bind_tools([ get_weather,calculate_tax])

weather_prompt = "Daejeon의 날씨는 어때?"
tax_prompt = "4750000원의 영수증에 대한 20% 세금이 얼마인지 계산해줘"


print(llm_with_tools.invoke(weather_prompt))