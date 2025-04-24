from itertools import combinations_with_replacement
from functools import lru_cache

# --- Brute Force ---

def brute_force_max_revenue(prices, total_tickets):
    """
    Calculate maximum revenue using brute force approach.
    Constraint: Lower prices cannot be used after higher prices.
    Based on trk.py implementation.
    """
    if not prices or total_tickets <= 0:
        return 0
        
    sorted_prices = sorted(prices, reverse=True)
    
    @lru_cache(maxsize=None)
    def get_max_revenue(tickets_left, max_price_index=0):
        if tickets_left == 0:
            return 0
        if max_price_index >= len(sorted_prices):
            return float('-inf') # Cannot fulfill tickets
        
        current_price = sorted_prices[max_price_index]
        max_rev = float('-inf')
        
        # Option 1: Use the current price at least once
        # We must use at least one ticket if we choose this price level
        revenue_using_current = current_price + get_max_revenue(tickets_left - 1, max_price_index)
        max_rev = max(max_rev, revenue_using_current)
        
        # Option 2: Don't use the current price level, move to the next lower price
        revenue_not_using_current = get_max_revenue(tickets_left, max_price_index + 1)
        max_rev = max(max_rev, revenue_not_using_current)
        
        return max_rev
    
    result = get_max_revenue(total_tickets)
    return result if result > float('-inf') else 0 # Return 0 if no solution found

# --- Dynamic Programming ---

def dynamic_programming_max_revenue(prices, total_tickets):
    """
    Calculate maximum revenue using dynamic programming approach.
    Based on trk.py implementation.
    Returns: (max_revenue, used_prices_list)
    """
    if not prices or total_tickets <= 0:
        return 0, []
        
    n = len(prices)
    prices_sorted = sorted(prices, reverse=True)
    
    # dp[i][j]: max revenue using j tickets from prices[0...i-1]
    dp = [[0] * (total_tickets + 1) for _ in range(n + 1)]
    # path[i][j] = 1 if prices[i-1] was used for dp[i][j], 0 otherwise
    path = [[0] * (total_tickets + 1) for _ in range(n + 1)] 
    
    for i in range(1, n + 1):
        current_price = prices_sorted[i-1]
        for j in range(1, total_tickets + 1):
            # Option 1: Don't use price i-1
            dp[i][j] = dp[i-1][j]
            path[i][j] = 0 # Mark path as coming from top
            
            # Option 2: Use price i-1 (if we have tickets left)
            # In this version (from trk.py), we can use the same price multiple times.
            revenue_using_current = current_price + dp[i][j-1]
            if revenue_using_current > dp[i][j]:
                dp[i][j] = revenue_using_current
                path[i][j] = 1 # Mark path as coming from left (used current price)

    # Reconstruct the path to find used prices
    used_prices = []
    i, j = n, total_tickets
    while j > 0 and i > 0: # Need i > 0 to access prices_sorted[i-1]
        if path[i][j] == 1:
            used_prices.append(prices_sorted[i-1])
            j -= 1 # Move left (used one ticket at price i)
            # Stay at the same price level 'i' because we can reuse it
        else:
            i -= 1 # Move up (didn't use price i-1)
            
    return dp[n][total_tickets], used_prices

# --- Optimized Greedy ---

def optimized_greedy_max_revenue(prices, total_tickets):
    """
    Calculate maximum revenue using the optimized greedy approach from trk.py.
    Returns: (max_revenue, used_prices_list)
    """
    if not prices or total_tickets <= 0:
        return 0, []
        
    sorted_prices = sorted(prices, reverse=True)
    n = len(sorted_prices)
    
    revenue = 0
    used_prices = []
    tickets_left = total_tickets
    
    i = 0
    while tickets_left > 0 and i < n:
        current_price = sorted_prices[i]
        revenue += current_price
        used_prices.append(current_price)
        tickets_left -= 1
        
        # Check if the next price is significantly lower
        # If it is, we might want to keep using the current higher price
        # This specific condition (price > next_price * 1.5) determines the strategy
        if i + 1 < n and sorted_prices[i] > sorted_prices[i+1] * 1.5:
            # Stay at the current price level (don't increment i)
            continue 
        else:
            # Move to the next price level
            i += 1
            
    # If tickets_left > 0 after loop (meaning we ran out of distinct prices but still need tickets),
    # the original code didn't explicitly handle this, implying we stop once we iterate through prices once.
    # However, the loop condition `while tickets_left > 0 and i < n` handles this correctly.
    
    return revenue, used_prices 