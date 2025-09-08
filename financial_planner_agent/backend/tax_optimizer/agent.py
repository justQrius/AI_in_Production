"""
Tax Optimizer Agent - provides tax-efficient investment strategies and tax-loss harvesting analysis.
"""

import os
import logging
from typing import Dict, Any, List
from datetime import datetime

from agents.extensions.models.litellm_model import LitellmModel

logger = logging.getLogger()


def calculate_unrealized_gains(portfolio_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Calculate unrealized gains/losses for each position."""
    positions_analysis = []

    for account in portfolio_data.get("accounts", []):
        account_type = account.get("account_type", "taxable")

        for position in account.get("positions", []):
            symbol = position.get("symbol", "")
            quantity = float(position.get("quantity", 0))
            cost_basis = float(position.get("cost_basis", 0))
            instrument = position.get("instrument", {})
            current_price = float(instrument.get("current_price", 100))

            market_value = quantity * current_price
            total_cost = quantity * cost_basis
            unrealized_gain = market_value - total_cost
            gain_percentage = (unrealized_gain / total_cost * 100) if total_cost > 0 else 0

            positions_analysis.append({
                "symbol": symbol,
                "account_type": account_type,
                "quantity": quantity,
                "cost_basis": cost_basis,
                "current_price": current_price,
                "market_value": round(market_value, 2),
                "unrealized_gain": round(unrealized_gain, 2),
                "gain_percentage": round(gain_percentage, 2),
                "instrument": instrument
            })

    return positions_analysis


def identify_tax_loss_harvesting(positions: List[Dict[str, Any]], tax_rate: float) -> Dict[str, Any]:
    """Identify tax-loss harvesting opportunities."""
    harvestable_losses = []
    total_harvestable_loss = 0
    potential_tax_savings = 0

    for pos in positions:
        if pos["account_type"] == "taxable" and pos["unrealized_gain"] < 0:
            loss_amount = abs(pos["unrealized_gain"])
            harvestable_losses.append({
                "symbol": pos["symbol"],
                "loss_amount": loss_amount,
                "market_value": pos["market_value"],
                "gain_percentage": pos["gain_percentage"]
            })
            total_harvestable_loss += loss_amount

    # Calculate tax savings (assuming losses offset capital gains)
    potential_tax_savings = total_harvestable_loss * tax_rate

    # Sort by largest losses first
    harvestable_losses.sort(key=lambda x: x["loss_amount"], reverse=True)

    return {
        "harvestable_positions": harvestable_losses[:10],  # Top 10
        "total_harvestable_loss": round(total_harvestable_loss, 2),
        "potential_tax_savings": round(potential_tax_savings, 2),
        "number_of_positions": len(harvestable_losses)
    }


def analyze_asset_location(portfolio_data: Dict[str, Any], positions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze asset location efficiency."""
    taxable_accounts = {"equity": 0, "bonds": 0, "reits": 0}
    tax_deferred_accounts = {"equity": 0, "bonds": 0, "reits": 0}

    for pos in positions:
        account_type = pos["account_type"]
        market_value = pos["market_value"]
        instrument = pos["instrument"]

        # Simplified asset class determination
        asset_allocation = instrument.get("allocation_asset_class", {})
        equity_pct = asset_allocation.get("equity", 0) / 100
        bonds_pct = asset_allocation.get("fixed_income", 0) / 100
        reits_pct = asset_allocation.get("real_estate", 0) / 100

        if account_type == "taxable":
            taxable_accounts["equity"] += market_value * equity_pct
            taxable_accounts["bonds"] += market_value * bonds_pct
            taxable_accounts["reits"] += market_value * reits_pct
        else:
            tax_deferred_accounts["equity"] += market_value * equity_pct
            tax_deferred_accounts["bonds"] += market_value * bonds_pct
            tax_deferred_accounts["reits"] += market_value * reits_pct

    # Calculate inefficiencies
    # Bonds and REITs should be in tax-deferred accounts (tax-inefficient)
    # Equities can be in taxable accounts (tax-efficient)
    inefficient_allocation = {
        "bonds_in_taxable": round(taxable_accounts["bonds"], 2),
        "reits_in_taxable": round(taxable_accounts["reits"], 2),
        "total_inefficient": round(taxable_accounts["bonds"] + taxable_accounts["reits"], 2)
    }

    return {
        "taxable_accounts": {k: round(v, 2) for k, v in taxable_accounts.items()},
        "tax_deferred_accounts": {k: round(v, 2) for k, v in tax_deferred_accounts.items()},
        "inefficiencies": inefficient_allocation
    }


def calculate_withdrawal_sequencing(
    portfolio_data: Dict[str, Any],
    annual_withdrawal: float,
    years: int = 10
) -> List[Dict[str, Any]]:
    """Calculate tax-optimized withdrawal sequencing."""
    # Simplified calculation for taxable vs tax-deferred withdrawal strategy
    sequencing_plan = []

    for year in range(1, min(years + 1, 11)):  # First 10 years
        # Tax-efficient strategy: Taxable first, then tax-deferred
        if year <= 5:
            source = "Taxable accounts"
            tax_rate = 0.15  # Long-term capital gains
        else:
            source = "Tax-deferred accounts (IRA/401k)"
            tax_rate = 0.22  # Ordinary income

        tax_on_withdrawal = annual_withdrawal * tax_rate
        net_withdrawal = annual_withdrawal - tax_on_withdrawal

        sequencing_plan.append({
            "year": year,
            "withdrawal_amount": annual_withdrawal,
            "source": source,
            "estimated_tax": round(tax_on_withdrawal, 2),
            "net_amount": round(net_withdrawal, 2),
            "tax_rate": f"{tax_rate * 100:.0f}%"
        })

    return sequencing_plan


def create_agent(
    job_id: str,
    portfolio_data: Dict[str, Any],
    user_preferences: Dict[str, Any],
    db=None
):
    """Create the tax optimizer agent with analysis context."""

    # Get model configuration
    model_id = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-3-7-sonnet-20250219-v1:0")
    bedrock_region = os.getenv("BEDROCK_REGION", "us-west-2")
    os.environ["AWS_REGION_NAME"] = bedrock_region

    model = LitellmModel(model=f"bedrock/{model_id}")

    # Extract user tax profile
    tax_bracket = user_preferences.get("tax_bracket", 24)
    state_tax = user_preferences.get("state_tax_rate", 5)
    filing_status = user_preferences.get("filing_status", "married_filing_jointly")
    time_horizon = user_preferences.get("investment_horizon", 20)

    # Calculate tax rate
    federal_rate = tax_bracket / 100
    state_rate = state_tax / 100
    combined_rate = federal_rate + state_rate

    # Analyze positions
    positions = calculate_unrealized_gains(portfolio_data)

    # Identify tax-loss harvesting opportunities
    tlh_opportunities = identify_tax_loss_harvesting(positions, combined_rate)

    # Analyze asset location
    asset_location = analyze_asset_location(portfolio_data, positions)

    # Calculate withdrawal sequencing
    annual_withdrawal = user_preferences.get("target_retirement_income", 80000)
    withdrawal_plan = calculate_withdrawal_sequencing(portfolio_data, annual_withdrawal)

    # Summarize account types
    account_summary = {}
    for account in portfolio_data.get("accounts", []):
        acc_type = account.get("account_type", "taxable")
        account_summary[acc_type] = account_summary.get(acc_type, 0) + 1

    # No tools needed - agent will return analysis as final output
    tools = []

    # Format comprehensive context for the agent
    task = f"""
# Tax Optimization Analysis Context

## User Tax Profile
- Federal Tax Bracket: {tax_bracket}%
- State Tax Rate: {state_tax}%
- Combined Tax Rate: {combined_rate * 100:.1f}%
- Filing Status: {filing_status.replace('_', ' ').title()}
- Investment Time Horizon: {time_horizon} years

## Account Structure
{", ".join([f"{k.replace('_', ' ').title()}: {v} account(s)" for k, v in account_summary.items()])}

## Tax-Loss Harvesting Opportunities
- Harvestable Positions: {tlh_opportunities['number_of_positions']}
- Total Harvestable Losses: ${tlh_opportunities['total_harvestable_loss']:,.0f}
- Potential Tax Savings: ${tlh_opportunities['potential_tax_savings']:,.0f}

Top Opportunities:
"""

    for opp in tlh_opportunities["harvestable_positions"][:5]:
        task += f"- {opp['symbol']}: ${opp['loss_amount']:,.0f} loss ({opp['gain_percentage']:.1f}% down)\n"

    task += f"""

## Asset Location Analysis
Current Allocation:
- Taxable Accounts: Equity ${asset_location['taxable_accounts']['equity']:,.0f}, Bonds ${asset_location['taxable_accounts']['bonds']:,.0f}, REITs ${asset_location['taxable_accounts']['reits']:,.0f}
- Tax-Deferred: Equity ${asset_location['tax_deferred_accounts']['equity']:,.0f}, Bonds ${asset_location['tax_deferred_accounts']['bonds']:,.0f}, REITs ${asset_location['tax_deferred_accounts']['reits']:,.0f}

Tax Inefficiencies:
- Bonds in Taxable Accounts: ${asset_location['inefficiencies']['bonds_in_taxable']:,.0f} (should be in tax-deferred)
- REITs in Taxable Accounts: ${asset_location['inefficiencies']['reits_in_taxable']:,.0f} (should be in tax-deferred)
- Total Inefficient Allocation: ${asset_location['inefficiencies']['total_inefficient']:,.0f}

## Withdrawal Sequencing Strategy (Next 10 Years)
"""

    for plan in withdrawal_plan[:5]:
        task += f"- Year {plan['year']}: ${plan['withdrawal_amount']:,.0f} from {plan['source']} → Tax: ${plan['estimated_tax']:,.0f} ({plan['tax_rate']})\n"

    total_tax_years_1_5 = sum(p["estimated_tax"] for p in withdrawal_plan[:5])
    task += f"\nTotal estimated tax (Years 1-5): ${total_tax_years_1_5:,.0f}\n"

    task += f"""

## Key Optimization Priorities
1. Immediate: Tax-loss harvesting to offset {tax_bracket}% federal + {state_tax}% state taxes
2. Strategic: Relocate tax-inefficient assets to tax-deferred accounts
3. Long-term: Implement tax-optimized withdrawal sequencing
4. Ongoing: Annual tax-loss harvesting review

Your task: Provide a comprehensive tax optimization strategy including:
1. Prioritized action items with specific dollar amounts
2. Tax savings estimates for each recommendation
3. Implementation timeline and considerations
4. Risk factors and wash-sale rule compliance

Provide your analysis in clear markdown format with specific recommendations and tax savings estimates.
"""

    return model, tools, task
