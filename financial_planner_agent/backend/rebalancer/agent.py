"""
Rebalancer Agent - provides portfolio rebalancing recommendations.
"""

import os
import logging
from typing import Dict, Any, List

from agents.extensions.models.litellm_model import LitellmModel

logger = logging.getLogger()


def calculate_current_allocation(portfolio_data: Dict[str, Any]) -> Dict[str, float]:
    """Calculate current asset allocation across the portfolio."""
    total_value = 0.0
    asset_values = {
        "equity": 0.0,
        "bonds": 0.0,
        "real_estate": 0.0,
        "commodities": 0.0,
        "cash": 0.0
    }

    for account in portfolio_data.get("accounts", []):
        cash = float(account.get("cash_balance", 0))
        asset_values["cash"] += cash
        total_value += cash

        for position in account.get("positions", []):
            quantity = float(position.get("quantity", 0))
            instrument = position.get("instrument", {})
            price = float(instrument.get("current_price", 100))
            value = quantity * price
            total_value += value

            # Get asset class allocation
            asset_allocation = instrument.get("allocation_asset_class", {})
            asset_values["equity"] += value * asset_allocation.get("equity", 0) / 100
            asset_values["bonds"] += value * asset_allocation.get("fixed_income", 0) / 100
            asset_values["real_estate"] += value * asset_allocation.get("real_estate", 0) / 100
            asset_values["commodities"] += value * asset_allocation.get("commodities", 0) / 100

    if total_value == 0:
        return asset_values

    # Convert to percentages
    return {k: round((v / total_value) * 100, 2) for k, v in asset_values.items()}


def calculate_rebalancing_trades(
    current_allocation: Dict[str, float],
    target_allocation: Dict[str, float],
    total_portfolio_value: float,
    threshold: float = 5.0
) -> List[Dict[str, Any]]:
    """Calculate specific trades needed to rebalance."""
    trades = []

    for asset_class, target_pct in target_allocation.items():
        current_pct = current_allocation.get(asset_class, 0)
        drift = current_pct - target_pct

        # Only rebalance if drift exceeds threshold
        if abs(drift) >= threshold:
            trade_amount = (total_portfolio_value * drift) / 100
            action = "sell" if drift > 0 else "buy"
            trades.append({
                "asset_class": asset_class,
                "action": action,
                "amount": abs(trade_amount),
                "current_pct": current_pct,
                "target_pct": target_pct,
                "drift_pct": drift,
                "priority": abs(drift) / threshold  # Higher priority for larger drifts
            })

    # Sort by priority (largest drifts first)
    trades.sort(key=lambda x: x["priority"], reverse=True)

    return trades


def estimate_transaction_costs(trades: List[Dict[str, Any]], cost_per_trade: float = 0.0) -> Dict[str, Any]:
    """Estimate transaction costs for rebalancing."""
    total_trades = len(trades)
    total_transaction_cost = total_trades * cost_per_trade
    total_volume = sum(trade["amount"] for trade in trades)

    return {
        "number_of_trades": total_trades,
        "total_transaction_cost": round(total_transaction_cost, 2),
        "total_volume": round(total_volume, 2),
        "cost_percentage": round((total_transaction_cost / total_volume * 100), 4) if total_volume > 0 else 0
    }


def create_agent(
    job_id: str,
    portfolio_data: Dict[str, Any],
    user_preferences: Dict[str, Any],
    db=None
):
    """Create the rebalancer agent with analysis context."""

    # Get model configuration
    model_id = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-3-7-sonnet-20250219-v1:0")
    bedrock_region = os.getenv("BEDROCK_REGION", "us-west-2")
    os.environ["AWS_REGION_NAME"] = bedrock_region

    model = LitellmModel(model=f"bedrock/{model_id}")

    # Extract rebalancing preferences
    target_allocation = user_preferences.get("target_allocation", {
        "equity": 60,
        "bonds": 30,
        "real_estate": 5,
        "commodities": 0,
        "cash": 5
    })
    threshold = user_preferences.get("rebalance_threshold", 5)
    strategy = user_preferences.get("rebalance_strategy", "threshold_based")
    tax_sensitivity = user_preferences.get("tax_sensitivity", "high")

    # Calculate current allocation
    current_allocation = calculate_current_allocation(portfolio_data)

    # Calculate total portfolio value
    total_value = 0.0
    available_cash = 0.0
    for account in portfolio_data.get("accounts", []):
        cash = float(account.get("cash_balance", 0))
        available_cash += cash
        total_value += cash

        for position in account.get("positions", []):
            quantity = float(position.get("quantity", 0))
            instrument = position.get("instrument", {})
            price = float(instrument.get("current_price", 100))
            total_value += quantity * price

    # Calculate rebalancing trades
    trades = calculate_rebalancing_trades(
        current_allocation,
        target_allocation,
        total_value,
        threshold
    )

    # Estimate costs
    cost_estimate = estimate_transaction_costs(trades, cost_per_trade=0)  # Assume commission-free

    # No tools needed
    tools = []

    # Format comprehensive context for the agent
    task = f"""
# Portfolio Rebalancing Analysis Context

## Portfolio Overview
- Total Portfolio Value: ${total_value:,.0f}
- Available Cash: ${available_cash:,.0f}
- Rebalancing Strategy: {strategy.replace('_', ' ').title()}
- Drift Threshold: {threshold}%
- Tax Sensitivity: {tax_sensitivity.title()}

## Current vs Target Allocation
"""

    for asset_class in ["equity", "bonds", "real_estate", "commodities", "cash"]:
        current = current_allocation.get(asset_class, 0)
        target = target_allocation.get(asset_class, 0)
        drift = current - target
        status = "✓" if abs(drift) < threshold else "⚠"
        task += f"{status} {asset_class.title()}: {current:.1f}% (target: {target:.1f}%, drift: {drift:+.1f}%)\n"

    task += f"""

## Recommended Trades ({len(trades)} actions needed)
"""

    for i, trade in enumerate(trades[:5], 1):
        task += f"{i}. {trade['action'].upper()} ${trade['amount']:,.0f} of {trade['asset_class'].title()} "
        task += f"(current: {trade['current_pct']:.1f}% → target: {trade['target_pct']:.1f}%)\n"

    task += f"""

## Transaction Cost Estimate
- Number of Trades: {cost_estimate['number_of_trades']}
- Total Transaction Cost: ${cost_estimate['total_transaction_cost']:,.0f}
- Total Trade Volume: ${cost_estimate['total_volume']:,.0f}
- Cost as % of Volume: {cost_estimate['cost_percentage']:.3f}%

## Rebalancing Strategies to Consider
1. **New Contributions**: Use incoming cash to buy underweight assets
2. **Tax-Loss Harvesting**: Sell positions with losses first
3. **Threshold Rebalancing**: Only trade when drift exceeds {threshold}%
4. **Annual Rebalancing**: Limit rebalancing frequency to reduce costs
5. **Account-Level Optimization**: Rebalance within tax-advantaged accounts first

Your task: Provide a comprehensive rebalancing strategy including:
1. Prioritized list of specific trades with dollar amounts
2. Tax-efficient implementation approach
3. Timeline and sequencing recommendations
4. Risk considerations and market timing factors

Provide your analysis in clear markdown format with actionable recommendations.
"""

    return model, tools, task
