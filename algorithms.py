from itertools import combinations_with_replacement
from functools import lru_cache

# --- Brute Force ---

def brute_force_max_revenue(prices, k):
    """
    Calculate maximum revenue using brute force approach.
    """
    if not prices or k <= 0:
        return 0
    
    prices = sorted(prices, reverse=True)
    
    @lru_cache(maxsize=None)
    def calculate_revenue(remaining_tickets, price_index):
        if remaining_tickets == 0 or price_index >= len(prices):
            return 0
        
        max_revenue = calculate_revenue(remaining_tickets, price_index + 1)
        
        if remaining_tickets > 0:
            current_price = prices[price_index]
            revenue_with_current = current_price + calculate_revenue(remaining_tickets - 1, price_index)
            max_revenue = max(max_revenue, revenue_with_current)
        
        return max_revenue
    
    return calculate_revenue(k, 0)

# --- Dynamic Programming ---

def dynamic_programming_max_revenue(prices, k):
    """
    Calculate maximum revenue using dynamic programming approach.
    """
    if not prices or k <= 0:
        return 0, []
    
    prices = sorted(prices, reverse=True)
    n = len(prices)
    
    dp = [[0] * (k + 1) for _ in range(n + 1)]
    
    for i in range(1, n + 1):
        for j in range(1, k + 1):
            dp[i][j] = dp[i-1][j]
            if j >= 1:
                dp[i][j] = max(dp[i][j], prices[i-1] + dp[i][j-1])
    
    used_prices = []
    i, j = n, k
    while i > 0 and j > 0:
        if dp[i][j] != dp[i-1][j]:
            used_prices.append(prices[i-1])
            j -= 1
        i -= 1
    
    return dp[n][k], used_prices

# --- Optimized Greedy ---

def optimized_greedy_max_revenue(prices, k):
    """
    Calculate maximum revenue using optimized greedy approach.
    """
    if not prices or k <= 0:
        return 0, []
    
    prices = sorted(prices, reverse=True)
    
    revenue = 0
    used_prices = []
    remaining_tickets = k
    
    for price in prices:
        if remaining_tickets <= 0:
            break
            
        tickets_at_price = min(remaining_tickets, k // len(prices) + 1)
        
        revenue += price * tickets_at_price
        used_prices.extend([price] * tickets_at_price)
        remaining_tickets -= tickets_at_price
    
    return revenue, used_prices 