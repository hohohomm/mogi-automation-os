# Lead Tracker — Schema

Use this as a Google Sheet or Airtable base to track every job/lead.

## Columns

| Column | Type | Description |
|--------|------|-------------|
| ID | Auto | Unique identifier |
| Date Found | Date | When you saw the listing |
| Platform | Text | Upwork / Fiverr / Airtasker / etc |
| Job Title | Text | Listing title |
| Client Name | Text | Buyer's name/handle |
| Description | Text | Full job description |
| Budget | Text | Stated budget or range |
| Fit Score | Number | From `bid_no_bid.py` |
| Decision | Select | BID / MAYBE / PASS |
| Proposal Sent | Date | When you applied |
| Proposal Text | Text | What you sent |
| Response | Select | No Reply / Interested / Negotiating / Won / Lost |
| Won Date | Date | When accepted |
| Fee | Number | Agreed payment amount |
| Payment Status | Select | Unpaid / Paid / Partial |
| Hours Spent | Number | Estimated time |
| Delivery Date | Date | When delivered |
| Follow-up Sent | Date | Post-delivery check |
| Repeat Client? | Boolean | Would work with again |
| Notes | Text | Anything notable |

## CSV Header Row

```
ID,Date Found,Platform,Job Title,Client Name,Description,Budget,Fit Score,Decision,Proposal Sent,Proposal Text,Response,Won Date,Fee,Payment Status,Hours Spent,Delivery Date,Follow-up Sent,Repeat Client?,Notes
```
