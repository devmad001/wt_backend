
sample_bad_section="""
{
  "all_transactions": [
    {
      "transaction_description": "Bill Pay Nbsc - A Division of Synovus Ban on-Line xxxxxx16350 on",
      "transaction_amount": 500.00,
      "transaction_date": "2019-01-09",
      "section": "Transaction history"
    },
    {
"""

#ADD THIS::    - Note: "section":"Transaction history" is not valid. Infer the section from the headings: Deposits and Additions or Withdrawals and Subtractions! 
sample_org_SMALLER_default="""
    Please retrieve details about the transactions from the following bank statement page.
    If you cannot find the information from this text then return "".  Do not make things up. Always return your response as a valid json (no single quotes).
    - Include any section heads (ie/ ATM & DEBIT CARD WITHDRAWLS, CASH TRANSACTIONS, ELECTRONIC WITHDRAWALS, etc)
    - Format the transaction_date as yyyy-mm-dd
    - The transaction_description should include the address and be fully descriptive (it may be multi-line)
    - Note: "section":"Transaction history" is not valid. Infer the section from the headings: Deposits and Additions or Withdrawals and Subtractions! 
    All the transactions should be included in a valid JSON list:

    {"all_transactions": [{"transaction_description": "full description", "transaction_amount": 123.45, "transaction_date": "2021-01-01", "section": "Cash transactions"}]}

    Bank Statement Page:
    =====================


(text char length: 3669)
full_prompt: Account number: 1010083000401      ■ January 9, 2019 - February 7, 2019 ■ Page 2 of 4
Transaction history
Check    Deposits/      Withdrawals/    Ending daily
Date     Number Description      Additions       Subtractions    balance
1/9      Bill Pay Nbsc - A Division of Synovus Ban on-Line xxxxxx16350 on        500.00          4,011.86
01-09
1/10     Purchase authorized on 01/09 Redbox *Dvd Rental 866-733-2693    7.42
IL S589009715899217 Card 9916
1/10     Bill Pay State Farm Bank - Credit Card on-Line Xxxxxxxxxxx77023         359.84          3,644.60
on 01-10
1/11     Bill Pay Albert Smith Recurring No Account Number on 01-11      150.00          3,494.60
1/14     ATM Check Deposit on 01/14 3601 Sandy Plains Rd Marietta GA     1,220.79
0002099 ATM ID 0726P Card 9916
1/14     Bill Pay Pennymac Loan Services on-Line xxxxx66083 on 01-14     1,000.00        3,715.39
1/15     ATM Check Deposit on 01/15 12172 Highway 92 Woodstock GA        750.00
0009326 ATM ID 6935B Card 9916
1/15     Bill Pay Cenlar FSB on-Line xxxxx75584 on 01-15         1,850.00
1/15     ATT Payment 011419 676086003Myw9I Jonathan Mikula       201.41          2,263.98
1/16     Bill Pay Card Services on-Line Xxxxxxxxxxx51678 on 01-16        150.00
Woodstock GA 0006155 ATM ID 6935B Card 9916
2/4      206 Check       2.00    10,065.02
2/5      ATM Check Deposit on 02/05 12172 Highway 92 Woodstock GA        1,000.00
0006472 ATM ID 6935B Card 9916
2/5      Purchase authorized on 02/04 Redbox *Dvd Rental 866-733-2693    3.71
IL S469035799680736 Card 9916
"""


sample_org_default="""
    Please retrieve details about the transactions from the following bank statement page.
    If you cannot find the information from this text then return "".  Do not make things up. Always return your response as a valid json (no single quotes).
    - Include any section heads (ie/ ATM & DEBIT CARD WITHDRAWLS, CASH TRANSACTIONS, ELECTRONIC WITHDRAWALS, etc)
    - Format the transaction_date as yyyy-mm-dd
    - The transaction_description should include the address and be fully descriptive (it may be multi-line)
    All the transactions should be included in a valid JSON list:

    {"all_transactions": [{"transaction_description": "full description", "transaction_amount": 123.45, "transaction_date": "2021-01-01", "section": "Cash transactions"}]}

    Bank Statement Page:
    =====================


(text char length: 3669)
full_prompt: Account number: 1010083000401      ■ January 9, 2019 - February 7, 2019 ■ Page 2 of 4
Transaction history
Check    Deposits/      Withdrawals/    Ending daily
Date     Number Description      Additions       Subtractions    balance
1/9      Bill Pay Nbsc - A Division of Synovus Ban on-Line xxxxxx16350 on        500.00          4,011.86
01-09
1/10     Purchase authorized on 01/09 Redbox *Dvd Rental 866-733-2693    7.42
IL S589009715899217 Card 9916
1/10     Bill Pay State Farm Bank - Credit Card on-Line Xxxxxxxxxxx77023         359.84          3,644.60
on 01-10
1/11     Bill Pay Albert Smith Recurring No Account Number on 01-11      150.00          3,494.60
1/14     ATM Check Deposit on 01/14 3601 Sandy Plains Rd Marietta GA     1,220.79
0002099 ATM ID 0726P Card 9916
1/14     Bill Pay Pennymac Loan Services on-Line xxxxx66083 on 01-14     1,000.00        3,715.39
1/15     ATM Check Deposit on 01/15 12172 Highway 92 Woodstock GA        750.00
0009326 ATM ID 6935B Card 9916
1/15     Bill Pay Chase Card Services on-Line Xxxxxxxxxxx44817 on 01-15          150.00
1/15     Bill Pay Cenlar FSB on-Line xxxxx75584 on 01-15         1,850.00
1/15     ATT Payment 011419 676086003Myw9I Jonathan Mikula       201.41          2,263.98
1/16     Bill Pay Card Services on-Line Xxxxxxxxxxx51678 on 01-16        150.00
1/16     Bill Pay Tjx Rewards on-Line Xxxxxxxxxxx21275 on 01-16          633.88          1,480.10
1/17     Bill Pay Barclays Bank Delaware - Credit on-Line        75.00
Xxxxxxxxxxx61517 on 01-17
1/17     Bill Pay T-Mobile -Not for Prepaid Plans on-Line xxxx66628 on   91.75
01-17
1/17     Bill Pay Cardmember Service on-Line Xxxxxxxxxxx22017 on         150.00          1,163.35
01-17
1/18     Bill Pay Cherokee County Water & Sewage A on-Line xxxxx70711    40.95   1,122.40
on 01-18
1/22     Purchase authorized on 01/20 Invisus, LLC 801-7246211 UT        42.99   1,079.41
S309021240658651 Card 9916
1/23     Money Transfer authorized on 01/22 From Zel*Marius Z Braun      165.00
GA S00389023230063399 Card 9916
1/23     ATM Check Deposit on 01/23 12172 Highway 92 Woodstock GA        3,050.01
0001942 ATM ID 6935B Card 9916
1/23     ATM Withdrawal authorized on 01/23 12172 Highway 92     100.00
Woodstock GA 0001941 ATM ID 6935B Card 9916
1/23     203 Check       50.00   4,144.42
1/24     Bill Pay Cobb Emc on-Line xxxx87003 on 01-24    151.00
1/24     Bill Pay Discover Card Services on-Line Xxxxxxxxxxx18247 on     300.00          3,693.42
01-24
1/28     Bill Pay Nbsc - A Division of Synovus Ban on-Line       50.00
Xxxxxxxxxxx00001 on 01-28
1/28     205 Check       165.00          3,478.42
1/31     Common Sense Pub Payment 2883 Jonathan William Mikul    8,333.00
1/31     Bill Pay Regions Bank on-Line Xxxxxxxxxxx15870 on 01-31         125.00
1/31     Bill Pay Chase Card Services on-Line Xxxxxxxxxxx46971 on 01-31          150.00          11,536.42
2/1      Bill Pay Wells Fargo Card Services on-Line xxxxxxx226 on 02-01          200.00
2/1      Bill Pay Capital One Credit Card on-Line Xxxxxxxxxxx11356 on    50.00
02-01
2/1      Bill Pay Scana Energy on-Line xxxxxxxx68971 on 02-01    110.28          11,176.14
2/4      ATM Check Deposit on 02/04 12172 Highway 92 Woodstock GA        38.00
0006156 ATM ID 6935B Card 9916
2/4      Recurring Payment authorized on 02/01 Sr *Stansberry Res        199.00
888-2612693 MD S389032547804803 Card 9916
2/4      Bill Pay Target Credit Card on-Line Xxxxxxxxxxx92803 on 02-04   380.28
2/4      Bill Pay Kohls on-Line xxxxx57050 on 02-04      417.84
2/4      ATM Withdrawal authorized on 02/04 12172 Highway 92     150.00
Woodstock GA 0006155 ATM ID 6935B Card 9916
2/4      206 Check       2.00    10,065.02
2/5      ATM Check Deposit on 02/05 12172 Highway 92 Woodstock GA        1,000.00
0006472 ATM ID 6935B Card 9916
2/5      Purchase authorized on 02/04 Redbox *Dvd Rental 866-733-2693    3.71
IL S469035799680736 Card 9916
"""