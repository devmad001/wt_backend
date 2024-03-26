import os
import sys
import codecs
import json
import re

from fastapi import FastAPI

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Sep 13, 2023  Init

"""
    30 questions
"""


#** see word doc for sample gpt4 comments

50sq=[]
50qs+=[(1,"What is the Primary account number for bank statement?")]
50qs+=[(2,"What is the beginning monthly balance?")]
50qs+=[(3,"What is the date the Account Opened?")]
50qs+=[(4,"What are the total deposits and additions?")]
50qs+=[(5,"What is the total deposits and additions for the Month?")]
50qs+=[(6,"What is the total deposits and additions for the Year?")]
50qs+=[(7,"What is the total deposits and additions for the Quarter?")]
50qs+=[(8,"What is the total deposits and additions for the Day?")]
50qs+=[(9,"What are the total deposits for the Month?")]
50qs+=[(10,"What are the total deposits for the Year?")]
50qs+=[(11,"What are the total deposits for the Quarter?")]
50qs+=[(12,"What are the total deposits for the Day?")]
50qs+=[(13,"What are the total inflows?")]
50qs+=[(14,"What is the total number of outflows? (Defined as money going out, so leaving account)")]
50qs+=[(15,"What is the total number of outflows via cash withdrawal?")]
50qs+=[(16,"What is the total number of outflows via check?")]
50qs+=[(17,"What is the total number of outflows via credit card payments?")]
50qs+=[(18,"What is the total number of outflows via Zelle, and what is the ID number?")]
50qs+=[(19,"What is the total number of outflows via Wire?")]
50qs+=[(20,"What is the total number of outflows via bank fees?")]
50qs+=[(21,"What % of the withdrawals are ATM vs debit card?")]
50qs+=[(22,"How many electronic withdrawals occurred in total by day, month, year and quarter?")]
50qs+=[(23,"How many electronic withdrawals occurred by Wire")]
50qs+=[(24,"How many electronic withdrawals occurred by Zelle,")]
50qs+=[(25,"What is the ending balance of the statement by Date?")]
50qs+=[(26,"How many book transfer credits occurred? Between which entity? From which bank? On which date, for how much money?")]
50qs+=[(27,"How many Zelle payments were made over the course of the month? Id Accounts sent and received?")]
50qs+=[(28,"How many Fed Wire credits came in during the month? ID accounts sent and received.")]
50qs+=[(29,"What is the payment ID on Zelle Transfers?")]
50qs+=[(30,"List of all companies where monies were sent and received?")]
50qs+=[(31,"List of all banks and amounts sent and received?")]
50qs+=[(32,"Top ATM used, Top bank used, Top Loan accounts, Top Credit Card Accounts")]
50qs+=[(33,"List top 10 payees for time-period with totals for each")]
50qs+=[(34,"List top 10 payors for time-period with totals for each")]
50qs+=[(35,"List all payments to IRS and total amount.")]
50qs+=[(36,"List all payees/payors that paid/received with the last five digits of amount as 000.00 and list the amount.")]
50qs+=[(37,"List all ATM transactions by location.")]
50qs+=[(38,"List all ATM transactions in order of amounts.")]
50qs+=[(39,"List credit card payments in order of amount and total.")]
50qs+=[(40,"List all Debit transactions by location.")]
50qs+=[(41,"List all Debit transactions by amount.")]
50qs+=[(42,"List Venmo transactions by top recipient/receiver")]
50qs+=[(43,"List all Credit Cards paid.")]
50qs+=[(44,"List all Debit cards on the account.")]
50qs+=[(45,"List any transactions that use the word “Airport.”")]
50qs+=[(46,"List any transactions that use the word “Ammo.”")]
50qs+=[(47,"List any transactions that use the word “Chemical.”")]
50qs+=[(48,"Program needs to list out all transactions related to a specific word or word string.")]
50qs+=[(49,"List all cash transactions, Deposit, Check written to “Cash,” and ATM withdrawal.")]


"""
Q26
26. How many book transfer credits occurred? Between which entity? From which bank? On which date, for how much money?

You'll need a Cypher query that pulls all book transfers, groups them by date, and provides the necessary details. Here's a hypothetical Cypher query:

// Fetching all book transfer transactions
MATCH (src:Entity)-[t:DEBIT_TRANSACTION]->(transaction:Transaction)-[r:CREDIT_TRANSACTION]->(dest:Entity)
WHERE transaction.transaction_type = "book_transfer"
RETURN 
    transaction.transaction_date AS Date,
    src.name AS Source_Entity,
    dest.name AS Destination_Entity,
    transaction.transaction_amount AS Amount
ORDER BY Date ASC;


For the Timeline of Account Transfers:
If you need a count of transfers for each date, you can modify the query:

MATCH (src:Entity)-[t:DEBIT_TRANSACTION]->(transaction:Transaction)-[r:CREDIT_TRANSACTION]->(dest:Entity)
WHERE transaction.transaction_type = "book_transfer"
WITH transaction.transaction_date AS Date, COUNT(transaction) AS TransferCount
RETURN Date, TransferCount
ORDER BY Date ASC;

"""

"""
Gpt-4 schema modification suggestions:
Given the list of questions, here's an analysis of the information required and suggestions for schema modifications:
1.	Primary Account Number for Bank Statement:
•	Your schema needs to have a BankStatement node, which can have properties like primary_account_number.
2.	Beginning Monthly Balance & Date the Account Opened:
•	Add start_date and beginning_balance to the Account properties.
3.	Total Deposits and Additions for Various Periods:
•	Period aggregations like Month, Year, Quarter, and Day would usually be computed dynamically based on the timestamps of Transaction nodes. Ensure the timestamp field is detailed enough to allow such calculations.
4.	Total Number of Outflows by Various Methods:
•	These can be computed by counting the DEBIT_TRANSACTION relationships with appropriate filtering on transaction_method.
5.	Handling of Duplicate Check Numbers:
•	Add a check_number property to the Transaction node. When aggregating, filter for unique check numbers.
6.	Percentage of Withdrawals by Method (ATM vs Debit Card):
•	Again, this would be computed by aggregating over the DEBIT_TRANSACTION relationships.
7.	Ending Balance of Statement by Date:
•	This typically requires a running total of credits and debits. This is often computed during queries rather than being stored directly.
8.	Book Transfer Credits:
•	You might want a specific transaction_type for book transfers and ensure Entity can represent other bank accounts or internal accounts for transfers.
9.	ID on Zelle Transfers:
•	This could be a unique identifier associated with Zelle transfers. You might want a zelle_id property for transactions of method Zelle.
10.	List of Companies, Banks, etc.:
•	This information would be stored in the Entity node. Companies or banks would be types of entities. Make sure you have a comprehensive set of types for Entity.
11.	Top Metrics:
•	These metrics would be computed dynamically based on the relationships and properties stored.
Modifications to the schema:
•	Add a BankStatement node with properties like:
jsonCopy code
"BankStatement": { "properties": ["primary_account_number", "statement_month", "statement_year"], "constraints": ["UNIQUE(primary_account_number)"], } 
•	Add start_date and beginning_balance to the Account properties.
•	Add check_number and zelle_id to the Transaction properties.
•	Expand Entity type options to include more specific types like 'bank' or 'company'.
By making these modifications and ensuring that your data ingestion process captures all the necessary details, you should be in a good position to answer the given set of questions.
 
Did you forget to answer all of them? there are 32 points.
ChatGPT
I apologize for that oversight. I'll address the remaining questions based on the schema you provided:
15.	Total Number of Outflows via Cash Withdrawal:
•	Compute this by filtering DEBIT_TRANSACTION with transaction_method set to "cash".
16.	Check Duplication:
•	You'll need to store check_number within Transaction if you want to prevent duplicate counting.
17.	Outflows via Credit Card Payments:
•	Compute by filtering DEBIT_TRANSACTION with transaction_method set to "credit_card".
18.	Outflows via Zelle and ID Number:
•	You'd compute this by filtering DEBIT_TRANSACTION with transaction_method set to "Zelle".
•	The "ID number" would likely be a unique transaction identifier, which seems to be your transaction_id.
19.	Outflows via Wire:
•	Compute by filtering DEBIT_TRANSACTION with transaction_method set to "wire_transfer".
20.	Outflows via Bank Fees:
•	You might want to add "bank_fee" to your transaction_type within Transaction.
21.	% of the Withdrawals ATM vs Debit Card:
•	This can be calculated based on the count of DEBIT_TRANSACTION relationships with the respective transaction_method and then taking the percentage.
23.	Electronic Withdrawals by Day, Month, Year, and Quarter:
•	This will be a dynamic calculation based on transaction_date and the filter on transaction_method.
25.	Ending Balance by Date:
•	This is often calculated by taking the beginning balance and applying all transactions up to and including that date.
26.	Book Transfer Credits:
•	Add a "book_transfer" value to the transaction_type field within Transaction.
27.	Zelle Payments in a Month:
•	Filter DEBIT_TRANSACTION with transaction_method set to "Zelle" and then filter by the desired month.
28.	Fed Wire Credits:
•	Add a "fed_wire" value to the transaction_method within Transaction.
29.	Payment ID on Zelle Transfers:
•	If it's different from the usual transaction ID, add a zelle_payment_id property to the Transaction.
30.	Companies Where Monies Were Sent and Received:
•	Filter transactions where Entity.type is "company".
31.	Banks and Amounts Sent and Received:
•	This would require an entity type of "bank" and then aggregation of amounts for each unique bank entity.
32.	Top Metrics:
•	These would be dynamic aggregations based on the type of entity and the transaction method and amount.

Schema Adjustments:
•	Add a check_number and zelle_payment_id property to the Transaction.
•	Add "bank_fee" and "book_transfer" to transaction_type within Transaction.
•	Ensure that Entity includes types for banks and companies.
These adjustments should enable answering the questions based on the schema. Again, I apologize for the oversight in the first explanation.



"""

def dev1():
    return

if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()

"""
"""