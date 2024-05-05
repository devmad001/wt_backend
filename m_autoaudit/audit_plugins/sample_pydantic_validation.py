import os
import sys
import json
import re
import time


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)


#0v1# JC  Feb 28, 2023  Setup



"""
    PYDANTIC VALIDATION SAMPLE

"""

from datetime import date
from typing import List
from pydantic import BaseModel, validator, conlist

class Transaction(BaseModel):
    date: date
    description: str
    amount: float  # Use positive values for credits and negative for debits
    balance: float

    # Custom validator to ensure balance makes sense with transactions
    @validator('balance')
    def balance_must_be_correct(cls, v, values, **kwargs):
        if 'amount' in values:
            # Assuming you have a way to track the previous balance, you could validate like this:
            # previous_balance + values['amount'] should equal the current balance
            pass  # Replace with actual validation logic
        return v

class BankStatement(BaseModel):
    account_holder: str
    account_number: str
    period_start: date
    period_end: date
    transactions: conlist(Transaction, min_items=1)  # Ensure there's at least one transaction

    # Validate that transactions are within the statement period
    @validator('transactions', each_item=True)
    def transactions_must_be_within_period(cls, v, values, **kwargs):
        if 'period_start' in values and 'period_end' in values:
            assert values['period_start'] <= v.date <= values['period_end'], 'Transaction date outside statement period'
        return v

    # Summarize transactions or perform other statement-level validations
    def summarize_transactions(self):
        total_credits = sum(t.amount for t in self.transactions if t.amount > 0)
        total_debits = sum(t.amount for t in self.transactions if t.amount < 0)
        return {
            "total_credits": total_credits,
            "total_debits": total_debits,
            "ending_balance": self.transactions[-1].balance
        }

class ExternalAuditor:
    def audit_statement(self, statement: BankStatement):
        summary = statement.summarize_transactions()
        # Perform your external audit logic here, like:
        # - Comparing ending balance with the sum of transactions
        # - Checking for any discrepancies in transaction descriptions
        # - Any other external validation rules
        # For simplicity, let's just print the summary here
        print(f"Audit Summary for {statement.account_holder}: {summary}")



# Example usage
if __name__ == "__main__":
    transactions = [
        {"date": date(2024, 1, 1), "description": "Deposit", "amount": 1000, "balance": 1000},
        {"date": date(2024, 1, 2), "description": "Withdrawal", "amount": -200, "balance": 800},
    ]
    statement = BankStatement(
        account_holder="John Doe",
        account_number="123456789",
        period_start=date(2024, 1, 1),
        period_end=date(2024, 1, 31),
        transactions=transactions
    )

    auditor = ExternalAuditor()
    auditor.audit_statement(statement)


if __name__=='__main__':
    branches=[]
    for b in branches:
        globals()[b]()


"""
"""








