from http.client import HTTPException
from typing import Union
from fastapi import APIRouter
import httpx
from pydantic import BaseModel, validator
from ..models.calculator import Calculator
from ..models.errors import CalculationError

router = APIRouter()

class CalculatorInput(BaseModel):
    hash_rate: Union[float, int] # in TH/s
    power_consumption: Union[float, int] # in W
    electricity_cost: Union[float, int] # in USD/kWh
    initial_investment: Union[float, int] # in USD

    @validator('hash_rate', 'power_consumption', 'electricity_cost', 'initial_investment')
    def check_positive(cls, v):
        if v <= 0:
            raise ValueError("All input values must be positive")
        return v

class CalculatorResult(BaseModel):
    dailyCost: float
    monthlyCost: float
    yearlyCost: float
    dailyRevenueUSD: float
    monthlyRevenueUSD: float
    yearlyRevenueUSD: float
    dailyRevenueBTC: float
    monthlyRevenueBTC: float
    yearlyRevenueBTC: float
    dailyProfitUSD: float
    monthlyProfitUSD: float
    yearlyProfitUSD: float
    breakevenTimeline: int
    costToMine: float

async def get_bitcoin_data():
    url = "https://api.blockchain.info/stats"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            data = response.json()
            return {
                "price": data["market_price_usd"],
                "block_reward": data["miners_revenue_btc"] / data["n_blocks_total"],
                "difficulty": data["difficulty"]
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to fetch Bitcoin data")


@router.post("/calculate", response_model=CalculatorResult)
async def calculate_profitability(input: CalculatorInput):
    try:
        bitcoin_data = await get_bitcoin_data()
        btc_price = bitcoin_data["price"]
        
        daily_cost = Calculator.calculate_cost_per_day(
            power_consumption_w=input.power_consumption, 
            electricity_cost=input.electricity_cost
        )
        daily_revenue_BTC = await Calculator.calculate_earned_btc_per_day(
            hash_rate_th_s=input.hash_rate,
            network_difficulty=bitcoin_data["difficulty"]
        )
        breakeven_timeline = Calculator.calculate_breakeven_timeline(
            daily_cost=daily_cost,
            daily_revenue_btc=daily_revenue_BTC,
            initial_investment=input.initial_investment,
            btc_price=btc_price
        )
        cost_to_mine = Calculator.cost_to_mine_one_BTC(
            daily_cost=daily_cost,
            daily_revenue_btc=daily_revenue_BTC,
            initial_investment=input.initial_investment,
            btc_price=btc_price
        )

        return CalculatorResult(
            dailyCost=round(daily_cost, 2),
            monthlyCost=round(daily_cost * 30, 2),
            yearlyCost=round(daily_cost * 365, 2),
            dailyRevenueUSD=round(daily_revenue_BTC * btc_price, 2),
            monthlyRevenueUSD=round(daily_revenue_BTC * btc_price * 30, 2),
            yearlyRevenueUSD=round(daily_revenue_BTC * btc_price * 365, 2),
            dailyRevenueBTC=round(daily_revenue_BTC, 8),
            monthlyRevenueBTC=round(daily_revenue_BTC * 30, 8),
            yearlyRevenueBTC=round(daily_revenue_BTC * 365, 8),
            dailyProfitUSD=round(daily_revenue_BTC * btc_price - daily_cost, 2),
            monthlyProfitUSD=round((daily_revenue_BTC * btc_price - daily_cost) * 30, 2),
            yearlyProfitUSD=round((daily_revenue_BTC * btc_price - daily_cost) * 365, 2),
            breakevenTimeline=breakeven_timeline,
            costToMine=round(cost_to_mine, 2)
        )
    except CalculationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

