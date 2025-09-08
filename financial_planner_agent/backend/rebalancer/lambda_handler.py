"""
Rebalancer Agent Lambda Handler
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

from src import Database
from templates import REBALANCER_INSTRUCTIONS
from agent import create_agent
from observability import observe

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_user_preferences(job_id: str) -> Dict[str, Any]:
    """Load user preferences from database."""
    try:
        db = Database()
        job = db.jobs.find_by_id(job_id)
        if job and job.get('clerk_user_id'):
            user = db.users.find_by_clerk_id(job['clerk_user_id'])
            if user:
                return {
                    'target_allocation': user.get('target_allocation', {
                        "equity": 60, "bonds": 30, "real_estate": 5, "cash": 5
                    }),
                    'rebalance_threshold': user.get('rebalance_threshold', 5),
                    'rebalance_strategy': user.get('rebalance_strategy', 'threshold_based'),
                    'tax_sensitivity': user.get('tax_sensitivity', 'high')
                }
    except Exception as e:
        logger.warning(f"Could not load user data: {e}. Using defaults.")

    return {
        'target_allocation': {"equity": 60, "bonds": 30, "real_estate": 5, "cash": 5},
        'rebalance_threshold': 5,
        'rebalance_strategy': 'threshold_based',
        'tax_sensitivity': 'high'
    }

@retry(
    retry=retry_if_exception_type((RateLimitError, AgentTemporaryError, TimeoutError, asyncio.TimeoutError)),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    before_sleep=lambda retry_state: logger.info(f"Rebalancer: Retrying in {retry_state.next_action.sleep} seconds...")
)
async def run_rebalancer_agent(job_id: str, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
    """Run the rebalancer agent."""

    user_preferences = get_user_preferences(job_id)
    db = Database()
    model, tools, task = create_agent(job_id, portfolio_data, user_preferences, db)

    with trace("Rebalancer Agent"):
        agent = Agent(
            name="Portfolio Rebalancer",
            instructions=REBALANCER_INSTRUCTIONS,
            model=model,
            tools=tools
        )

        try:
            result = await Runner.run(agent, input=task, max_turns=20)
        except (TimeoutError, asyncio.TimeoutError) as e:
            logger.warning(f"Rebalancer timeout: {e}")
            raise AgentTemporaryError(f"Timeout: {e}")
        except Exception as e:
            if "timeout" in str(e).lower() or "throttled" in str(e).lower():
                raise AgentTemporaryError(f"Temporary error: {e}")
            raise

        rebalancer_payload = {
            'analysis': result.final_output,
            'generated_at': datetime.utcnow().isoformat(),
            'agent': 'rebalancer'
        }

        success = db.jobs.update_rebalancing(job_id, rebalancer_payload)

        return {
            'success': success,
            'message': 'Rebalancing analysis completed' if success else 'Analysis completed but failed to save',
            'final_output': result.final_output
        }

def lambda_handler(event, context):
    """Lambda handler for rebalancer agent."""
    with observe() as observability:
        try:
            logger.info(f"Rebalancer Lambda invoked")

            if isinstance(event, str):
                event = json.loads(event)

            job_id = event.get('job_id')
            if not job_id:
                return {'statusCode': 400, 'body': json.dumps({'error': 'job_id is required'})}

            portfolio_data = event.get('portfolio_data')
            if not portfolio_data:
                logger.info(f"Rebalancer: Loading portfolio data for job {job_id}")
                try:
                    import sys
                    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
                    from src import Database

                    db = Database()
                    job = db.jobs.find_by_id(job_id)
                    if job:
                        if observability:
                            observability.create_event(name="Rebalancer Started!", status_message="OK")

                        user_id = job['clerk_user_id']
                        accounts = db.accounts.find_by_user(user_id)

                        portfolio_data = {'user_id': user_id, 'job_id': job_id, 'accounts': []}

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

                        logger.info(f"Rebalancer: Loaded {len(portfolio_data['accounts'])} accounts")
                    else:
                        return {'statusCode': 404, 'body': json.dumps({'error': f'Job {job_id} not found'})}
                except Exception as e:
                    logger.error(f"Could not load portfolio: {e}")
                    return {'statusCode': 400, 'body': json.dumps({'error': 'No portfolio data provided'})}

            result = asyncio.run(run_rebalancer_agent(job_id, portfolio_data))

            return {'statusCode': 200, 'body': json.dumps(result)}

        except Exception as e:
            logger.error(f"Error in rebalancer: {e}", exc_info=True)
            return {'statusCode': 500, 'body': json.dumps({'success': False, 'error': str(e)})}
