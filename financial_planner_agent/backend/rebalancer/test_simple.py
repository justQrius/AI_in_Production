#!/usr/bin/env python3
"""Simple test for Rebalancer agent"""

import json
from dotenv import load_dotenv

load_dotenv(override=True)

from src import Database
from src.schemas import JobCreate
from lambda_handler import lambda_handler

def test_rebalancer():
    db = Database()
    job_create = JobCreate(
        clerk_user_id="test_user_rebalancer_001",
        job_type="portfolio_analysis",
        request_payload={"test": True}
    )
    job_id = db.jobs.create(job_create.model_dump())
    print(f"Created test job: {job_id}")

    test_event = {
        "job_id": job_id,
        "portfolio_data": {
            "accounts": [{
                "name": "Investment Account",
                "account_type": "taxable",
                "cash_balance": 1000,
                "positions": [
                    {
                        "symbol": "VTI",
                        "quantity": 100,
                        "cost_basis": 200,
                        "instrument": {
                            "name": "Vanguard Total Stock Market ETF",
                            "current_price": 220,
                            "allocation_asset_class": {"equity": 100}
                        }
                    }
                ]
            }]
        }
    }

    print("Testing Rebalancer Agent...")
    result = lambda_handler(test_event, None)
    print(f"Status: {result['statusCode']}")

    if result['statusCode'] == 200:
        body = json.loads(result['body'])
        print(f"Success: {body.get('success', False)}")

if __name__ == "__main__":
    test_rebalancer()
