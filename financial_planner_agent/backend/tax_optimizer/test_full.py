#!/usr/bin/env python3
"""
Full AWS Lambda test for Tax Optimizer agent
"""

import json
import boto3
from dotenv import load_dotenv

load_dotenv(override=True)

from src import Database
from src.schemas import JobCreate

lambda_client = boto3.client('lambda')

def test_tax_optimizer_lambda():
    """Test the deployed tax optimizer Lambda function"""

    db = Database()
    job_create = JobCreate(
        clerk_user_id="test_user_tax_lambda_001",
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
                        }
                    ]
                }
            ]
        }
    }

    print("Testing Tax Optimizer Lambda...")
    print("=" * 60)

    response = lambda_client.invoke(
        FunctionName='alex-tax-optimizer',
        InvocationType='RequestResponse',
        Payload=json.dumps(test_event)
    )

    result = json.loads(response['Payload'].read())
    print(f"Lambda Response: {json.dumps(result, indent=2)[:500]}...")

if __name__ == "__main__":
    test_tax_optimizer_lambda()
