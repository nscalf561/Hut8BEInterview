import pytest
from fastapi.testclient import TestClient
from main import app
from app.models.calculator import Calculator, CalculationError
import pytest
import asyncio
from app.models.calculator import Calculator

client = TestClient(app)

@pytest.mark.asyncio
async def test_calculate_earned_btc_per_day():
    result = await Calculator.calculate_earned_btc_per_day(100, 0.000000000000001)
    assert isinstance(result, float)
    assert result > 0

def test_calculate_cost_per_day():
    result = Calculator.calculate_cost_per_day(1000, 0.1)
    assert isinstance(result, float)
    assert result == 2.40

def test_calculate_breakeven_timeline():
    result = Calculator.calculate_breakeven_timeline(100, 0.01, 10000, 50000)
    assert isinstance(result, int)
    assert result >= 0

def test_cost_to_mine_one_btc():
    result = Calculator.cost_to_mine_one_BTC(100, 0.01, 10000, 50000)
    assert isinstance(result, float)
    assert result > 0

def test_api_calculate_profitability():
    response = client.post(
        "/calculate/",
        json={
            "hash_rate": 100,
            "power_consumption": 1000,
            "electricity_cost": 0.1,
            "initial_investment": 10000
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "dailyCost" in data
    assert "dailyRevenueUSD" in data
    assert "breakevenTimeline" in data
    assert "costToMine" in data

def test_api_invalid_input():
    response = client.post(
        "/calculate/",
        json={
            "hash_rate": -100,
            "power_consumption": 1000,
            "electricity_cost": 0.1,
            "initial_investment": 10000
        }
    )
    assert response.status_code == 422
    assert "detail" in response.json()

@pytest.mark.parametrize("input_data, expected_status", [
    ({"hash_rate": 100, "power_consumption": 1000, "electricity_cost": 0.1, "initial_investment": 10000}, 200),
    ({"hash_rate": -100, "power_consumption": 1000, "electricity_cost": 0.1, "initial_investment": 10000}, 422),
    ({"hash_rate": 100, "power_consumption": 0, "electricity_cost": 0.1, "initial_investment": 10000}, 422),
    ({"hash_rate": 100, "power_consumption": 1000, "electricity_cost": -0.1, "initial_investment": 10000}, 422),
])
def test_api_calculate_profitability_parametrized(input_data, expected_status):
    response = client.post("/calculate/", json=input_data)
    assert response.status_code == expected_status