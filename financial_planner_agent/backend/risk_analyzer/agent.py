"""
Risk Analyzer Agent - provides comprehensive portfolio risk analysis.
"""

import os
import logging
import math
from typing import Dict, Any, List

from agents.extensions.models.litellm_model import LitellmModel

logger = logging.getLogger()


def calculate_portfolio_volatility(portfolio_data: Dict[str, Any]) -> float:
    """Calculate estimated portfolio volatility (standard deviation)."""
    # Simplified: weight asset classes by their typical volatilities
    volatilities = {
        "equity": 0.18,  # 18% annual volatility
        "bonds": 0.05,   # 5% annual volatility
        "real_estate": 0.12,  # 12% annual volatility
        "commodities": 0.20,  # 20% annual volatility
        "cash": 0.01     # 1% annual volatility
    }

    total_value = 0.0
    weighted_variance = 0.0

    for account in portfolio_data.get("accounts", []):
        cash = float(account.get("cash_balance", 0))
        total_value += cash
        weighted_variance += cash * (volatilities["cash"] ** 2)

        for position in account.get("positions", []):
            quantity = float(position.get("quantity", 0))
            instrument = position.get("instrument", {})
            price = float(instrument.get("current_price", 100))
            value = quantity * price
            total_value += value

            # Get asset class allocation
            asset_allocation = instrument.get("allocation_asset_class", {})
            for asset_class, pct in asset_allocation.items():
                if asset_class in volatilities:
                    weight = (value * pct / 100) / total_value if total_value > 0 else 0
                    weighted_variance += (weight * volatilities[asset_class.replace('fixed_income', 'bonds')]) ** 2

    portfolio_volatility = math.sqrt(weighted_variance) if weighted_variance > 0 else 0
    return round(portfolio_volatility * 100, 2)  # Return as percentage


def identify_concentration_risks(portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
    """Identify concentration risks in the portfolio."""
    position_values = []
    sector_values = {}
    region_values = {}
    total_value = 0.0

    for account in portfolio_data.get("accounts", []):
        cash = float(account.get("cash_balance", 0))
        total_value += cash

        for position in account.get("positions", []):
            symbol = position.get("symbol", "")
            quantity = float(position.get("quantity", 0))
            instrument = position.get("instrument", {})
            price = float(instrument.get("current_price", 100))
            value = quantity * price
            total_value += value

            position_values.append({
                "symbol": symbol,
                "value": value,
                "name": instrument.get("name", symbol)
            })

            # Aggregate sector exposure
            sectors = instrument.get("allocation_sectors", {})
            for sector, pct in sectors.items():
                sector_value = value * pct / 100
                sector_values[sector] = sector_values.get(sector, 0) + sector_value

            # Aggregate regional exposure
            regions = instrument.get("allocation_regions", {})
            for region, pct in regions.items():
                region_value = value * pct / 100
                region_values[region] = region_values.get(region, 0) + region_value

    # Sort positions by value
    position_values.sort(key=lambda x: x["value"], reverse=True)

    # Calculate top 10 concentration
    top_10_value = sum(p["value"] for p in position_values[:10])
    top_10_pct = (top_10_value / total_value * 100) if total_value > 0 else 0

    # Find most concentrated sector
    top_sector = max(sector_values.items(), key=lambda x: x[1]) if sector_values else ("None", 0)
    top_sector_pct = (top_sector[1] / total_value * 100) if total_value > 0 else 0

    # Find most concentrated region
    top_region = max(region_values.items(), key=lambda x: x[1]) if region_values else ("None", 0)
    top_region_pct = (top_region[1] / total_value * 100) if total_value > 0 else 0

    return {
        "top_10_holdings": position_values[:10],
        "top_10_concentration_pct": round(top_10_pct, 2),
        "top_sector": top_sector[0],
        "top_sector_pct": round(top_sector_pct, 2),
        "top_region": top_region[0],
        "top_region_pct": round(top_region_pct, 2),
        "number_of_positions": len(position_values)
    }


def calculate_value_at_risk(portfolio_value: float, volatility: float, confidence: float = 0.95) -> float:
    """Calculate Value at Risk (VaR) using normal distribution assumption."""
    # Z-score for 95% confidence: 1.65
    z_score = 1.65 if confidence == 0.95 else 2.33  # 95% or 99%
    var = portfolio_value * (volatility / 100) * z_score
    return round(var, 2)


def create_agent(
    job_id: str,
    portfolio_data: Dict[str, Any],
    user_preferences: Dict[str, Any],
    db=None
):
    """Create the risk analyzer agent with analysis context."""

    # Get model configuration
    model_id = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-3-7-sonnet-20250219-v1:0")
    bedrock_region = os.getenv("BEDROCK_REGION", "us-west-2")
    os.environ["AWS_REGION_NAME"] = bedrock_region

    model = LitellmModel(model=f"bedrock/{model_id}")

    # Extract risk preferences
    risk_tolerance = user_preferences.get("risk_tolerance", "moderate")
    investment_horizon = user_preferences.get("investment_horizon", 20)
    age = user_preferences.get("current_age", 40)
    target_volatility = user_preferences.get("target_volatility", 12)

    # Calculate portfolio metrics
    total_value = 0.0
    for account in portfolio_data.get("accounts", []):
        cash = float(account.get("cash_balance", 0))
        total_value += cash
        for position in account.get("positions", []):
            quantity = float(position.get("quantity", 0))
            instrument = position.get("instrument", {})
            price = float(instrument.get("current_price", 100))
            total_value += quantity * price

    # Calculate risk metrics
    volatility = calculate_portfolio_volatility(portfolio_data)
    concentration = identify_concentration_risks(portfolio_data)
    var_95 = calculate_value_at_risk(total_value, volatility, 0.95)

    # No tools needed
    tools = []

    # Format comprehensive context for the agent
    task = f"""
# Portfolio Risk Analysis Context

## Portfolio Overview
- Total Portfolio Value: ${total_value:,.0f}
- Estimated Annual Volatility: {volatility:.2f}%
- Target Volatility: {target_volatility:.2f}%
- Risk Tolerance: {risk_tolerance.title()}
- Investment Horizon: {investment_horizon} years
- Current Age: {age}

## Volatility Assessment
- Current Volatility: {volatility:.2f}%
- Volatility vs Target: {"Above" if volatility > target_volatility else "Below"} target by {abs(volatility - target_volatility):.2f}%
- 95% Value at Risk (1 year): ${var_95:,.0f}
- Maximum Expected Loss (95% confidence): {(var_95 / total_value * 100):.2f}%

## Concentration Risk Analysis
- Number of Positions: {concentration['number_of_positions']}
- Top 10 Holdings: {concentration['top_10_concentration_pct']:.1f}% of portfolio
- Most Concentrated Sector: {concentration['top_sector']} ({concentration['top_sector_pct']:.1f}%)
- Most Concentrated Region: {concentration['top_region']} ({concentration['top_region_pct']:.1f}%)

### Top Holdings
"""

    for i, holding in enumerate(concentration["top_10_holdings"][:5], 1):
        holding_pct = (holding["value"] / total_value * 100) if total_value > 0 else 0
        task += f"{i}. {holding['symbol']}: ${holding['value']:,.0f} ({holding_pct:.1f}%)\n"

    task += f"""

## Risk Thresholds & Flags
- ⚠ Individual position > 10% of portfolio
- ⚠ Sector concentration > 30%
- ⚠ Regional concentration > 60%
- ⚠ Top 10 holdings > 70%
- ⚠ Volatility > {target_volatility + 3}% (target + 3%)

## Risk Mitigation Strategies to Consider
1. **Diversification**: Add more positions to reduce concentration
2. **Sector Rotation**: Rebalance overweight sectors
3. **Geographic Diversification**: Expand international exposure
4. **Volatility Reduction**: Increase allocation to lower-volatility assets
5. **Hedging**: Consider defensive positions or options strategies

Your task: Provide a comprehensive risk analysis including:
1. Detailed assessment of current risk level vs tolerance
2. Specific concentration risks that need attention
3. Quantified recommendations to reduce portfolio risk
4. Risk-adjusted return optimization suggestions
5. Stress testing scenarios and potential downsides

Provide your analysis in clear markdown format with specific metrics and actionable recommendations.
"""

    return model, tools, task
