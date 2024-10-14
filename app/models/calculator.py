from typing import Union

from .errors import CalculationError
from decimal import InvalidOperation


class Calculator:
    @staticmethod
    async def calculate_earned_btc_per_day(
        hash_rate_th_s: Union[float, int],
        network_difficulty: float
    ) -> float:
        """
        Calculate the amount of Bitcoin earned per day.

        :param hash_rate_th_s: The hash rate in TH/s (terahashes per second)
        :param block_reward: The current block reward in BTC
        :param network_difficulty: The current network difficulty
        :return: The amount of BTC earned per day
        """
        try:
            SECONDS_IN_A_DAY = 86400
            TERRAHASES_IN_A_HASH = 1e12 # need to convert terrahashes to hashes
            BLOCK_REWARD = 3.125 # FIXME: need to find a good source of truth for this value

            btc_per_day = (hash_rate_th_s * TERRAHASES_IN_A_HASH * BLOCK_REWARD) / (network_difficulty * SECONDS_IN_A_DAY)
            return btc_per_day 
        except ZeroDivisionError:
            raise CalculationError("Network difficulty cannot be zero")
        except InvalidOperation:
            raise CalculationError("Error in BTC calculation. Check your inputs.")

    @staticmethod
    def calculate_cost_per_day(
        power_consumption_w: Union[int, float],
        electricity_cost: Union[int, float]
    ) -> Union[int, float]:
        """
        Calculate the cost of mining per day.

        :param power_consumption: The power consumption in Wh
        :param electricity_cost: The cost of electricity in USD per kWh
        :return: The cost of mining per day
        """
        try:
            WATTS_IN_A_KILOWATT = 1000
            return power_consumption_w * 24 * electricity_cost / WATTS_IN_A_KILOWATT
        except InvalidOperation:
            raise CalculationError("Error in cost calculation. Check your inputs.")


    @staticmethod
    def calculate_breakeven_timeline(
        daily_cost: Union[int, float],
        daily_revenue_btc: Union[int, float],
        initial_investment: Union[int, float],
        btc_price: Union[int, float]
    ) -> int:
        """
        Calculate the breakeven timeline.

        :param daily_cost: The daily cost of mining in USD
        :param daily_revenue_btc: The daily revenue in BTC
        :param initial_investment: The initial investment in USD
        :param btc_price: The price of Bitcoin in USD
        :return: The breakeven timeline in months
        """
        try:
            days_to_breakeven = int(initial_investment / (daily_revenue_btc * btc_price - daily_cost))
            if days_to_breakeven <= 0:
                #TODO: Should this raise an error?  What if the network is down?
                return 0
            months_to_breakeven = days_to_breakeven // 30
            return months_to_breakeven
        except InvalidOperation:
            raise CalculationError("Error in breakeven calculation. Check your inputs.")


    @staticmethod
    def cost_to_mine_one_BTC(
        daily_cost: Union[int, float],
        daily_revenue_btc: Union[int, float],
        initial_investment: Union[int, float],
        btc_price: Union[int, float]
    ) -> Union[int, float]:
        """
        Calculate the cost to mine one Bitcoin.

        :param daily_cost: The daily cost of mining in USD
        :param daily_revenue_btc: The daily revenue in BTC
        :param initial_investment: The initial investment in USD
        :param btc_price: The price of Bitcoin in USD
        :return: The cost to mine one Bitcoin
        """
        return initial_investment / (daily_revenue_btc * btc_price - daily_cost)
    