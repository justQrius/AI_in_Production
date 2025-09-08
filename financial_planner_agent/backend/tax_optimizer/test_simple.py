#!/usr/bin/env python3
"""
Simple test for Tax Optimizer agent
"""

import json
from dotenv import load_dotenv

load_dotenv(override=True)

from src import Database
from src.schemas import JobCreate
from lambda_handler import lambda_handler

def test_tax_optimizer():
    """Test the tax optimizer agent with portfolio data"""

    db = Database()
    job_create = JobCreate(
        clerk_user_id="test_user_tax_001",
        job_type="portfolio_analysis",
        request_payload={"test": True}
    )
    job_id = db.jobs.create(job_create.model_dump())
    print(f"Created test job: {job_id}")

    test_event = {
        "job_id": job_id,
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
                }
            ]
        }
    }

    print("Testing Tax Optimizer Agent...")
    print("=" * 60)

    result = lambda_handler(test_event, None)

    print(f"Status Code: {result['statusCode']}")

    if result['statusCode'] == 200:
        body = json.loads(result['body'])
        print(f"Success: {body.get('success', False)}")
        print(f"Message: {body.get('message', 'N/A')}")

        if body.get('final_output'):
            output = body['final_output']
            print(f"\nAnalysis length: {len(output)} characters")
            print(f"Preview: {output[:200]}...")
    else:
        print(f"Error: {result.get('body', 'Unknown error')}")

if __name__ == "__main__":
    test_tax_optimizer()
