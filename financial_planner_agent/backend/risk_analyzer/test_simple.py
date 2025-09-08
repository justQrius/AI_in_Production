#!/usr/bin/env python3
"""Simple test for Risk Analyzer agent"""

import json
from dotenv import load_dotenv

load_dotenv(override=True)

from src import Database
from src.schemas import JobCreate
from lambda_handler import lambda_handler

def test_risk_analyzer():
    db = Database()
    job_create = JobCreate(
        clerk_user_id="test_user_risk_001",
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
                        "symbol": "SPY",
                        "quantity": 100,
                        "cost_basis": 400,
                        "instrument": {
                            "name": "SPDR S&P 500 ETF",
                            "current_price": 450,
                            "allocation_asset_class": {"equity": 100},
                            "allocation_sectors": {"technology": 30, "healthcare": 15},
                            "allocation_regions": {"north_america": 80, "europe": 15}
                        }
                    }
                ]
            }]
        }
    }

    print("Testing Risk Analyzer Agent...")
    result = lambda_handler(test_event, None)
    print(f"Status: {result['statusCode']}")

    if result['statusCode'] == 200:
        body = json.loads(result['body'])
        print(f"Success: {body.get('success', False)}")

if __name__ == "__main__":
    test_risk_analyzer()
