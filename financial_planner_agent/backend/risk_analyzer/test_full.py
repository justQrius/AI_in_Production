#!/usr/bin/env python3
"""Full AWS Lambda test for Risk Analyzer agent"""

import json
import boto3
from dotenv import load_dotenv

load_dotenv(override=True)

from src import Database
from src.schemas import JobCreate

lambda_client = boto3.client('lambda')

def test_risk_analyzer_lambda():
    db = Database()
    job_create = JobCreate(
        clerk_user_id="test_user_risk_lambda_001",
        job_type="portfolio_analysis",
        request_payload={"test": True}
    )
    job_id = db.jobs.create(job_create.model_dump())

    print("Testing Risk Analyzer Lambda...")
    response = lambda_client.invoke(
        FunctionName='alex-risk-analyzer',
        InvocationType='RequestResponse',
        Payload=json.dumps({"job_id": job_id})
    )

    result = json.loads(response['Payload'].read())
    print(f"Result: {json.dumps(result, indent=2)[:500]}...")

if __name__ == "__main__":
    test_risk_analyzer_lambda()
