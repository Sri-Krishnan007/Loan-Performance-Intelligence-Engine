**# Loan Performance Intelligence Engine**

**## Synthetic Data Dictionary & Business Rules**

\> **\*\*Dataset Type:\*\*** Synthetic development dataset  

\> **\*\*Purpose:\*\*** Model development, testing, profiling, credit risk experimentation, anomaly detection, stress scenario simulation, and LLM grounding.

\>

\> This dictionary fully documents the database schemas, financial validation rules, stress scenarios, submission formats, and LLM grounding context implemented across the dataset generation pipeline.

\---

**# 1. Loan Static Attributes**

**\*\*Source File:\*\*** \`loan\_static\_attributes.csv\`  

**\*\*Description:\*\*** Describes the mortgage loan parameters established at origination. These fields are fixed throughout the loan lifecycle.

\| Field | Type | Description | Expected Values / Range / Business Rules |

\|---|---|---|---|

\| \`loan\_id\` | string | Unique loan identifier. | Prefix \`LN\` followed by a 6-digit sequence (e.g., \`LN100000\`) |

\| \`origination\_month\` | date | The month when the mortgage loan closed and originated. | \`YYYY-MM-01\` (First of month, range: Jan 2018 – Dec 2024) |

\| \`original\_balance\` | numeric | The original loan amount at closing. | \`$75,000.00\` to \`$1,500,000.00\` (Log-normal distribution) |

\| \`interest\_rate\` | numeric | Annual mortgage interest rate (percentage). | **\*\*Risk-Adjusted\*\***: Derived from vintage base prime rates, adjusted for Credit Score Band (-0.50% to +1.20%) and LTV (-0.20% to +0.40%) risk premiums, plus Gaussian noise. Range: \`2.00%\` to \`11.00%\` |

\| \`credit\_score\_band\` | categorical | Borrower FICO credit score range at underwriting. | \`580-619\`, \`620-659\`, \`660-699\`, \`700-739\`, \`740-779\`, \`780+\` |

\| \`ltv\_band\` | categorical | Loan-to-Value ratio band at origination. | \`0-60\`, \`60-70\`, \`70-80\` (Standard agency peak), \`80-90\`, \`90-100\` |

\| \`dti\_band\` | categorical | Debt-to-Income ratio band at underwriting. | \`0-20\`, \`20-30\`, \`30-40\`, \`40-50\` |

\| \`state\` | categorical | U.S. state abbreviation associated with the property. | Two-letter state code (e.g., \`CA\`, \`TX\`, \`NY\`) |

\| \`loan\_purpose\` | categorical | The reason the borrower secured the loan. | \`Purchase\` (68%), \`Refinance\` (32%) |

\| \`occupancy\_type\` | categorical | Borrower's residency status for the property. | \`Primary Residence\` (78%), \`Second Home\` (10%), \`Investment\` (12%) |

\| \`property\_type\` | categorical | Architecture type of the mortgaged property. | \`Single Family\` (58%), \`Condominium\` (20%), \`Townhouse\` (15%), \`Multi Unit\` (7%) |

\| \`servicer\_name\` | categorical | Named entity handling billing, escrow, and collection. | \`Servicer\_A\` through \`Servicer\_E\` |

\| \`vintage\` | integer | Year of loan origination. | \`2018\` to \`2024\` (Extracted from \`origination\_month\`) |

\---

**# 2. Monthly Loan Performance**

**\*\*Source Files:\*\***  

\* \`loan\_monthly\_performance\_train.csv\` (Primary panel dataset; 33 columns including targets)

\* \`loan\_monthly\_performance\_test.csv\` (Unlabeled test dataset; 25 columns, target-free)

**### A. Time & Identification**

\| Field | Type | Description |

\|---|---|---|

\| \`loan\_id\` | string | Unique loan identifier (foreign key mapping to static attributes). |

\| \`month\_index\` | integer | Zero-indexed sequential month number since origination (0 = origination month). |

\| \`reporting\_month\` | date | The reporting period month (\`YYYY-MM-01\`). |

\| \`origination\_month\` | date | Copy of origination month from static attributes. |

\| \`loan\_age\_months\` | integer | Number of months elapsed since origination (matches \`month\_index\`). |

\| \`remaining\_term\_months\` | integer | Remaining scheduled payments (Total Term – Loan Age). Total Term is randomly chosen from \`[180, 240, 300, 360]\` months. |

**### B. Dynamic Financial & Underwriting Features**

\| Field | Type | Description |

\|---|---|---|

\| \`original\_balance\` | numeric | Original loan balance copied from static attributes. |

\| \`current\_balance\` | numeric | Estimated remaining principal balance. Follows standard fixed-rate mortgage amortization based on \`original\_balance\`, \`interest\_rate\`, and \`loan\_age\_months\`. Set to \`0\` or near \`0\` upon prepayment or default. |

\| \`interest\_rate\` | numeric | Annual mortgage interest rate copied from static attributes. |

\| \`credit\_score\_band\` | categorical | Borrower underwriting FICO band (copied from static attributes). |

\| \`ltv\_band\` | categorical | Origination LTV band (copied from static attributes). |

\| \`dti\_band\` | categorical | Origination DTI band (copied from static attributes). |

\| \`state\` | categorical | Property U.S. state (copied from static attributes). |

\| \`loan\_purpose\` | categorical | Loan purpose (copied from static attributes). |

\| \`occupancy\_type\` | categorical | Property occupancy type (copied from static attributes). |

\| \`property\_type\` | categorical | Property architecture type (copied from static attributes). |

\| \`servicer\_name\` | categorical | Active servicing entity (copied from static attributes). |

**### C. Operational & Credit State Features**

\| Field | Type | Description | Expected Values / Range |

\|---|---|---|---|

\| \`current\_status\` | categorical | Credit status of the loan in the reporting month. | \`Current\`, \`Delinquent\`, \`Default\`, \`Prepaid\` |

\| \`days\_past\_due\` | integer | Delinquency bucket represented by days past due (DPD). | \`0\` (Current/Prepaid), \`30\`, \`60\`, \`90\` (Default or severe delinquency) |

\| \`modification\_flag\` | binary | Indicator if loan terms were modified during the month to avoid default. | \`0\` (No), \`1\` (Yes; occurs only when DPD $\ge$ 60) |

\| \`prepayment\_flag\` | binary | Current-month observed prepayment payoff event (loan closed early). | \`0\` (No), \`1\` (Yes) |

\| \`default\_flag\` | binary | Current-month observed foreclosure / default event. | \`0\` (No), \`1\` (Yes) |

\| \`loss\_severity\_band\` | categorical | Extent of financial loss upon default. | \`None\` (for non-defaults), \`Low\`, \`Medium\`, \`High\` (defaults only) |

\| \`last\_updated\_at\` | datetime | System timestamp of the last record update. | Date/time format |

\| \`source\_system\` | categorical | Database system of record supplying the data. | \`ServicingCore\` (60%), \`LoanPlatform\` (25%), \`RiskSystem\` (15%) |

\| \`document\_status\` | categorical | Completeness status of physical loan folders. | \`Complete\` (60%), \`Pending\` (20%), \`Missing\` (20%) |

\---

**# 3. Future Performance Target & Exception Fields**

\> **\*\*Note:\*\*** These columns are present *\*only\** in \`loan\_monthly\_performance\_train.csv\` to train supervised predictive models. They are forbidden in \`loan\_monthly\_performance\_test.csv\`.

\| Field | Type | Description | Generation / Underwriting Rule |

\|---|---|---|---|

\| \`next\_3m\_delinquency\_flag\` | binary | Will the loan experience delinquency (status = \`Delinquent\`) in the next 3 months? | Max of \`current\_status == 'Delinquent'\` in forward rolling window $[t+1, t+3]$ |

\| \`next\_6m\_delinquency\_flag\` | binary | Will the loan experience delinquency in the next 6 months? | Max of \`current\_status == 'Delinquent'\` in forward rolling window $[t+1, t+6]$ |

\| \`next\_12m\_default\_flag\` | binary | Will the loan default in the next 12 months? | Max of \`default\_flag == 1\` in forward rolling window $[t+1, t+12]$ |

\| \`next\_12m\_prepayment\_flag\` | binary | Will the loan prepay in the next 12 months? | Max of \`prepayment\_flag == 1\` in forward rolling window $[t+1, t+12]$ |

\| \`next\_state\` | categorical | The exact credit status of the loan in month $t+1$. | Shifted value of \`current\_status\` from month $t+1$ (defaults to \`'Current'\` if last row) |

\| \`exception\_required\` | binary | Flag indicating if manual operational review is required. | Set to \`1\` if DPD $\ge$ 60, document status is \`'Missing'\`, modification flag is \`1\`, or status is \`'Default'\`; else \`0\` |

\| \`exception\_type\` | categorical | Specific categorization of the exception. | \`Severe Delinquency\` (if DPD $\ge$ 60), \`Documentation Gap\` (if document missing), \`Loan Modification\` (if modified), \`Default Review\` (if default status), else \`None\` |

\---

**# 4. Servicer Updates (Second-Source Data)**

**\*\*Source File:\*\*** \`servicer\_updates.csv\`  

**\*\*Description:\*\*** An independent, second-source dataset representing monthly reports from servicer feeds. It is sampled from 45% of the training performance records and contains controlled noise for reconciliation modeling.

\| Field | Type | Description | Expected Values / Range |

\|---|---|---|---|

\| \`source\_record\_id\` | string | Unique record ID in the servicer feed. | Format: \`SRV-{loan\_id}-{YYYYMM}\` |

\| \`loan\_id\` | string | Loan identifier. | Maps to static attributes. |

\| \`reporting\_month\` | date | The reporting month of the update feed. | \`YYYY-MM-01\` |

\| \`servicer\_name\` | categorical | Name of the reporting servicer. | \`Servicer\_A\` through \`Servicer\_E\` |

\| \`servicer\_update\_type\` | categorical | Verification category of the record. | \`MATCH\` (88% - agrees with primary database)\<br>\`PARTIAL\_UPDATE\` (5% - some fields missing/NaN)\<br>\`STALE\` (4% - old data, delay in processing)\<br>\`CONFLICT\` (3% - explicit data mismatches) |

\| \`servicer\_current\_balance\` | numeric | Servicer's record of remaining principal balance. | Discrepant under \`STALE\` (+1% to +8% higher) and \`CONFLICT\` (+1% to +5% random variation) |

\| \`servicer\_days\_past\_due\` | numeric | Servicer's record of delinquency days. | Randomly different from primary DPD under \`STALE\` and \`CONFLICT\` |

\| \`servicer\_status\` | categorical | Servicer's record of credit status. | Discrepant under \`CONFLICT\` (assigned a random alternative status) |

\| \`servicer\_modification\_flag\` | numeric | Servicer's record of modification flag. | May be \`NaN\` under \`PARTIAL\_UPDATE\` |

\| \`servicer\_document\_status\` | categorical | Servicer's record of document status. | Discrepant under \`CONFLICT\` (random alternative status) |

\| \`last\_updated\_at\` | datetime | Internal timestamp of last database update in the servicer's local system. | **\*\*Temporal Alignment\*\***: Generated to occur before receipt date. Stale records indicate an older database update (60 to 180 days before receipt). |

\| \`source\_system\` | string | Origin identifier. | Hardcoded to \`ServicerFeed\` |

\| \`record\_received\_at\` | datetime | Timestamp when the update record was loaded into the primary database. | Received **\*\*3 to 35 days\*\*** after the reporting month end. |

\---

**# 5. Macroeconomic Stress Scenarios**

**\*\*Source File:\*\*** \`macro\_scenarios.csv\`  

**\*\*Description:\*\*** Defines stress scenario parameters used for portfolio performance projections and simulation (Task 5).

\| Scenario Name | Key Financial Assumptions | Modeling Impact Guidelines |

\|---|---|---|

\| **\*\*Base Case\*\*** | Stable interest rates (flat yield curve); unemployment rate remains low ($\approx 4\\%$); standard GDP growth. | Portfolio delinquency remains around base rates ($\approx 3.3\\%$). Default rate holds at normal levels ($\approx 1.1\\%$). |

\| **\*\*Adverse Credit\*\*** | Macroeconomic recession; unemployment doubles; home prices drop by 20% (boosting LTVs). | Triggers high delinquency and default multipliers. Delinquency rates typically double ($\ge 6.5\\%$), default and default severity levels increase significantly. |

\| **\*\*High Prepayment\*\*** | Rapid interest rate drop (e.g., 200 bps decline in mortgage interest rates); stable credit conditions. | Accelerates refinancing behavior. Prepayment rates jump significantly, especially for high-interest-rate vintages (e.g., 2023–2024 loans). |

\---

**# 6. Core Credit & Operational Relationship Rules**

The datasets are subject to several deterministic checks to enforce mortgage domain sanity. The following validation rules must always hold:

**### A. Financial Amortization Bounds**

1\. **\*\*Original Balance:\*\*** Must be strictly positive at all times:

   $$\text{original\\\_balance} > 0$$

2\. **\*\*Current Balance Range:\*\*** Current outstanding principal cannot be negative and must never exceed the origination balance:

   $$0 \le \text{current\\\_balance} \le \text{original\\\_balance}$$

**### B. Credit Delinquency Roll-Rate Rules**

1\. **\*\*Days Past Due (DPD) Range:\*\*** Permitted values are strictly limited to standard mortgage delinquency buckets:

   $$\text{days\\\_past\\\_due} \in \\{0, 30, 60, 90\\}$$

2\. **\*\*Sequential Progression (Transition Matrix):\*\***

   \* A loan in **\*\*Current\*\*** status can only transition to **\*\*30 DPD\*\*** when entering delinquency. It cannot skip directly to 60 or 90 DPD.

   \* A delinquent loan must roll sequentially (e.g., $30 \rightarrow 60 \rightarrow 90$) unless it stays in the same bucket, cures to a lower bucket (partial payment), or fully cures to \`0 DPD\` (cured status).

**### C. Absorptive Terminal States**

Once a loan enters a terminal status, it is considered closed. No subsequent monthly performance records can exist in the panel dataset after:

1\. **\*\*\`Prepaid\` (Payoff):\*\*** \`prepayment\_flag == 1\` and status becomes \`Prepaid\`. Remaining balance is paid off (reaches \`$0.00\` or a nominal residual amount).

2\. **\*\*\`Default\` (Loss/Charge-off):\*\*** \`default\_flag == 1\` and status becomes \`Default\`. Outstanding balance remains static, and \`loss\_severity\_band\` is assigned.

**### D. System Timestamp Chronology**

All system updates must adhere to logical temporal bounds. It is structurally impossible to receive a record before it is last modified:

$$\text{last\\\_updated\\\_at} < \text{record\\\_received\\\_at}$$

Furthermore, the record receipt date must fall after the close of the corresponding reporting period:

$$\text{record\\\_received\\\_at} \ge \text{reporting\\\_month}$$

\---

**# 7. Model Submission Schema**

**\*\*Source File:\*\*** \`submission.csv\` / \`submission\_template.csv\`  

**\*\*Description:\*\*** Format required for submission and performance scoring. Each row corresponds to a monthly performance record in the test dataset.

\| Field | Type | Description | Expected Value / Format |

\|---|---|---|---|

\| \`loan\_id\` | string | Unique loan identifier. | Maps to static attributes. |

\| \`reporting\_month\` | date | The reporting month of the prediction. | \`YYYY-MM-01\` |

\| \`pred\_next\_state\` | categorical | Predicted status for month $t+1$. | \`Current\`, \`Delinquent\`, \`Default\`, \`Prepaid\` |

\| \`prob\_delinquency\_3m\` | numeric | Predicted probability of delinquency within the next 3 months. | Float range $[0.0, 1.0]$ |

\| \`prob\_default\_12m\` | numeric | Predicted probability of default within the next 12 months. | Float range $[0.0, 1.0]$ |

\| \`prob\_prepayment\_12m\` | numeric | Predicted probability of prepayment within the next 12 months. | Float range $[0.0, 1.0]$ |

\| \`anomaly\_score\` | numeric | Quantitative outlier/anomaly score for the record. | Float range $[0.0, 1.0]$ |

\| \`exception\_type\` | categorical | Predicted exception categorization. | \`Severe Delinquency\`, \`Documentation Gap\`, \`Loan Modification\`, \`Default Review\`, \`None\` |

\| \`top\_drivers\` | string | Plain-text explanation of the principal risk drivers. | Text (e.g. \`FICO=590, LTV=95%, DPD=60\`) |

\| \`confidence\_level\` | categorical | Model confidence in the prediction. | \`High\`, \`Medium\`, \`Low\` |

\---

**# 8. LLM Grounding Guidelines (Task 7)**

The data dictionary serves as the core semantic asset for Retrieval-Augmented Generation (RAG) and prompt grounding in the LLM-assisted Reviewer Copilot.

\* **\*\*Grounding Constraint:\*\*** The Copilot must restrict its terminology and classifications to the schema definitions specified in this file. 

\* **\*\*Operational Actions:\*\*** LLM explanations for flagged exceptions must cite the exact business rule triggers. For example:

  > *\*"Loan LN100234 has been flagged with exception 'Documentation Gap' because its \`document\_status\` is marked as 'Missing' in reporting month 2024-05-01."\**

\* **\*\*Verification Checks:\*\*** Prompt templates should instruct the LLM to cross-reference the data dictionary before recommending servicer updates reconciliation or predicting risk factors.

\---

**# 9. Synthetic Data Limitations**

This dataset is designed for development and benchmarking. Users must account for the following structural simplifications compared to real-world mortgage portfolios:

\* **\*\*Amortization:\*\*** Uses ideal mathematical amortization. Real portfolios feature partial payments (curtailments), escrow payments, and dynamic rate adjustments that diverge from clean curves.

\* **\*\*Macroeconomics:\*\*** Delinquency and prepayment rates follow standard logistic approximations based on static vintage averages rather than actual daily dynamic bond yield or regional home price indices.

\* **\*\*Loss Severity:\*\*** Assigned randomly among bands upon default, whereas real RMBS severity depends on foreclosure costs, asset sale prices, and local state timelines.