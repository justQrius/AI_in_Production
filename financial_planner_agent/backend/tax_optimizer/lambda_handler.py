"""
Tax Optimizer Agent Lambda Handler
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any
from datetime import datetime

from agents import Agent, Runner, trace
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from litellm.exceptions import RateLimitError


class AgentTemporaryError(Exception):
    """Temporary error that should trigger retry"""
    pass

try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass

# Import database package
from src import Database

from templates import TAX_OPTIMIZER_INSTRUCTIONS
from agent import create_agent
from observability import observe

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_user_preferences(job_id: str) -> Dict[str, Any]:
    """Load user preferences from database."""
    try:
        db = Database()

        # Get the job to find the user
        job = db.jobs.find_by_id(job_id)
        if job and job.get('clerk_user_id'):
            # Get user preferences
            user = db.users.find_by_clerk_id(job['clerk_user_id'])
            if user:
                return {
                    'tax_bracket': user.get('tax_bracket', 24),
                    'state_tax_rate': user.get('state_tax_rate', 5),
                    'filing_status': user.get('filing_status', 'married_filing_jointly'),
                    'investment_horizon': user.get('investment_horizon', 20),
                    'target_retirement_income': float(user.get('target_retirement_income', 80000))
                }
    except Exception as e:
        logger.warning(f"Could not load user data: {e}. Using defaults.")

    return {
        'tax_bracket': 24,
        'state_tax_rate': 5,
        'filing_status': 'married_filing_jointly',
        'investment_horizon': 20,
        'target_retirement_income': 80000.0
    }

@retry(
    retry=retry_if_exception_type((RateLimitError, AgentTemporaryError, TimeoutError, asyncio.TimeoutError)),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    before_sleep=lambda retry_state: logger.info(f"Tax Optimizer: Temporary error, retrying in {retry_state.next_action.sleep} seconds...")
)
async def run_tax_optimizer_agent(job_id: str, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
    """Run the tax optimizer agent."""

    # Get user preferences
    user_preferences = get_user_preferences(job_id)

    # Initialize database
    db = Database()

    # Create agent
    model, tools, task = create_agent(job_id, portfolio_data, user_preferences, db)

    # Run agent
    with trace("Tax Optimizer Agent"):
        agent = Agent(
            name="Tax Optimizer",
            instructions=TAX_OPTIMIZER_INSTRUCTIONS,
            model=model,
            tools=tools
        )

        try:
            result = await Runner.run(
                agent,
                input=task,
                max_turns=20
            )
        except (TimeoutError, asyncio.TimeoutError) as e:
            logger.warning(f"Tax optimizer timeout: {e}")
            raise AgentTemporaryError(f"Timeout during agent execution: {e}")
        except Exception as e:
            error_str = str(e).lower()
            if "timeout" in error_str or "throttled" in error_str:
                logger.warning(f"Tax optimizer temporary error: {e}")
                raise AgentTemporaryError(f"Temporary error: {e}")
            raise

        # Save the analysis to database
        tax_payload = {
            'analysis': result.final_output,
            'generated_at': datetime.utcnow().isoformat(),
            'agent': 'tax_optimizer'
        }

        success = db.jobs.update_tax_analysis(job_id, tax_payload)

        if not success:
            logger.error(f"Failed to save tax analysis for job {job_id}")

        return {
            'success': success,
            'message': 'Tax optimization analysis completed' if success else 'Analysis completed but failed to save',
            'final_output': result.final_output
        }

def lambda_handler(event, context):
    """
    Lambda handler expecting job_id in event.

    Expected event:
    {
        "job_id": "uuid",
        "portfolio_data": {...}
    }
    """
    with observe() as observability:
        try:
            logger.info(f"Tax Optimizer Lambda invoked with event: {json.dumps(event)[:500]}")

            # Parse event
            if isinstance(event, str):
                event = json.loads(event)

            job_id = event.get('job_id')
            if not job_id:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'job_id is required'})
                }

            portfolio_data = event.get('portfolio_data')
            if not portfolio_data:
                # Load from database
                logger.info(f"Tax Optimizer: Loading portfolio data for job {job_id}")
                try:
                    import sys
                    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
                    from src import Database

                    db = Database()
                    job = db.jobs.find_by_id(job_id)
                    if job:
                        if observability:
                            observability.create_event(
                                name="Tax Optimizer Started!", status_message="OK"
                            )

                        user_id = job['clerk_user_id']
                        user = db.users.find_by_clerk_id(user_id)
                        accounts = db.accounts.find_by_user(user_id)

                        portfolio_data = {
                            'user_id': user_id,
                            'job_id': job_id,
                            'accounts': []
                        }

                        for account in accounts:
                            account_data = {
                                'id': account['id'],
                                'name': account['account_name'],
                                'account_type': account.get('account_type', 'taxable'),
                                'cash_balance': float(account.get('cash_balance', 0)),
                                'positions': []
                            }

                            positions = db.positions.find_by_account(account['id'])
                            for position in positions:
                                instrument = db.instruments.find_by_symbol(position['symbol'])
                                if instrument:
                                    account_data['positions'].append({
                                        'symbol': position['symbol'],
                                        'quantity': float(position['quantity']),
                                        'cost_basis': float(position.get('cost_basis', 100)),
                                        'instrument': instrument
                                    })

                            portfolio_data['accounts'].append(account_data)

                        logger.info(f"Tax Optimizer: Loaded {len(portfolio_data['accounts'])} accounts")
                    else:
                        logger.error(f"Tax Optimizer: Job {job_id} not found")
                        return {
                            'statusCode': 404,
                            'body': json.dumps({'error': f'Job {job_id} not found'})
                        }
                except Exception as e:
                    logger.error(f"Could not load portfolio from database: {e}")
                    return {
                        'statusCode': 400,
                        'body': json.dumps({'error': 'No portfolio data provided'})
                    }

            logger.info(f"Tax Optimizer: Processing job {job_id}")

            # Run the agent
            result = asyncio.run(run_tax_optimizer_agent(job_id, portfolio_data))

            logger.info(f"Tax Optimizer completed for job {job_id}")

            return {
                'statusCode': 200,
                'body': json.dumps(result)
            }

        except Exception as e:
            logger.error(f"Error in tax optimizer: {e}", exc_info=True)
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'success': False,
                    'error': str(e)
                })
            }

# For local testing
if __name__ == "__main__":
    test_event = {
        "job_id": "test-tax-123",
        "portfolio_data": {
            "accounts": [
                {
                    "name": "Taxable Brokerage",
                    "account_type": "taxable",
                    "cash_balance": 5000,
                    "positions": [
                        {
                            "symbol": "VTI",
                            "quantity": 50,
                            "cost_basis": 200,
                            "instrument": {
                                "name": "Vanguard Total Stock Market ETF",
                                "current_price": 220,
                                "allocation_asset_class": {"equity": 100}
                            }
                        },
                        {
                            "symbol": "BND",
                            "quantity": 100,
                            "cost_basis": 80,
                            "instrument": {
                                "name": "Vanguard Total Bond Market ETF",
                                "current_price": 75,
                                "allocation_asset_class": {"fixed_income": 100}
                            }
                        }
                    ]
                },
                {
                    "name": "401(k)",
                    "account_type": "tax_deferred",
                    "cash_balance": 2000,
                    "positions": [
                        {
                            "symbol": "VNQ",
                            "quantity": 75,
                            "cost_basis": 90,
                            "instrument": {
                                "name": "Vanguard Real Estate ETF",
                                "current_price": 95,
                                "allocation_asset_class": {"real_estate": 100}
                            }
                        }
                    ]
                }
            ]
        }
    }

    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))
