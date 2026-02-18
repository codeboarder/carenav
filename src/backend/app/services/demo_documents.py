"""
Demo documents service for CareNav Florida.
Built by Gregory Katz and Rick Weyenberg
Code is as-is, open source
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import Document, Patient, get_async_session_maker
from app.services.knowledge_base import get_knowledge_base_service


DEMO_DOCUMENTS = [
    {
        "name": "Bank Statement - Checking - January 2026",
        "category": "bank",
        "doc_type": "bank_statement_jan_2026",
        "content": """FIRST NATIONAL BANK - CHECKING ACCOUNT STATEMENT
Account Number: ****4521
Statement Period: January 1-31, 2026
Account Holder: Margaret A. Thompson
Address: 1234 Palm Beach Blvd, West Palm Beach, FL 33401

═══════════════════════════════════════════════════════════════════════════════
ACCOUNT SUMMARY
═══════════════════════════════════════════════════════════════════════════════
Beginning Balance (01/01/2026):                              $1,650.00
Total Deposits and Credits:                                  +$2,300.00
Total Withdrawals and Debits:                                -$2,450.00
Ending Balance (01/31/2026):                                 $1,500.00

═══════════════════════════════════════════════════════════════════════════════
DETAILED TRANSACTION HISTORY - 30 DAY PERIOD
═══════════════════════════════════════════════════════════════════════════════

DATE        DESCRIPTION                                    AMOUNT      BALANCE
---------------------------------------------------------------------------
01/01/26    Beginning Balance                                         $1,650.00
01/02/26    DEBIT CARD - WALGREENS #5421                  -$23.45     $1,626.55
01/03/26    DIRECT DEPOSIT - SOC SEC ADMIN XXXX4521    +$1,850.00     $3,476.55
01/03/26    DEBIT CARD - PUBLIX #0892                     -$67.32     $3,409.23
01/04/26    CHECK #1247 - PALM BEACH WATER UTILITY        -$45.00     $3,364.23
01/05/26    DIRECT DEPOSIT - PENSION ROBERT THOMPSON     +$450.00     $3,814.23
01/06/26    DEBIT CARD - CVS PHARMACY #4521               -$34.50     $3,779.73
01/07/26    DEBIT CARD - PUBLIX #0892                     -$52.18     $3,727.55
01/08/26    ATM WITHDRAWAL - FIRST NATIONAL ATM           -$60.00     $3,667.55
01/09/26    DEBIT CARD - WALMART SUPERCENTER              -$89.45     $3,578.10
01/10/26    ACH DEBIT - MEDICARE PREMIUM                 -$174.70     $3,403.40
01/10/26    DEBIT CARD - SHELL GAS STATION                -$45.00     $3,358.40
01/11/26    DEBIT CARD - PUBLIX #0892                     -$78.23     $3,280.17
01/12/26    CHECK #1248 - FIRST BAPTIST CHURCH (TITHE)    -$50.00     $3,230.17
01/13/26    DEBIT CARD - BEALLS OUTLET                    -$34.99     $3,195.18
01/14/26    DEBIT CARD - PUBLIX #0892                     -$45.67     $3,149.51
01/15/26    ACH DEBIT - FLORIDA POWER & LIGHT            -$185.00     $2,964.51
01/15/26    ACH DEBIT - AT&T WIRELESS                     -$65.00     $2,899.51
01/16/26    DEBIT CARD - CVS PHARMACY #4521               -$28.75     $2,870.76
01/17/26    DEBIT CARD - PUBLIX #0892                     -$92.34     $2,778.42
01/18/26    DEBIT CARD - DOLLAR GENERAL                   -$18.45     $2,759.97
01/19/26    CHECK #1249 - DR. RODRIGUEZ (COPAY)           -$25.00     $2,734.97
01/20/26    DEBIT CARD - PUBLIX #0892                    -$112.30     $2,622.67
01/21/26    DEBIT CARD - WALGREENS #5421                  -$45.00     $2,577.67
01/22/26    ACH DEBIT - AARP MEMBERSHIP                   -$16.00     $2,561.67
01/23/26    DEBIT CARD - PUBLIX #0892                     -$56.78     $2,504.89
01/24/26    DEBIT CARD - ROSS DRESS FOR LESS             -$42.99     $2,461.90
01/25/26    ACH DEBIT - HUMANA PART D PREMIUM             -$32.50     $2,429.40
01/26/26    DEBIT CARD - PUBLIX #0892                     -$67.45     $2,361.95
01/27/26    DEBIT CARD - CVS PHARMACY #4521               -$89.00     $2,272.95
01/28/26    EMERGENCY ROOM COPAY - PALM BEACH GEN        -$250.00     $2,022.95
01/29/26    DEBIT CARD - PUBLIX #0892                     -$34.56     $1,988.39
01/30/26    ACH DEBIT - COMCAST XFINITY                  -$125.00     $1,863.39
01/31/26    MONTHLY SERVICE FEE                           -$12.00     $1,851.39
01/31/26    DEBIT CARD - PUBLIX #0892                     -$78.23     $1,773.16
01/31/26    CHECK #1250 - LAWN SERVICE                   -$100.00     $1,673.16
01/31/26    DEBIT CARD - SHELL GAS STATION                -$38.00     $1,635.16
01/31/26    TRANSFER TO SAVINGS                          -$135.16     $1,500.00

═══════════════════════════════════════════════════════════════════════════════
MONTHLY EXPENSE ANALYSIS
═══════════════════════════════════════════════════════════════════════════════
Groceries (Publix, Walmart):                                    $774.06
Healthcare (Medicare, Copays, Pharmacy):                        $633.95
Utilities (FPL, Water, Comcast, AT&T):                         $420.00
Transportation (Gas):                                            $83.00
Personal/Retail:                                                $112.43
Church/Charitable:                                               $50.00
Home Maintenance:                                               $100.00
Other:                                                          $276.56
---------------------------------------------------------------------------
TOTAL MONTHLY EXPENSES:                                       $2,450.00

═══════════════════════════════════════════════════════════════════════════════
ACCOUNT NOTICES
═══════════════════════════════════════════════════════════════════════════════
- Your account is in good standing
- Direct deposit is active for Social Security and Pension
- Overdraft protection is NOT enabled on this account
- Average daily balance this period: $2,847.23

For questions, call 1-800-555-BANK or visit your local branch.
Statement Date: February 1, 2026""",
        "extracted_data": {
            "account_type": "checking",
            "account_number": "****4521",
            "bank_name": "First National Bank",
            "beginning_balance": 1650.00,
            "ending_balance": 1500.00,
            "total_deposits": 2300.00,
            "total_withdrawals": 2450.00,
            "total_transactions": 35,
            "social_security_income": 1850.00,
            "pension_income": 450.00,
            "medicare_premium": 174.70,
            "grocery_expenses": 774.06,
            "healthcare_expenses": 633.95,
            "utility_expenses": 420.00
        },
        "ai_analysis": "Comprehensive 30-day transaction history shows regular income pattern: Social Security ($1,850/mo) on the 3rd and pension ($450/mo) on the 5th. Monthly expenses total $2,450 with groceries ($774) and healthcare ($634) being largest categories. The ER visit on 1/28 ($250 copay) corresponds to the wandering incident that led to hospitalization. Balance of $1,500 is countable for Medicaid. Combined with savings, total assets are $3,000 - requiring $1,000 spend-down."
    },
    {
        "name": "Bank Statement - Savings - January 2026",
        "category": "bank",
        "doc_type": "bank_statement",
        "content": """FIRST NATIONAL BANK - SAVINGS ACCOUNT STATEMENT
Account Number: ****4522
Statement Period: January 1-31, 2026
Account Holder: Margaret A. Thompson

BEGINNING BALANCE (1/1/26): $1,500.00

DEPOSITS AND CREDITS:
01/31/26  Interest Earned                  +$0.38

WITHDRAWALS AND DEBITS:
None

ENDING BALANCE (1/31/26): $1,500.38

Annual Percentage Yield: 0.30%""",
        "extracted_data": {
            "account_type": "savings",
            "account_number": "****4522",
            "bank_name": "First National Bank",
            "ending_balance": 1500.38,
            "interest_earned": 0.38
        },
        "ai_analysis": "Savings account with $1,500 balance. Combined with checking ($1,500), total bank assets are $3,000 - which is $1,000 over the Medicaid asset limit of $2,000."
    },
    {
        "name": "DD-214 - Certificate of Release",
        "category": "veteran",
        "doc_type": "dd214",
        "content": """CERTIFICATE OF RELEASE OR DISCHARGE FROM ACTIVE DUTY
DD FORM 214

1. NAME: THOMPSON, ROBERT JAMES
2. SERVICE NUMBER: RA 12345678
3. SOCIAL SECURITY NUMBER: ***-**-6789
4. GRADE, RATE OR RANK: E-5 / SERGEANT
5. PAY GRADE: E-5
6. DATE OF BIRTH: 15 MAY 1940
7. PLACE OF ENTRY INTO ACTIVE DUTY: MIAMI, FLORIDA

8. HOME OF RECORD AT TIME OF ENTRY: WEST PALM BEACH, FL

9. DATE ENTERED ACTIVE DUTY: 01 JUNE 1965
10. SEPARATION DATE: 15 AUGUST 1969
11. TOTAL ACTIVE SERVICE: 4 YEARS, 2 MONTHS, 14 DAYS

12. BRANCH: U.S. ARMY
13. PRIMARY SPECIALTY: 11B INFANTRYMAN

14. DECORATIONS AND AWARDS:
- Vietnam Service Medal
- National Defense Service Medal
- Army Commendation Medal
- Combat Infantryman Badge

15. CHARACTER OF SERVICE: HONORABLE

16. WARTIME SERVICE: VIETNAM ERA (Aug 5, 1964 - May 7, 1975)

This document certifies that Robert James Thompson served honorably in the United States Army during the Vietnam War era.""",
        "extracted_data": {
            "veteran_name": "Robert James Thompson",
            "service_number": "RA 12345678",
            "branch": "U.S. Army",
            "rank": "E-5 / Sergeant",
            "service_start": "1965-06-01",
            "service_end": "1969-08-15",
            "discharge_type": "Honorable",
            "wartime_service": "Vietnam Era"
        },
        "ai_analysis": "Robert Thompson served 4+ years in the U.S. Army during the Vietnam War era with an Honorable discharge. This qualifies his surviving spouse Margaret for VA Survivors Pension with Aid & Attendance benefits of up to $1,432/month."
    },
    {
        "name": "Death Certificate - Robert Thompson",
        "category": "legal",
        "doc_type": "death_certificate",
        "content": """STATE OF FLORIDA - CERTIFICATE OF DEATH
DEPARTMENT OF HEALTH - VITAL RECORDS

DECEDENT INFORMATION:
Name: Robert James Thompson
Date of Death: March 15, 2020
Time of Death: 14:32
Place of Death: Good Samaritan Medical Center, West Palm Beach, FL
County of Death: Palm Beach

PERSONAL INFORMATION:
Date of Birth: May 15, 1940
Age at Death: 79 years
Sex: Male
Race: White
Marital Status: Married
Surviving Spouse: Margaret Ann Thompson

CAUSE OF DEATH:
Immediate Cause: Cardiac Arrest
Due to: Congestive Heart Failure
Due to: Coronary Artery Disease

CERTIFIER:
Dr. Michael Rodriguez, MD
Good Samaritan Medical Center

REGISTRATION NUMBER: 2020-123456
DATE FILED: March 18, 2020""",
        "extracted_data": {
            "decedent_name": "Robert James Thompson",
            "date_of_death": "2020-03-15",
            "place_of_death": "West Palm Beach, FL",
            "surviving_spouse": "Margaret Ann Thompson",
            "cause_of_death": "Cardiac Arrest due to Congestive Heart Failure"
        },
        "ai_analysis": "Death certificate confirms Robert Thompson passed on March 15, 2020. Margaret is listed as surviving spouse. This document is required for VA Survivors Pension application (Form 21-534EZ)."
    },
    {
        "name": "Marriage Certificate",
        "category": "legal",
        "doc_type": "marriage_certificate",
        "content": """STATE OF FLORIDA - CERTIFICATE OF MARRIAGE
PALM BEACH COUNTY CLERK OF COURT

BRIDE:
Name: Margaret Ann Wilson
Date of Birth: March 15, 1942
Place of Birth: Jacksonville, Florida
Residence: West Palm Beach, Florida

GROOM:
Name: Robert James Thompson
Date of Birth: May 15, 1940
Place of Birth: Miami, Florida
Residence: West Palm Beach, Florida

MARRIAGE INFORMATION:
Date of Marriage: June 20, 1964
Place of Marriage: First Baptist Church, West Palm Beach, FL
County: Palm Beach

OFFICIANT:
Rev. William Harrison
First Baptist Church

WITNESSES:
1. James Wilson (Father of Bride)
2. Dorothy Thompson (Mother of Groom)

CERTIFICATE NUMBER: 1964-MC-45678
DATE RECORDED: June 22, 1964

This certifies that the above-named persons were united in marriage in accordance with the laws of the State of Florida.""",
        "extracted_data": {
            "bride_name": "Margaret Ann Wilson",
            "groom_name": "Robert James Thompson",
            "marriage_date": "1964-06-20",
            "marriage_location": "West Palm Beach, FL",
            "years_married": 55
        },
        "ai_analysis": "Marriage certificate confirms Margaret and Robert were married on June 20, 1964 - 55 years before Robert's death. This establishes Margaret's eligibility as a surviving spouse for VA benefits."
    },
    {
        "name": "Social Security Statement",
        "category": "income",
        "doc_type": "social_security_statement",
        "content": """SOCIAL SECURITY ADMINISTRATION
BENEFIT VERIFICATION LETTER

Date: January 15, 2026

Beneficiary: Margaret A. Thompson
SSN: ***-**-4521
Date of Birth: March 15, 1942

CURRENT BENEFIT INFORMATION:

Benefit Type: Retirement (Old-Age)
Monthly Benefit Amount: $1,850.00
Medicare Part B Premium: -$174.70
Net Monthly Deposit: $1,675.30

Payment Method: Direct Deposit
Bank: First National Bank
Account: ****4521

BENEFIT HISTORY:
- Initial Claim Date: March 2007
- Full Retirement Age Reached: March 2008
- Current COLA Adjustment: 3.2% (January 2026)

This letter verifies that Margaret A. Thompson is currently receiving Social Security retirement benefits as stated above.

For questions, call 1-800-772-1213 (TTY 1-800-325-0778)""",
        "extracted_data": {
            "beneficiary": "Margaret A. Thompson",
            "benefit_type": "Retirement",
            "monthly_benefit": 1850.00,
            "medicare_deduction": 174.70,
            "net_deposit": 1675.30
        },
        "ai_analysis": "Social Security provides $1,850/month gross, $1,675.30 net after Medicare Part B deduction. This income will be applied toward facility costs under Medicaid's patient responsibility rules."
    },
    {
        "name": "Medical Records - Hospital Admission",
        "category": "medical",
        "doc_type": "medical_record",
        "content": """PALM BEACH GENERAL HOSPITAL
ADMISSION SUMMARY

PATIENT: Margaret A. Thompson
DOB: 03/15/1942 (Age 83)
MRN: 789456123
ADMISSION DATE: January 28, 2026
ATTENDING PHYSICIAN: Dr. Sarah Chen, MD (Internal Medicine)

CHIEF COMPLAINT:
Patient found wandering outside home at 3:00 AM by neighbor. Confused and disoriented. Unable to recall home address or family contact information.

HISTORY OF PRESENT ILLNESS:
83-year-old female with known history of Alzheimer's disease brought to ER by EMS after being found wandering in nightgown in 45-degree weather. Neighbor called 911 when patient could not identify herself or provide emergency contact. Patient was hypothermic (96.2°F) and dehydrated on arrival.

PAST MEDICAL HISTORY:
1. Alzheimer's Disease - diagnosed 2023
2. Hypertension - controlled on lisinopril
3. Type 2 Diabetes - diet controlled
4. Osteoarthritis - bilateral knees
5. Hypothyroidism - on levothyroxine

MEDICATIONS:
- Donepezil 10mg daily (Alzheimer's)
- Lisinopril 20mg daily (HTN)
- Levothyroxine 50mcg daily (thyroid)
- Acetaminophen 650mg PRN (pain)

SOCIAL HISTORY:
- Widow since March 2020 (husband Robert deceased)
- Lives alone in single-family home
- Adult daughter lives in California (primary contact)
- No local family support
- Previously independent with IADLs, declining over past 6 months

PHYSICAL EXAMINATION:
- General: Elderly female, appears stated age, confused but cooperative
- Vital Signs: BP 142/88, HR 78, RR 18, Temp 96.2°F (hypothermic)
- Neuro: Alert but disoriented to time and place. MMSE 16/30.
- Cardiac: Regular rate and rhythm, no murmurs
- Pulmonary: Clear to auscultation bilaterally
- Extremities: No edema, good pulses

ASSESSMENT:
1. Alzheimer's Disease, moderate stage with wandering behavior
2. Hypothermia, mild - resolved with warming
3. Dehydration - IV fluids administered
4. Unsafe living situation - patient cannot live alone

PLAN:
1. Admit for observation and stabilization
2. Social work consult for discharge planning
3. Recommend Memory Care placement - patient not safe to return home
4. Contact daughter regarding care planning
5. Initiate Medicaid application process

DISCHARGE RECOMMENDATION:
Patient requires 24-hour supervised care in a Memory Care facility. Not safe to return home alone. Recommend placement within 7-10 days pending insurance/Medicaid approval.

Dr. Sarah Chen, MD
Internal Medicine
Palm Beach General Hospital""",
        "extracted_data": {
            "patient_name": "Margaret A. Thompson",
            "admission_date": "2026-01-28",
            "attending_physician": "Dr. Sarah Chen, MD",
            "primary_diagnosis": "Alzheimer's Disease, moderate stage",
            "secondary_diagnoses": ["Hypertension", "Type 2 Diabetes", "Hypothyroidism"],
            "mmse_score": 16,
            "discharge_recommendation": "Memory Care facility"
        },
        "ai_analysis": "Hospital admission documents wandering episode indicating unsafe living situation. MMSE score of 16/30 confirms moderate cognitive impairment. Physician recommends Memory Care placement within 7-10 days. This medical documentation supports both Medicaid ICP application and VA Aid & Attendance eligibility."
    },
    {
        "name": "Cognitive Assessment - MMSE",
        "category": "medical",
        "doc_type": "cognitive_assessment",
        "content": """PALM BEACH GENERAL HOSPITAL
COGNITIVE ASSESSMENT REPORT

PATIENT: Margaret A. Thompson
DOB: 03/15/1942
DATE OF ASSESSMENT: January 29, 2026
EXAMINER: Dr. Sarah Chen, MD

MINI-MENTAL STATE EXAMINATION (MMSE)

ORIENTATION (10 points possible):
- Time (year, season, date, day, month): 2/5
- Place (state, county, town, hospital, floor): 3/5
ORIENTATION SCORE: 5/10

REGISTRATION (3 points possible):
- Named 3 objects: 3/3
REGISTRATION SCORE: 3/3

ATTENTION AND CALCULATION (5 points possible):
- Serial 7s or WORLD backwards: 2/5
ATTENTION SCORE: 2/5

RECALL (3 points possible):
- Recalled 3 objects: 1/3
RECALL SCORE: 1/3

LANGUAGE (9 points possible):
- Naming (2 items): 2/2
- Repetition: 1/1
- 3-stage command: 2/3
- Reading: 1/1
- Writing: 0/1
- Copying: 0/1
LANGUAGE SCORE: 6/9

TOTAL MMSE SCORE: 16/30

INTERPRETATION:
- 24-30: Normal cognition
- 18-23: Mild cognitive impairment
- 10-17: MODERATE COGNITIVE IMPAIRMENT ← Patient's range
- 0-9: Severe cognitive impairment

CLOCK DRAWING TEST:
Score: 2/5 (significant impairment)
- Drew circle: Yes
- Numbers present: Partial (missing 10, 11, 12)
- Numbers in correct position: No
- Hands present: Yes
- Correct time shown: No

FUNCTIONAL ASSESSMENT (Activities of Daily Living):

BASIC ADLs:
- Bathing: Requires Assistance
- Dressing: Requires Assistance
- Toileting: Supervision Needed
- Transferring: Independent
- Eating: Supervision Needed (forgets to eat)
- Continence: Occasional accidents

INSTRUMENTAL ADLs:
- Medication Management: Unable (forgets doses, takes wrong pills)
- Meal Preparation: Unable (safety concern with stove)
- Housekeeping: Unable
- Laundry: Unable
- Transportation: Unable (no longer drives)
- Shopping: Unable
- Telephone Use: Limited (can answer but cannot dial)
- Financial Management: Unable

CLINICAL IMPRESSION:
Margaret Thompson demonstrates moderate cognitive impairment consistent with her Alzheimer's diagnosis. She requires assistance with 2+ ADLs and is unable to manage IADLs independently. Her wandering behavior and inability to recognize danger indicate she cannot safely live alone.

RECOMMENDATIONS:
1. 24-hour supervised care in Memory Care facility
2. Continue current Alzheimer's medication (Donepezil)
3. Regular cognitive reassessment every 6 months
4. Safety measures for wandering prevention

This assessment supports eligibility for:
- VA Aid & Attendance (requires assistance with 2+ ADLs)
- Florida Medicaid ICP (requires nursing facility level of care)

Dr. Sarah Chen, MD
Internal Medicine""",
        "extracted_data": {
            "mmse_score": 16,
            "mmse_interpretation": "Moderate cognitive impairment",
            "clock_drawing_score": 2,
            "adl_bathing": "Requires Assistance",
            "adl_dressing": "Requires Assistance",
            "adl_toileting": "Supervision Needed",
            "adl_transferring": "Independent",
            "adl_eating": "Supervision Needed",
            "adl_medication": "Unable"
        },
        "ai_analysis": "MMSE score of 16/30 indicates moderate cognitive impairment. Patient requires assistance with bathing, dressing, and eating - meeting the VA Aid & Attendance requirement of needing help with 2+ ADLs. Clock drawing test (2/5) shows significant executive function impairment. This documentation is critical for both VA Form 21-2680 and Medicaid CARES assessment."
    },
    {
        "name": "Medicare Summary Notice",
        "category": "insurance",
        "doc_type": "medicare_summary",
        "content": """MEDICARE SUMMARY NOTICE
For: Margaret A. Thompson
Medicare Number: 1EG4-TE5-MK72
Date of This Notice: January 2026

YOUR MEDICARE COVERAGE:

PART A (Hospital Insurance): ACTIVE
- Premium: $0 (paid through work history)
- Deductible: $1,632 per benefit period
- Coverage: Inpatient hospital, skilled nursing (limited), hospice

PART B (Medical Insurance): ACTIVE
- Premium: $174.70/month (deducted from Social Security)
- Deductible: $240/year (met)
- Coverage: Doctor visits, outpatient care, preventive services

PART D (Prescription Drug): ACTIVE
- Plan: SilverScript Choice
- Premium: $28.50/month
- Coverage: Prescription medications

MEDIGAP SUPPLEMENT: NONE

IMPORTANT NOTICE ABOUT LONG-TERM CARE:

Medicare does NOT cover:
- Long-term nursing home care
- Assisted living facilities
- Memory care facilities
- Custodial care (help with daily activities)

Medicare only covers skilled nursing facility care for up to 100 days following a qualifying hospital stay, and only if skilled care is needed.

For long-term care coverage, consider:
- Medicaid (for those who qualify financially)
- Long-term care insurance
- Private pay

Questions? Call 1-800-MEDICARE (1-800-633-4227)
TTY: 1-877-486-2048""",
        "extracted_data": {
            "medicare_number": "1EG4-TE5-MK72",
            "part_a_status": "Active",
            "part_b_status": "Active",
            "part_b_premium": 174.70,
            "part_d_plan": "SilverScript Choice",
            "part_d_premium": 28.50,
            "medigap": "None"
        },
        "ai_analysis": "Medicare is active but does NOT cover long-term Memory Care costs. Margaret has no Medigap supplement or long-term care insurance. The coverage gap for Memory Care ($7,500-9,500/month) must be filled by Medicaid ICP and VA Aid & Attendance benefits."
    },
    {
        "name": "Property Tax Statement - Homestead",
        "category": "property",
        "doc_type": "property_tax",
        "content": """PALM BEACH COUNTY PROPERTY APPRAISER
2025 TAX STATEMENT

PROPERTY OWNER: Margaret A. Thompson
PROPERTY ADDRESS: 1234 Palm Way, West Palm Beach, FL 33401
PARCEL ID: 12-34-56-78-90-000-1234

PROPERTY INFORMATION:
- Property Type: Single Family Residence
- Year Built: 1975
- Living Area: 1,450 sq ft
- Lot Size: 0.25 acres
- Bedrooms: 3
- Bathrooms: 2

ASSESSED VALUES:
- Market Value: $285,000
- Assessed Value: $185,000 (with homestead exemption)
- Homestead Exemption: $50,000

TAX INFORMATION:
- 2025 Property Tax: $3,245.00
- Homestead Exemption: Applied
- Senior Exemption: Applied

MORTGAGE INFORMATION:
- Mortgage Holder: None (paid off)
- Outstanding Balance: $0

HOMESTEAD STATUS: ACTIVE
This property qualifies for Florida Homestead Exemption under Article X, Section 4 of the Florida Constitution.

For Medicaid purposes: Primary residence is EXEMPT from countable assets if applicant intends to return home or if spouse continues to reside there.""",
        "extracted_data": {
            "property_address": "1234 Palm Way, West Palm Beach, FL 33401",
            "market_value": 285000,
            "assessed_value": 185000,
            "mortgage_balance": 0,
            "homestead_status": "Active",
            "property_tax": 3245.00
        },
        "ai_analysis": "Home is owned free and clear (no mortgage). Market value of $285,000 is well under Florida's $713,000 homestead equity cap for Medicaid. As a homestead property, it is EXEMPT from Medicaid countable assets. Property taxes of $3,245/year should be maintained to protect the asset."
    },
    {
        "name": "AI Comprehensive Analysis Report",
        "category": "ai_analysis",
        "doc_type": "ai_comprehensive_report",
        "content": """CARENAV AI COMPREHENSIVE ANALYSIS REPORT
Generated: February 4, 2026
Patient: Margaret A. Thompson (Age 83)

═══════════════════════════════════════════════════════════════
EXECUTIVE SUMMARY
═══════════════════════════════════════════════════════════════

Margaret Thompson, 83, is a widow of Vietnam veteran Robert Thompson who passed in March 2020. She is currently hospitalized at Palm Beach General following a wandering episode and requires Memory Care placement. Based on comprehensive analysis of her financial documents, military records, and care needs, she qualifies for significant benefits that will substantially reduce her out-of-pocket care costs.

CRITICAL FINDING: With proper benefit applications, Margaret's Memory Care costs can be reduced to $0 out-of-pocket.

═══════════════════════════════════════════════════════════════
FINANCIAL ANALYSIS
═══════════════════════════════════════════════════════════════

MONTHLY INCOME:
- Social Security:        $1,850.00
- Pension (Robert's):     $  450.00
- TOTAL MONTHLY INCOME:   $2,300.00

CURRENT ASSETS:
- Checking Account:       $1,500.00
- Savings Account:        $1,500.00
- TOTAL COUNTABLE:        $3,000.00

MEDICAID ASSET ANALYSIS:
- Asset Limit:            $2,000.00
- Current Assets:         $3,000.00
- OVER LIMIT BY:          $1,000.00

EXEMPT ASSETS (Not Counted):
- Homestead:              $285,000 (exempt - under $713K cap)
- Personal Property:      Exempt
- One Vehicle:            Exempt

═══════════════════════════════════════════════════════════════
BENEFITS ELIGIBILITY MATRIX
═══════════════════════════════════════════════════════════════

PROGRAM                  STATUS      MONTHLY VALUE    ACTION REQUIRED
─────────────────────────────────────────────────────────────────
Florida Medicaid ICP     Pending     ~$8,000+        Spend down $1,000
VA Survivors Pension     Eligible    $1,432          Submit Form 21-534EZ
VA Aid & Attendance      Eligible    (included)      Medical evidence
Medicare Part A          Active      Hospital        None
Medicare Part B          Active      -$174.70        None
─────────────────────────────────────────────────────────────────
TOTAL MONTHLY BENEFIT               $9,432+

═══════════════════════════════════════════════════════════════
CARE COST PROJECTION
═══════════════════════════════════════════════════════════════

Memory Care Facility (Palm Beach avg):    $7,500 - $9,500/month

INCOME APPLIED TO CARE:
- Social Security:                        -$1,850
- Pension:                                -$  450
- VA Aid & Attendance:                    -$1,432
- Medicaid Coverage (remainder):          -$3,768 to -$5,768

NET OUT-OF-POCKET (with all benefits):    $0

═══════════════════════════════════════════════════════════════
60-MONTH LOOK-BACK ANALYSIS
═══════════════════════════════════════════════════════════════

Period Reviewed: January 2021 - January 2026

YEAR    FINDING                         STATUS
────────────────────────────────────────────────
2021    No reportable transfers         CLEAR
2022    No reportable transfers         CLEAR
2023    No reportable transfers         CLEAR
2024    No reportable transfers         CLEAR
2025    No reportable transfers         CLEAR
────────────────────────────────────────────────

RESULT: No disqualifying asset transfers found. No penalty period will apply to Medicaid application.

═══════════════════════════════════════════════════════════════
DECEASED SPOUSE DEBT ANALYSIS
═══════════════════════════════════════════════════════════════

Robert Thompson passed away in March 2020. Under Florida law (a common law property state), Margaret is generally NOT responsible for Robert's individual debts.

DEBT IDENTIFIED:
- Credit card in Robert's name only: $2,400

ANALYSIS RESULT: Margaret is NOT liable for this debt. If contacted by collectors, she should inform them that Robert is deceased and she is not responsible for his individual debts.

WARNING: Do NOT pay this debt - it would waste assets needed for Margaret's care.

═══════════════════════════════════════════════════════════════
RECOMMENDED ACTION PLAN
═══════════════════════════════════════════════════════════════

WEEK 1 (URGENT):
□ Day 1-2: Contact funeral home for prepaid funeral contract ($1,000)
□ Day 2-3: Tour Sunrise of Palm Beach Memory Care
□ Day 3-4: Meet with hospital social worker for Medicaid application
□ Day 4-5: Have Dr. Chen complete VA Form 21-2680

WEEK 2:
□ Complete VA Form 21-534EZ
□ Submit VA application
□ Confirm Medicaid application submitted
□ Finalize facility admission

EXPECTED OUTCOME:
Margaret placed in Memory Care with all benefit applications submitted within 14 days.

═══════════════════════════════════════════════════════════════
AI CONFIDENCE LEVEL: 95%
═══════════════════════════════════════════════════════════════

This analysis is based on documents provided and Florida elder law as of 2026. Recommend consultation with elder law attorney for complex situations.

Report Generated by CareNav AI
Powered by Azure OpenAI""",
        "extracted_data": {
            "total_monthly_income": 2300.00,
            "total_countable_assets": 3000.00,
            "over_medicaid_limit_by": 1000.00,
            "va_benefit_eligible": True,
            "va_monthly_benefit": 1432.00,
            "medicaid_eligible_after_spenddown": True,
            "lookback_clear": True,
            "deceased_spouse_debt_liable": False,
            "projected_out_of_pocket": 0
        },
        "ai_analysis": "Comprehensive AI analysis shows Margaret qualifies for both VA Survivors Pension ($1,432/mo) and Florida Medicaid ICP after spending down $1,000. With all benefits applied, her Memory Care costs will be $0 out-of-pocket. No issues found in 60-month look-back. Not liable for deceased spouse's debts."
    },
    {
        "name": "VA Benefits Application Guide",
        "category": "ai_analysis",
        "doc_type": "ai_guide",
        "content": """VA BENEFITS APPLICATION GUIDE
For: Margaret A. Thompson (Surviving Spouse)
Generated by CareNav AI

═══════════════════════════════════════════════════════════════
ELIGIBILITY CONFIRMED
═══════════════════════════════════════════════════════════════

Margaret qualifies for VA Survivors Pension with Aid & Attendance because:
✓ Robert served 90+ days active duty (4 years, 2 months)
✓ Robert served during wartime (Vietnam Era)
✓ Robert received Honorable discharge
✓ Margaret was married to Robert at time of death
✓ Margaret has not remarried
✓ Margaret needs help with daily activities (2+ ADLs)
✓ Net worth under $150,538 limit

MONTHLY BENEFIT: $1,432

═══════════════════════════════════════════════════════════════
STEP-BY-STEP APPLICATION PROCESS
═══════════════════════════════════════════════════════════════

STEP 1: GATHER REQUIRED DOCUMENTS
─────────────────────────────────
□ DD-214 (Certificate of Release) - OBTAINED ✓
□ Death Certificate - OBTAINED ✓
□ Marriage Certificate - OBTAINED ✓
□ Medical Evidence of Need - OBTAINED ✓ (Hospital records)

STEP 2: COMPLETE VA FORM 21-534EZ
─────────────────────────────────
Application for DIC, Death Pension, and/or Accrued Benefits

Download: https://www.va.gov/find-forms/about-form-21-534ez/

Key sections to complete:
- Section I: Claimant Information (Margaret's info)
- Section II: Veteran Information (Robert's info)
- Section III: Military Service (from DD-214)
- Section IV: Marital Information
- Section V: Net Worth (list all assets)
- Section VI: Income (Social Security, pension)
- Section VII: Medical Expenses

STEP 3: COMPLETE VA FORM 21-2680
─────────────────────────────────
Examination for Housebound Status or Permanent Need for Regular Aid and Attendance

This form must be completed by a PHYSICIAN (Dr. Chen)

Key sections:
- Patient's diagnoses
- Ability to perform daily activities
- Need for assistance
- Restrictions on activities

STEP 4: SUBMIT APPLICATION
─────────────────────────────────
Options:
1. ONLINE: VA.gov (fastest)
2. BY MAIL: VA Pension Management Center
   Department of Veterans Affairs
   Pension Intake Center
   PO Box 5365
   Janesville, WI 53547-5365
3. IN PERSON: Palm Beach County Veterans Service Office
   Recommended - FREE assistance with application

═══════════════════════════════════════════════════════════════
IMPORTANT PHONE NUMBERS
═══════════════════════════════════════════════════════════════

VA Benefits Hotline: 1-800-827-1000
Palm Beach County VSO: (561) 355-4760
eBenefits Help Desk: 1-800-983-0937

═══════════════════════════════════════════════════════════════
PROCESSING TIME & RETROACTIVE BENEFITS
═══════════════════════════════════════════════════════════════

Expected Processing: 3-6 months
Benefits are RETROACTIVE to application date

Example: If Margaret applies February 4, 2026 and is approved June 2026, she will receive a lump sum for February-June ($1,432 x 4 = $5,728) plus ongoing monthly payments.

═══════════════════════════════════════════════════════════════
TIPS FOR FASTER APPROVAL
═══════════════════════════════════════════════════════════════

1. Submit ALL documents with initial application
2. Use a Veterans Service Organization (VSO) - FREE help
3. Include detailed medical evidence
4. Respond promptly to any VA requests
5. Keep copies of everything submitted

Report Generated by CareNav AI""",
        "extracted_data": {
            "benefit_type": "VA Survivors Pension with Aid & Attendance",
            "monthly_amount": 1432.00,
            "forms_required": ["21-534EZ", "21-2680"],
            "processing_time": "3-6 months",
            "retroactive": True
        },
        "ai_analysis": "Step-by-step guide for VA Survivors Pension application. All required documents have been obtained. Recommend using Palm Beach County VSO for free application assistance. Benefits are retroactive to application date."
    },
    {
        "name": "Florida Medicaid ICP Application Guide",
        "category": "ai_analysis",
        "doc_type": "ai_guide",
        "content": """FLORIDA MEDICAID ICP APPLICATION GUIDE
For: Margaret A. Thompson
Generated by CareNav AI

═══════════════════════════════════════════════════════════════
PROGRAM OVERVIEW
═══════════════════════════════════════════════════════════════

Florida Medicaid Institutional Care Program (ICP) covers:
- Nursing facility care
- Memory Care in approved facilities
- 24-hour skilled nursing

Monthly Value: $8,000+ (covers facility costs minus patient responsibility)

═══════════════════════════════════════════════════════════════
ELIGIBILITY REQUIREMENTS
═══════════════════════════════════════════════════════════════

ASSET LIMIT: $2,000
Margaret's Current Assets: $3,000
OVER LIMIT BY: $1,000 ← Must spend down

INCOME LIMIT: $2,829/month
Margaret's Income: $2,300/month ✓ UNDER LIMIT

MEDICAL NECESSITY: Must require nursing facility level of care
Margaret's Status: ✓ QUALIFIES (per hospital assessment)

═══════════════════════════════════════════════════════════════
STEP-BY-STEP APPLICATION PROCESS
═══════════════════════════════════════════════════════════════

STEP 1: COMPLETE SPEND-DOWN ($1,000)
─────────────────────────────────────
Reduce countable assets from $3,000 to $2,000 or less

RECOMMENDED SPEND-DOWN OPTIONS:
□ Prepaid funeral contract: $1,000 (BEST OPTION)
  - Must be IRREVOCABLE
  - Florida-licensed funeral home
  - Completely exempt from Medicaid count

Alternative options:
□ Prepay dental work
□ Purchase medical equipment (wheelchair, walker)
□ Pay outstanding medical bills
□ Home repairs (if returning home possible)

WARNING: Do NOT give money to family members - creates penalty!

STEP 2: GATHER 60-MONTH BANK STATEMENTS
─────────────────────────────────────────
All checking, savings, investment accounts from January 2021 - Present

STATUS: ✓ OBTAINED
LOOK-BACK RESULT: ✓ CLEAR - No disqualifying transfers

STEP 3: APPLY VIA ACCESS FLORIDA
─────────────────────────────────
Online: www.myflorida.com/accessflorida
Phone: 1-866-762-2237

Application can be started by:
- Margaret (with assistance)
- Family member with Power of Attorney
- Hospital social worker (RECOMMENDED)

STEP 4: CARES ASSESSMENT
─────────────────────────
Florida will schedule a Comprehensive Assessment and Review for Long-Term Care Services (CARES)

This assessment determines:
- Level of care needed
- Appropriate placement
- Services required

Margaret's expected result: Nursing Facility Level of Care (qualifies for ICP)

═══════════════════════════════════════════════════════════════
REQUIRED DOCUMENTS CHECKLIST
═══════════════════════════════════════════════════════════════

IDENTIFICATION:
□ Social Security Card - OBTAINED ✓
□ Medicare Card - OBTAINED ✓
□ Photo ID (Driver's License) - OBTAINED ✓

FINANCIAL:
□ Bank Statements (60 months) - OBTAINED ✓
□ Social Security Award Letter - OBTAINED ✓
□ Pension Statement - OBTAINED ✓

PROPERTY:
□ Property Tax Statement - OBTAINED ✓
□ Homestead Exemption Proof - OBTAINED ✓
□ Vehicle Title - NEEDED

MEDICAL:
□ Hospital Records - OBTAINED ✓
□ Physician Statement of Need - OBTAINED ✓
□ List of Medications - OBTAINED ✓

LEGAL:
□ Power of Attorney - NEEDED
□ Death Certificate (spouse) - OBTAINED ✓

═══════════════════════════════════════════════════════════════
PATIENT RESPONSIBILITY CALCULATION
═══════════════════════════════════════════════════════════════

Once approved, Margaret will pay a "patient responsibility" amount:

Monthly Income:                    $2,300.00
Less: Personal Needs Allowance:    -$130.00
Less: Medicare Part B Premium:     -$174.70
─────────────────────────────────────────────
PATIENT RESPONSIBILITY:            $1,995.30/month

Medicaid pays the remainder of facility costs.

═══════════════════════════════════════════════════════════════
PROCESSING TIME
═══════════════════════════════════════════════════════════════

Standard Processing: 45-90 days
Expedited Processing: 15-30 days (available due to hospital discharge)

REQUEST EXPEDITED PROCESSING because:
- Patient is in hospital
- Discharge deadline approaching
- Unsafe to return home

═══════════════════════════════════════════════════════════════
IMPORTANT CONTACTS
═══════════════════════════════════════════════════════════════

ACCESS Florida: 1-866-762-2237
FL Elder Helpline: 1-800-963-5337
SHINE (Medicare Help): 1-800-963-5337
Palm Beach DCF Office: (561) 837-5000

Report Generated by CareNav AI""",
        "extracted_data": {
            "program": "Florida Medicaid ICP",
            "asset_limit": 2000.00,
            "current_assets": 3000.00,
            "spenddown_needed": 1000.00,
            "income_limit": 2829.00,
            "current_income": 2300.00,
            "patient_responsibility": 1995.30,
            "processing_time": "45-90 days"
        },
        "ai_analysis": "Medicaid ICP application guide showing $1,000 spend-down required. Recommend prepaid funeral contract as best spend-down option. 60-month look-back is clear. Request expedited processing due to hospital discharge timeline."
    },
    {
        "name": "AI Facility Comparison Report",
        "category": "ai_analysis",
        "doc_type": "ai_facility_report",
        "content": """AI FACILITY COMPARISON REPORT
Top Memory Care Facilities for Margaret Thompson
Palm Beach County, Florida
Generated by CareNav AI

═══════════════════════════════════════════════════════════════
SEARCH CRITERIA
═══════════════════════════════════════════════════════════════

Care Level Required: Memory Care (MC)
Location: Palm Beach County, FL
Budget: Medicaid-eligible facilities preferred
Distance: Within 10 miles of Palm Beach General Hospital
Special Requirements: 24-hour supervision, wandering prevention

═══════════════════════════════════════════════════════════════
TOP 3 RECOMMENDED FACILITIES
═══════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────┐
│ #1 SUNRISE OF PALM BEACH                                    │
│ MATCH SCORE: 92/100 ★★★★★                                   │
├─────────────────────────────────────────────────────────────┤
│ Address: 2500 N. Flagler Drive, West Palm Beach, FL 33407   │
│ Phone: (561) 555-0123                                       │
│ Distance: 3.2 miles from hospital                           │
│                                                             │
│ RATES:                                                      │
│ • Private Room: $7,200 - $8,500/month                       │
│ • Semi-Private: $6,500 - $7,200/month                       │
│                                                             │
│ MEDICAID: ✓ Accepts Medicaid                                │
│ • Medicaid beds available: Yes                              │
│ • Private pay requirement: None (day-one Medicaid OK)       │
│                                                             │
│ FEATURES:                                                   │
│ • Dedicated Memory Care unit (32 beds)                      │
│ • Secured outdoor garden                                    │
│ • 24-hour nursing staff                                     │
│ • Wandering prevention system                               │
│ • Music & art therapy programs                              │
│                                                             │
│ QUALITY:                                                    │
│ • State Rating: 4.5/5 stars                                 │
│ • Last Inspection: December 2025 - No deficiencies          │
│ • Staff-to-resident ratio: 1:5                              │
│                                                             │
│ AVAILABILITY: 2 beds available (as of Feb 2026)             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ #2 BROOKDALE WEST PALM BEACH                                │
│ MATCH SCORE: 87/100 ★★★★☆                                   │
├─────────────────────────────────────────────────────────────┤
│ Address: 1800 Forest Hill Blvd, West Palm Beach, FL 33406   │
│ Phone: (561) 555-0456                                       │
│ Distance: 5.8 miles from hospital                           │
│                                                             │
│ RATES:                                                      │
│ • Private Room: $6,800 - $8,200/month                       │
│ • Semi-Private: $5,900 - $6,800/month                       │
│                                                             │
│ MEDICAID: ✓ Accepts Medicaid                                │
│ • Medicaid beds available: Limited                          │
│ • Private pay requirement: 6 months preferred               │
│                                                             │
│ FEATURES:                                                   │
│ • Dedicated Memory Care unit (24 beds)                      │
│ • Indoor walking path                                       │
│ • 24-hour nursing staff                                     │
│ • Pet therapy program                                       │
│                                                             │
│ QUALITY:                                                    │
│ • State Rating: 4.0/5 stars                                 │
│ • Last Inspection: November 2025 - 1 minor deficiency       │
│ • Staff-to-resident ratio: 1:6                              │
│                                                             │
│ AVAILABILITY: WAITLIST (estimated 2-3 months)               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ #3 ALLEGRO SENIOR LIVING                                    │
│ MATCH SCORE: 84/100 ★★★★☆                                   │
├─────────────────────────────────────────────────────────────┤
│ Address: 3000 S. Ocean Blvd, Palm Beach, FL 33480           │
│ Phone: (561) 555-0789                                       │
│ Distance: 4.1 miles from hospital                           │
│                                                             │
│ RATES:                                                      │
│ • Private Room: $7,500 - $9,000/month                       │
│ • Semi-Private: Not available                               │
│                                                             │
│ MEDICAID: ✗ Does NOT accept Medicaid                        │
│ • Private pay only                                          │
│                                                             │
│ FEATURES:                                                   │
│ • Dedicated Memory Care unit (20 beds)                      │
│ • Ocean views                                               │
│ • 24-hour nursing staff                                     │
│ • Gourmet dining                                            │
│ • Spa services                                              │
│                                                             │
│ QUALITY:                                                    │
│ • State Rating: 4.2/5 stars                                 │
│ • Last Inspection: October 2025 - No deficiencies           │
│ • Staff-to-resident ratio: 1:4                              │
│                                                             │
│ AVAILABILITY: 1 bed available                               │
│                                                             │
│ ⚠️ NOT RECOMMENDED: Does not accept Medicaid                │
└─────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════
AI RECOMMENDATION
═══════════════════════════════════════════════════════════════

RECOMMENDED: SUNRISE OF PALM BEACH

Reasons:
1. Highest match score (92/100)
2. Accepts Medicaid from day one (critical for Margaret)
3. Immediate availability (2 beds)
4. Closest to hospital (3.2 miles) - easy transition
5. Excellent state rating (4.5/5 stars)
6. No recent inspection deficiencies
7. Dedicated Memory Care with wandering prevention

ACTION REQUIRED:
□ Call (561) 555-0123 to schedule tour
□ Request Medicaid-pending admission information
□ Tour facility within 48 hours (beds fill quickly)

═══════════════════════════════════════════════════════════════
COST COMPARISON WITH BENEFITS
═══════════════════════════════════════════════════════════════

                        Sunrise     Brookdale   Allegro
Monthly Rate:           $7,500      $7,000      $8,000
Less: Patient Resp.     -$1,995     -$1,995     N/A
Less: VA A&A            -$1,432     -$1,432     N/A
Less: Medicaid          -$4,073     -$3,573     N/A
─────────────────────────────────────────────────────────────
NET OUT-OF-POCKET:      $0          $0          $8,000/mo

Allegro is NOT viable for Margaret due to no Medicaid acceptance.

Report Generated by CareNav AI""",
        "extracted_data": {
            "recommended_facility": "Sunrise of Palm Beach",
            "match_score": 92,
            "monthly_rate": "7200-8500",
            "accepts_medicaid": True,
            "availability": "2 beds",
            "distance": 3.2,
            "state_rating": 4.5
        },
        "ai_analysis": "Sunrise of Palm Beach is the top recommendation with 92/100 match score. Accepts Medicaid from day one, has immediate availability, and is closest to the hospital. With all benefits applied, Margaret's out-of-pocket cost will be $0."
    },
    {
        "name": "Weekly Action Plan",
        "category": "ai_analysis",
        "doc_type": "ai_action_plan",
        "content": """AI-GENERATED WEEKLY ACTION PLAN
For: Margaret Thompson Care Team
Week of February 3-9, 2026
Generated by CareNav AI

═══════════════════════════════════════════════════════════════
WEEK OVERVIEW
═══════════════════════════════════════════════════════════════

GOAL: Place Margaret in Memory Care with all benefit applications submitted

CRITICAL DEADLINE: Hospital discharge by February 10, 2026

STATUS SUMMARY:
• Medicaid: $1,000 over asset limit - SPEND-DOWN REQUIRED
• VA Benefits: Eligible for $1,432/month - APPLICATION NEEDED
• Facility: Sunrise of Palm Beach recommended - TOUR NEEDED

═══════════════════════════════════════════════════════════════
MONDAY, FEBRUARY 3 - URGENT
═══════════════════════════════════════════════════════════════

□ 9:00 AM - Call Sunrise of Palm Beach
  Phone: (561) 555-0123
  Purpose: Schedule tour for Tuesday
  Ask about: Medicaid-pending admission process

□ 10:00 AM - Contact funeral home for prepaid contract
  Recommended: Palm Beach Memorial
  Phone: (561) 555-2345
  Amount: $1,000 (spend-down)
  IMPORTANT: Must be IRREVOCABLE contract

□ 2:00 PM - Call daughter (Sarah) with update
  Update on: Hospital status, facility options, benefit applications

═══════════════════════════════════════════════════════════════
TUESDAY, FEBRUARY 4 - HIGH PRIORITY
═══════════════════════════════════════════════════════════════

□ 10:00 AM - Tour Sunrise of Palm Beach
  Address: 2500 N. Flagler Drive, West Palm Beach
  Duration: ~2 hours
  
  QUESTIONS TO ASK:
  • What is the Medicaid-pending admission process?
  • What is the current availability?
  • What is the move-in timeline?
  • What items should Margaret bring?
  • Can we see the Memory Care unit?
  • What is the staff-to-resident ratio?

□ 1:00 PM - Pick up prepaid funeral contract
  Bring: Check for $1,000
  Get: Receipt and contract copy for Medicaid application

□ 3:00 PM - Review admission paperwork from Sunrise

═══════════════════════════════════════════════════════════════
WEDNESDAY, FEBRUARY 5 - HIGH PRIORITY
═══════════════════════════════════════════════════════════════

□ 9:00 AM - Meet with hospital social worker
  Location: Palm Beach General Hospital, Social Services
  Purpose: Initiate Medicaid application
  
  BRING:
  • Bank statements (60 months)
  • Social Security statement
  • Prepaid funeral contract (spend-down proof)
  • Property tax statement
  • Medicare card

□ 11:00 AM - Request expedited Medicaid processing
  Reason: Hospital discharge deadline
  
□ 2:00 PM - Have Dr. Chen complete VA Form 21-2680
  Form: Examination for Aid & Attendance
  Location: Hospital, Dr. Chen's office

═══════════════════════════════════════════════════════════════
THURSDAY, FEBRUARY 6 - MEDIUM PRIORITY
═══════════════════════════════════════════════════════════════

□ 9:00 AM - Complete VA Form 21-534EZ
  Download: www.va.gov/find-forms/about-form-21-534ez/
  
  DOCUMENTS NEEDED:
  • DD-214
  • Death Certificate
  • Marriage Certificate
  • Bank statements
  • Social Security statement

□ 1:00 PM - Gather all supporting documents for VA
  Make copies of everything
  Organize in folder

□ 3:00 PM - Call Palm Beach County VSO for assistance
  Phone: (561) 355-4760
  Purpose: Review application before submission

═══════════════════════════════════════════════════════════════
FRIDAY, FEBRUARY 7 - MEDIUM PRIORITY
═══════════════════════════════════════════════════════════════

□ 9:00 AM - Submit VA application
  Options:
  1. Online at VA.gov (fastest)
  2. Through VSO (recommended)
  3. By mail to Pension Intake Center

□ 11:00 AM - Follow up with Sunrise on admission
  Confirm: Bed availability
  Confirm: Move-in date
  Confirm: What to bring

□ 2:00 PM - Confirm Medicaid application submitted
  Call ACCESS Florida: 1-866-762-2237
  Get: Application confirmation number

□ 4:00 PM - Update daughter on week's progress

═══════════════════════════════════════════════════════════════
WEEKEND TASKS (IF NEEDED)
═══════════════════════════════════════════════════════════════

□ Prepare Margaret's belongings for move
  • Comfortable clothing (labeled)
  • Family photos
  • Favorite items
  • Toiletries

□ Notify utility companies of upcoming move
□ Forward mail to facility or family member
□ Cancel unnecessary subscriptions

═══════════════════════════════════════════════════════════════
EXPECTED OUTCOME
═══════════════════════════════════════════════════════════════

By end of week:
✓ Spend-down complete ($1,000 prepaid funeral)
✓ Medicaid application submitted (expedited)
✓ VA application submitted
✓ Facility selected and admission scheduled
✓ Margaret ready for safe discharge

NEXT WEEK:
• Margaret moves to Sunrise of Palm Beach
• Follow up on Medicaid approval
• Follow up on VA approval

═══════════════════════════════════════════════════════════════
EMERGENCY CONTACTS
═══════════════════════════════════════════════════════════════

Hospital Social Worker: (561) 555-1000
Sunrise of Palm Beach: (561) 555-0123
VA Benefits Hotline: 1-800-827-1000
ACCESS Florida: 1-866-762-2237
Daughter (Sarah): (555) 123-4567

Report Generated by CareNav AI""",
        "extracted_data": {
            "week_start": "2026-02-03",
            "week_end": "2026-02-09",
            "critical_deadline": "2026-02-10",
            "tasks_monday": 3,
            "tasks_tuesday": 3,
            "tasks_wednesday": 3,
            "tasks_thursday": 3,
            "tasks_friday": 4
        },
        "ai_analysis": "Detailed day-by-day action plan for the week. Prioritizes spend-down completion, facility tour, and benefit applications. All tasks aligned with hospital discharge deadline of February 10."
    },
    {
        "name": "Spend-Down Options Analysis",
        "category": "ai_analysis",
        "doc_type": "ai_spenddown_analysis",
        "content": """MEDICAID SPEND-DOWN OPTIONS ANALYSIS
For: Margaret A. Thompson
Amount to Spend Down: $1,000
Generated by CareNav AI

═══════════════════════════════════════════════════════════════
CURRENT SITUATION
═══════════════════════════════════════════════════════════════

Current Countable Assets: $3,000
Medicaid Asset Limit: $2,000
AMOUNT OVER LIMIT: $1,000

Margaret must reduce her countable assets by $1,000 to qualify for Florida Medicaid ICP (Institutional Care Program).

═══════════════════════════════════════════════════════════════
LEGAL SPEND-DOWN OPTIONS (RANKED BY RECOMMENDATION)
═══════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────┐
│ OPTION 1: PREPAID FUNERAL CONTRACT (RECOMMENDED)           │
│ Amount: $1,000                                              │
│ Legal Basis: FL Stat. 497.458; 42 CFR 435.725              │
├─────────────────────────────────────────────────────────────┤
│ PROS:                                                       │
│ • 100% exempt from Medicaid count                          │
│ • Provides peace of mind for family                        │
│ • Can include: casket, burial, service, flowers            │
│ • Immediate spend-down (same day)                          │
│                                                             │
│ CONS:                                                       │
│ • Must be IRREVOCABLE (cannot get money back)              │
│                                                             │
│ HOW TO DO IT:                                               │
│ 1. Call Palm Beach Memorial: (561) 555-2345                │
│ 2. Request irrevocable prepaid funeral contract            │
│ 3. Pay $1,000 by check                                     │
│ 4. Get receipt and contract copy                           │
│ 5. Submit to Medicaid as spend-down proof                  │
│                                                             │
│ TIMELINE: Same day                                          │
│ AI CONFIDENCE: 98%                                          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ OPTION 2: PREPAID DENTAL WORK                              │
│ Amount: Up to $1,000                                        │
│ Legal Basis: 42 CFR 435.725                                │
├─────────────────────────────────────────────────────────────┤
│ PROS:                                                       │
│ • Improves quality of life                                 │
│ • Medical necessity documentation                          │
│ • Fully exempt from Medicaid                               │
│                                                             │
│ CONS:                                                       │
│ • May require dental appointment scheduling                │
│ • Margaret may not need dental work                        │
│                                                             │
│ EXAMPLES:                                                   │
│ • Dentures: $500-2,000                                     │
│ • Dental cleaning: $100-200                                │
│ • Fillings: $150-300 each                                  │
│                                                             │
│ TIMELINE: 1-2 weeks                                         │
│ AI CONFIDENCE: 85%                                          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ OPTION 3: MEDICAL EQUIPMENT                                │
│ Amount: Up to $1,000                                        │
│ Legal Basis: 42 CFR 435.725                                │
├─────────────────────────────────────────────────────────────┤
│ PROS:                                                       │
│ • Useful for Margaret's care                               │
│ • Fully exempt from Medicaid                               │
│                                                             │
│ EXAMPLES:                                                   │
│ • Wheelchair: $200-500                                     │
│ • Walker with seat: $100-200                               │
│ • Hearing aids: $500-2,000                                 │
│ • Glasses: $200-500                                        │
│                                                             │
│ TIMELINE: 1-3 days                                          │
│ AI CONFIDENCE: 90%                                          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ OPTION 4: PAY OUTSTANDING MEDICAL BILLS                    │
│ Amount: Varies                                              │
│ Legal Basis: 42 CFR 435.725                                │
├─────────────────────────────────────────────────────────────┤
│ PROS:                                                       │
│ • Reduces debt                                             │
│ • Fully exempt from Medicaid                               │
│                                                             │
│ CURRENT MEDICAL BILLS:                                      │
│ • Hospital copay (current stay): $250                      │
│ • Previous doctor visits: $150                             │
│ • Pharmacy balance: $75                                    │
│ • TOTAL: $475                                              │
│                                                             │
│ NOTE: Only covers $475 of $1,000 needed                    │
│                                                             │
│ TIMELINE: Same day                                          │
│ AI CONFIDENCE: 95%                                          │
└─────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════
PROHIBITED ACTIONS (WILL CREATE PENALTIES)
═══════════════════════════════════════════════════════════════

DO NOT:
✗ Give money to family members
✗ Pay deceased spouse's debts (Robert's credit card)
✗ Make charitable donations
✗ Transfer assets to trusts
✗ Add children to bank accounts

PENALTY CALCULATION:
Gift Amount ÷ $10,809 = Penalty Months

Example: $10,000 gift = 1 month penalty (no Medicaid coverage)

═══════════════════════════════════════════════════════════════
AI RECOMMENDATION
═══════════════════════════════════════════════════════════════

RECOMMENDED: Option 1 - Prepaid Funeral Contract ($1,000)

This is the fastest, safest, and most straightforward spend-down option. It can be completed in one day and provides 100% Medicaid exemption.

ACTION STEPS:
1. Call Palm Beach Memorial today: (561) 555-2345
2. Request irrevocable prepaid funeral contract
3. Pay $1,000 by check
4. Get receipt and contract copy
5. Provide to hospital social worker for Medicaid application

Report Generated by CareNav AI""",
        "extracted_data": {
            "amount_to_spend_down": 1000.00,
            "recommended_option": "Prepaid Funeral Contract",
            "options_count": 4,
            "prohibited_actions": ["gifts to family", "pay deceased spouse debt", "charitable donations"]
        },
        "ai_analysis": "Detailed analysis of legal spend-down options. Prepaid funeral contract is recommended as fastest and safest option. Can be completed same day. Includes warnings about prohibited actions that would create Medicaid penalties."
    },
    {
        "name": "Care Cost Projection - 5 Year",
        "category": "ai_analysis",
        "doc_type": "ai_cost_projection",
        "content": """5-YEAR CARE COST PROJECTION
For: Margaret A. Thompson
Generated by CareNav AI

═══════════════════════════════════════════════════════════════
PROJECTION ASSUMPTIONS
═══════════════════════════════════════════════════════════════

Current Age: 83
Life Expectancy: 88-92 (based on actuarial tables)
Care Level: Memory Care (moderate Alzheimer's)
Location: Palm Beach County, Florida
Inflation Rate: 4% annually (healthcare)

═══════════════════════════════════════════════════════════════
SCENARIO 1: WITHOUT BENEFITS (PRIVATE PAY ONLY)
═══════════════════════════════════════════════════════════════

YEAR 1 (2026):
Memory Care: $7,500/month x 12 = $90,000
Medicare Part B: $174.70/month x 12 = $2,096
Medications: $150/month x 12 = $1,800
Personal Needs: $100/month x 12 = $1,200
YEAR 1 TOTAL: $95,096

YEAR 2 (2027):
Memory Care (4% increase): $93,600
Other costs: $5,304
YEAR 2 TOTAL: $98,904

YEAR 3 (2028):
Memory Care: $97,344
Other costs: $5,516
YEAR 3 TOTAL: $102,860

YEAR 4 (2029):
Memory Care: $101,238
Other costs: $5,737
YEAR 4 TOTAL: $106,975

YEAR 5 (2030):
Memory Care: $105,288
Other costs: $5,966
YEAR 5 TOTAL: $111,254

═══════════════════════════════════════════════════════════════
5-YEAR TOTAL WITHOUT BENEFITS: $515,089
═══════════════════════════════════════════════════════════════

FUNDING GAP:
Margaret's Assets: $3,000
Margaret's 5-Year Income: $138,000 ($2,300/mo x 60)
TOTAL AVAILABLE: $141,000
SHORTFALL: $374,089

Without benefits, Margaret would exhaust all resources in approximately 18 months.

═══════════════════════════════════════════════════════════════
SCENARIO 2: WITH ALL BENEFITS (RECOMMENDED)
═══════════════════════════════════════════════════════════════

MONTHLY INCOME APPLIED TO CARE:
Social Security: $1,850
Pension: $450
VA Aid & Attendance: $1,432
TOTAL MONTHLY: $3,732

MONTHLY COSTS:
Memory Care: $7,500
Less: Patient Responsibility: -$1,995
Less: VA A&A: -$1,432
Medicaid Covers: -$4,073
NET OUT-OF-POCKET: $0

YEAR 1 (2026): $0 out-of-pocket
YEAR 2 (2027): $0 out-of-pocket
YEAR 3 (2028): $0 out-of-pocket
YEAR 4 (2029): $0 out-of-pocket
YEAR 5 (2030): $0 out-of-pocket

═══════════════════════════════════════════════════════════════
5-YEAR TOTAL WITH BENEFITS: $0
═══════════════════════════════════════════════════════════════

SAVINGS: $515,089 over 5 years

═══════════════════════════════════════════════════════════════
BENEFIT VALUE SUMMARY
═══════════════════════════════════════════════════════════════

VA Aid & Attendance (5 years):
$1,432/month x 60 months = $85,920

Florida Medicaid ICP (5 years):
~$4,073/month x 60 months = $244,380

TOTAL BENEFIT VALUE: $330,300

═══════════════════════════════════════════════════════════════
KEY TAKEAWAYS
═══════════════════════════════════════════════════════════════

1. Without benefits, Margaret would be bankrupt in 18 months
2. With benefits, Margaret pays $0 out-of-pocket
3. Total 5-year savings: $515,089
4. Benefits provide $330,300 in direct value
5. Margaret's home ($285,000) is protected from Medicaid estate recovery while she's alive

RECOMMENDATION: Apply for all benefits immediately to secure this financial protection.

Report Generated by CareNav AI""",
        "extracted_data": {
            "projection_years": 5,
            "without_benefits_total": 515089,
            "with_benefits_total": 0,
            "total_savings": 515089,
            "va_benefit_value": 85920,
            "medicaid_benefit_value": 244380,
            "months_until_bankrupt_without_benefits": 18
        },
        "ai_analysis": "5-year cost projection shows Margaret would be bankrupt in 18 months without benefits. With VA A&A and Medicaid, her out-of-pocket cost is $0. Total 5-year savings of $515,089. Critical to apply for benefits immediately."
    },
    {
        "name": "Legal Considerations Summary",
        "category": "legal",
        "doc_type": "ai_legal_summary",
        "content": """LEGAL CONSIDERATIONS SUMMARY
For: Margaret A. Thompson
Generated by CareNav AI

═══════════════════════════════════════════════════════════════
DISCLAIMER
═══════════════════════════════════════════════════════════════

This summary is for informational purposes only and does not constitute legal advice. Consult with a Florida elder law attorney for specific legal guidance.

═══════════════════════════════════════════════════════════════
POWER OF ATTORNEY STATUS
═══════════════════════════════════════════════════════════════

CURRENT STATUS: NEEDS ATTENTION

Margaret's cognitive assessment (MMSE 16/30) indicates moderate impairment. She may still have capacity to execute legal documents, but this window is closing.

RECOMMENDED ACTIONS:
□ Execute Durable Power of Attorney (Financial)
□ Execute Healthcare Surrogate Designation
□ Execute Living Will (Advance Directive)
□ Review/update beneficiary designations

URGENCY: HIGH - Should be completed within 7 days while Margaret still has capacity.

RECOMMENDED ATTORNEY:
Elder Law Associates of Palm Beach
(561) 555-3456
Specializes in: Medicaid planning, VA benefits, estate planning

═══════════════════════════════════════════════════════════════
HOMESTEAD PROTECTION
═══════════════════════════════════════════════════════════════

Margaret's home at 1234 Palm Way is protected under Florida Homestead laws:

CURRENT PROTECTIONS:
✓ Exempt from Medicaid countable assets
✓ Protected from creditors (Article X, Section 4, FL Constitution)
✓ Property tax exemptions applied

EQUITY: $285,000 (under $713,000 Medicaid cap)

IMPORTANT CONSIDERATIONS:
1. Home remains exempt as long as Margaret intends to return OR
2. Home remains exempt if spouse resides there (N/A - Robert deceased)
3. After Margaret's death, Medicaid may seek estate recovery

ESTATE RECOVERY:
Florida Medicaid can seek recovery from Margaret's estate after death for benefits paid. The home may be subject to a lien.

PROTECTION OPTIONS:
• Lady Bird Deed (Enhanced Life Estate Deed)
• Irrevocable Trust (consult attorney)
• Transfer to child with caregiver exemption (if applicable)

═══════════════════════════════════════════════════════════════
DECEASED SPOUSE DEBT
═══════════════════════════════════════════════════════════════

Robert Thompson passed away March 15, 2020.

IDENTIFIED DEBT:
• Credit card in Robert's name only: $2,400

LEGAL ANALYSIS:
Florida is a COMMON LAW property state (not community property).

RESULT: Margaret is NOT personally liable for Robert's individual debts.

WHAT TO DO IF CREDITORS CALL:
1. State: "The account holder is deceased"
2. State: "I am not responsible for this debt"
3. State: "Do not contact me again"
4. Request written communication only
5. Do NOT make any payments

WARNING: Paying any amount could be construed as accepting responsibility.

═══════════════════════════════════════════════════════════════
MEDICAID LOOK-BACK PERIOD
═══════════════════════════════════════════════════════════════

PERIOD: 60 months (January 2021 - January 2026)

REVIEW RESULT: CLEAR

No disqualifying transfers found during look-back period.

WHAT WOULD HAVE CAUSED PROBLEMS:
• Gifts to family members
• Selling assets below market value
• Adding children to deeds or accounts
• Large charitable donations
• Paying others' debts

═══════════════════════════════════════════════════════════════
GUARDIANSHIP CONSIDERATIONS
═══════════════════════════════════════════════════════════════

CURRENT STATUS: Not needed if POA executed

If Margaret loses capacity before executing POA:
• Court-appointed guardian may be required
• Costly process ($3,000-10,000+)
• Time-consuming (2-6 months)
• Court oversight of all decisions

RECOMMENDATION: Execute POA immediately to avoid guardianship.

═══════════════════════════════════════════════════════════════
RECOMMENDED LEGAL DOCUMENTS
═══════════════════════════════════════════════════════════════

PRIORITY 1 (This Week):
□ Durable Power of Attorney (Financial)
□ Healthcare Surrogate Designation
□ Living Will / Advance Directive

PRIORITY 2 (Within 30 Days):
□ Review/update will
□ Consider Lady Bird Deed for home
□ Review beneficiary designations on accounts

ESTIMATED LEGAL COSTS:
• POA + Healthcare Surrogate + Living Will: $500-1,000
• Will update: $300-500
• Lady Bird Deed: $500-1,000

TOTAL ESTIMATED: $1,300-2,500

Report Generated by CareNav AI""",
        "extracted_data": {
            "poa_status": "Needs Attention",
            "homestead_protected": True,
            "homestead_equity": 285000,
            "deceased_spouse_debt": 2400,
            "liable_for_spouse_debt": False,
            "lookback_clear": True,
            "guardianship_needed": False,
            "estimated_legal_costs": "1300-2500"
        },
        "ai_analysis": "Legal summary highlighting urgent need for POA while Margaret has capacity. Home is protected under Florida Homestead. Not liable for deceased spouse's debt. Look-back period is clear. Guardianship can be avoided if POA executed immediately."
    },
    {
        "name": "Family Meeting Notes Template",
        "category": "ai_analysis",
        "doc_type": "ai_meeting_template",
        "content": """FAMILY MEETING NOTES TEMPLATE
For: Margaret Thompson Care Planning
Generated by CareNav AI

═══════════════════════════════════════════════════════════════
MEETING DETAILS
═══════════════════════════════════════════════════════════════

Date: ________________
Time: ________________
Location: ________________ (or Video Call)

ATTENDEES:
□ Sarah Thompson (Daughter) - Primary Contact
□ Hospital Social Worker
□ Dr. Sarah Chen (Attending Physician)
□ Facility Representative (if touring)
□ Elder Law Attorney (if available)
□ Other: ________________

═══════════════════════════════════════════════════════════════
AGENDA
═══════════════════════════════════════════════════════════════

1. CURRENT STATUS UPDATE (10 minutes)
   • Margaret's medical condition
   • Hospital discharge timeline
   • Immediate care needs

2. CARE OPTIONS DISCUSSION (15 minutes)
   • Memory Care placement (recommended)
   • Facility options reviewed
   • Family preferences

3. FINANCIAL OVERVIEW (15 minutes)
   • Current assets: $3,000
   • Monthly income: $2,300
   • Benefit eligibility (VA, Medicaid)
   • Projected costs with benefits: $0/month

4. ACTION ITEMS REVIEW (10 minutes)
   • Spend-down completion
   • Benefit applications
   • Legal documents needed
   • Facility selection

5. QUESTIONS & CONCERNS (10 minutes)
   • Family questions
   • Clarifications needed

═══════════════════════════════════════════════════════════════
KEY DISCUSSION POINTS
═══════════════════════════════════════════════════════════════

MEDICAL SITUATION:
• Diagnosis: Alzheimer's Disease, moderate stage
• MMSE Score: 16/30
• Hospital admission: Wandering episode
• Physician recommendation: Memory Care placement
• Cannot safely live alone

FINANCIAL SITUATION:
• Total assets: $3,000 (checking + savings)
• Over Medicaid limit by: $1,000
• Home equity: $285,000 (exempt)
• No mortgage

BENEFIT ELIGIBILITY:
• VA Survivors Pension: $1,432/month (eligible)
• Florida Medicaid ICP: Eligible after $1,000 spend-down
• Combined benefits cover all care costs

RECOMMENDED FACILITY:
• Sunrise of Palm Beach
• Match score: 92/100
• Accepts Medicaid from day one
• 2 beds currently available
• 3.2 miles from hospital

═══════════════════════════════════════════════════════════════
DECISIONS NEEDED
═══════════════════════════════════════════════════════════════

□ Confirm spend-down method (prepaid funeral recommended)
□ Approve facility selection
□ Designate POA (if not already done)
□ Assign responsibility for benefit applications
□ Set move-in target date

═══════════════════════════════════════════════════════════════
ACTION ITEMS ASSIGNMENT
═══════════════════════════════════════════════════════════════

TASK                          ASSIGNED TO      DUE DATE
─────────────────────────────────────────────────────────────
Complete spend-down           ____________     ____________
Tour Sunrise facility         ____________     ____________
Submit VA application         ____________     ____________
Submit Medicaid application   ____________     ____________
Execute POA documents         ____________     ____________
Coordinate move-in            ____________     ____________

═══════════════════════════════════════════════════════════════
NOTES FROM MEETING
═══════════════════════════════════════════════════════════════

[Space for handwritten or typed notes]

_______________________________________________________________
_______________________________________________________________
_______________________________________________________________
_______________________________________________________________
_______________________________________________________________

═══════════════════════════════════════════════════════════════
NEXT MEETING
═══════════════════════════════════════════════════════════════

Date: ________________
Purpose: ________________

Report Generated by CareNav AI""",
        "extracted_data": {
            "document_type": "meeting_template",
            "agenda_items": 5,
            "decisions_needed": 5,
            "action_items": 6
        },
        "ai_analysis": "Family meeting template to facilitate care planning discussion. Includes agenda, key discussion points, decisions needed, and action item assignments. Designed to ensure all stakeholders are aligned on Margaret's care plan."
    },
    {
        "name": "Care Transition Checklist",
        "category": "ai_analysis",
        "doc_type": "ai_transition_checklist",
        "content": """CARE TRANSITION CHECKLIST
Hospital to Memory Care Facility
For: Margaret A. Thompson
Generated by CareNav AI

═══════════════════════════════════════════════════════════════
TRANSITION OVERVIEW
═══════════════════════════════════════════════════════════════

FROM: Palm Beach General Hospital
TO: Sunrise of Palm Beach (Memory Care)
TARGET DATE: February 10, 2026
TRANSPORT: Medical transport recommended

═══════════════════════════════════════════════════════════════
PRE-MOVE CHECKLIST (1 WEEK BEFORE)
═══════════════════════════════════════════════════════════════

ADMINISTRATIVE:
□ Confirm facility admission date
□ Sign admission agreement
□ Provide insurance information (Medicare, Medicaid pending)
□ Complete facility health questionnaire
□ Provide emergency contact information
□ Provide POA documentation

FINANCIAL:
□ Complete spend-down ($1,000)
□ Confirm Medicaid application submitted
□ Confirm VA application submitted
□ Set up automatic payment for patient responsibility
□ Provide bank account information for direct deposit

MEDICAL:
□ Request hospital discharge summary
□ Request medication list (MAR)
□ Request physician orders for facility
□ Schedule follow-up appointments
□ Transfer prescriptions to facility pharmacy
□ Provide vaccination records

═══════════════════════════════════════════════════════════════
ITEMS TO BRING TO FACILITY
═══════════════════════════════════════════════════════════════

CLOTHING (Label everything with name):
□ 7 comfortable outfits (easy to put on/remove)
□ 7 sets of undergarments
□ 2 pairs of non-slip shoes/slippers
□ 2 sweaters or cardigans
□ 1 warm jacket
□ Pajamas (3-4 sets)
□ Robe

PERSONAL ITEMS:
□ Family photos (framed, no glass)
□ Favorite blanket or pillow
□ Small radio or music player
□ Books or magazines
□ Familiar decorative items

TOILETRIES:
□ Toothbrush and toothpaste
□ Hairbrush/comb
□ Shampoo and conditioner
□ Body wash/soap
□ Deodorant
□ Moisturizer
□ Denture care items (if applicable)

DOCUMENTS TO BRING:
□ Photo ID (copy)
□ Medicare card (copy)
□ Medicaid pending letter (copy)
□ VA application receipt (copy)
□ POA documentation (copy)
□ Advance directive (copy)
□ Insurance cards (copies)

DO NOT BRING:
✗ Valuables or jewelry
✗ Large amounts of cash
✗ Medications (facility will manage)
✗ Sharp objects
✗ Electrical appliances (check with facility)

═══════════════════════════════════════════════════════════════
MOVE DAY CHECKLIST
═══════════════════════════════════════════════════════════════

MORNING:
□ Confirm transport arranged
□ Pack all items
□ Complete hospital discharge paperwork
□ Receive discharge medications (for transport only)
□ Get copies of all medical records

TRANSPORT:
□ Accompany Margaret during transport
□ Bring comfort items for the ride
□ Have facility address and phone ready
□ Bring snacks and water

ARRIVAL AT FACILITY:
□ Meet with admissions coordinator
□ Tour room and common areas
□ Meet nursing staff
□ Review care plan
□ Unpack and arrange personal items
□ Stay for first meal if possible

═══════════════════════════════════════════════════════════════
FIRST WEEK AT FACILITY
═══════════════════════════════════════════════════════════════

DAY 1-2:
□ Allow Margaret to settle in
□ Short visits only (30-60 minutes)
□ Bring familiar items if forgotten
□ Meet with care team

DAY 3-4:
□ Check on adjustment
□ Review initial care notes
□ Address any concerns with staff
□ Longer visits if Margaret is comfortable

DAY 5-7:
□ Attend care plan meeting
□ Review medication management
□ Discuss activity participation
□ Establish visiting schedule

═══════════════════════════════════════════════════════════════
POST-MOVE TASKS
═══════════════════════════════════════════════════════════════

WITHIN 1 WEEK:
□ Update address with Social Security
□ Update address with VA
□ Forward mail to family member
□ Cancel unnecessary subscriptions
□ Notify utility companies (if closing home)

WITHIN 30 DAYS:
□ Follow up on Medicaid application
□ Follow up on VA application
□ Review first facility invoice
□ Attend first care conference
□ Update emergency contacts

ONGOING:
□ Regular visits (recommended: 2-3x per week)
□ Communicate with care team
□ Monitor care quality
□ Review monthly statements
□ Attend quarterly care conferences

═══════════════════════════════════════════════════════════════
IMPORTANT CONTACTS
═══════════════════════════════════════════════════════════════

Sunrise of Palm Beach: (561) 555-0123
Hospital Social Worker: (561) 555-1000
Daughter (Sarah): (555) 123-4567
VA Benefits: 1-800-827-1000
ACCESS Florida: 1-866-762-2237

Report Generated by CareNav AI""",
        "extracted_data": {
            "from_location": "Palm Beach General Hospital",
            "to_location": "Sunrise of Palm Beach",
            "target_date": "2026-02-10",
            "pre_move_tasks": 18,
            "move_day_tasks": 12,
            "first_week_tasks": 10,
            "post_move_tasks": 10
        },
        "ai_analysis": "Comprehensive checklist for transitioning Margaret from hospital to Memory Care facility. Covers pre-move preparation, items to bring, move day logistics, first week adjustment, and post-move tasks. Designed to ensure smooth transition and minimize stress."
    },
    {
        "name": "Medication Management Summary",
        "category": "medical",
        "doc_type": "medication_summary",
        "content": """MEDICATION MANAGEMENT SUMMARY
For: Margaret A. Thompson
Generated by CareNav AI

═══════════════════════════════════════════════════════════════
CURRENT MEDICATIONS
═══════════════════════════════════════════════════════════════

MEDICATION          DOSE        FREQUENCY    PURPOSE
─────────────────────────────────────────────────────────────
Donepezil           10mg        Once daily   Alzheimer's
(Aricept)                       at bedtime   (memory)

Lisinopril          20mg        Once daily   Blood pressure
                                in morning   (hypertension)

Levothyroxine       50mcg       Once daily   Thyroid
(Synthroid)                     in morning   (hypothyroidism)
                                empty stomach

Acetaminophen       650mg       As needed    Pain relief
(Tylenol)                       (max 4x/day) (arthritis)

═══════════════════════════════════════════════════════════════
MEDICATION DETAILS
═══════════════════════════════════════════════════════════════

DONEPEZIL (Aricept) 10mg
─────────────────────────────────────────────────────────────
Purpose: Treats symptoms of Alzheimer's disease
How it works: Increases acetylcholine in the brain
Important notes:
• Take at bedtime to reduce nausea
• May cause vivid dreams
• Do not stop suddenly without doctor's advice
• Takes 4-6 weeks to see full effect
Cost: ~$15/month (generic)

LISINOPRIL 20mg
─────────────────────────────────────────────────────────────
Purpose: Controls high blood pressure
How it works: Relaxes blood vessels
Important notes:
• Take in the morning
• May cause dizziness when standing
• Avoid potassium supplements
• Report persistent cough to doctor
Cost: ~$10/month (generic)

LEVOTHYROXINE (Synthroid) 50mcg
─────────────────────────────────────────────────────────────
Purpose: Replaces thyroid hormone
How it works: Supplements low thyroid levels
Important notes:
• Take on empty stomach (30-60 min before food)
• Take at same time each day
• Avoid taking with calcium or iron supplements
• Requires regular blood tests (TSH)
Cost: ~$10/month (generic)

ACETAMINOPHEN (Tylenol) 650mg
─────────────────────────────────────────────────────────────
Purpose: Pain relief for arthritis
How it works: Reduces pain signals
Important notes:
• Maximum 3,000mg per day (4 doses)
• Avoid alcohol
• Check other medications for acetaminophen
• Safer than NSAIDs for elderly
Cost: ~$5/month (OTC)

═══════════════════════════════════════════════════════════════
MEDICATION SCHEDULE
═══════════════════════════════════════════════════════════════

MORNING (7:00 AM - Empty Stomach):
• Levothyroxine 50mcg

MORNING (8:00 AM - With Breakfast):
• Lisinopril 20mg

AS NEEDED (Throughout Day):
• Acetaminophen 650mg (for pain)

BEDTIME (9:00 PM):
• Donepezil 10mg

═══════════════════════════════════════════════════════════════
PHARMACY INFORMATION
═══════════════════════════════════════════════════════════════

Current Pharmacy: CVS Pharmacy
Address: 500 Palm Beach Lakes Blvd, West Palm Beach, FL
Phone: (561) 555-7890
Prescription Numbers: On file

AFTER FACILITY ADMISSION:
Medications will be managed by facility pharmacy.
All prescriptions will be transferred automatically.

═══════════════════════════════════════════════════════════════
MEDICATION COSTS
═══════════════════════════════════════════════════════════════

MONTHLY MEDICATION COSTS:
Donepezil (generic):     $15
Lisinopril (generic):    $10
Levothyroxine (generic): $10
Acetaminophen (OTC):     $5
─────────────────────────────────────────────────────────────
TOTAL:                   $40/month

Medicare Part D covers most costs.
Facility will include medication management in care.

═══════════════════════════════════════════════════════════════
ALLERGIES & INTERACTIONS
═══════════════════════════════════════════════════════════════

KNOWN ALLERGIES:
• Penicillin (rash)
• Sulfa drugs (hives)

DRUG INTERACTIONS TO AVOID:
• NSAIDs (ibuprofen, naproxen) - risk with Lisinopril
• Potassium supplements - risk with Lisinopril
• Calcium/Iron - interferes with Levothyroxine absorption

═══════════════════════════════════════════════════════════════
NOTES FOR FACILITY
═══════════════════════════════════════════════════════════════

1. Margaret may forget if she took medications
2. Requires supervision for all medication administration
3. Donepezil at bedtime reduces nausea
4. Levothyroxine must be given on empty stomach
5. Monitor for signs of low blood pressure (dizziness)

Report Generated by CareNav AI""",
        "extracted_data": {
            "total_medications": 4,
            "monthly_cost": 40,
            "allergies": ["Penicillin", "Sulfa drugs"],
            "requires_supervision": True
        },
        "ai_analysis": "Medication summary showing 4 current medications totaling $40/month. Includes detailed schedule, pharmacy information, and notes for facility staff. Margaret requires supervision for all medication administration due to cognitive impairment."
    },
    {
        "name": "Emergency Contact Card",
        "category": "ai_analysis",
        "doc_type": "emergency_contacts",
        "content": """EMERGENCY CONTACT CARD
For: Margaret A. Thompson
Generated by CareNav AI

═══════════════════════════════════════════════════════════════
PATIENT INFORMATION
═══════════════════════════════════════════════════════════════

Name: Margaret Ann Thompson
Date of Birth: March 15, 1942
Age: 83
Medicare #: 1EG4-TE5-MK72
Blood Type: A+

Primary Diagnosis: Alzheimer's Disease (moderate)
Allergies: Penicillin, Sulfa drugs

═══════════════════════════════════════════════════════════════
PRIMARY EMERGENCY CONTACT
═══════════════════════════════════════════════════════════════

Name: Sarah Thompson (Daughter)
Relationship: Daughter
Phone (Cell): (555) 123-4567
Phone (Work): (555) 123-8901
Email: sarah.thompson@email.com
Address: 456 Oak Street, San Diego, CA 92101

Authorization: Full medical decision-making authority
POA Status: Healthcare Surrogate (pending execution)

═══════════════════════════════════════════════════════════════
SECONDARY EMERGENCY CONTACT
═══════════════════════════════════════════════════════════════

Name: Michael Thompson (Son)
Relationship: Son
Phone (Cell): (555) 234-5678
Email: michael.thompson@email.com
Address: 789 Pine Avenue, Atlanta, GA 30301

Authorization: Contact for updates only

═══════════════════════════════════════════════════════════════
MEDICAL CONTACTS
═══════════════════════════════════════════════════════════════

PRIMARY CARE PHYSICIAN:
Dr. Robert Martinez, MD
Palm Beach Internal Medicine
Phone: (561) 555-2000
Fax: (561) 555-2001

NEUROLOGIST:
Dr. Jennifer Lee, MD
Palm Beach Neurology Associates
Phone: (561) 555-3000

HOSPITAL:
Palm Beach General Hospital
Emergency: (561) 555-1000
Address: 1000 Medical Center Way, West Palm Beach, FL

═══════════════════════════════════════════════════════════════
FACILITY CONTACT (After Admission)
═══════════════════════════════════════════════════════════════

Facility: Sunrise of Palm Beach
Address: 2500 N. Flagler Drive, West Palm Beach, FL 33407
Main Phone: (561) 555-0123
Nursing Station: (561) 555-0124
Administrator: (561) 555-0125

═══════════════════════════════════════════════════════════════
BENEFITS & INSURANCE CONTACTS
═══════════════════════════════════════════════════════════════

MEDICARE:
Phone: 1-800-MEDICARE (1-800-633-4227)
TTY: 1-877-486-2048

VA BENEFITS:
Phone: 1-800-827-1000
eBenefits: www.ebenefits.va.gov

FLORIDA MEDICAID (ACCESS):
Phone: 1-866-762-2237
Website: www.myflorida.com/accessflorida

SOCIAL SECURITY:
Phone: 1-800-772-1213
TTY: 1-800-325-0778

═══════════════════════════════════════════════════════════════
LEGAL CONTACTS
═══════════════════════════════════════════════════════════════

ELDER LAW ATTORNEY:
Elder Law Associates of Palm Beach
Phone: (561) 555-3456
Contact for: POA, estate planning, Medicaid issues

VETERANS SERVICE OFFICER:
Palm Beach County VSO
Phone: (561) 355-4760
Contact for: VA benefits assistance

═══════════════════════════════════════════════════════════════
OTHER IMPORTANT CONTACTS
═══════════════════════════════════════════════════════════════

PHARMACY:
CVS Pharmacy
Phone: (561) 555-7890

FLORIDA ELDER HELPLINE:
Phone: 1-800-963-5337

ALZHEIMER'S ASSOCIATION 24/7 HELPLINE:
Phone: 1-800-272-3900

═══════════════════════════════════════════════════════════════
WALLET CARD (Print and Cut)
═══════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────┐
│ MARGARET A. THOMPSON                                        │
│ DOB: 03/15/1942                                            │
│ Medicare: 1EG4-TE5-MK72                                    │
│                                                             │
│ DIAGNOSIS: Alzheimer's Disease                             │
│ ALLERGIES: Penicillin, Sulfa                               │
│                                                             │
│ EMERGENCY CONTACT:                                          │
│ Sarah Thompson (Daughter): (555) 123-4567                  │
│                                                             │
│ PHYSICIAN:                                                  │
│ Dr. Robert Martinez: (561) 555-2000                        │
└─────────────────────────────────────────────────────────────┘

Report Generated by CareNav AI""",
        "extracted_data": {
            "primary_contact": "Sarah Thompson",
            "primary_phone": "(555) 123-4567",
            "secondary_contact": "Michael Thompson",
            "pcp": "Dr. Robert Martinez",
            "allergies": ["Penicillin", "Sulfa drugs"]
        },
        "ai_analysis": "Comprehensive emergency contact card with all important phone numbers for family, medical providers, benefits agencies, and legal contacts. Includes printable wallet card for Margaret to carry."
    },
    {
        "name": "Benefits Timeline Projection",
        "category": "ai_analysis",
        "doc_type": "ai_benefits_timeline",
        "content": """BENEFITS TIMELINE PROJECTION
For: Margaret A. Thompson
Generated by CareNav AI

═══════════════════════════════════════════════════════════════
OVERVIEW
═══════════════════════════════════════════════════════════════

This timeline shows when each benefit is expected to be approved and the projected monthly income at each stage.

═══════════════════════════════════════════════════════════════
CURRENT STATUS (February 2026)
═══════════════════════════════════════════════════════════════

INCOME:
• Social Security: $1,850/month (active)
• Pension: $450/month (active)
• VA Benefits: $0 (not yet applied)
• Medicaid: Not approved

MONTHLY INCOME: $2,300
CARE COSTS: $7,500/month
GAP: -$5,200/month (UNSUSTAINABLE)

═══════════════════════════════════════════════════════════════
WEEK 1-2: APPLICATION PHASE
═══════════════════════════════════════════════════════════════

ACTIONS:
□ Complete $1,000 spend-down
□ Submit VA Form 21-534EZ
□ Submit Medicaid application (expedited)
□ Admit to facility (Medicaid pending)

STATUS:
• VA: Application submitted
• Medicaid: Application submitted (expedited)

MONTHLY INCOME: $2,300
CARE COSTS: $7,500/month
FACILITY ACCEPTS: Medicaid-pending admission

═══════════════════════════════════════════════════════════════
MONTH 1-2: MEDICAID APPROVAL (Expected)
═══════════════════════════════════════════════════════════════

EXPECTED: Medicaid ICP approval (expedited processing)

UPON APPROVAL:
• Medicaid covers facility costs minus patient responsibility
• Patient responsibility: ~$1,995/month
• Medicaid pays: ~$5,505/month to facility

MONTHLY INCOME: $2,300
PATIENT RESPONSIBILITY: $1,995
MEDICAID COVERS: $5,505
OUT-OF-POCKET: $0 (income covers patient responsibility)

═══════════════════════════════════════════════════════════════
MONTH 3-6: VA APPROVAL (Expected)
═══════════════════════════════════════════════════════════════

EXPECTED: VA Survivors Pension with A&A approval

UPON APPROVAL:
• Monthly benefit: $1,432
• RETROACTIVE payment from application date
• Estimated lump sum: $4,296 - $8,592 (3-6 months)

NEW MONTHLY INCOME:
• Social Security: $1,850
• Pension: $450
• VA A&A: $1,432
• TOTAL: $3,732

PATIENT RESPONSIBILITY: $1,995
REMAINING INCOME: $1,737 (personal use)

═══════════════════════════════════════════════════════════════
MONTH 6+: FULL BENEFITS ACTIVE
═══════════════════════════════════════════════════════════════

ALL BENEFITS ACTIVE:
• Social Security: $1,850/month
• Pension: $450/month
• VA A&A: $1,432/month
• Medicaid ICP: Covers facility costs

MONTHLY SUMMARY:
Total Income: $3,732
Patient Responsibility: -$1,995
Personal Needs Allowance: +$130 (from Medicaid)
─────────────────────────────────────────────────────────────
NET AVAILABLE: $1,867/month

This covers:
• Medicare Part B premium: $174.70
• Prescription copays: ~$40
• Personal items: ~$100
• Remaining: ~$1,552/month (savings or family)

═══════════════════════════════════════════════════════════════
TIMELINE VISUALIZATION
═══════════════════════════════════════════════════════════════

WEEK 1-2        MONTH 1-2       MONTH 3-6       MONTH 6+
─────────────────────────────────────────────────────────────
Apply for       Medicaid        VA Approval     Full Benefits
Benefits        Approval        (retroactive)   Active
                (expedited)

Income:         Income:         Income:         Income:
$2,300          $2,300          $3,732          $3,732

Gap:            Gap:            Gap:            Gap:
-$5,200         $0              $0              $0
(facility       (Medicaid       (VA adds        (stable)
covers          covers)         $1,432)
pending)

═══════════════════════════════════════════════════════════════
RETROACTIVE BENEFITS PROJECTION
═══════════════════════════════════════════════════════════════

VA RETROACTIVE PAYMENT:
If approved in Month 4 (April 2026):
• February: $1,432
• March: $1,432
• April: $1,432
• LUMP SUM: $4,296

If approved in Month 6 (June 2026):
• February-June: $1,432 x 5 = $7,160

MEDICAID RETROACTIVE:
• Medicaid can be retroactive up to 3 months
• May cover facility costs from admission date

═══════════════════════════════════════════════════════════════
ANNUAL BENEFIT VALUE
═══════════════════════════════════════════════════════════════

YEAR 1 (2026):
VA A&A (10 months): $14,320
Medicaid (10 months): ~$55,050
TOTAL BENEFIT VALUE: $69,370

YEAR 2+ (Full Year):
VA A&A: $17,184
Medicaid: ~$66,060
TOTAL BENEFIT VALUE: $83,244/year

═══════════════════════════════════════════════════════════════
KEY MILESTONES
═══════════════════════════════════════════════════════════════

□ Week 1: Spend-down complete
□ Week 2: All applications submitted
□ Month 1-2: Medicaid approval
□ Month 3-6: VA approval
□ Month 6: Full benefits active

Report Generated by CareNav AI""",
        "extracted_data": {
            "current_monthly_income": 2300,
            "projected_monthly_income": 3732,
            "medicaid_approval_expected": "Month 1-2",
            "va_approval_expected": "Month 3-6",
            "annual_benefit_value": 83244,
            "va_retroactive_estimate": "4296-7160"
        },
        "ai_analysis": "Benefits timeline showing progression from application to full approval. Medicaid expected in 1-2 months (expedited), VA in 3-6 months. VA benefits are retroactive to application date. Annual benefit value of $83,244 once fully active."
    },
    {
        "name": "Quality of Life Care Plan",
        "category": "ai_analysis",
        "doc_type": "ai_care_plan",
        "content": """QUALITY OF LIFE CARE PLAN
For: Margaret A. Thompson
Generated by CareNav AI

═══════════════════════════════════════════════════════════════
PERSON-CENTERED CARE OVERVIEW
═══════════════════════════════════════════════════════════════

This care plan focuses on maintaining Margaret's quality of life, dignity, and engagement while managing her Alzheimer's disease.

═══════════════════════════════════════════════════════════════
PERSONAL HISTORY & PREFERENCES
═══════════════════════════════════════════════════════════════

BACKGROUND:
• Born: March 15, 1942 in Jacksonville, FL
• Married Robert Thompson in 1964 (55 years)
• Raised two children: Sarah and Michael
• Worked as elementary school teacher (30 years)
• Widowed March 2020

INTERESTS & HOBBIES:
• Reading (especially romance novels)
• Gardening (roses were her specialty)
• Cooking (famous for her key lime pie)
• Church activities (First Baptist Church)
• Watching old movies (Audrey Hepburn favorites)

MUSIC PREFERENCES:
• Big band era (Glenn Miller, Benny Goodman)
• 1960s pop (The Beatles, Elvis)
• Hymns and gospel music

FOOD PREFERENCES:
• Likes: Southern cooking, sweet tea, key lime pie
• Dislikes: Spicy food, seafood
• Dietary needs: Diabetic-friendly options

═══════════════════════════════════════════════════════════════
DAILY ROUTINE RECOMMENDATIONS
═══════════════════════════════════════════════════════════════

MORNING (7:00 AM - 12:00 PM):
• 7:00 - Wake up, bathroom assistance
• 7:30 - Morning medications (empty stomach)
• 8:00 - Breakfast (prefers eggs and toast)
• 8:30 - Morning medications (with food)
• 9:00 - Personal grooming (needs assistance)
• 10:00 - Morning activity (music therapy, exercise)
• 11:00 - Social time or quiet activity

AFTERNOON (12:00 PM - 6:00 PM):
• 12:00 - Lunch
• 1:00 - Rest time (may nap)
• 2:00 - Afternoon activity (art, gardening)
• 3:00 - Snack time
• 4:00 - Family visit time (if scheduled)
• 5:00 - Evening preparation

EVENING (6:00 PM - 10:00 PM):
• 6:00 - Dinner
• 7:00 - Evening activity (movie, music)
• 8:00 - Wind-down time
• 9:00 - Evening medications, bedtime routine
• 9:30 - Lights out

═══════════════════════════════════════════════════════════════
COMMUNICATION STRATEGIES
═══════════════════════════════════════════════════════════════

EFFECTIVE APPROACHES:
• Use simple, short sentences
• Speak slowly and clearly
• Make eye contact
• Use her name frequently
• Give one instruction at a time
• Allow extra time for responses
• Use visual cues and gestures

AVOID:
• Arguing or correcting
• Asking "Do you remember?"
• Speaking loudly (she's not deaf)
• Rushing or showing impatience
• Complex questions

CALMING TECHNIQUES:
• Play familiar music
• Look at family photos together
• Gentle hand massage
• Soft, reassuring voice
• Redirect rather than confront

═══════════════════════════════════════════════════════════════
ACTIVITY RECOMMENDATIONS
═══════════════════════════════════════════════════════════════

HIGH ENGAGEMENT ACTIVITIES:
• Music therapy (big band, hymns)
• Looking at photo albums
• Simple gardening (potted plants)
• Folding towels (familiar task)
• Watching old movies

MODERATE ENGAGEMENT:
• Art therapy (painting, coloring)
• Pet therapy visits
• Gentle exercise classes
• Bingo (with assistance)
• Sensory activities

SOCIAL ACTIVITIES:
• Small group activities (3-4 people)
• One-on-one visits preferred
• Church services (if available)
• Family video calls

═══════════════════════════════════════════════════════════════
BEHAVIORAL CONSIDERATIONS
═══════════════════════════════════════════════════════════════

WANDERING RISK: HIGH
• History of wandering episode
• Requires secured Memory Care unit
• Door alarms recommended
• GPS bracelet consideration

SUNDOWNING: MODERATE RISK
• May become more confused in evening
• Keep environment calm after 4 PM
• Reduce stimulation before bedtime
• Night light in room

AGITATION TRIGGERS:
• Loud noises
• Unfamiliar people
• Changes in routine
• Feeling rushed
• Being corrected

CALMING STRATEGIES:
• Soft music
• Familiar objects
• Gentle touch
• Quiet environment
• Favorite snacks

═══════════════════════════════════════════════════════════════
FAMILY INVOLVEMENT
═══════════════════════════════════════════════════════════════

VISITING RECOMMENDATIONS:
• Best times: 10 AM - 11 AM, 2 PM - 4 PM
• Avoid: Evening hours (sundowning)
• Duration: 30-60 minutes optimal
• Bring: Family photos, favorite treats

ACTIVITIES DURING VISITS:
• Look at photo albums together
• Listen to music
• Take short walks (supervised)
• Read to her
• Simple crafts

COMMUNICATION WITH FACILITY:
• Weekly check-in calls
• Attend care conferences
• Report any concerns promptly
• Share updates about family

═══════════════════════════════════════════════════════════════
GOALS OF CARE
═══════════════════════════════════════════════════════════════

SHORT-TERM (1-3 months):
□ Successful transition to Memory Care
□ Establish comfortable daily routine
□ Maintain current cognitive function
□ Build relationships with staff

LONG-TERM (6-12 months):
□ Maximize quality of life
□ Maintain dignity and independence where possible
□ Keep engaged in meaningful activities
□ Support family connections

COMFORT MEASURES:
□ Pain management as needed
□ Emotional support
□ Spiritual care (if desired)
□ Family presence during difficult times

Report Generated by CareNav AI""",
        "extracted_data": {
            "wandering_risk": "High",
            "sundowning_risk": "Moderate",
            "preferred_activities": ["music therapy", "photo albums", "gardening"],
            "best_visit_times": ["10 AM - 11 AM", "2 PM - 4 PM"],
            "communication_style": "Simple, short sentences"
        },
        "ai_analysis": "Person-centered care plan focusing on Margaret's quality of life. Includes personal history, daily routine recommendations, communication strategies, activity suggestions, and behavioral considerations. Designed to help facility staff provide individualized care."
    },
    # ═══════════════════════════════════════════════════════════════
    # SSN/SSA INFORMATION
    # ═══════════════════════════════════════════════════════════════
    {
        "name": "Social Security Administration - Benefits Statement",
        "category": "income",
        "doc_type": "ssa_benefits_statement",
        "content": """SOCIAL SECURITY ADMINISTRATION
BENEFIT VERIFICATION LETTER

Date: January 15, 2026

═══════════════════════════════════════════════════════════════
BENEFICIARY INFORMATION
═══════════════════════════════════════════════════════════════

Name: MARGARET ANN THOMPSON
Social Security Number: XXX-XX-4589
Date of Birth: March 15, 1942
Medicare Claim Number: 1EG4-TE5-MK72

═══════════════════════════════════════════════════════════════
CURRENT BENEFIT INFORMATION
═══════════════════════════════════════════════════════════════

Benefit Type: RETIREMENT (Title II)
Monthly Benefit Amount: $1,850.00
Payment Day: 3rd of each month
Payment Method: Direct Deposit

Bank: First National Bank
Account: ****4521 (Checking)

═══════════════════════════════════════════════════════════════
BENEFIT HISTORY
═══════════════════════════════════════════════════════════════

Year    Monthly Amount    Annual Total    COLA Increase
────────────────────────────────────────────────────────────────
2026    $1,850.00        $22,200.00      3.2%
2025    $1,792.64        $21,511.68      2.5%
2024    $1,749.40        $20,992.80      3.2%
2023    $1,695.16        $20,341.92      8.7%

═══════════════════════════════════════════════════════════════
MEDICARE PREMIUM DEDUCTIONS
═══════════════════════════════════════════════════════════════

Medicare Part B Premium: $174.70/month
Deducted from: Social Security benefit
Net Deposit: $1,675.30/month

═══════════════════════════════════════════════════════════════
SPOUSE BENEFITS (DECEASED)
═══════════════════════════════════════════════════════════════

Deceased Spouse: ROBERT JAMES THOMPSON
SSN: XXX-XX-7823
Date of Death: March 15, 2020
Spouse's PIA at Death: $2,100.00

Margaret elected to receive her own retirement benefit ($1,850)
rather than survivor benefit ($1,575) as it was higher.

═══════════════════════════════════════════════════════════════
WORK HISTORY SUMMARY
═══════════════════════════════════════════════════════════════

Total Quarters of Coverage: 156 (39 years)
Primary Employer: Palm Beach County School District
Position: Elementary School Teacher
Years Worked: 1965-2004

Highest 35 Years Earnings (Indexed):
Year        Earnings
────────────────────
2004        $52,450
2003        $51,200
2002        $49,800
...
(35 years averaged for benefit calculation)

Average Indexed Monthly Earnings (AIME): $3,245
Primary Insurance Amount (PIA): $1,850.00

═══════════════════════════════════════════════════════════════
IMPORTANT NOTICES
═══════════════════════════════════════════════════════════════

1. Report any changes in address or banking information
2. Benefits may be affected by other income sources
3. Contact SSA if entering a nursing facility for 30+ days
4. Medicare enrollment is automatic at age 65

CONTACT INFORMATION:
Social Security Administration
1-800-772-1213 (TTY 1-800-325-0778)
www.ssa.gov
Local Office: 1645 Palm Beach Lakes Blvd, West Palm Beach, FL

This letter is provided for verification purposes.""",
        "extracted_data": {
            "ssn_last_four": "4589",
            "medicare_number": "1EG4-TE5-MK72",
            "monthly_benefit": 1850.00,
            "annual_benefit": 22200.00,
            "medicare_premium": 174.70,
            "net_deposit": 1675.30,
            "benefit_type": "Retirement",
            "payment_day": 3,
            "deceased_spouse_ssn_last_four": "7823"
        },
        "ai_analysis": "SSA benefits statement showing $1,850/month retirement benefit. Medicare Part B premium of $174.70 deducted, leaving net deposit of $1,675.30. Margaret chose her own benefit over survivor benefit as it was higher. 39 years of work history as school teacher."
    },
    {
        "name": "Social Security Card - Margaret Thompson",
        "category": "identity",
        "doc_type": "ssn_card",
        "content": """SOCIAL SECURITY CARD INFORMATION

═══════════════════════════════════════════════════════════════
CARD DETAILS
═══════════════════════════════════════════════════════════════

Name: MARGARET ANN THOMPSON
Social Security Number: XXX-XX-4589
(Full number on file: 591-42-4589)

Card Status: VALID
Issue Date: Original issued 1960
Replacement: Last replacement 2015

═══════════════════════════════════════════════════════════════
VERIFICATION STATUS
═══════════════════════════════════════════════════════════════

SSN Verified: YES
Name Match: YES
Date of Birth Match: YES
Citizenship Status: U.S. CITIZEN

═══════════════════════════════════════════════════════════════
USAGE NOTES
═══════════════════════════════════════════════════════════════

This SSN is required for:
• Medicaid application (ACCESS Florida)
• VA benefits application (Form 21-534EZ)
• Facility admission paperwork
• Medicare enrollment verification
• Tax purposes

IMPORTANT: Keep original card in secure location.
Provide copies only, never original card.

Document verified by CareNav AI""",
        "extracted_data": {
            "full_ssn": "591-42-4589",
            "ssn_last_four": "4589",
            "card_status": "Valid",
            "citizenship": "U.S. Citizen"
        },
        "ai_analysis": "Social Security card verified. SSN 591-42-4589 confirmed valid. Required for all benefit applications including Medicaid and VA. Original card should be kept secure; provide copies only."
    },
    {
        "name": "Medicare Card and Coverage Summary",
        "category": "insurance",
        "doc_type": "medicare_card",
        "content": """MEDICARE BENEFICIARY INFORMATION

═══════════════════════════════════════════════════════════════
MEDICARE CARD DETAILS
═══════════════════════════════════════════════════════════════

Name: MARGARET A THOMPSON
Medicare Number: 1EG4-TE5-MK72
Sex: Female
Effective Date: March 1, 2007 (Age 65)

═══════════════════════════════════════════════════════════════
COVERAGE DETAILS
═══════════════════════════════════════════════════════════════

PART A (Hospital Insurance)
Effective: 03-01-2007
Premium: $0 (Premium-free based on work history)
Coverage: Inpatient hospital, skilled nursing facility,
         hospice, home health care

PART B (Medical Insurance)
Effective: 03-01-2007
Premium: $174.70/month (2026)
Coverage: Doctor visits, outpatient care, preventive
         services, durable medical equipment

PART D (Prescription Drug)
Plan: SilverScript Choice (PDP)
Premium: $28.50/month
Effective: 01-01-2024
Coverage: Prescription medications

═══════════════════════════════════════════════════════════════
2026 COVERAGE SUMMARY
═══════════════════════════════════════════════════════════════

PART A BENEFITS USED (2026):
Hospital Days Used: 5 (Current admission)
Hospital Days Remaining: 55 (of 60 per benefit period)
SNF Days Used: 0
SNF Days Remaining: 100

PART B DEDUCTIBLE:
Annual Deductible: $257.00
Amount Met: $257.00 (MET)

PART D COVERAGE:
Deductible: $545.00
Amount Met: $200.00
Current Phase: Initial Coverage
Out-of-Pocket: $345.00 remaining to deductible

═══════════════════════════════════════════════════════════════
WHAT MEDICARE DOES NOT COVER
═══════════════════════════════════════════════════════════════

IMPORTANT FOR MARGARET'S SITUATION:

✗ Long-term care (custodial care)
✗ Memory Care facility costs
✗ Assisted Living facility costs
✗ Most nursing home care (beyond 100 days SNF)
✗ Personal care assistance (bathing, dressing)

This is why Medicaid is essential for Margaret's care.
Medicare will NOT pay for Memory Care placement.

═══════════════════════════════════════════════════════════════
MEDICARE SAVINGS PROGRAMS
═══════════════════════════════════════════════════════════════

Margaret may qualify for:
• QMB (Qualified Medicare Beneficiary) - Pays Part B premium
• SLMB (Specified Low-Income Medicare Beneficiary)
• QI (Qualifying Individual)

With Medicaid approval, Margaret will automatically
receive QMB benefits (Part B premium paid by Medicaid).

Contact: 1-800-MEDICARE (1-800-633-4227)
Website: www.medicare.gov

Document verified by CareNav AI""",
        "extracted_data": {
            "medicare_number": "1EG4-TE5-MK72",
            "part_a_effective": "2007-03-01",
            "part_b_effective": "2007-03-01",
            "part_b_premium": 174.70,
            "part_d_plan": "SilverScript Choice",
            "part_d_premium": 28.50,
            "hospital_days_used": 5,
            "hospital_days_remaining": 55
        },
        "ai_analysis": "Medicare coverage active since 2007. Part B premium $174.70/month. Critical note: Medicare does NOT cover long-term care or Memory Care facility costs. Medicaid is essential for Margaret's care needs. May qualify for QMB to have Part B premium paid."
    },
    # ═══════════════════════════════════════════════════════════════
    # 2-YEAR BANK RECORDS (2024-2026)
    # ═══════════════════════════════════════════════════════════════
    {
        "name": "Bank Statement - Checking - 2024 Annual Summary",
        "category": "bank",
        "doc_type": "bank_statement_annual",
        "content": """FIRST NATIONAL BANK
ANNUAL ACCOUNT SUMMARY - 2024

Account Holder: Margaret A. Thompson
Account Number: ****4521 (Checking)
Statement Period: January 1 - December 31, 2024

═══════════════════════════════════════════════════════════════
ANNUAL SUMMARY
═══════════════════════════════════════════════════════════════

Beginning Balance (01/01/24): $2,450.00
Total Deposits: $27,600.00
Total Withdrawals: $27,850.00
Ending Balance (12/31/24): $2,200.00

═══════════════════════════════════════════════════════════════
MONTHLY BALANCES - 2024
═══════════════════════════════════════════════════════════════

Month       Beginning    Deposits    Withdrawals   Ending
────────────────────────────────────────────────────────────────
January     $2,450.00    $2,300.00   $2,150.00    $2,600.00
February    $2,600.00    $2,300.00   $2,400.00    $2,500.00
March       $2,500.00    $2,300.00   $2,350.00    $2,450.00
April       $2,450.00    $2,300.00   $2,200.00    $2,550.00
May         $2,550.00    $2,300.00   $2,450.00    $2,400.00
June        $2,400.00    $2,300.00   $2,300.00    $2,400.00
July        $2,400.00    $2,300.00   $2,500.00    $2,200.00
August      $2,200.00    $2,300.00   $2,100.00    $2,400.00
September   $2,400.00    $2,300.00   $2,350.00    $2,350.00
October     $2,350.00    $2,300.00   $2,400.00    $2,250.00
November    $2,250.00    $2,300.00   $2,300.00    $2,250.00
December    $2,250.00    $2,300.00   $2,350.00    $2,200.00

═══════════════════════════════════════════════════════════════
INCOME SOURCES - 2024
═══════════════════════════════════════════════════════════════

Social Security (Monthly):
12 deposits x $1,749.40 = $20,992.80

Pension - Robert Thompson Estate (Monthly):
12 deposits x $450.00 = $5,400.00

Interest Income:
Annual interest earned = $12.20

Other Income:
Tax refund (April) = $1,195.00

TOTAL INCOME 2024: $27,600.00

═══════════════════════════════════════════════════════════════
EXPENSE CATEGORIES - 2024
═══════════════════════════════════════════════════════════════

Category                    Annual Total    Monthly Avg
────────────────────────────────────────────────────────────────
Medicare Premium            $2,036.40       $169.70
Utilities (FPL, Water)      $2,340.00       $195.00
Groceries (Publix)          $3,120.00       $260.00
Pharmacy (CVS)              $780.00         $65.00
Property Tax                $3,200.00       (paid quarterly)
Home Insurance              $2,400.00       (paid annually)
Auto Insurance              $1,200.00       (paid semi-annual)
Gas/Transportation          $960.00         $80.00
Medical Copays              $450.00         $37.50
Phone/Cable                 $1,440.00       $120.00
Church Tithe                $2,400.00       $200.00
Miscellaneous               $7,523.60       $626.97
────────────────────────────────────────────────────────────────
TOTAL EXPENSES 2024:        $27,850.00

═══════════════════════════════════════════════════════════════
NOTABLE TRANSACTIONS - 2024
═══════════════════════════════════════════════════════════════

03/15/24  Robert's Memorial Service (4yr)    -$350.00
04/15/24  Tax Refund Deposit                 +$1,195.00
06/20/24  Home Insurance Annual              -$2,400.00
08/10/24  New Eyeglasses                     -$425.00
11/25/24  Holiday Gifts                      -$500.00

═══════════════════════════════════════════════════════════════
ACCOUNT ANALYSIS
═══════════════════════════════════════════════════════════════

Average Daily Balance: $2,375.00
Lowest Balance: $2,100.00 (July 15)
Highest Balance: $3,395.00 (April 18)
Overdrafts: 0
NSF Fees: $0

NO LARGE TRANSFERS OR GIFTS IDENTIFIED
(Important for Medicaid look-back compliance)

Document generated for Medicaid application purposes.""",
        "extracted_data": {
            "year": 2024,
            "account_type": "checking",
            "beginning_balance": 2450.00,
            "ending_balance": 2200.00,
            "total_deposits": 27600.00,
            "total_withdrawals": 27850.00,
            "average_balance": 2375.00,
            "overdrafts": 0,
            "large_transfers": False
        },
        "ai_analysis": "2024 checking account shows stable income and expenses. No large transfers or gifts that would trigger Medicaid look-back concerns. Average balance around $2,375. Income primarily from Social Security ($1,749/mo) and pension ($450/mo)."
    },
    {
        "name": "Bank Statement - Checking - 2025 Annual Summary",
        "category": "bank",
        "doc_type": "bank_statement_annual",
        "content": """FIRST NATIONAL BANK
ANNUAL ACCOUNT SUMMARY - 2025

Account Holder: Margaret A. Thompson
Account Number: ****4521 (Checking)
Statement Period: January 1 - December 31, 2025

═══════════════════════════════════════════════════════════════
ANNUAL SUMMARY
═══════════════════════════════════════════════════════════════

Beginning Balance (01/01/25): $2,200.00
Total Deposits: $28,311.68
Total Withdrawals: $28,861.68
Ending Balance (12/31/25): $1,650.00

═══════════════════════════════════════════════════════════════
MONTHLY BALANCES - 2025
═══════════════════════════════════════════════════════════════

Month       Beginning    Deposits    Withdrawals   Ending
────────────────────────────────────────────────────────────────
January     $2,200.00    $2,242.64   $2,100.00    $2,342.64
February    $2,342.64    $2,242.64   $2,300.00    $2,285.28
March       $2,285.28    $2,242.64   $2,250.00    $2,277.92
April       $2,277.92    $2,242.64   $2,200.00    $2,320.56
May         $2,320.56    $2,242.64   $2,400.00    $2,163.20
June        $2,163.20    $2,242.64   $2,350.00    $2,055.84
July        $2,055.84    $2,242.64   $2,500.00    $1,798.48
August      $1,798.48    $2,242.64   $2,100.00    $1,941.12
September   $1,941.12    $2,242.64   $2,450.00    $1,733.76
October     $1,733.76    $2,242.64   $2,300.00    $1,676.40
November    $1,676.40    $2,242.64   $2,400.00    $1,519.04
December    $1,519.04    $3,742.64   $3,611.68    $1,650.00

Note: December includes extra pension payment and holiday expenses

═══════════════════════════════════════════════════════════════
INCOME SOURCES - 2025
═══════════════════════════════════════════════════════════════

Social Security (Monthly):
12 deposits x $1,792.64 = $21,511.68 (2.5% COLA increase)

Pension - Robert Thompson Estate (Monthly):
12 deposits x $450.00 = $5,400.00

Interest Income:
Annual interest earned = $8.50

Other Income:
Tax refund (April) = $891.50
Extra pension payment (December) = $500.00

TOTAL INCOME 2025: $28,311.68

═══════════════════════════════════════════════════════════════
EXPENSE CATEGORIES - 2025
═══════════════════════════════════════════════════════════════

Category                    Annual Total    Monthly Avg
────────────────────────────────────────────────────────────────
Medicare Premium            $2,096.40       $174.70
Utilities (FPL, Water)      $2,580.00       $215.00
Groceries (Publix)          $3,360.00       $280.00
Pharmacy (CVS)              $960.00         $80.00
Property Tax                $3,400.00       (paid quarterly)
Home Insurance              $2,640.00       (paid annually)
Auto Insurance              $1,320.00       (paid semi-annual)
Gas/Transportation          $720.00         $60.00
Medical Copays              $1,250.00       $104.17
Phone/Cable                 $1,560.00       $130.00
Church Tithe                $2,400.00       $200.00
Home Repairs                $1,500.00       (AC repair July)
Miscellaneous               $5,075.28       $422.94
────────────────────────────────────────────────────────────────
TOTAL EXPENSES 2025:        $28,861.68

═══════════════════════════════════════════════════════════════
NOTABLE TRANSACTIONS - 2025
═══════════════════════════════════════════════════════════════

03/15/25  Robert's Memorial Service (5yr)    -$400.00
04/15/25  Tax Refund Deposit                 +$891.50
06/20/25  Home Insurance Annual              -$2,640.00
07/22/25  AC Repair (Emergency)              -$1,500.00
09/05/25  Neurologist Visit (New)            -$350.00
10/15/25  Memory Assessment                  -$200.00
11/20/25  Increased Pharmacy Costs           -$150.00
12/25/25  Holiday Gifts (Reduced)            -$300.00

═══════════════════════════════════════════════════════════════
CONCERNING TRENDS IDENTIFIED
═══════════════════════════════════════════════════════════════

1. DECLINING BALANCE TREND
   January: $2,342 → December: $1,650
   Net decrease: $692 (29% decline)

2. INCREASED MEDICAL EXPENSES
   2024: $450 in copays
   2025: $1,250 in copays (178% increase)
   New neurology visits indicate cognitive concerns

3. REDUCED TRANSPORTATION
   2024: $960 gas/transport
   2025: $720 gas/transport (25% decrease)
   May indicate reduced driving ability

4. EMERGENCY EXPENSES
   AC repair in July depleted reserves

NO LARGE TRANSFERS OR GIFTS IDENTIFIED
(Medicaid look-back compliant)

Document generated for Medicaid application purposes.""",
        "extracted_data": {
            "year": 2025,
            "account_type": "checking",
            "beginning_balance": 2200.00,
            "ending_balance": 1650.00,
            "total_deposits": 28311.68,
            "total_withdrawals": 28861.68,
            "balance_decline": 692.00,
            "medical_expense_increase": "178%",
            "overdrafts": 0,
            "large_transfers": False
        },
        "ai_analysis": "2025 checking shows declining balance trend (down $692). Medical expenses increased 178% with new neurology visits indicating cognitive concerns. Transportation costs decreased suggesting reduced driving. No Medicaid look-back issues."
    },
    {
        "name": "Bank Statement - Savings - 2024 Annual Summary",
        "category": "bank",
        "doc_type": "bank_statement_annual",
        "content": """FIRST NATIONAL BANK
ANNUAL ACCOUNT SUMMARY - 2024

Account Holder: Margaret A. Thompson
Account Number: ****8832 (Savings)
Statement Period: January 1 - December 31, 2024

═══════════════════════════════════════════════════════════════
ANNUAL SUMMARY
═══════════════════════════════════════════════════════════════

Beginning Balance (01/01/24): $3,500.00
Total Deposits: $45.50
Total Withdrawals: $1,500.00
Ending Balance (12/31/24): $2,045.50

═══════════════════════════════════════════════════════════════
MONTHLY BALANCES - 2024
═══════════════════════════════════════════════════════════════

Month       Beginning    Interest    Withdrawals   Ending
────────────────────────────────────────────────────────────────
January     $3,500.00    $3.50       $0.00        $3,503.50
February    $3,503.50    $3.50       $0.00        $3,507.00
March       $3,507.00    $3.51       $0.00        $3,510.51
April       $3,510.51    $3.51       $0.00        $3,514.02
May         $3,514.02    $3.51       $0.00        $3,517.53
June        $3,517.53    $3.52       $0.00        $3,521.05
July        $3,521.05    $3.52       $1,500.00    $2,024.57
August      $2,024.57    $3.52       $0.00        $2,028.09
September   $2,028.09    $3.53       $0.00        $2,031.62
October     $2,031.62    $3.53       $0.00        $2,035.15
November    $2,035.15    $3.53       $0.00        $2,038.68
December    $2,038.68    $6.82       $0.00        $2,045.50

═══════════════════════════════════════════════════════════════
TRANSACTION DETAILS
═══════════════════════════════════════════════════════════════

DEPOSITS:
Monthly interest credits (12 months): $45.50
Annual Percentage Yield (APY): 1.25%

WITHDRAWALS:
07/22/24  Transfer to Checking         -$1,500.00
          (For AC repair emergency)

═══════════════════════════════════════════════════════════════
ACCOUNT ANALYSIS
═══════════════════════════════════════════════════════════════

This savings account represents Margaret's emergency fund.
The July withdrawal was for an emergency AC repair.

Average Balance: $2,940.00
Interest Rate: 1.25% APY
Interest Earned: $45.50

NO GIFTS OR TRANSFERS TO THIRD PARTIES
(Medicaid look-back compliant)

Document generated for Medicaid application purposes.""",
        "extracted_data": {
            "year": 2024,
            "account_type": "savings",
            "beginning_balance": 3500.00,
            "ending_balance": 2045.50,
            "interest_earned": 45.50,
            "withdrawals": 1500.00,
            "apy": 1.25,
            "large_transfers": False
        },
        "ai_analysis": "2024 savings account declined from $3,500 to $2,045 due to emergency AC repair withdrawal in July. Interest earned $45.50 at 1.25% APY. No gifts or third-party transfers - Medicaid compliant."
    },
    {
        "name": "Bank Statement - Savings - 2025 Annual Summary",
        "category": "bank",
        "doc_type": "bank_statement_annual",
        "content": """FIRST NATIONAL BANK
ANNUAL ACCOUNT SUMMARY - 2025

Account Holder: Margaret A. Thompson
Account Number: ****8832 (Savings)
Statement Period: January 1 - December 31, 2025

═══════════════════════════════════════════════════════════════
ANNUAL SUMMARY
═══════════════════════════════════════════════════════════════

Beginning Balance (01/01/25): $2,045.50
Total Deposits: $25.75
Total Withdrawals: $500.00
Ending Balance (12/31/25): $1,571.25

═══════════════════════════════════════════════════════════════
MONTHLY BALANCES - 2025
═══════════════════════════════════════════════════════════════

Month       Beginning    Interest    Withdrawals   Ending
────────────────────────────────────────────────────────────────
January     $2,045.50    $2.13       $0.00        $2,047.63
February    $2,047.63    $2.13       $0.00        $2,049.76
March       $2,049.76    $2.14       $0.00        $2,051.90
April       $2,051.90    $2.14       $0.00        $2,054.04
May         $2,054.04    $2.14       $0.00        $2,056.18
June        $2,056.18    $2.14       $0.00        $2,058.32
July        $2,058.32    $2.14       $0.00        $2,060.46
August      $2,060.46    $2.15       $0.00        $2,062.61
September   $2,062.61    $2.15       $500.00      $1,564.76
October     $1,564.76    $2.15       $0.00        $1,566.91
November    $1,566.91    $2.17       $0.00        $1,569.08
December    $1,569.08    $2.17       $0.00        $1,571.25

═══════════════════════════════════════════════════════════════
TRANSACTION DETAILS
═══════════════════════════════════════════════════════════════

DEPOSITS:
Monthly interest credits (12 months): $25.75
Annual Percentage Yield (APY): 1.25%

WITHDRAWALS:
09/10/25  Transfer to Checking         -$500.00
          (For neurologist and memory assessment)

═══════════════════════════════════════════════════════════════
ACCOUNT ANALYSIS
═══════════════════════════════════════════════════════════════

Savings balance continues to decline as medical expenses increase.
September withdrawal was for cognitive assessment appointments.

Average Balance: $1,876.00
Interest Rate: 1.25% APY
Interest Earned: $25.75

TREND ANALYSIS:
2023 Ending Balance: $3,500.00
2024 Ending Balance: $2,045.50 (-41%)
2025 Ending Balance: $1,571.25 (-23%)

Total 2-year decline: $1,928.75 (55% reduction)

NO GIFTS OR TRANSFERS TO THIRD PARTIES
(Medicaid look-back compliant)

Document generated for Medicaid application purposes.""",
        "extracted_data": {
            "year": 2025,
            "account_type": "savings",
            "beginning_balance": 2045.50,
            "ending_balance": 1571.25,
            "interest_earned": 25.75,
            "withdrawals": 500.00,
            "two_year_decline": 1928.75,
            "decline_percentage": 55,
            "large_transfers": False
        },
        "ai_analysis": "2025 savings declined to $1,571. September withdrawal for cognitive assessments. Two-year decline of 55% ($1,929) shows depleting reserves. No gifts or third-party transfers - Medicaid compliant."
    },
    {
        "name": "Complete Asset Inventory - January 2026",
        "category": "financial",
        "doc_type": "asset_inventory",
        "content": """COMPLETE ASSET INVENTORY
For: Margaret A. Thompson
As of: January 31, 2026
Prepared for: Medicaid Application

═══════════════════════════════════════════════════════════════
COUNTABLE ASSETS (Subject to Medicaid Limit)
═══════════════════════════════════════════════════════════════

BANK ACCOUNTS:
First National Bank - Checking (****4521)    $1,500.00
First National Bank - Savings (****8832)     $1,500.00
────────────────────────────────────────────────────────────────
TOTAL COUNTABLE ASSETS:                      $3,000.00

MEDICAID ASSET LIMIT:                        $2,000.00
AMOUNT OVER LIMIT:                           $1,000.00

═══════════════════════════════════════════════════════════════
EXEMPT ASSETS (Not Counted for Medicaid)
═══════════════════════════════════════════════════════════════

PRIMARY RESIDENCE:
Address: 1234 Palm Way, West Palm Beach, FL 33401
Market Value: $285,000.00
Mortgage Balance: $0.00 (Paid off 2010)
Equity: $285,000.00
Status: EXEMPT (Homestead)
Condition: Intent to return OR transfer to family

PERSONAL PROPERTY:
Household furnishings: ~$5,000 (estimated)
Clothing and personal items: ~$1,000
Status: EXEMPT

VEHICLE:
2018 Toyota Camry
Value: ~$12,000 (KBB estimate)
Loan Balance: $0.00
Status: EXEMPT (one vehicle exempt)

PREPAID BURIAL:
Existing burial plot (Robert Thompson): $0
Margaret's burial: NOT YET PURCHASED
Recommendation: Purchase irrevocable prepaid funeral ($1,000)
Status: Would be EXEMPT if purchased

LIFE INSURANCE:
Policy: None currently
Status: N/A

═══════════════════════════════════════════════════════════════
INCOME SOURCES (Monthly)
═══════════════════════════════════════════════════════════════

Social Security Retirement:           $1,850.00
Pension (Robert Thompson Estate):     $450.00
────────────────────────────────────────────────────────────────
TOTAL MONTHLY INCOME:                 $2,300.00

ANNUAL INCOME:                        $27,600.00

═══════════════════════════════════════════════════════════════
DEBTS AND LIABILITIES
═══════════════════════════════════════════════════════════════

MARGARET'S DEBTS:
None identified

DECEASED SPOUSE'S DEBTS (Robert):
Credit Card (Capital One): $2,400.00
Status: NOT Margaret's responsibility
        (Florida common law property state)

═══════════════════════════════════════════════════════════════
ASSET HISTORY (3-YEAR TREND)
═══════════════════════════════════════════════════════════════

Year    Checking    Savings     Total       Change
────────────────────────────────────────────────────────────────
2023    $2,450      $3,500      $5,950      --
2024    $2,200      $2,046      $4,246      -$1,704 (-29%)
2025    $1,650      $1,571      $3,221      -$1,025 (-24%)
2026*   $1,500      $1,500      $3,000      -$221 (-7%)

*As of January 31, 2026

TOTAL 3-YEAR DECLINE: $2,950 (50% reduction)

═══════════════════════════════════════════════════════════════
MEDICAID ELIGIBILITY ANALYSIS
═══════════════════════════════════════════════════════════════

CURRENT STATUS: NOT ELIGIBLE (Over asset limit)

REQUIRED ACTION:
Spend down $1,000 in countable assets

RECOMMENDED SPEND-DOWN:
Irrevocable prepaid funeral contract: $1,000
Result: Assets reduced to $2,000 (at limit)

AFTER SPEND-DOWN:
Checking: $500.00
Savings: $1,500.00
Total: $2,000.00
Status: ELIGIBLE

═══════════════════════════════════════════════════════════════
VERIFICATION DOCUMENTS ATTACHED
═══════════════════════════════════════════════════════════════

□ Bank statements (24 months) - Checking
□ Bank statements (24 months) - Savings
□ Property tax statement (homestead)
□ Vehicle registration
□ Social Security benefit letter
□ Pension statement

Document prepared by CareNav AI for Medicaid application.""",
        "extracted_data": {
            "total_countable_assets": 3000.00,
            "medicaid_limit": 2000.00,
            "amount_over_limit": 1000.00,
            "home_value": 285000.00,
            "home_equity": 285000.00,
            "vehicle_value": 12000.00,
            "monthly_income": 2300.00,
            "three_year_asset_decline": 2950.00,
            "decline_percentage": 50
        },
        "ai_analysis": "Complete asset inventory showing $3,000 countable assets ($1,000 over Medicaid limit). Home ($285K) and vehicle ($12K) are exempt. 3-year asset decline of 50% shows depleting resources. Recommend $1,000 prepaid funeral for spend-down."
    },
    # ═══════════════════════════════════════════════════════════════
    # 3-YEAR MEDICAL HISTORY (2023-2026)
    # ═══════════════════════════════════════════════════════════════
    {
        "name": "Medical History - 2023 Annual Summary",
        "category": "medical",
        "doc_type": "medical_history_annual",
        "content": """MEDICAL HISTORY - 2023
Patient: Margaret A. Thompson
DOB: March 15, 1942
Medicare #: 1EG4-TE5-MK72

═══════════════════════════════════════════════════════════════
ANNUAL WELLNESS VISIT - MARCH 2023
═══════════════════════════════════════════════════════════════

Provider: Dr. Robert Martinez, MD
Date: March 20, 2023
Location: Palm Beach Internal Medicine

VITAL SIGNS:
Blood Pressure: 138/82 mmHg (slightly elevated)
Heart Rate: 72 bpm
Weight: 145 lbs
Height: 5'4"
BMI: 24.9 (normal)

DIAGNOSES (Active):
1. Essential Hypertension (I10) - Controlled
2. Hypothyroidism (E03.9) - Controlled
3. Osteoarthritis, multiple sites (M15.9) - Mild

COGNITIVE SCREENING:
Mini-Cog: 4/5 (normal)
No concerns noted at this time

MEDICATIONS:
- Lisinopril 20mg daily (hypertension)
- Levothyroxine 50mcg daily (thyroid)
- Acetaminophen PRN (arthritis pain)

LABS:
TSH: 2.1 mIU/L (normal)
Lipid Panel: Total cholesterol 195, LDL 110, HDL 55
A1C: 5.6% (normal, no diabetes)
CBC: Within normal limits
CMP: Within normal limits

ASSESSMENT:
83-year-old female in good health for age.
Hypertension and hypothyroidism well-controlled.
Mild arthritis managed with OTC medications.
No cognitive concerns at this time.

PLAN:
- Continue current medications
- Annual labs in 12 months
- Colonoscopy due (declined, age-appropriate)
- Flu shot administered

═══════════════════════════════════════════════════════════════
OTHER VISITS - 2023
═══════════════════════════════════════════════════════════════

JUNE 15, 2023 - Urgent Care
Chief Complaint: UTI symptoms
Diagnosis: Urinary tract infection (N39.0)
Treatment: Ciprofloxacin 500mg x 7 days
Outcome: Resolved

SEPTEMBER 8, 2023 - Primary Care
Chief Complaint: Knee pain (right)
Diagnosis: Osteoarthritis flare
Treatment: Physical therapy referral, continue Tylenol
Outcome: Improved with PT

DECEMBER 5, 2023 - Primary Care
Chief Complaint: Follow-up, medication refills
Notes: Patient doing well. Daughter Sarah called
       expressing mild concern about mother's memory
       (forgetting appointments). Advised to monitor.
Assessment: Age-appropriate memory changes, no intervention
            needed at this time.

═══════════════════════════════════════════════════════════════
HOSPITALIZATIONS - 2023
═══════════════════════════════════════════════════════════════

None

═══════════════════════════════════════════════════════════════
SPECIALIST VISITS - 2023
═══════════════════════════════════════════════════════════════

None required

═══════════════════════════════════════════════════════════════
2023 SUMMARY
═══════════════════════════════════════════════════════════════

Overall Health Status: GOOD
Cognitive Status: NORMAL (early concerns noted by family)
Functional Status: INDEPENDENT
Living Situation: Alone at home
Driving: Yes, independently

Total Medical Costs 2023: ~$450 (copays)
Hospitalizations: 0
ER Visits: 0
Urgent Care: 1

Document compiled from medical records.""",
        "extracted_data": {
            "year": 2023,
            "overall_status": "Good",
            "cognitive_status": "Normal",
            "functional_status": "Independent",
            "hospitalizations": 0,
            "er_visits": 0,
            "diagnoses": ["Hypertension", "Hypothyroidism", "Osteoarthritis"],
            "mini_cog_score": "4/5",
            "early_memory_concerns": True
        },
        "ai_analysis": "2023 medical history shows Margaret in good health with controlled hypertension and hypothyroidism. First documented memory concern from daughter in December - described as 'forgetting appointments.' Mini-Cog normal at 4/5. Living independently."
    },
    {
        "name": "Medical History - 2024 Annual Summary",
        "category": "medical",
        "doc_type": "medical_history_annual",
        "content": """MEDICAL HISTORY - 2024
Patient: Margaret A. Thompson
DOB: March 15, 1942
Medicare #: 1EG4-TE5-MK72

═══════════════════════════════════════════════════════════════
ANNUAL WELLNESS VISIT - MARCH 2024
═══════════════════════════════════════════════════════════════

Provider: Dr. Robert Martinez, MD
Date: March 18, 2024
Location: Palm Beach Internal Medicine

VITAL SIGNS:
Blood Pressure: 142/85 mmHg (elevated)
Heart Rate: 76 bpm
Weight: 142 lbs (3 lb loss from 2023)
Height: 5'4"
BMI: 24.4

DIAGNOSES (Active):
1. Essential Hypertension (I10) - Less controlled
2. Hypothyroidism (E03.9) - Controlled
3. Osteoarthritis, multiple sites (M15.9) - Mild
4. Mild Cognitive Impairment (G31.84) - NEW

COGNITIVE SCREENING:
Mini-Cog: 3/5 (borderline)
MMSE: 24/30 (mild impairment)
  - Orientation: 8/10
  - Registration: 3/3
  - Attention: 3/5
  - Recall: 1/3 (significant)
  - Language: 9/9

ASSESSMENT:
Cognitive decline noted since last year. Daughter reports:
- Forgetting recent conversations
- Repeating questions
- Difficulty managing medications
- Got lost driving to familiar location (once)

PLAN:
- Refer to neurology for evaluation
- Start Donepezil 5mg daily
- Increase Lisinopril to 20mg (was 10mg)
- Driving evaluation recommended
- Follow-up in 3 months

═══════════════════════════════════════════════════════════════
NEUROLOGY CONSULTATION - MAY 2024
═══════════════════════════════════════════════════════════════

Provider: Dr. Jennifer Lee, MD (Neurologist)
Date: May 10, 2024
Location: Palm Beach Neurology Associates

CHIEF COMPLAINT:
Memory concerns, referred by PCP

HISTORY:
Progressive memory decline over past 6-12 months.
Daughter notes patient repeats stories, forgets appointments,
and had one episode of getting lost while driving.

EXAMINATION:
- Alert and oriented x2 (person, place; not date)
- MMSE: 23/30
- Clock drawing: Abnormal (numbers clustered)
- Naming: Mild difficulty with low-frequency words

DIAGNOSTIC WORKUP:
- MRI Brain: Mild hippocampal atrophy, no acute findings
- B12: Normal
- TSH: Normal
- RPR: Negative

DIAGNOSIS:
Probable Alzheimer's Disease, Mild Stage (G30.9)

PLAN:
- Continue Donepezil, increase to 10mg in 4 weeks
- Consider Memantine if decline continues
- Driving cessation recommended
- Safety evaluation of home
- Caregiver support resources provided
- Follow-up in 6 months

═══════════════════════════════════════════════════════════════
OTHER VISITS - 2024
═══════════════════════════════════════════════════════════════

JUNE 20, 2024 - Primary Care
Chief Complaint: Medication check, BP follow-up
Notes: BP improved on higher dose Lisinopril
       Tolerating Donepezil well
       Daughter now managing medications

AUGUST 15, 2024 - Primary Care
Chief Complaint: Confusion episode
Notes: Patient found by neighbor wandering in yard
       at 6 AM, confused about where she was.
       Resolved within 30 minutes.
Assessment: Likely sundowning/early morning confusion
Plan: Safety assessment, consider increased supervision

OCTOBER 22, 2024 - Primary Care
Chief Complaint: Weight loss, decreased appetite
Notes: 5 lb weight loss over 3 months
       Daughter reports patient forgetting to eat
Assessment: Weight loss related to cognitive decline
Plan: Ensure meals provided, nutritional supplements

DECEMBER 10, 2024 - Primary Care
Chief Complaint: Annual follow-up
Notes: Cognitive decline progressing
       Now needs help with bathing, dressing
       Daughter considering care options
MMSE: 20/30 (moderate impairment)

═══════════════════════════════════════════════════════════════
HOSPITALIZATIONS - 2024
═══════════════════════════════════════════════════════════════

None

═══════════════════════════════════════════════════════════════
2024 SUMMARY
═══════════════════════════════════════════════════════════════

Overall Health Status: DECLINING
Cognitive Status: MILD TO MODERATE IMPAIRMENT
Functional Status: NEEDS ASSISTANCE WITH IADLs
Living Situation: Alone (with daily daughter check-ins)
Driving: CEASED (May 2024)

PROGRESSION:
- March MMSE: 24/30 (mild)
- December MMSE: 20/30 (moderate)
- 4-point decline in 9 months

KEY EVENTS:
- Alzheimer's diagnosis (May)
- Driving cessation (May)
- Wandering episode (August)
- Weight loss (October)
- Increased care needs (December)

Total Medical Costs 2024: ~$1,250 (copays)
Hospitalizations: 0
ER Visits: 0
Specialist Visits: 2 (neurology)

Document compiled from medical records.""",
        "extracted_data": {
            "year": 2024,
            "overall_status": "Declining",
            "cognitive_status": "Mild to Moderate Impairment",
            "functional_status": "Needs Assistance with IADLs",
            "hospitalizations": 0,
            "alzheimers_diagnosis_date": "2024-05-10",
            "mmse_march": 24,
            "mmse_december": 20,
            "mmse_decline": 4,
            "driving_ceased": "2024-05",
            "wandering_episode": True,
            "weight_loss": "5 lbs"
        },
        "ai_analysis": "2024 marked significant decline. Alzheimer's diagnosis in May. MMSE dropped from 24 to 20 (4 points in 9 months). Key events: driving cessation, wandering episode, weight loss. Now needs help with bathing and dressing. Living alone becoming unsafe."
    },
    {
        "name": "Medical History - 2025 Annual Summary",
        "category": "medical",
        "doc_type": "medical_history_annual",
        "content": """MEDICAL HISTORY - 2025
Patient: Margaret A. Thompson
DOB: March 15, 1942
Medicare #: 1EG4-TE5-MK72

═══════════════════════════════════════════════════════════════
ANNUAL WELLNESS VISIT - MARCH 2025
═══════════════════════════════════════════════════════════════

Provider: Dr. Robert Martinez, MD
Date: March 15, 2025
Location: Palm Beach Internal Medicine

VITAL SIGNS:
Blood Pressure: 135/80 mmHg (controlled)
Heart Rate: 74 bpm
Weight: 138 lbs (4 lb loss from 2024)
Height: 5'4"
BMI: 23.7

DIAGNOSES (Active):
1. Alzheimer's Disease, Moderate (G30.1) - Progressing
2. Essential Hypertension (I10) - Controlled
3. Hypothyroidism (E03.9) - Controlled
4. Osteoarthritis (M15.9) - Stable
5. Weight Loss, Unintentional (R63.4) - NEW

COGNITIVE SCREENING:
MMSE: 18/30 (moderate impairment)
  - Orientation: 5/10 (significant decline)
  - Registration: 3/3
  - Attention: 2/5
  - Recall: 0/3 (unable)
  - Language: 8/9

FUNCTIONAL ASSESSMENT:
ADLs (Activities of Daily Living):
- Bathing: Needs assistance
- Dressing: Needs assistance
- Toileting: Mostly independent
- Transferring: Independent
- Eating: Needs reminders
- Continence: Occasional accidents

IADLs (Instrumental ADLs):
- Medications: Cannot manage (daughter does)
- Finances: Cannot manage (daughter does)
- Cooking: Cannot safely cook
- Shopping: Cannot do alone
- Transportation: Cannot drive
- Housework: Cannot do

ASSESSMENT:
Moderate Alzheimer's with continued decline.
No longer safe to live alone.
Recommend 24-hour supervision.

PLAN:
- Continue Donepezil 10mg
- Add Memantine 5mg, titrate to 10mg
- Discuss care placement with family
- Home safety evaluation
- Caregiver respite resources

═══════════════════════════════════════════════════════════════
NEUROLOGY FOLLOW-UP - JUNE 2025
═══════════════════════════════════════════════════════════════

Provider: Dr. Jennifer Lee, MD
Date: June 12, 2025

ASSESSMENT:
Moderate Alzheimer's Disease, progressing as expected.
MMSE: 17/30

BEHAVIORAL SYMPTOMS:
- Sundowning (increased evening confusion)
- Occasional agitation
- Sleep disturbance
- Repetitive questioning

RECOMMENDATIONS:
- Continue current medications
- Melatonin 3mg at bedtime for sleep
- Structured daily routine
- Memory Care placement recommended
- Follow-up in 6 months or sooner if needed

═══════════════════════════════════════════════════════════════
OTHER VISITS - 2025
═══════════════════════════════════════════════════════════════

APRIL 8, 2025 - Primary Care
Chief Complaint: Fall at home
Notes: Patient fell getting out of bed at night
       No injuries, but concerning pattern
       Daughter now staying overnight 3x/week

JULY 22, 2025 - Primary Care
Chief Complaint: Increased confusion
Notes: Daughter reports patient not recognizing
       her sometimes. Calling her by sister's name.
Assessment: Disease progression
Plan: Continue medications, support family

SEPTEMBER 5, 2025 - Neurology
Chief Complaint: Cognitive reassessment
MMSE: 16/30
Notes: Continued decline. Patient now needs help
       with most ADLs. Wandering risk high.
Recommendation: Memory Care placement urgent

OCTOBER 15, 2025 - Primary Care
Chief Complaint: Urinary incontinence
Notes: New onset urinary incontinence
       Likely related to cognitive decline
Plan: Incontinence supplies, rule out UTI
      UTI negative

NOVEMBER 20, 2025 - Primary Care
Chief Complaint: Behavioral changes
Notes: Patient becoming more agitated in evenings
       Refusing care at times
       Daughter exhausted from caregiving
Assessment: Caregiver burnout, patient needs
            higher level of care
Plan: Urgent discussion re: placement

═══════════════════════════════════════════════════════════════
HOSPITALIZATIONS - 2025
═══════════════════════════════════════════════════════════════

None (but multiple near-misses with falls, wandering)

═══════════════════════════════════════════════════════════════
2025 SUMMARY
═══════════════════════════════════════════════════════════════

Overall Health Status: SIGNIFICANT DECLINE
Cognitive Status: MODERATE ALZHEIMER'S
Functional Status: DEPENDENT FOR MOST ADLs
Living Situation: Alone (daughter staying 3-4 nights/week)
Driving: No (ceased May 2024)

PROGRESSION:
- March MMSE: 18/30
- June MMSE: 17/30
- September MMSE: 16/30
- 2-point decline in 6 months

KEY EVENTS:
- Fall at home (April)
- Not recognizing daughter (July)
- Urinary incontinence onset (October)
- Behavioral changes/agitation (November)
- Memory Care recommended (September)

CAREGIVER STATUS:
Daughter Sarah experiencing burnout
Working full-time while providing care
Staying overnight 3-4 nights per week
Emotionally and physically exhausted

Total Medical Costs 2025: ~$1,800 (copays)
Hospitalizations: 0
ER Visits: 0
Specialist Visits: 3 (neurology)

Document compiled from medical records.""",
        "extracted_data": {
            "year": 2025,
            "overall_status": "Significant Decline",
            "cognitive_status": "Moderate Alzheimer's",
            "functional_status": "Dependent for Most ADLs",
            "hospitalizations": 0,
            "mmse_march": 18,
            "mmse_september": 16,
            "mmse_decline": 2,
            "fall_incident": True,
            "incontinence_onset": "2025-10",
            "not_recognizing_family": True,
            "caregiver_burnout": True,
            "memory_care_recommended": True
        },
        "ai_analysis": "2025 showed continued decline. MMSE dropped from 18 to 16. New symptoms: falls, incontinence, not recognizing daughter, behavioral changes. Daughter experiencing caregiver burnout. Memory Care placement urgently recommended by September."
    },
    {
        "name": "Medical History - January 2026 (Current Hospitalization)",
        "category": "medical",
        "doc_type": "medical_history_current",
        "content": """MEDICAL HISTORY - JANUARY 2026
Patient: Margaret A. Thompson
DOB: March 15, 1942
Medicare #: 1EG4-TE5-MK72

═══════════════════════════════════════════════════════════════
CURRENT HOSPITALIZATION
═══════════════════════════════════════════════════════════════

FACILITY: Palm Beach General Hospital
ADMISSION DATE: January 28, 2026
ADMISSION TYPE: Emergency
ATTENDING: Dr. Sarah Chen, MD (Hospitalist)

CHIEF COMPLAINT:
Found wandering outside home at 2 AM in nightgown,
disoriented, brought by police to ER.

HISTORY OF PRESENT ILLNESS:
83-year-old female with moderate Alzheimer's disease
found by neighbor wandering in the street at 2 AM.
Patient was confused, unable to state her name or
address. Police brought her to ER. Daughter contacted.

Patient had been alone at home (daughter was not
staying that night). This is the most serious
wandering episode to date.

EMERGENCY DEPARTMENT COURSE:
- Arrived 2:45 AM, confused, hypothermic (96.2°F)
- No injuries identified
- Labs: UTI ruled out, metabolic panel normal
- CT Head: No acute findings, chronic atrophy
- Warmed with blankets, IV fluids
- Admitted for observation and social work evaluation

═══════════════════════════════════════════════════════════════
HOSPITAL COURSE
═══════════════════════════════════════════════════════════════

DAY 1 (January 28):
- Admitted to medical floor
- Reoriented to environment
- Social work consulted
- Daughter at bedside, very distressed
- Patient calm but confused

DAY 2 (January 29):
- Medically stable
- MMSE performed: 16/30
- PT/OT evaluation: Needs 24-hour supervision
- Social work: Discussed discharge options
- Cannot safely return home alone

DAY 3 (January 30):
- Family meeting held
- Options discussed: Memory Care placement
- Daughter agrees placement necessary
- Social work initiating Medicaid application
- Facility search begun

DAY 4 (January 31):
- Medically ready for discharge
- Awaiting placement
- CareNav AI system engaged to assist family

DAY 5 (February 1):
- Continued awaiting placement
- Patient stable, pleasant, cooperative
- Enjoying activities with volunteers

═══════════════════════════════════════════════════════════════
CURRENT DIAGNOSES
═══════════════════════════════════════════════════════════════

PRIMARY:
1. Alzheimer's Disease, Moderate Stage (G30.1)
2. Wandering due to dementia (F02.81)

SECONDARY:
3. Essential Hypertension (I10) - Controlled
4. Hypothyroidism (E03.9) - Controlled
5. Urinary Incontinence (R32)
6. Unintentional Weight Loss (R63.4)
7. Osteoarthritis (M15.9)

═══════════════════════════════════════════════════════════════
CURRENT MEDICATIONS (Hospital)
═══════════════════════════════════════════════════════════════

1. Donepezil 10mg PO daily at bedtime
2. Memantine 10mg PO daily
3. Lisinopril 20mg PO daily
4. Levothyroxine 50mcg PO daily (empty stomach)
5. Melatonin 3mg PO at bedtime
6. Acetaminophen 650mg PO Q6H PRN pain

═══════════════════════════════════════════════════════════════
COGNITIVE ASSESSMENT (January 29, 2026)
═══════════════════════════════════════════════════════════════

MMSE: 16/30 (Moderate Impairment)

Breakdown:
- Orientation to Time: 1/5
- Orientation to Place: 3/5
- Registration: 3/3
- Attention/Calculation: 2/5
- Recall: 0/3
- Naming: 2/2
- Repetition: 1/1
- 3-Stage Command: 2/3
- Reading: 1/1
- Writing: 0/1
- Copying: 1/1

INTERPRETATION:
Moderate cognitive impairment consistent with
moderate-stage Alzheimer's disease. Significant
deficits in orientation, attention, and recall.
Unable to live independently.

═══════════════════════════════════════════════════════════════
FUNCTIONAL ASSESSMENT
═══════════════════════════════════════════════════════════════

PHYSICAL THERAPY EVALUATION:
- Ambulation: Independent with supervision
- Balance: Mildly impaired
- Fall Risk: MODERATE
- Recommendation: Supervision for all mobility

OCCUPATIONAL THERAPY EVALUATION:
- Bathing: Requires assistance
- Dressing: Requires assistance
- Grooming: Requires cueing
- Toileting: Requires reminders, occasional accidents
- Feeding: Independent with setup
- Transfers: Independent

OVERALL FUNCTIONAL LEVEL:
Requires 24-hour supervision
Cannot safely live alone
Memory Care level of care appropriate

═══════════════════════════════════════════════════════════════
DISCHARGE PLANNING
═══════════════════════════════════════════════════════════════

DISCHARGE DISPOSITION: Memory Care Facility

RECOMMENDED LEVEL OF CARE:
Memory Care (secured dementia unit)

FACILITY REQUIREMENTS:
- 24-hour supervision
- Secured unit (wandering risk)
- Medication management
- Assistance with ADLs
- Structured activities program
- Accepts Medicaid (pending)

TARGET DISCHARGE DATE: February 10, 2026
(Pending facility bed availability and Medicaid application)

DISCHARGE MEDICATIONS:
(To be continued at facility)
1. Donepezil 10mg daily at bedtime
2. Memantine 10mg daily
3. Lisinopril 20mg daily
4. Levothyroxine 50mcg daily
5. Melatonin 3mg at bedtime
6. Acetaminophen PRN

FOLLOW-UP:
- PCP: 2 weeks post-discharge
- Neurology: 3 months
- Facility physician will assume care

═══════════════════════════════════════════════════════════════
PHYSICIAN NOTES
═══════════════════════════════════════════════════════════════

"Margaret is a pleasant 83-year-old woman with moderate
Alzheimer's disease who can no longer safely live alone.
This hospitalization was precipitated by a serious
wandering episode that could have resulted in injury
or death. She requires Memory Care placement with
24-hour supervision in a secured unit.

The family is engaged and supportive. Daughter Sarah
has been providing significant care but is experiencing
burnout. Placement is in Margaret's best interest and
will also allow the daughter to resume a more
sustainable caregiving role.

Prognosis: Alzheimer's disease will continue to
progress. With appropriate care, Margaret can maintain
quality of life for the foreseeable future."

- Dr. Sarah Chen, MD
  Hospitalist, Palm Beach General Hospital

Document compiled from hospital records.""",
        "extracted_data": {
            "admission_date": "2026-01-28",
            "admission_reason": "Wandering episode",
            "hospital": "Palm Beach General Hospital",
            "attending": "Dr. Sarah Chen",
            "mmse_score": 16,
            "discharge_disposition": "Memory Care Facility",
            "target_discharge": "2026-02-10",
            "current_medications": 6,
            "fall_risk": "Moderate",
            "requires_24hr_supervision": True,
            "secured_unit_needed": True
        },
        "ai_analysis": "Current hospitalization since January 28, 2026 due to serious wandering episode (found outside at 2 AM). MMSE 16/30 confirms moderate Alzheimer's. Cannot live alone - requires Memory Care with secured unit. Target discharge February 10 pending Medicaid and facility placement."
    },
    {
        "name": "3-Year Medical Timeline Summary",
        "category": "medical",
        "doc_type": "ai_medical_timeline",
        "content": """3-YEAR MEDICAL TIMELINE SUMMARY
Patient: Margaret A. Thompson
Period: 2023-2026
Generated by CareNav AI

═══════════════════════════════════════════════════════════════
DISEASE PROGRESSION TIMELINE
═══════════════════════════════════════════════════════════════

2023 ─────────────────────────────────────────────────────────
│
├─ MAR: Annual wellness - Mini-Cog 4/5 (normal)
│       No cognitive concerns documented
│
├─ DEC: First memory concern noted by daughter
│       "Forgetting appointments"
│       Physician: "Age-appropriate changes"
│
│  STATUS: INDEPENDENT, HEALTHY
│  MMSE: Not performed (no indication)
│
2024 ─────────────────────────────────────────────────────────
│
├─ MAR: MMSE 24/30 - Mild Cognitive Impairment diagnosed
│       Started Donepezil 5mg
│
├─ MAY: Neurology consult - ALZHEIMER'S DIAGNOSED
│       MRI shows hippocampal atrophy
│       Donepezil increased to 10mg
│       DRIVING CEASED
│
├─ AUG: First wandering episode (found in yard 6 AM)
│
├─ OCT: Weight loss noted (5 lbs)
│       Forgetting to eat
│
├─ DEC: MMSE 20/30 - Moderate impairment
│       Needs help with bathing, dressing
│
│  STATUS: NEEDS ASSISTANCE, DECLINING
│  MMSE DECLINE: 24 → 20 (4 points)
│
2025 ─────────────────────────────────────────────────────────
│
├─ MAR: MMSE 18/30
│       Memantine added
│       "No longer safe to live alone" documented
│
├─ APR: Fall at home (no injury)
│       Daughter staying overnight 3x/week
│
├─ JUN: MMSE 17/30
│       Sundowning, sleep disturbance
│
├─ JUL: Not recognizing daughter sometimes
│
├─ SEP: MMSE 16/30
│       MEMORY CARE RECOMMENDED
│
├─ OCT: Urinary incontinence onset
│
├─ NOV: Behavioral changes, agitation
│       Caregiver burnout documented
│
│  STATUS: DEPENDENT, SIGNIFICANT DECLINE
│  MMSE DECLINE: 18 → 16 (2 points)
│
2026 ─────────────────────────────────────────────────────────
│
├─ JAN 28: HOSPITALIZED - Serious wandering episode
│          Found outside at 2 AM, hypothermic
│          MMSE 16/30 confirmed
│
├─ JAN 30: Family meeting - Memory Care agreed
│
├─ FEB (projected): Discharge to Memory Care
│
│  STATUS: HOSPITALIZED, AWAITING PLACEMENT
│  REQUIRES: 24-hour supervision, secured unit

═══════════════════════════════════════════════════════════════
COGNITIVE DECLINE CHART
═══════════════════════════════════════════════════════════════

MMSE Score Over Time:

30 │ ████████████████████████████████████████ Normal
   │
25 │ ████████████████████████ ← Mar 2024 (24)
   │                          ↘
20 │ ████████████████████      ← Dec 2024 (20)
   │                      ↘
18 │ ██████████████████        ← Mar 2025 (18)
   │                    ↘
16 │ ████████████████          ← Sep 2025 / Jan 2026 (16)
   │
10 │ Severe Impairment
   │
 0 └──────────────────────────────────────────────────────
     2023      2024           2025           2026

TOTAL DECLINE: 8+ points over 2 years
RATE: ~4 points per year (moderate progression)

═══════════════════════════════════════════════════════════════
KEY MILESTONES
═══════════════════════════════════════════════════════════════

DIAGNOSIS MILESTONES:
□ Dec 2023: First family concern
□ Mar 2024: MCI diagnosed
□ May 2024: Alzheimer's diagnosed
□ Sep 2025: Memory Care recommended
□ Jan 2026: Hospitalized, placement imminent

FUNCTIONAL MILESTONES:
□ May 2024: Driving ceased
□ Jun 2024: Daughter managing medications
□ Dec 2024: Needs help bathing/dressing
□ Mar 2025: Cannot live alone safely
□ Oct 2025: Incontinence onset
□ Jan 2026: Requires 24-hour supervision

SAFETY INCIDENTS:
□ Aug 2024: Wandering (yard, 6 AM)
□ Apr 2025: Fall at home
□ Jan 2026: Wandering (street, 2 AM) - HOSPITALIZED

═══════════════════════════════════════════════════════════════
TREATMENT HISTORY
═══════════════════════════════════════════════════════════════

MEDICATIONS TIMELINE:
Mar 2024: Donepezil 5mg started
May 2024: Donepezil increased to 10mg
Mar 2025: Memantine 10mg added
Jun 2025: Melatonin 3mg added (sleep)

CURRENT REGIMEN:
- Donepezil 10mg (Alzheimer's)
- Memantine 10mg (Alzheimer's)
- Lisinopril 20mg (blood pressure)
- Levothyroxine 50mcg (thyroid)
- Melatonin 3mg (sleep)
- Acetaminophen PRN (pain)

═══════════════════════════════════════════════════════════════
PROGNOSIS
═══════════════════════════════════════════════════════════════

CURRENT STAGE: Moderate Alzheimer's Disease

EXPECTED PROGRESSION:
- Continued cognitive decline (2-4 MMSE points/year)
- Increasing care needs
- Eventually severe stage (MMSE <10)
- Average survival from diagnosis: 4-8 years

WITH APPROPRIATE CARE:
- Quality of life can be maintained
- Safety ensured in Memory Care
- Family relationships preserved
- Dignity maintained

RECOMMENDATION:
Immediate Memory Care placement is medically necessary
and in Margaret's best interest.

Report Generated by CareNav AI""",
        "extracted_data": {
            "timeline_years": 3,
            "total_mmse_decline": 8,
            "decline_rate_per_year": 4,
            "diagnosis_date": "2024-05",
            "current_stage": "Moderate Alzheimer's",
            "wandering_incidents": 3,
            "falls": 1,
            "medications_count": 6,
            "memory_care_recommended": "2025-09",
            "hospitalized": "2026-01-28"
        },
        "ai_analysis": "Comprehensive 3-year timeline showing progression from normal cognition to moderate Alzheimer's requiring Memory Care. MMSE declined 8+ points (24→16). Key events: diagnosis May 2024, driving ceased, multiple wandering episodes, hospitalization January 2026. Memory Care placement medically necessary."
    },
    # Additional Critical Documents
    {
        "name": "Durable Power of Attorney - Healthcare",
        "category": "legal",
        "doc_type": "poa_healthcare",
        "content": """DURABLE POWER OF ATTORNEY FOR HEALTH CARE
STATE OF FLORIDA

PRINCIPAL: Margaret Ann Thompson
Date of Birth: March 15, 1942
Address: 4521 Palm Beach Lakes Blvd, West Palm Beach, FL 33401
Social Security Number: XXX-XX-4567

I, Margaret Ann Thompson, being of sound mind, hereby designate the following person as my Health Care Surrogate:

PRIMARY HEALTH CARE SURROGATE:
Name: Sarah Thompson-Martinez
Relationship: Daughter
Address: 1234 Oak Street, San Diego, CA 92101
Phone: (619) 555-0123
Email: sarah.martinez@email.com

ALTERNATE HEALTH CARE SURROGATE:
Name: Michael Thompson
Relationship: Son
Address: 789 Maple Avenue, Atlanta, GA 30301
Phone: (404) 555-0456
Email: michael.thompson@email.com

POWERS GRANTED:
My Health Care Surrogate is authorized to:

1. Consent to or refuse any medical treatment, surgical procedure, or diagnostic procedure
2. Access all my medical records and health information (HIPAA authorization included)
3. Employ and discharge health care providers
4. Make decisions about my admission to or discharge from any hospital, nursing home, assisted living facility, or other health care facility
5. Make decisions regarding organ donation
6. Make decisions about autopsy
7. Make decisions about disposition of my remains

END-OF-LIFE DECISIONS:
If I have a terminal condition or am in a persistent vegetative state, my surrogate may:
- Withhold or withdraw life-prolonging procedures
- Provide, withhold, or withdraw artificially provided nutrition and hydration
- Make decisions consistent with my wishes as expressed in my Living Will

This Power of Attorney shall not be affected by my subsequent incapacity or disability.

EXECUTION:
Signed this 15th day of June, 2023

_______________________________
Margaret Ann Thompson, Principal

WITNESSES:
1. James Wilson, 123 Main St, West Palm Beach, FL
2. Dorothy Brown, 456 Oak Ave, West Palm Beach, FL

NOTARY:
State of Florida, County of Palm Beach
Sworn and subscribed before me this 15th day of June, 2023
Notary Public: Maria Garcia
Commission Number: GG123456
Commission Expires: December 31, 2026""",
        "extracted_data": {
            "principal": "Margaret Ann Thompson",
            "primary_surrogate": "Sarah Thompson-Martinez",
            "primary_relationship": "Daughter",
            "primary_phone": "(619) 555-0123",
            "alternate_surrogate": "Michael Thompson",
            "alternate_relationship": "Son",
            "execution_date": "2023-06-15",
            "notarized": True,
            "hipaa_included": True
        },
        "ai_analysis": "Healthcare POA designates daughter Sarah Thompson-Martinez as primary decision-maker for all medical decisions. Document is properly executed with witnesses and notarization. HIPAA authorization is included. This document is essential for facility admission and medical decision-making."
    },
    {
        "name": "Durable Power of Attorney - Financial",
        "category": "legal",
        "doc_type": "poa_financial",
        "content": """DURABLE POWER OF ATTORNEY FOR FINANCES
STATE OF FLORIDA

PRINCIPAL: Margaret Ann Thompson
Date of Birth: March 15, 1942
Address: 4521 Palm Beach Lakes Blvd, West Palm Beach, FL 33401
Social Security Number: XXX-XX-4567

I, Margaret Ann Thompson, being of sound mind, hereby appoint the following person as my Attorney-in-Fact:

PRIMARY ATTORNEY-IN-FACT:
Name: Sarah Thompson-Martinez
Relationship: Daughter
Address: 1234 Oak Street, San Diego, CA 92101
Phone: (619) 555-0123

ALTERNATE ATTORNEY-IN-FACT:
Name: Michael Thompson
Relationship: Son
Address: 789 Maple Avenue, Atlanta, GA 30301
Phone: (404) 555-0456

POWERS GRANTED:
My Attorney-in-Fact is authorized to:

BANKING AND FINANCIAL:
- Access, manage, and close bank accounts
- Deposit and withdraw funds
- Write checks and make electronic transfers
- Open new accounts as needed
- Access safe deposit boxes

REAL PROPERTY:
- Manage, lease, or sell real estate
- Pay property taxes and insurance
- Make repairs and improvements
- Execute deeds and mortgages

GOVERNMENT BENEFITS:
- Apply for Social Security, Medicare, Medicaid, and VA benefits
- Receive and manage benefit payments
- Appeal benefit decisions
- Complete required paperwork

TAXES:
- Prepare and file tax returns
- Pay taxes owed
- Receive refunds
- Represent me before the IRS

LEGAL MATTERS:
- Hire attorneys and other professionals
- Settle claims and lawsuits
- Sign contracts on my behalf

HEALTH CARE PAYMENTS:
- Pay medical bills and insurance premiums
- Manage health savings accounts
- Apply for Medicaid spend-down

GIFTING AUTHORITY:
- Make gifts up to annual exclusion amount ($18,000 per person in 2024)
- Make gifts for Medicaid planning purposes as advised by elder law attorney

DURABILITY CLAUSE:
This Power of Attorney shall not be affected by my subsequent incapacity or disability and shall remain in full force and effect.

EXECUTION:
Signed this 15th day of June, 2023

_______________________________
Margaret Ann Thompson, Principal

WITNESSES:
1. James Wilson, 123 Main St, West Palm Beach, FL
2. Dorothy Brown, 456 Oak Ave, West Palm Beach, FL

NOTARY:
State of Florida, County of Palm Beach
Sworn and subscribed before me this 15th day of June, 2023
Notary Public: Maria Garcia
Commission Number: GG123456
Commission Expires: December 31, 2026""",
        "extracted_data": {
            "principal": "Margaret Ann Thompson",
            "primary_agent": "Sarah Thompson-Martinez",
            "primary_relationship": "Daughter",
            "alternate_agent": "Michael Thompson",
            "execution_date": "2023-06-15",
            "notarized": True,
            "durable": True,
            "gifting_authority": True,
            "medicaid_planning_authority": True
        },
        "ai_analysis": "Financial POA grants daughter Sarah broad authority over finances, including Medicaid application, benefit management, and gifting for Medicaid planning. Document is durable (remains valid if Margaret becomes incapacitated). Essential for managing spend-down and facility payments."
    },
    {
        "name": "Advance Directive / Living Will",
        "category": "legal",
        "doc_type": "advance_directive",
        "content": """LIVING WILL / ADVANCE DIRECTIVE
STATE OF FLORIDA

Declaration made this 15th day of June, 2023

I, Margaret Ann Thompson, being of sound mind, willfully and voluntarily make known my desire that my dying not be artificially prolonged under the circumstances set forth below.

DECLARATION:

If at any time I am incapacitated and:
(a) I have a terminal condition, or
(b) I have an end-stage condition, or
(c) I am in a persistent vegetative state

AND my attending or treating physician and another consulting physician have determined that there is no reasonable medical probability of my recovery from such condition, I direct that life-prolonging procedures be withheld or withdrawn when the application of such procedures would serve only to prolong artificially the process of dying.

SPECIFIC INSTRUCTIONS:

1. ARTIFICIAL NUTRITION AND HYDRATION:
   [X] I DO NOT want artificial nutrition and hydration if it will only prolong the dying process
   [ ] I DO want artificial nutrition and hydration even if it only prolongs dying

2. PAIN MANAGEMENT:
   [X] I want maximum pain relief, even if it may hasten my death
   [ ] I want pain relief only if it will not hasten my death

3. CARDIOPULMONARY RESUSCITATION (CPR):
   [X] I DO NOT want CPR if I am in a terminal condition
   [ ] I DO want CPR attempted regardless of my condition

4. MECHANICAL VENTILATION:
   [X] I DO NOT want mechanical ventilation if it will only prolong dying
   [ ] I DO want mechanical ventilation regardless

5. DIALYSIS:
   [X] I DO NOT want dialysis if it will only prolong dying
   [ ] I DO want dialysis regardless

6. ANTIBIOTICS:
   [X] I want antibiotics only for comfort (e.g., to treat painful infections)
   [ ] I want all antibiotics regardless of prognosis

7. ORGAN DONATION:
   [X] I wish to donate any organs or tissues that may help others
   [ ] I do not wish to donate organs

COMFORT CARE:
I understand that this declaration does not affect the responsibility of my health care providers to provide basic comfort care. I want to receive:
- Pain medication as needed
- Hygiene care
- Emotional and spiritual support
- Companionship

PERSONAL STATEMENT:
I have lived a full life and am at peace with my mortality. I do not want my family burdened by prolonged medical interventions that will not restore my quality of life. I trust my daughter Sarah to honor these wishes.

EXECUTION:

_______________________________
Margaret Ann Thompson

WITNESSES:
We declare that the person who signed this document, or asked another to sign for her, did so in our presence, that she appears to be of sound mind and under no duress, fraud, or undue influence.

1. Witness: James Wilson
   Address: 123 Main St, West Palm Beach, FL
   
2. Witness: Dorothy Brown
   Address: 456 Oak Ave, West Palm Beach, FL

NOTARY:
State of Florida, County of Palm Beach
Sworn before me this 15th day of June, 2023
Notary Public: Maria Garcia""",
        "extracted_data": {
            "declarant": "Margaret Ann Thompson",
            "execution_date": "2023-06-15",
            "no_artificial_nutrition": True,
            "no_cpr_if_terminal": True,
            "no_mechanical_ventilation": True,
            "maximum_pain_relief": True,
            "organ_donor": True,
            "notarized": True
        },
        "ai_analysis": "Living Will clearly states Margaret's end-of-life wishes: no life-prolonging procedures if terminal, maximum comfort care, organ donation desired. Document is properly witnessed and notarized. Facility and healthcare providers should have copy on file."
    },
    {
        "name": "HIPAA Authorization Form",
        "category": "legal",
        "doc_type": "hipaa_authorization",
        "content": """AUTHORIZATION FOR RELEASE OF HEALTH INFORMATION
(HIPAA Compliant)

PATIENT INFORMATION:
Name: Margaret Ann Thompson
Date of Birth: March 15, 1942
Address: 4521 Palm Beach Lakes Blvd, West Palm Beach, FL 33401
Phone: (561) 555-4521
Social Security Number: XXX-XX-4567

I hereby authorize the following individuals to receive my protected health information:

AUTHORIZED PERSONS:

1. Sarah Thompson-Martinez (Daughter)
   Phone: (619) 555-0123
   Email: sarah.martinez@email.com
   Relationship: Daughter / Healthcare Surrogate
   
2. Michael Thompson (Son)
   Phone: (404) 555-0456
   Email: michael.thompson@email.com
   Relationship: Son / Alternate Surrogate

3. Elder Law Attorney - Jennifer Walsh, Esq.
   Phone: (561) 555-7890
   Firm: Walsh Elder Law, P.A.
   Purpose: Medicaid/VA benefits applications

INFORMATION TO BE DISCLOSED:
[X] Complete medical records
[X] Mental health records
[X] Substance abuse records (if any)
[X] HIV/AIDS related information (if any)
[X] Billing and insurance information
[X] Diagnostic test results
[X] Treatment plans and progress notes
[X] Medication lists
[X] Cognitive assessments

PURPOSE OF DISCLOSURE:
- Coordination of care
- Insurance and benefits applications (Medicaid, VA)
- Legal planning and representation
- Family caregiving and decision-making

PROVIDERS AUTHORIZED TO RELEASE INFORMATION:
- All current and former healthcare providers
- All hospitals and emergency rooms
- All pharmacies
- Medicare and insurance companies
- Social Security Administration

DURATION:
This authorization is valid from the date signed until:
[X] Revoked in writing by me or my legal representative
[ ] Specific date: _______________

PATIENT RIGHTS:
- I understand I may revoke this authorization at any time in writing
- I understand that information disclosed may be re-disclosed by the recipient
- I understand that treatment cannot be conditioned on signing this authorization
- I understand I am entitled to a copy of this authorization

SIGNATURE:

_______________________________
Margaret Ann Thompson                    Date: June 15, 2023

OR

_______________________________
Sarah Thompson-Martinez                  Date: January 28, 2026
(As Healthcare Surrogate under POA)""",
        "extracted_data": {
            "patient": "Margaret Ann Thompson",
            "authorized_persons": ["Sarah Thompson-Martinez", "Michael Thompson", "Jennifer Walsh, Esq."],
            "full_medical_records": True,
            "mental_health_included": True,
            "billing_included": True,
            "valid_until": "Revoked in writing",
            "signed_date": "2023-06-15"
        },
        "ai_analysis": "HIPAA authorization allows daughter Sarah and son Michael to access all medical records and coordinate care. Elder law attorney also authorized for benefits applications. Essential for Medicaid/VA applications and facility coordination."
    },
    {
        "name": "Birth Certificate - Margaret Thompson",
        "category": "identity",
        "doc_type": "birth_certificate",
        "content": """STATE OF FLORIDA
DEPARTMENT OF HEALTH
OFFICE OF VITAL RECORDS

CERTIFICATE OF LIVE BIRTH

CHILD'S NAME: Margaret Ann Wilson
DATE OF BIRTH: March 15, 1942
TIME OF BIRTH: 7:42 AM
SEX: Female
PLACE OF BIRTH: St. Vincent's Hospital, Jacksonville, Florida
COUNTY: Duval

MOTHER'S INFORMATION:
Name: Dorothy Mae Wilson (née Johnson)
Age at Birth: 24
Birthplace: Georgia
Residence: Jacksonville, Florida
Occupation: Homemaker

FATHER'S INFORMATION:
Name: James Robert Wilson
Age at Birth: 26
Birthplace: Florida
Residence: Jacksonville, Florida
Occupation: Railroad Worker

CERTIFICATE NUMBER: 1942-123456
DATE FILED: March 18, 1942
REGISTRAR: William H. Patterson

This is to certify that the above is a true copy or abstract of the record on file in the Office of Vital Records, Florida Department of Health.

CERTIFIED COPY ISSUED: January 10, 2026
State Registrar: [Signature]
Seal: [Official Seal of Florida]

NOTE: This certified copy is required for:
- Medicaid application (proof of citizenship)
- VA benefits application
- Social Security verification""",
        "extracted_data": {
            "full_name": "Margaret Ann Wilson",
            "date_of_birth": "1942-03-15",
            "place_of_birth": "Jacksonville, Florida",
            "mother_name": "Dorothy Mae Wilson",
            "father_name": "James Robert Wilson",
            "certificate_number": "1942-123456",
            "us_citizen": True
        },
        "ai_analysis": "Birth certificate confirms Margaret was born in Florida on March 15, 1942, establishing U.S. citizenship. Required for Medicaid application (citizenship verification) and VA benefits. Current age: 83 years."
    },
    {
        "name": "Florida Driver's License / State ID",
        "category": "identity",
        "doc_type": "state_id",
        "content": """FLORIDA DEPARTMENT OF HIGHWAY SAFETY AND MOTOR VEHICLES
IDENTIFICATION CARD

CARD TYPE: Florida Identification Card (Non-Driver)
STATUS: Valid

CARDHOLDER INFORMATION:
Name: THOMPSON, MARGARET ANN
Date of Birth: 03/15/1942
Sex: Female
Height: 5'04"
Weight: 135 lbs
Eyes: Blue
Hair: Gray

ADDRESS:
4521 Palm Beach Lakes Blvd
West Palm Beach, FL 33401

CARD DETAILS:
ID Number: T621-421-42-123-0
Issue Date: 06/15/2023
Expiration Date: 03/15/2031
Class: E (ID Card Only)

RESTRICTIONS:
- Not valid for driving (surrendered driver's license 05/2024)
- REAL ID Compliant

ORGAN DONOR: Yes

EMERGENCY CONTACT:
Sarah Thompson-Martinez
(619) 555-0123

VETERAN DESIGNATION: N/A
(Spouse of Veteran - Robert Thompson, U.S. Army)

NOTE: Driver's license was voluntarily surrendered in May 2024 due to cognitive impairment. Physician recommended cessation of driving. ID card issued for identification purposes only.""",
        "extracted_data": {
            "name": "Margaret Ann Thompson",
            "id_number": "T621-421-42-123-0",
            "date_of_birth": "1942-03-15",
            "address": "4521 Palm Beach Lakes Blvd, West Palm Beach, FL 33401",
            "expiration_date": "2031-03-15",
            "real_id_compliant": True,
            "driving_status": "Surrendered May 2024",
            "organ_donor": True
        },
        "ai_analysis": "Florida ID card (non-driver) confirms identity and residency. Driver's license was surrendered in May 2024 due to cognitive impairment - this is documented in medical records. REAL ID compliant for federal purposes. Valid until 2031."
    },
    {
        "name": "Hospital Discharge Summary",
        "category": "medical",
        "doc_type": "discharge_summary",
        "content": """PALM BEACH GENERAL HOSPITAL
DISCHARGE SUMMARY

PATIENT: Margaret Ann Thompson
MRN: 789456123
DOB: 03/15/1942 (Age 83)
ADMISSION DATE: January 28, 2026
DISCHARGE DATE: February 5, 2026
LENGTH OF STAY: 8 days
ATTENDING PHYSICIAN: Dr. Sarah Chen, MD

DISCHARGE DISPOSITION:
Memory Care Facility - Sunrise Senior Living of Palm Beach Gardens

PRINCIPAL DIAGNOSIS:
1. Alzheimer's Disease, Moderate Stage (G30.1)
2. Wandering due to dementia (F03.90)

SECONDARY DIAGNOSES:
3. Mild hypothermia, resolved (T68.XXXA)
4. Dehydration, resolved (E86.0)
5. Hypertension, controlled (I10)
6. Hypothyroidism (E03.9)
7. Type 2 Diabetes, diet-controlled (E11.9)
8. Urinary incontinence (R32)

HOSPITAL COURSE:
Mrs. Thompson was admitted on 01/28/2026 after being found wandering outside her home at 3:00 AM by a neighbor. She was confused, disoriented, and mildly hypothermic (96.2°F). She was unable to provide her name, address, or emergency contact information.

During hospitalization:
- Hypothermia resolved with warming blankets
- Dehydration treated with IV fluids
- Cognitive assessment confirmed moderate Alzheimer's (MMSE 16/30)
- Social work consulted for discharge planning
- Family meeting held on 01/30/2026 - daughter agreed to Memory Care placement
- Medicaid application initiated
- VA Survivors Pension application initiated

DISCHARGE MEDICATIONS:
1. Donepezil 10mg PO daily at bedtime (Alzheimer's)
2. Memantine 10mg PO daily (Alzheimer's)
3. Lisinopril 20mg PO daily (hypertension)
4. Levothyroxine 50mcg PO daily on empty stomach (thyroid)
5. Melatonin 3mg PO at bedtime (sleep)
6. Acetaminophen 650mg PO Q6H PRN pain

DISCHARGE INSTRUCTIONS:
1. 24-hour supervision required - patient is a fall and wandering risk
2. Secured Memory Care unit recommended
3. Medication management by facility staff
4. Regular meals and hydration monitoring
5. Structured activities program
6. Physical therapy 2x/week for strength and balance

FOLLOW-UP APPOINTMENTS:
1. PCP (Dr. Rodriguez): 2 weeks post-discharge
2. Neurology (Dr. Patel): 3 months
3. Facility physician will assume primary care

CONDITION AT DISCHARGE:
Stable. Alert but disoriented to time. Ambulatory with supervision. Eating and drinking adequately.

PROGNOSIS:
Alzheimer's disease will continue to progress. With appropriate Memory Care placement, patient can maintain quality of life and safety. Family is engaged and supportive.

DISCHARGE PLANNER: Maria Santos, MSW
DISCHARGE DATE/TIME: February 5, 2026 at 10:00 AM

_______________________________
Dr. Sarah Chen, MD
Attending Physician
Palm Beach General Hospital""",
        "extracted_data": {
            "patient": "Margaret Ann Thompson",
            "admission_date": "2026-01-28",
            "discharge_date": "2026-02-05",
            "length_of_stay": 8,
            "discharge_disposition": "Memory Care Facility",
            "facility_name": "Sunrise Senior Living of Palm Beach Gardens",
            "principal_diagnosis": "Alzheimer's Disease, Moderate Stage",
            "medications_count": 6,
            "follow_up_pcp": "2 weeks",
            "follow_up_neurology": "3 months"
        },
        "ai_analysis": "Discharge summary documents 8-day hospitalization for wandering episode. Discharged to Sunrise Senior Living Memory Care on February 5, 2026. Medicaid and VA applications initiated during hospitalization. Follow-up appointments scheduled. This document is required for facility admission and benefits applications."
    },
    {
        "name": "Nursing Assessment - Level of Care",
        "category": "medical",
        "doc_type": "nursing_assessment",
        "content": """NURSING FACILITY LEVEL OF CARE ASSESSMENT
FLORIDA AGENCY FOR HEALTH CARE ADMINISTRATION

PATIENT INFORMATION:
Name: Margaret Ann Thompson
Date of Birth: 03/15/1942
Assessment Date: February 3, 2026
Assessor: Jennifer Williams, RN, BSN
Facility: Palm Beach General Hospital

PURPOSE:
This assessment determines whether the patient meets nursing facility level of care criteria for Florida Medicaid Institutional Care Program (ICP).

SECTION A: MEDICAL CONDITIONS
Primary Diagnosis: Alzheimer's Disease, Moderate Stage
ICD-10: G30.1

Co-morbidities:
- Hypertension (I10)
- Hypothyroidism (E03.9)
- Type 2 Diabetes (E11.9)
- Urinary Incontinence (R32)
- History of falls
- Wandering behavior

SECTION B: COGNITIVE STATUS
MMSE Score: 16/30 (Moderate Impairment)
Short-term memory: Severely impaired
Long-term memory: Moderately impaired
Decision-making: Severely impaired
Orientation: Disoriented to time, partially oriented to place

SECTION C: ACTIVITIES OF DAILY LIVING (ADLs)

                        Independent  Supervision  Limited Assist  Extensive Assist  Total Depend
Bed Mobility                           X
Transfer                               X
Locomotion                             X
Dressing                                              X
Eating                                 X
Toilet Use                             X
Personal Hygiene                                      X
Bathing                                               X

ADL SCORE: 12/24 (Requires assistance with 4+ ADLs)

SECTION D: BEHAVIORAL SYMPTOMS
[X] Wandering - HIGH RISK (recent incident requiring hospitalization)
[X] Sundowning - Increased confusion in evening
[X] Repetitive questions
[X] Resistance to care - Occasional
[ ] Physical aggression
[ ] Verbal aggression
[X] Sleep disturbance

SECTION E: SKILLED NURSING NEEDS
[X] Medication management (6 medications, complex regimen)
[X] Cognitive monitoring
[X] Fall prevention program
[X] Wandering prevention (secured unit required)
[X] Nutritional monitoring (weight loss history)
[X] Incontinence care

SECTION F: LEVEL OF CARE DETERMINATION

Based on this assessment, the patient:

[X] MEETS NURSING FACILITY LEVEL OF CARE CRITERIA

Justification:
1. Moderate cognitive impairment (MMSE 16/30) requiring 24-hour supervision
2. Requires assistance with 4+ ADLs
3. High wandering risk requiring secured environment
4. Complex medication regimen requiring professional management
5. Unable to live safely in community setting

RECOMMENDED PLACEMENT:
[X] Memory Care / Dementia Special Care Unit
[ ] Skilled Nursing Facility
[ ] Assisted Living Facility

MEDICAID ICP ELIGIBILITY:
This assessment supports eligibility for Florida Medicaid Institutional Care Program (ICP) based on medical necessity.

_______________________________
Jennifer Williams, RN, BSN
Date: February 3, 2026

_______________________________
Dr. Sarah Chen, MD (Physician Certification)
Date: February 3, 2026""",
        "extracted_data": {
            "patient": "Margaret Ann Thompson",
            "assessment_date": "2026-02-03",
            "mmse_score": 16,
            "adl_score": "12/24",
            "adls_requiring_assistance": 4,
            "wandering_risk": "High",
            "meets_nursing_facility_criteria": True,
            "recommended_placement": "Memory Care",
            "medicaid_icp_eligible": True
        },
        "ai_analysis": "Nursing assessment confirms Margaret meets Florida Medicaid ICP nursing facility level of care criteria. Key factors: MMSE 16/30, requires assistance with 4+ ADLs, high wandering risk, complex medication needs. This document is REQUIRED for Medicaid ICP application."
    },
    {
        "name": "Physical Therapy Evaluation",
        "category": "medical",
        "doc_type": "pt_evaluation",
        "content": """PHYSICAL THERAPY EVALUATION
PALM BEACH GENERAL HOSPITAL

PATIENT: Margaret Ann Thompson
DOB: 03/15/1942
DATE OF EVALUATION: January 30, 2026
EVALUATING THERAPIST: Robert Martinez, PT, DPT
REFERRING PHYSICIAN: Dr. Sarah Chen, MD
DIAGNOSIS: Alzheimer's Disease with gait instability

REASON FOR REFERRAL:
Evaluate mobility, balance, and fall risk following hospital admission for wandering episode.

PATIENT HISTORY:
83-year-old female with moderate Alzheimer's disease. History of one fall at home in April 2025 (no injury). Found wandering outside at 3 AM on 01/28/2026. Lives alone (unsafe). Daughter reports progressive decline in mobility over past year.

PRIOR LEVEL OF FUNCTION:
- Ambulated independently in home
- Used no assistive device
- Managed stairs with rail
- No formal exercise program

OBJECTIVE FINDINGS:

RANGE OF MOTION:
- Lower extremities: Within functional limits
- Upper extremities: Within functional limits
- Cervical spine: Mildly limited rotation

STRENGTH (Manual Muscle Testing):
- Hip flexors: 4/5 bilateral
- Knee extensors: 4/5 bilateral
- Ankle dorsiflexors: 4/5 bilateral
- Overall: Mild generalized weakness

BALANCE ASSESSMENT:
- Berg Balance Scale: 38/56 (Moderate fall risk)
- Timed Up and Go (TUG): 16 seconds (Elevated fall risk)
- Single leg stance: Unable to perform safely
- Tandem stance: 5 seconds with loss of balance

GAIT ANALYSIS:
- Gait pattern: Slow, shuffling, reduced arm swing
- Step length: Shortened bilateral
- Gait speed: 0.6 m/s (below normal)
- Assistive device: None currently, RECOMMENDED
- Supervision required: YES

FUNCTIONAL MOBILITY:
- Bed mobility: Supervision for safety
- Transfers: Supervision for safety
- Ambulation: Supervision required, moderate fall risk
- Stairs: Not assessed (not safe)

COGNITIVE IMPACT ON MOBILITY:
Patient has difficulty following multi-step commands. Requires frequent cueing for safety. Does not recognize environmental hazards. Impulsive movements increase fall risk.

FALL RISK ASSESSMENT:
[X] HIGH FALL RISK

Risk Factors:
- Cognitive impairment (MMSE 16/30)
- Balance deficits (Berg 38/56)
- Gait abnormalities
- History of falls
- Wandering behavior
- Impaired safety awareness

ASSESSMENT:
Margaret Thompson presents with moderate mobility impairments secondary to Alzheimer's disease and age-related deconditioning. She demonstrates elevated fall risk due to balance deficits, gait abnormalities, and cognitive impairment affecting safety awareness.

GOALS (2-week):
1. Improve Berg Balance Scale to 42/56
2. Improve TUG to 14 seconds
3. Ambulate 150 feet with supervision and rolling walker
4. Caregiver education on fall prevention

PLAN:
- PT 2x/week for 2 weeks during hospitalization
- Balance training exercises
- Gait training with rolling walker
- Caregiver/facility staff education
- Recommend continued PT at Memory Care facility

EQUIPMENT RECOMMENDATIONS:
1. Rolling walker (4-wheeled) for ambulation
2. Non-skid footwear
3. Bed/chair alarms for wandering prevention
4. Hip protectors (optional)

_______________________________
Robert Martinez, PT, DPT
License #: PT12345
Date: January 30, 2026""",
        "extracted_data": {
            "patient": "Margaret Ann Thompson",
            "evaluation_date": "2026-01-30",
            "berg_balance_score": 38,
            "tug_time_seconds": 16,
            "gait_speed": 0.6,
            "fall_risk": "High",
            "assistive_device_recommended": "Rolling walker",
            "supervision_required": True,
            "pt_frequency": "2x/week"
        },
        "ai_analysis": "PT evaluation documents high fall risk with Berg Balance Score 38/56 and TUG 16 seconds. Cognitive impairment significantly impacts mobility safety. Rolling walker recommended. Requires supervision for all mobility. This supports need for 24-hour care in Memory Care facility."
    },
    {
        "name": "Occupational Therapy Evaluation",
        "category": "medical",
        "doc_type": "ot_evaluation",
        "content": """OCCUPATIONAL THERAPY EVALUATION
PALM BEACH GENERAL HOSPITAL

PATIENT: Margaret Ann Thompson
DOB: 03/15/1942
DATE OF EVALUATION: January 30, 2026
EVALUATING THERAPIST: Amanda Chen, OTR/L
REFERRING PHYSICIAN: Dr. Sarah Chen, MD
DIAGNOSIS: Alzheimer's Disease, Moderate Stage

REASON FOR REFERRAL:
Evaluate ADL function and cognitive-functional status for discharge planning.

OCCUPATIONAL PROFILE:
Margaret is an 83-year-old widow who lived alone until this hospitalization. She was a retired elementary school teacher. Enjoys gardening, reading (no longer able), and spending time with grandchildren. Daughter Sarah is primary family contact (lives in California).

PRIOR LEVEL OF FUNCTION (per daughter):
- 6 months ago: Independent with basic ADLs, needed reminders for medications
- 3 months ago: Needed help with bathing, dressing; forgetting to eat
- Current: Requires assistance with most ADLs

COGNITIVE-FUNCTIONAL ASSESSMENT:

ALLEN COGNITIVE LEVEL SCREEN (ACLS):
Score: 3.8 (out of 6.0)
Interpretation: Manual Actions Level
- Can perform familiar, repetitive tasks with setup
- Unable to problem-solve or adapt to new situations
- Requires 24-hour supervision
- Cannot live independently

EXECUTIVE FUNCTION:
- Sequencing: Severely impaired (cannot sequence dressing)
- Problem-solving: Severely impaired
- Safety awareness: Severely impaired
- Judgment: Severely impaired

ADL PERFORMANCE ASSESSMENT:

BATHING:
- Current: Requires moderate assistance
- Issues: Forgets steps, water temperature judgment impaired
- Safety concern: HIGH (drowning, burns)

DRESSING:
- Current: Requires moderate assistance
- Issues: Cannot sequence, chooses inappropriate clothing
- Needs: Clothing laid out, verbal cues throughout

GROOMING:
- Current: Requires setup and verbal cues
- Issues: Forgets to brush teeth, comb hair
- Can complete with cueing

TOILETING:
- Current: Requires reminders and supervision
- Issues: Forgets location of bathroom, occasional accidents
- Incontinence: Urinary (occasional)

FEEDING:
- Current: Independent with setup
- Issues: Forgets to eat if not prompted, eats slowly
- Nutrition concern: Weight loss (5 lbs in 6 months)

MEDICATION MANAGEMENT:
- Current: UNABLE - requires complete management
- Issues: Cannot remember if taken, takes wrong doses
- Safety concern: CRITICAL

FUNCTIONAL COGNITION:
- Telephone use: Can answer, cannot dial
- Money management: Unable
- Meal preparation: Unable (safety concern with stove)
- Housekeeping: Unable
- Shopping: Unable
- Transportation: Unable (no longer drives)

HOME SAFETY ASSESSMENT (reported):
- Stove left on multiple times
- Front door left unlocked
- Wandering outside at night
- Medications mismanaged
- CONCLUSION: Home is NOT SAFE for independent living

ASSESSMENT:
Margaret Thompson demonstrates significant functional impairment secondary to moderate Alzheimer's disease. ACLS score of 3.8 indicates she requires 24-hour supervision and cannot live independently. She requires assistance with bathing, dressing, and medication management. Safety awareness is severely impaired.

RECOMMENDATIONS:
1. 24-hour supervised care (Memory Care facility)
2. Structured daily routine
3. Simplified environment with visual cues
4. Medication management by trained staff
5. Supervised bathing with safety equipment
6. Clothing laid out daily
7. Meal supervision and prompting
8. Meaningful activities program (gardening, music)

DISCHARGE RECOMMENDATION:
Patient requires Memory Care level of care. Not safe to return home alone. Recommend facility with:
- Secured unit (wandering prevention)
- Structured activities program
- 24-hour nursing supervision
- Medication management

_______________________________
Amanda Chen, OTR/L
License #: OT98765
Date: January 30, 2026""",
        "extracted_data": {
            "patient": "Margaret Ann Thompson",
            "evaluation_date": "2026-01-30",
            "acls_score": 3.8,
            "acls_interpretation": "Manual Actions Level - requires 24-hour supervision",
            "bathing": "Moderate assistance",
            "dressing": "Moderate assistance",
            "toileting": "Supervision and reminders",
            "feeding": "Independent with setup",
            "medication_management": "Unable",
            "home_safety": "Not safe for independent living",
            "recommended_care_level": "Memory Care"
        },
        "ai_analysis": "OT evaluation confirms Margaret cannot live independently. ACLS 3.8 indicates need for 24-hour supervision. Requires assistance with bathing, dressing, and complete medication management. Home safety assessment documents multiple hazards. Strongly supports Memory Care placement and Medicaid ICP eligibility."
    },
    {
        "name": "VA Form 21-2680 - Examination for Housebound Status",
        "category": "veteran",
        "doc_type": "va_form_21_2680",
        "content": """DEPARTMENT OF VETERANS AFFAIRS
EXAMINATION FOR HOUSEBOUND STATUS OR PERMANENT NEED FOR
REGULAR AID AND ATTENDANCE

VA FORM 21-2680

SECTION I - VETERAN/CLAIMANT INFORMATION
Name of Veteran: Robert James Thompson (Deceased)
VA File Number: 12345678
Name of Claimant: Margaret Ann Thompson (Surviving Spouse)
Relationship: Widow
Date of Birth: March 15, 1942
Social Security Number: XXX-XX-4567

SECTION II - DIAGNOSES
List all diagnoses affecting the claimant's need for aid and attendance:

1. Alzheimer's Disease, Moderate Stage (G30.1)
   - Duration: 2+ years (diagnosed May 2024)
   - Prognosis: Progressive, no cure

2. Urinary Incontinence (R32)
   - Duration: 3 months
   - Prognosis: Chronic

3. Hypertension (I10)
   - Duration: 15+ years
   - Prognosis: Controlled with medication

4. Hypothyroidism (E03.9)
   - Duration: 10+ years
   - Prognosis: Controlled with medication

SECTION III - FUNCTIONAL ASSESSMENT

A. Does the claimant require the regular aid and attendance of another person?
[X] YES  [ ] NO

B. Specific limitations requiring aid and attendance:

1. BATHING: [X] Requires assistance
   Details: Cannot safely bathe alone due to cognitive impairment. Does not recognize water temperature dangers. Forgets bathing steps.

2. DRESSING: [X] Requires assistance
   Details: Cannot sequence dressing. Chooses inappropriate clothing. Needs clothes laid out and verbal cues.

3. TOILETING: [X] Requires supervision/assistance
   Details: Forgets bathroom location. Occasional incontinence. Needs reminders.

4. EATING: [X] Requires supervision
   Details: Forgets to eat without prompting. Weight loss documented.

5. MEDICATION MANAGEMENT: [X] Unable to self-manage
   Details: Cannot remember medications. Has taken wrong doses. Requires complete management.

6. PROTECTION FROM HAZARDS: [X] Unable to protect self
   Details: Wanders at night (found outside at 3 AM). Left stove on. Does not recognize dangers. Requires 24-hour supervision.

C. Is the claimant blind or nearly blind? [ ] YES [X] NO

D. Is the claimant bedridden? [ ] YES [X] NO

E. Can the claimant travel beyond the home without assistance?
[ ] YES [X] NO
Details: Cannot drive (license surrendered). Gets lost easily. Cannot use public transportation.

SECTION IV - MENTAL STATUS
MMSE Score: 16/30 (Moderate Cognitive Impairment)
Orientation: Disoriented to time, partially oriented to place
Memory: Severely impaired short-term, moderately impaired long-term
Judgment: Severely impaired
Insight: Limited awareness of deficits

SECTION V - CERTIFICATION

I certify that I have examined the above-named claimant and that the information provided is accurate based on my professional assessment.

Examining Physician: Dr. Sarah Chen, MD
Medical License #: FL-MD-123456
Address: Palm Beach General Hospital
         2000 45th Street, West Palm Beach, FL 33407
Phone: (561) 555-1000
Date of Examination: February 3, 2026

_______________________________
Physician Signature

SECTION VI - CONCLUSION

Based on this examination, the claimant:
[X] REQUIRES the regular aid and attendance of another person
[ ] Is housebound
[ ] Neither

This claimant meets the criteria for VA Aid and Attendance benefits due to:
- Cognitive impairment requiring 24-hour supervision
- Inability to perform 2+ ADLs without assistance
- Inability to protect self from daily hazards

_______________________________
Dr. Sarah Chen, MD
Date: February 3, 2026""",
        "extracted_data": {
            "claimant": "Margaret Ann Thompson",
            "veteran": "Robert James Thompson (Deceased)",
            "relationship": "Surviving Spouse",
            "examination_date": "2026-02-03",
            "requires_aid_attendance": True,
            "bathing_assistance": True,
            "dressing_assistance": True,
            "toileting_assistance": True,
            "medication_management": "Unable",
            "protection_from_hazards": "Unable",
            "mmse_score": 16,
            "examining_physician": "Dr. Sarah Chen, MD"
        },
        "ai_analysis": "VA Form 21-2680 documents Margaret's need for Aid and Attendance benefits. Physician certifies she requires assistance with bathing, dressing, toileting, and cannot protect herself from hazards. This completed form supports VA Survivors Pension with A&A ($1,432/month). Submit with VA Form 21-534EZ."
    },
    {
        "name": "60-Month Look-Back Analysis - Detailed",
        "category": "financial",
        "doc_type": "lookback_analysis",
        "content": """MEDICAID 60-MONTH LOOK-BACK ANALYSIS
Prepared by CareNav AI
Date: February 4, 2026

APPLICANT: Margaret Ann Thompson
DOB: March 15, 1942
LOOK-BACK PERIOD: February 2021 - February 2026 (60 months)

═══════════════════════════════════════════════════════════════
EXECUTIVE SUMMARY
═══════════════════════════════════════════════════════════════

FINDING: NO DISQUALIFYING TRANSFERS IDENTIFIED

Margaret Thompson's financial records for the 60-month look-back period show no gifts, transfers, or asset dispositions that would trigger a Medicaid penalty period.

═══════════════════════════════════════════════════════════════
FLORIDA MEDICAID TRANSFER RULES
═══════════════════════════════════════════════════════════════

Under Florida Medicaid rules (42 U.S.C. § 1396p):
- Any transfer of assets for less than fair market value within 60 months of Medicaid application may result in a penalty period
- Penalty period = Value of transfer ÷ Average monthly nursing home cost ($9,703 in 2026)
- Certain transfers are exempt (spouse, disabled child, etc.)

═══════════════════════════════════════════════════════════════
YEAR-BY-YEAR ANALYSIS
═══════════════════════════════════════════════════════════════

2021 (Feb-Dec):
─────────────────────────────────────────────────────────────
Income:
- Social Security: $1,650/month × 11 = $18,150
- Robert's Pension: $450/month × 11 = $4,950
- Total Income: $23,100

Major Expenses:
- Property taxes: $3,200
- Homeowner's insurance: $2,400
- Utilities: $2,640
- Medical (Medicare copays): $1,200
- Living expenses: $12,000

Transfers/Gifts: NONE
Asset Sales: NONE
Account Closures: NONE

End of Year Assets:
- Checking: $4,200
- Savings: $8,500
- Home equity: ~$180,000 (exempt)
- Vehicle: $8,000

2022 (Full Year):
─────────────────────────────────────────────────────────────
Income:
- Social Security: $1,700/month × 12 = $20,400
- Robert's Pension: $450/month × 12 = $5,400
- Total Income: $25,800

Major Expenses:
- Property taxes: $3,400
- Homeowner's insurance: $2,600
- Utilities: $2,880
- Medical: $1,800
- Home repairs (roof): $4,500
- Living expenses: $13,000

Transfers/Gifts: NONE
Asset Sales: NONE

End of Year Assets:
- Checking: $3,800
- Savings: $6,200
- Home equity: ~$185,000 (exempt)
- Vehicle: $6,500

2023 (Full Year):
─────────────────────────────────────────────────────────────
Income:
- Social Security: $1,750/month × 12 = $21,000
- Robert's Pension: $450/month × 12 = $5,400
- Total Income: $26,400

Major Expenses:
- Property taxes: $3,600
- Homeowner's insurance: $2,800
- Utilities: $3,000
- Medical (increased due to diagnosis): $3,500
- Alzheimer's medications: $1,200
- Living expenses: $14,000

Transfers/Gifts: NONE
Asset Sales: Vehicle sold for $6,000 (fair market value)

End of Year Assets:
- Checking: $3,200
- Savings: $5,000
- Home equity: ~$190,000 (exempt)
- Vehicle: NONE (sold, no longer driving)

NOTE: Vehicle sale at fair market value is NOT a disqualifying transfer.

2024 (Full Year):
─────────────────────────────────────────────────────────────
Income:
- Social Security: $1,800/month × 12 = $21,600
- Robert's Pension: $450/month × 12 = $5,400
- Total Income: $27,000

Major Expenses:
- Property taxes: $3,800
- Homeowner's insurance: $3,000
- Utilities: $3,200
- Medical/medications: $4,500
- In-home caregiver (part-time): $6,000
- Living expenses: $12,000

Transfers/Gifts: NONE
Asset Sales: NONE

End of Year Assets:
- Checking: $2,500
- Savings: $3,500
- Home equity: ~$195,000 (exempt)

NOTE: In-home caregiver expenses are legitimate care costs, not transfers.

2025 (Full Year):
─────────────────────────────────────────────────────────────
Income:
- Social Security: $1,850/month × 12 = $22,200
- Robert's Pension: $450/month × 12 = $5,400
- Total Income: $27,600

Major Expenses:
- Property taxes: $4,000
- Homeowner's insurance: $3,200
- Utilities: $3,400
- Medical/medications: $5,200
- In-home caregiver (increased): $9,600
- Living expenses: $10,000

Transfers/Gifts: NONE
Asset Sales: NONE

End of Year Assets:
- Checking: $1,800
- Savings: $2,000
- Home equity: ~$200,000 (exempt)

2026 (Jan-Feb):
─────────────────────────────────────────────────────────────
Income:
- Social Security: $1,850 × 2 = $3,700
- Robert's Pension: $450 × 2 = $900
- Total Income: $4,600

Major Expenses:
- Hospital copays: $500
- Medications: $200

Transfers/Gifts: NONE

Current Assets (as of Feb 4, 2026):
- Checking: $1,500
- Savings: $1,500
- Home equity: ~$200,000 (exempt)
- TOTAL COUNTABLE: $3,000

═══════════════════════════════════════════════════════════════
DETAILED TRANSFER ANALYSIS
═══════════════════════════════════════════════════════════════

GIFTS TO FAMILY MEMBERS: NONE
- No birthday gifts over $50
- No holiday gifts over $50
- No cash gifts to children or grandchildren
- No payments for others' expenses

CHARITABLE DONATIONS: Minimal
- Annual church donations: ~$500/year
- Small charitable gifts are not considered disqualifying transfers

LOANS TO OTHERS: NONE
- No loans to family members
- No promissory notes

TRUST TRANSFERS: NONE
- No assets placed in trust
- No irrevocable trusts created

ANNUITY PURCHASES: NONE
- No annuities purchased during look-back period

LIFE ESTATE DEEDS: NONE
- Home remains in Margaret's name only
- No life estate created

JOINT ACCOUNT CHANGES: NONE
- No accounts converted to joint ownership
- No beneficiary changes that constitute transfers

═══════════════════════════════════════════════════════════════
HOME EQUITY ANALYSIS
═══════════════════════════════════════════════════════════════

Property: 4521 Palm Beach Lakes Blvd, West Palm Beach, FL 33401
Current Value: ~$200,000
Mortgage: NONE (paid off)
Home Equity: $200,000

FLORIDA HOMESTEAD EXEMPTION:
- Home is EXEMPT from Medicaid asset calculation
- No equity limit in Florida for Medicaid purposes
- Home remains exempt as long as applicant intends to return
  OR spouse resides there

ESTATE RECOVERY:
- Florida may seek recovery from estate after death
- Home may be subject to Medicaid lien
- Consider: Transfer to daughter after Medicaid approval
  (would not affect current eligibility)

═══════════════════════════════════════════════════════════════
CONCLUSION
═══════════════════════════════════════════════════════════════

LOOK-BACK ANALYSIS RESULT: CLEAR

No disqualifying transfers identified during the 60-month look-back period. Margaret Thompson's asset decline from ~$12,700 (Feb 2021) to $3,000 (Feb 2026) is fully explained by:

1. Legitimate living expenses
2. Medical costs and medications
3. In-home caregiver expenses (documented)
4. Property maintenance
5. Vehicle sale at fair market value

MEDICAID ELIGIBILITY IMPACT:
- No penalty period will be imposed
- Application can proceed immediately
- Current assets ($3,000) require $1,000 spend-down

RECOMMENDATIONS:
1. Proceed with Medicaid ICP application
2. Spend down $1,000 on allowable expenses
3. Retain all receipts for verification
4. Home will remain exempt

Report Generated by CareNav AI
Date: February 4, 2026""",
        "extracted_data": {
            "applicant": "Margaret Ann Thompson",
            "lookback_period": "February 2021 - February 2026",
            "lookback_months": 60,
            "disqualifying_transfers": 0,
            "penalty_period": 0,
            "gifts_identified": 0,
            "trust_transfers": 0,
            "home_equity": 200000,
            "home_exempt": True,
            "current_countable_assets": 3000,
            "spend_down_needed": 1000,
            "result": "CLEAR - No penalty"
        },
        "ai_analysis": "Comprehensive 60-month look-back analysis shows NO disqualifying transfers. Asset decline from $12,700 to $3,000 is fully explained by legitimate expenses. No penalty period will be imposed. Medicaid application can proceed immediately with $1,000 spend-down."
    },
    {
        "name": "Prescription Drug Cost Analysis",
        "category": "medical",
        "doc_type": "prescription_analysis",
        "content": """PRESCRIPTION DRUG COST ANALYSIS
Prepared by CareNav AI
Date: February 4, 2026

PATIENT: Margaret Ann Thompson
DOB: March 15, 1942
PHARMACY: CVS Pharmacy #4521, West Palm Beach, FL
INSURANCE: Medicare Part D (SilverScript Choice)

═══════════════════════════════════════════════════════════════
CURRENT MEDICATIONS
═══════════════════════════════════════════════════════════════

1. DONEPEZIL 10mg (Aricept)
   Purpose: Alzheimer's disease
   Dosage: 1 tablet daily at bedtime
   Quantity: 30 tablets/month
   
   Costs:
   - Retail price: $485.00/month
   - Medicare Part D copay: $47.00/month
   - With Extra Help: $0.00/month
   
   Notes: Brand name. Generic available but patient stable on brand.

2. MEMANTINE 10mg (Namenda)
   Purpose: Alzheimer's disease (moderate-severe)
   Dosage: 1 tablet daily
   Quantity: 30 tablets/month
   
   Costs:
   - Retail price: $412.00/month
   - Medicare Part D copay: $42.00/month
   - With Extra Help: $0.00/month
   
   Notes: Added March 2025 when MMSE dropped below 20.

3. LISINOPRIL 20mg
   Purpose: Hypertension
   Dosage: 1 tablet daily
   Quantity: 30 tablets/month
   
   Costs:
   - Retail price: $15.00/month
   - Medicare Part D copay: $3.00/month
   - With Extra Help: $0.00/month
   
   Notes: Generic. Well-controlled blood pressure.

4. LEVOTHYROXINE 50mcg (Synthroid)
   Purpose: Hypothyroidism
   Dosage: 1 tablet daily on empty stomach
   Quantity: 30 tablets/month
   
   Costs:
   - Retail price: $28.00/month
   - Medicare Part D copay: $4.00/month
   - With Extra Help: $0.00/month
   
   Notes: Generic. Stable thyroid levels.

5. MELATONIN 3mg (OTC)
   Purpose: Sleep regulation
   Dosage: 1 tablet at bedtime
   Quantity: 30 tablets/month
   
   Costs:
   - Retail price: $8.00/month
   - Not covered by Medicare (OTC)
   - Patient pays: $8.00/month

6. ACETAMINOPHEN 650mg (Tylenol)
   Purpose: Pain relief (PRN)
   Dosage: As needed, max 4x daily
   Quantity: ~60 tablets/month
   
   Costs:
   - Retail price: $12.00/month
   - Not covered by Medicare (OTC)
   - Patient pays: $12.00/month

═══════════════════════════════════════════════════════════════
MONTHLY COST SUMMARY
═══════════════════════════════════════════════════════════════

                          Retail    Part D    With Extra Help
Donepezil 10mg           $485.00    $47.00         $0.00
Memantine 10mg           $412.00    $42.00         $0.00
Lisinopril 20mg           $15.00     $3.00         $0.00
Levothyroxine 50mcg       $28.00     $4.00         $0.00
Melatonin 3mg (OTC)        $8.00     $8.00         $8.00
Acetaminophen (OTC)       $12.00    $12.00        $12.00
─────────────────────────────────────────────────────────────
TOTAL MONTHLY:           $960.00   $116.00        $20.00

ANNUAL COSTS:
- Without insurance: $11,520/year
- With Medicare Part D: $1,392/year
- With Extra Help (LIS): $240/year

═══════════════════════════════════════════════════════════════
MEDICARE EXTRA HELP (LOW-INCOME SUBSIDY)
═══════════════════════════════════════════════════════════════

Margaret QUALIFIES for Medicare Extra Help based on:
- Income: $2,300/month (below $1,903 individual limit for full subsidy)
- Assets: $3,000 (below $17,220 limit)

EXTRA HELP BENEFITS:
- $0 copay for generic drugs
- $0 copay for brand-name drugs
- No deductible
- No coverage gap ("donut hole")

APPLICATION STATUS: Automatic enrollment pending with Medicaid approval

═══════════════════════════════════════════════════════════════
FACILITY MEDICATION MANAGEMENT
═══════════════════════════════════════════════════════════════

When Margaret moves to Memory Care:

MEDICATION ADMINISTRATION:
- All medications will be administered by facility staff
- Medications stored in locked medication room
- Electronic medication administration records (eMAR)
- Pharmacy delivers medications in unit-dose packaging

COST CHANGES:
- Facility may use contracted pharmacy
- Medicare Part D continues to cover prescription costs
- Facility cannot charge extra for medication administration
  (included in daily rate)

MEDICATION REVIEW:
- Facility physician will review all medications
- Potential simplification of regimen
- Consider: Combination Namzaric (donepezil + memantine)
  - Would reduce pill burden
  - Similar cost with Part D

═══════════════════════════════════════════════════════════════
RECOMMENDATIONS
═══════════════════════════════════════════════════════════════

1. APPLY FOR EXTRA HELP
   - Will reduce monthly drug costs from $116 to $20
   - Application submitted with Medicaid
   - Retroactive to Medicaid approval date

2. CONSIDER GENERIC ALTERNATIVES
   - Donepezil: Already generic available
   - Memantine: Generic available
   - Discuss with physician if brand necessary

3. MEDICATION SYNCHRONIZATION
   - All prescriptions filled on same day each month
   - Reduces pharmacy trips
   - Easier for facility management

4. 90-DAY SUPPLY
   - Consider mail-order for maintenance medications
   - Lower copays for 90-day supply
   - Not applicable once in facility (30-day max)

═══════════════════════════════════════════════════════════════
DRUG INTERACTION CHECK
═══════════════════════════════════════════════════════════════

No significant drug interactions identified.

Minor considerations:
- Donepezil may cause bradycardia (monitor with lisinopril)
- Take levothyroxine on empty stomach, 30-60 min before other meds
- Melatonin may enhance sedation (appropriate for sleep)

Report Generated by CareNav AI
Pharmacy Data Source: CVS Caremark
Date: February 4, 2026""",
        "extracted_data": {
            "patient": "Margaret Ann Thompson",
            "total_medications": 6,
            "prescription_medications": 4,
            "otc_medications": 2,
            "monthly_cost_retail": 960.00,
            "monthly_cost_part_d": 116.00,
            "monthly_cost_extra_help": 20.00,
            "annual_savings_extra_help": 1152.00,
            "qualifies_extra_help": True,
            "drug_interactions": "None significant"
        },
        "ai_analysis": "Prescription analysis shows $116/month current cost with Medicare Part D. Margaret qualifies for Extra Help (Low-Income Subsidy) which will reduce costs to $20/month. Alzheimer's medications (Donepezil, Memantine) are the most expensive. No significant drug interactions. Facility will manage all medications."
    },
    {
        "name": "Facility Admission Checklist",
        "category": "planning",
        "doc_type": "admission_checklist",
        "content": """MEMORY CARE FACILITY ADMISSION CHECKLIST
Prepared by CareNav AI for Margaret Thompson
Target Admission Date: February 5, 2026
Facility: Sunrise Senior Living of Palm Beach Gardens

═══════════════════════════════════════════════════════════════
REQUIRED DOCUMENTS - MUST HAVE BEFORE ADMISSION
═══════════════════════════════════════════════════════════════

IDENTIFICATION:
[X] Photo ID (Florida ID Card)
[X] Social Security Card (copy)
[X] Medicare Card (copy)
[X] Birth Certificate (copy)

LEGAL DOCUMENTS:
[X] Durable Power of Attorney - Healthcare
[X] Durable Power of Attorney - Financial
[X] Advance Directive / Living Will
[X] HIPAA Authorization Form
[ ] DNR Order (if applicable) - Discuss with family

MEDICAL RECORDS:
[X] Hospital Discharge Summary
[X] Current Medication List
[X] Physician Orders for admission
[X] Recent lab results (within 30 days)
[X] TB test results (within 12 months)
[X] COVID-19 vaccination record
[X] Physical Therapy evaluation
[X] Occupational Therapy evaluation
[X] Cognitive Assessment (MMSE)
[X] Nursing Assessment / Level of Care

FINANCIAL DOCUMENTS:
[X] Proof of income (Social Security statement)
[X] Bank statements (last 3 months)
[X] Medicaid application receipt
[X] VA benefits application receipt
[ ] Private pay agreement (for interim period)

INSURANCE:
[X] Medicare card
[X] Medicare Part D card
[X] Medicaid pending letter
[ ] Long-term care insurance (N/A - none)

═══════════════════════════════════════════════════════════════
PERSONAL ITEMS TO BRING
═══════════════════════════════════════════════════════════════

CLOTHING (Label all items with name):
[ ] 7 daytime outfits (comfortable, easy to put on)
[ ] 7 nightgowns/pajamas
[ ] 2 sweaters or cardigans
[ ] 7 sets of undergarments
[ ] 7 pairs of socks
[ ] 2 pairs of non-skid shoes/slippers
[ ] 1 robe
[ ] 1 jacket/coat

TOILETRIES:
[ ] Toothbrush and toothpaste
[ ] Hairbrush/comb
[ ] Shampoo and conditioner
[ ] Body wash/soap
[ ] Deodorant
[ ] Moisturizer
[ ] Denture supplies (if applicable)
[ ] Hearing aid supplies (if applicable)
[ ] Eyeglasses (with case)

COMFORT ITEMS:
[ ] Family photos (framed, 3-5)
[ ] Favorite blanket or pillow
[ ] Small radio or music player
[ ] Books or magazines (large print)
[ ] Stuffed animal or comfort object
[ ] Religious items (Bible, rosary, etc.)

MEDICAL EQUIPMENT:
[X] Rolling walker (provided by PT)
[ ] Eyeglasses
[ ] Hearing aids (if applicable)
[ ] Dentures (if applicable)
[ ] CPAP machine (if applicable) - N/A

DO NOT BRING:
- Valuables or expensive jewelry
- Large amounts of cash (facility has petty cash)
- Medications (facility will order from pharmacy)
- Electric blankets or heating pads
- Candles or incense
- Sharp objects (scissors, knives)
- Alcohol

═══════════════════════════════════════════════════════════════
FINANCIAL ARRANGEMENTS
═══════════════════════════════════════════════════════════════

FACILITY COSTS:
- Memory Care daily rate: $250/day ($7,500/month)
- Includes: Room, meals, activities, basic care
- Additional charges: Incontinence supplies (~$150/month)

PAYMENT PLAN (Pending Medicaid Approval):

MONTH 1-2 (Private Pay Period):
- Estimated Medicaid approval: 45-60 days
- Private pay required: ~$15,000-$20,000
- Source: Spend-down of assets + income

AFTER MEDICAID APPROVAL:
- Medicaid pays facility directly
- Patient responsibility: ~$2,100/month
  (Income minus $130 personal needs allowance)
- VA A&A ($1,432/month) can offset patient responsibility

NET MONTHLY COST TO FAMILY: $0
(Medicaid + VA covers all costs)

═══════════════════════════════════════════════════════════════
ADMISSION DAY SCHEDULE
═══════════════════════════════════════════════════════════════

February 5, 2026:

10:00 AM - Arrive at Sunrise Senior Living
           Address: 3000 Gardens Parkway
                    Palm Beach Gardens, FL 33410

10:15 AM - Meet with Admissions Coordinator
           - Sign admission agreement
           - Review policies and procedures
           - Provide emergency contacts

11:00 AM - Nursing Assessment
           - Vital signs
           - Medication reconciliation
           - Care plan discussion

11:30 AM - Room orientation
           - Unpack belongings
           - Meet roommate (if applicable)
           - Familiarize with call system

12:00 PM - Lunch in dining room
           - Meet other residents
           - Assess dining needs

1:00 PM  - Activities orientation
           - Tour of facility
           - Introduction to activity program

2:00 PM  - Family meeting with care team
           - Discuss care preferences
           - Set communication expectations
           - Schedule first care conference (30 days)

3:00 PM  - Family departure
           - Short, positive goodbye
           - Staff will redirect and engage Margaret

═══════════════════════════════════════════════════════════════
FAMILY RESPONSIBILITIES
═══════════════════════════════════════════════════════════════

SARAH (Daughter - POA):
[ ] Sign admission agreement
[ ] Provide payment for first month
[ ] Complete Medicaid application follow-up
[ ] Complete VA application follow-up
[ ] Set up automatic payment from Margaret's account
[ ] Notify Social Security of address change
[ ] Notify Medicare of address change
[ ] Cancel home utilities (after home decision)
[ ] Arrange home maintenance/sale

ONGOING:
[ ] Visit regularly (recommended: 2-3x/week initially)
[ ] Attend care conferences (monthly for first 90 days)
[ ] Communicate concerns to Director of Nursing
[ ] Keep facility updated on family contact info
[ ] Replenish clothing and toiletries as needed

═══════════════════════════════════════════════════════════════
IMPORTANT CONTACTS
═══════════════════════════════════════════════════════════════

FACILITY:
Sunrise Senior Living of Palm Beach Gardens
Phone: (561) 555-2000
Director of Nursing: Jennifer Adams, RN
Admissions: Maria Santos

FAMILY:
Sarah Thompson-Martinez (Daughter/POA)
Phone: (619) 555-0123
Email: sarah.martinez@email.com

Michael Thompson (Son/Alternate)
Phone: (404) 555-0456

MEDICAL:
Dr. Rodriguez (PCP): (561) 555-3000
Dr. Patel (Neurology): (561) 555-4000
Facility Physician: Dr. Williams

LEGAL/FINANCIAL:
Elder Law Attorney: Jennifer Walsh, Esq.
Phone: (561) 555-7890

VA Regional Office: 1-800-827-1000
Medicaid (ACCESS Florida): 1-866-762-2237

Checklist Generated by CareNav AI
Date: February 4, 2026""",
        "extracted_data": {
            "patient": "Margaret Ann Thompson",
            "facility": "Sunrise Senior Living of Palm Beach Gardens",
            "admission_date": "2026-02-05",
            "daily_rate": 250,
            "monthly_rate": 7500,
            "documents_complete": 18,
            "documents_pending": 2,
            "private_pay_estimate": "15000-20000",
            "net_monthly_cost_after_benefits": 0
        },
        "ai_analysis": "Comprehensive admission checklist for Memory Care placement. Most required documents are complete. Private pay of $15-20K needed during Medicaid processing (45-60 days). After Medicaid and VA approval, net cost to family will be $0. Admission scheduled for February 5, 2026."
    },
    {
        "name": "Florida Medicaid ICP Rules & Regulations",
        "category": "ai_analysis",
        "doc_type": "medicaid_rules",
        "content": """FLORIDA MEDICAID INSTITUTIONAL CARE PROGRAM (ICP)
COMPREHENSIVE RULES AND REGULATIONS GUIDE
Prepared by CareNav AI for Decision Support

═══════════════════════════════════════════════════════════════════════════════
SECTION 1: ELIGIBILITY REQUIREMENTS
═══════════════════════════════════════════════════════════════════════════════

1.1 FINANCIAL ELIGIBILITY - ASSET LIMITS

COUNTABLE ASSETS (Must be ≤ $2,000 for single applicant):
- Bank accounts (checking, savings, money market)
- Certificates of deposit (CDs)
- Stocks, bonds, mutual funds
- Cash value of life insurance (if face value > $2,500)
- Additional vehicles beyond one primary vehicle
- Investment real estate
- Retirement accounts (IRAs, 401k) if applicant can access funds

EXEMPT ASSETS (Not counted toward $2,000 limit):
- Primary residence (if equity ≤ $713,000 in 2026)
- One vehicle (regardless of value)
- Personal belongings and household goods
- Prepaid burial/funeral plans (irrevocable)
- Burial plot and headstone
- Life insurance with face value ≤ $2,500
- Term life insurance (no cash value)

1.2 INCOME RULES

INCOME CAP: Florida is an "Income Cap" state
- Monthly income must be ≤ $2,829 (2026 limit) OR
- Income placed in Qualified Income Trust (Miller Trust)

PATIENT RESPONSIBILITY:
- All income minus allowable deductions goes to facility
- Personal Needs Allowance: $130/month retained by patient
- Medicare/health insurance premiums deducted first
- Spousal allowance if applicable

1.3 MEDICAL ELIGIBILITY

LEVEL OF CARE REQUIREMENT:
- Must require "nursing facility level of care"
- Determined by CARES assessment
- Criteria: Need assistance with 2+ ADLs OR
- Cognitive impairment requiring 24-hour supervision

═══════════════════════════════════════════════════════════════════════════════
SECTION 2: LOOK-BACK PERIOD AND TRANSFER PENALTIES
═══════════════════════════════════════════════════════════════════════════════

2.1 60-MONTH LOOK-BACK PERIOD

Florida reviews ALL financial transactions for 60 months (5 years) prior to application.

TRANSFERS THAT TRIGGER PENALTIES:
- Gifts to family members
- Transfers to trusts
- Adding names to accounts/deeds
- Selling assets below fair market value
- Paying for services not received

PENALTY CALCULATION:
Penalty Period = Transfer Amount ÷ $10,809 (2026 divisor)
Example: $50,000 gift = 4.6 months of ineligibility

2.2 EXEMPT TRANSFERS (No Penalty):
- Transfers to spouse
- Transfers to disabled child
- Transfers to caregiver child (lived in home 2+ years)
- Transfers to sibling with equity interest
- Transfer of home to child under 21
- Transfers for fair market value

2.3 CURE PROVISIONS:
- Return of transferred assets eliminates penalty
- Partial return reduces penalty proportionally
- Promissory notes may cure if properly structured

═══════════════════════════════════════════════════════════════════════════════
SECTION 3: SPEND-DOWN STRATEGIES (LEGAL)
═══════════════════════════════════════════════════════════════════════════════

3.1 APPROVED SPEND-DOWN METHODS:

PREPAID EXPENSES:
- Prepay funeral/burial (irrevocable contract)
- Prepay rent/facility costs
- Pay off debts (mortgage, credit cards, medical bills)

HOME IMPROVEMENTS:
- Accessibility modifications (ramps, grab bars)
- Roof repair, HVAC replacement
- Any improvement that increases home value

MEDICAL EXPENSES:
- Dental work, dentures, hearing aids
- Eyeglasses, medical equipment
- Pay outstanding medical bills

PERSONAL ITEMS:
- New clothing, furniture for facility room
- Personal care items

LEGAL FEES:
- Elder law attorney fees
- Medicaid planning costs

3.2 PROHIBITED SPEND-DOWN:
- Gifts to family (triggers penalty)
- Paying family for "services" without contract
- Purchasing assets that become countable
- Transferring to trusts without proper structure

═══════════════════════════════════════════════════════════════════════════════
SECTION 4: DECEASED SPOUSE DEBT RULES
═══════════════════════════════════════════════════════════════════════════════

4.1 FLORIDA COMMON LAW PROPERTY STATE

CRITICAL RULE: Florida is a COMMON LAW property state, NOT community property.

SURVIVING SPOUSE LIABILITY:
- NOT automatically responsible for deceased spouse's individual debts
- Only responsible if:
  * Co-signed the debt
  * Debt was for necessities (food, shelter, medical)
  * Joint account holder

4.2 PROTECTED ASSETS:
- Assets titled solely in surviving spouse's name
- Life insurance proceeds (if beneficiary is surviving spouse)
- Retirement accounts with surviving spouse as beneficiary
- Homestead property (Florida Constitution protection)

4.3 CREDITOR LIMITATIONS:
- Creditors can only pursue deceased's estate
- If estate is insolvent, unsecured debts discharged
- Medical debt of deceased does NOT transfer to widow

APPLICATION TO MARGARET THOMPSON:
Robert's individual debts (if any) do NOT become Margaret's responsibility.
His pension continues to her as survivor benefit - this is INCOME, not debt.

═══════════════════════════════════════════════════════════════════════════════
SECTION 5: APPLICATION PROCESS
═══════════════════════════════════════════════════════════════════════════════

5.1 REQUIRED DOCUMENTATION:
- Photo ID and Social Security card
- Birth certificate
- Bank statements (60 months)
- Tax returns (5 years)
- Property deeds
- Vehicle titles
- Life insurance policies
- Retirement account statements
- Medical records proving level of care

5.2 TIMELINE:
- Application submission: Day 1
- CARES assessment: 7-14 days
- Financial review: 30-45 days
- Approval/Denial: 45-90 days
- Retroactive coverage: Up to 3 months prior

5.3 APPEAL RIGHTS:
- 90 days to request fair hearing
- Can continue receiving benefits during appeal
- Legal representation recommended

═══════════════════════════════════════════════════════════════════════════════
SECTION 6: AI DECISION MATRIX FOR MARGARET THOMPSON
═══════════════════════════════════════════════════════════════════════════════

ELIGIBILITY ASSESSMENT:

ASSET TEST:
- Current Assets: $3,000 (checking $1,500 + savings $1,500)
- Asset Limit: $2,000
- STATUS: OVER BY $1,000 - REQUIRES SPEND-DOWN

INCOME TEST:
- Monthly Income: $2,300 (SS $1,850 + Pension $450)
- Income Cap: $2,829
- STATUS: UNDER CAP - NO MILLER TRUST NEEDED

MEDICAL TEST:
- Diagnosis: Alzheimer's Disease, moderate stage
- ADL Needs: Bathing, Dressing, Medication Management
- MMSE Score: 16/30 (moderate impairment)
- STATUS: MEETS NURSING FACILITY LEVEL OF CARE

LOOK-BACK REVIEW:
- No gifts identified in 60-month period
- No property transfers
- STATUS: NO PENALTY PERIOD

RECOMMENDED ACTIONS:
1. Spend down $1,000 on:
   - Prepaid funeral expenses ($500)
   - Medical supplies for facility ($300)
   - Legal fees for POA documents ($200)
2. Submit Medicaid application immediately
3. Apply for VA Survivors Pension concurrently
4. Arrange private pay for 45-60 day processing period

PROJECTED OUTCOME:
- Medicaid approval: 45-60 days
- VA approval: 60-90 days
- Net monthly cost after benefits: $0

Document Generated by CareNav AI
Florida Medicaid Rules Reference: F.A.C. 65A-1.712
Last Updated: February 2026""",
        "extracted_data": {
            "document_type": "Medicaid Rules Guide",
            "asset_limit": 2000,
            "income_cap_2026": 2829,
            "look_back_months": 60,
            "penalty_divisor_2026": 10809,
            "personal_needs_allowance": 130,
            "home_equity_limit": 713000,
            "florida_property_type": "Common Law",
            "surviving_spouse_debt_liability": "Limited",
            "application_timeline_days": "45-90"
        },
        "ai_analysis": "Comprehensive Florida Medicaid ICP rules document for AI decision support. Key findings for Margaret: Assets $1,000 over limit (requires spend-down), income under cap (no Miller Trust needed), meets medical criteria (Alzheimer's with ADL needs), no look-back penalties. Florida's common law property rules protect Margaret from Robert's individual debts."
    },
    {
        "name": "VA Aid & Attendance Benefits Guide",
        "category": "ai_analysis",
        "doc_type": "va_benefits_guide",
        "content": """VA AID & ATTENDANCE (A&A) BENEFITS
COMPREHENSIVE ELIGIBILITY AND APPLICATION GUIDE
Prepared by CareNav AI for Decision Support

═══════════════════════════════════════════════════════════════════════════════
SECTION 1: PROGRAM OVERVIEW
═══════════════════════════════════════════════════════════════════════════════

1.1 WHAT IS AID & ATTENDANCE?

Aid & Attendance is an enhanced VA pension benefit for veterans and surviving
spouses who need help with activities of daily living or are housebound.

BENEFIT AMOUNTS (2026 Rates):
- Veteran without dependents: $2,229/month
- Veteran with spouse: $2,642/month
- Surviving spouse: $1,432/month
- Housebound veteran: $1,732/month

1.2 KEY ADVANTAGE:
- Tax-free benefit
- Can be used for ANY care expenses
- Combines with Medicaid (not counted as income for Medicaid)
- No estate recovery

═══════════════════════════════════════════════════════════════════════════════
SECTION 2: ELIGIBILITY REQUIREMENTS
═══════════════════════════════════════════════════════════════════════════════

2.1 MILITARY SERVICE REQUIREMENTS

VETERAN MUST HAVE:
- 90 days of active duty service
- At least 1 day during a wartime period
- Discharge other than dishonorable

WARTIME PERIODS:
- World War II: Dec 7, 1941 - Dec 31, 1946
- Korean War: June 27, 1950 - Jan 31, 1955
- Vietnam Era: Aug 5, 1964 - May 7, 1975 (Feb 28, 1961 if served in Vietnam)
- Gulf War: Aug 2, 1990 - Present

2.2 MEDICAL REQUIREMENTS (Must meet ONE):
- Need help with at least 2 ADLs (bathing, dressing, eating, toileting, transferring)
- Bedridden
- Patient in nursing home due to mental or physical incapacity
- Blind or nearly blind (5/200 vision or less)
- Cognitive impairment requiring supervision

2.3 FINANCIAL REQUIREMENTS

NET WORTH LIMIT: $155,356 (2026)
- Includes all assets EXCEPT primary residence
- Includes spouse's assets if married

INCOME LIMIT: Must have medical expenses that reduce income
- Unreimbursed Medical Expenses (UME) deducted from income
- Facility costs count as UME
- In-home care costs count as UME

═══════════════════════════════════════════════════════════════════════════════
SECTION 3: SURVIVING SPOUSE ELIGIBILITY
═══════════════════════════════════════════════════════════════════════════════

3.1 REQUIREMENTS FOR SURVIVING SPOUSE:

MARRIAGE REQUIREMENTS:
- Married to veteran at time of death, OR
- Married for at least 1 year, OR
- Had child with veteran

REMARRIAGE RULES:
- Remarriage after age 57 does not disqualify
- Remarriage before age 57 ends eligibility (unless marriage ends)

VETERAN'S SERVICE:
- Deceased veteran must have met service requirements
- Veteran did NOT need to have filed VA claim before death
- Veteran did NOT need to die from service-related cause

3.2 SURVIVING SPOUSE BENEFIT AMOUNT:
- Maximum: $1,432/month (2026)
- Reduced by countable income after UME deduction

═══════════════════════════════════════════════════════════════════════════════
SECTION 4: UNREIMBURSED MEDICAL EXPENSES (UME)
═══════════════════════════════════════════════════════════════════════════════

4.1 QUALIFYING EXPENSES:

FACILITY COSTS:
- Nursing home room and board
- Assisted living facility costs
- Memory care facility costs
- Adult day care

IN-HOME CARE:
- Home health aides
- Personal care attendants
- Skilled nursing visits

MEDICAL COSTS:
- Medicare premiums
- Medigap premiums
- Part D premiums
- Prescription copays
- Doctor visit copays
- Medical equipment
- Incontinence supplies

4.2 UME CALCULATION EXAMPLE (Margaret Thompson):

Monthly Income:
- Social Security: $1,850
- Pension: $450
- TOTAL INCOME: $2,300

Monthly UME:
- Memory Care facility: $7,500
- Medicare Part B: $175
- Part D premium: $33
- Prescriptions: $50
- TOTAL UME: $7,758

COUNTABLE INCOME = $2,300 - $7,758 = -$5,458 (negative = $0)

Since countable income is $0, Margaret qualifies for FULL benefit of $1,432/month.

═══════════════════════════════════════════════════════════════════════════════
SECTION 5: APPLICATION PROCESS
═══════════════════════════════════════════════════════════════════════════════

5.1 REQUIRED FORMS:

FOR SURVIVING SPOUSE:
- VA Form 21-534EZ (Application for DIC, Death Pension, and Accrued Benefits)
- VA Form 21-2680 (Examination for Housebound Status or Aid & Attendance)
- VA Form 21P-0969 (Income and Asset Statement)

5.2 REQUIRED DOCUMENTS:
- Veteran's DD-214 (discharge papers)
- Death certificate
- Marriage certificate
- Applicant's birth certificate
- Medical records showing care needs
- Bank statements (12 months)
- Facility agreement showing costs

5.3 TIMELINE:
- Initial review: 2-4 weeks
- Evidence development: 30-60 days
- Decision: 60-120 days average
- Retroactive to application date

5.4 EXPEDITED PROCESSING:
- Age 85+: Priority processing
- Terminal illness: Expedited
- Homeless: Expedited
- Financial hardship: May qualify

═══════════════════════════════════════════════════════════════════════════════
SECTION 6: AI DECISION MATRIX FOR MARGARET THOMPSON
═══════════════════════════════════════════════════════════════════════════════

ELIGIBILITY ASSESSMENT:

VETERAN SERVICE (Robert Thompson):
- Branch: U.S. Army
- Active Duty: June 1, 1965 - August 15, 1969
- Wartime Service: Vietnam Era (Aug 5, 1964 - May 7, 1975)
- Discharge: Honorable
- STATUS: MEETS SERVICE REQUIREMENTS

SURVIVING SPOUSE STATUS:
- Marriage Date: June 20, 1964
- Marriage Duration: 55 years at time of death
- Remarriage: None
- STATUS: ELIGIBLE AS SURVIVING SPOUSE

MEDICAL REQUIREMENTS:
- Diagnosis: Alzheimer's Disease
- ADL Needs: Bathing, Dressing, Medication Management
- Care Setting: Memory Care facility
- STATUS: MEETS A&A MEDICAL CRITERIA

FINANCIAL REQUIREMENTS:
- Total Assets: $3,000 (well under $155,356 limit)
- Monthly Income: $2,300
- Monthly UME: $7,758 (facility + medical)
- Countable Income: $0
- STATUS: QUALIFIES FOR FULL BENEFIT

BENEFIT CALCULATION:
- Maximum Surviving Spouse A&A: $1,432/month
- Less Countable Income: $0
- MONTHLY BENEFIT: $1,432

RECOMMENDED ACTIONS:
1. Complete VA Form 21-534EZ
2. Obtain VA Form 21-2680 from physician
3. Gather all required documents
4. Submit application immediately
5. Request expedited processing (age 83)

PROJECTED TIMELINE:
- Application submission: February 2026
- Expected approval: April-May 2026
- Retroactive payment: Back to February 2026

Document Generated by CareNav AI
VA Benefits Reference: 38 CFR 3.351, 3.352
Last Updated: February 2026""",
        "extracted_data": {
            "document_type": "VA A&A Benefits Guide",
            "surviving_spouse_max_benefit": 1432,
            "veteran_max_benefit": 2229,
            "net_worth_limit_2026": 155356,
            "wartime_periods": ["WWII", "Korea", "Vietnam", "Gulf War"],
            "required_forms": ["21-534EZ", "21-2680", "21P-0969"],
            "processing_time_days": "60-120",
            "margaret_eligible": True,
            "margaret_benefit_amount": 1432
        },
        "ai_analysis": "Comprehensive VA Aid & Attendance guide for surviving spouses. Margaret Thompson qualifies for full $1,432/month benefit based on: Robert's Vietnam-era service with honorable discharge, 55-year marriage, Alzheimer's diagnosis requiring ADL assistance, and $0 countable income after UME deduction. Recommend immediate application with expedited processing request."
    },
    {
        "name": "Elder Care Decision Matrix - AI Guidance",
        "category": "ai_analysis",
        "doc_type": "decision_matrix",
        "content": """CARENAV AI DECISION MATRIX
COMPREHENSIVE ELDER CARE NAVIGATION GUIDE
Version 2.0 - February 2026

═══════════════════════════════════════════════════════════════════════════════
SECTION 1: CARE LEVEL DETERMINATION
═══════════════════════════════════════════════════════════════════════════════

1.1 COGNITIVE ASSESSMENT SCORING

MMSE (Mini-Mental State Examination):
- 24-30: Normal cognition → Independent living possible
- 18-23: Mild impairment → Assisted living with supervision
- 10-17: Moderate impairment → Memory Care required
- 0-9: Severe impairment → Skilled Nursing or Memory Care

FUNCTIONAL ASSESSMENT (ADLs):
- Independent in all ADLs → Home with minimal support
- Needs help with 1-2 ADLs → Assisted Living
- Needs help with 3+ ADLs → Skilled Nursing or Memory Care
- Total dependence → Skilled Nursing Facility

BEHAVIORAL FACTORS:
- Wandering behavior → Memory Care (secured unit)
- Aggression/agitation → Specialized Memory Care
- Fall risk → Facility with 24-hour supervision
- Medication non-compliance → Facility-managed medications

1.2 CARE LEVEL RECOMMENDATIONS

INDEPENDENT LIVING:
- MMSE 24+
- Independent in ADLs
- No safety concerns
- Cost: $2,000-4,000/month

ASSISTED LIVING (AL):
- MMSE 18-23
- Needs help with 1-2 ADLs
- Medication reminders needed
- Cost: $4,000-6,000/month

MEMORY CARE (MC):
- MMSE 10-23 with dementia diagnosis
- Wandering or safety concerns
- Needs structured environment
- Cost: $6,000-10,000/month

SKILLED NURSING FACILITY (SNF):
- MMSE any score
- Complex medical needs
- Needs 24-hour nursing care
- Cost: $8,000-12,000/month

═══════════════════════════════════════════════════════════════════════════════
SECTION 2: FINANCIAL PATHWAY DECISION TREE
═══════════════════════════════════════════════════════════════════════════════

2.1 ASSET ASSESSMENT

IF Total Assets > $500,000:
→ Private pay recommended
→ Consider long-term care insurance
→ Asset protection planning with elder law attorney

IF Total Assets $100,000 - $500,000:
→ Hybrid approach
→ Private pay initially
→ Medicaid planning for future
→ Spend-down strategies

IF Total Assets $2,000 - $100,000:
→ Medicaid planning priority
→ Legal spend-down strategies
→ Apply for VA benefits if eligible
→ Bridge financing may be needed

IF Total Assets < $2,000:
→ Immediate Medicaid application
→ VA benefits application
→ May qualify for expedited processing

2.2 INCOME ASSESSMENT

IF Monthly Income > $10,000:
→ Private pay sustainable
→ No government benefits needed

IF Monthly Income $5,000 - $10,000:
→ May need supplemental benefits
→ VA A&A can help offset costs
→ Medicaid for catastrophic coverage

IF Monthly Income $2,829 - $5,000:
→ Miller Trust required for Medicaid
→ VA benefits important supplement
→ Patient responsibility will be high

IF Monthly Income < $2,829:
→ No Miller Trust needed
→ Medicaid income test passed
→ VA benefits maximize coverage

═══════════════════════════════════════════════════════════════════════════════
SECTION 3: BENEFIT STACKING STRATEGIES
═══════════════════════════════════════════════════════════════════════════════

3.1 OPTIMAL BENEFIT COMBINATION

SCENARIO: Surviving spouse of veteran, needs Memory Care

STEP 1: Apply for Medicaid ICP
- Covers facility room and board
- Patient pays "patient responsibility" from income

STEP 2: Apply for VA Survivors Pension with A&A
- Up to $1,432/month additional
- Can offset patient responsibility
- Tax-free benefit

STEP 3: Medicare continues
- Covers physician visits
- Covers hospitalizations
- Part D covers prescriptions

RESULT: Maximum coverage, minimum out-of-pocket

3.2 TIMING STRATEGY

MONTH 1:
- Submit Medicaid application
- Submit VA application same day
- Arrange private pay bridge

MONTHS 2-3:
- Medicaid processing
- VA processing
- Continue private pay

MONTHS 3-4:
- Medicaid approval (retroactive)
- VA approval (retroactive)
- Reimbursement for private pay period

3.3 BENEFIT INTERACTION RULES

VA + MEDICAID:
- VA A&A is NOT counted as income for Medicaid
- Both benefits can be received simultaneously
- VA benefit can pay patient responsibility

MEDICARE + MEDICAID:
- Medicare is primary payer
- Medicaid is secondary (pays what Medicare doesn't)
- "Dual eligible" status

═══════════════════════════════════════════════════════════════════════════════
SECTION 4: FACILITY SELECTION CRITERIA
═══════════════════════════════════════════════════════════════════════════════

4.1 QUALITY INDICATORS

STAFFING RATIOS:
- Memory Care: 1 staff per 5-6 residents (day)
- Skilled Nursing: 1 CNA per 8-10 residents
- RN on-site 24/7 for SNF

INSPECTION RESULTS:
- Check Florida AHCA website
- Review deficiency citations
- Look for patterns of problems

RESIDENT SATISFACTION:
- Family reviews
- Resident council feedback
- Staff turnover rates

4.2 FINANCIAL CONSIDERATIONS

MEDICAID ACCEPTANCE:
- Verify facility accepts Medicaid
- Check for Medicaid bed availability
- Understand private pay requirements

CONTRACT TERMS:
- 30-day notice for discharge
- Rate increase policies
- Additional fee structures

4.3 LOCATION FACTORS

FAMILY ACCESS:
- Within 30 minutes of primary caregiver
- Easy parking and visiting hours
- Family involvement programs

MEDICAL ACCESS:
- Proximity to hospital
- Physician availability
- Specialist access

═══════════════════════════════════════════════════════════════════════════════
SECTION 5: MARGARET THOMPSON - COMPLETE ANALYSIS
═══════════════════════════════════════════════════════════════════════════════

5.1 PATIENT PROFILE

Demographics:
- Age: 83 years old
- Marital Status: Widow (husband Robert deceased 2020)
- Location: Palm Beach County, Florida
- Living Situation: Alone in single-family home (unsafe)

Medical Status:
- Primary Diagnosis: Alzheimer's Disease, moderate stage
- MMSE Score: 16/30
- ADL Needs: Bathing, Dressing, Medication Management
- Recent Event: Wandering episode, hospitalization

5.2 CARE LEVEL DETERMINATION

MMSE 16/30 = Moderate cognitive impairment
+ Wandering behavior
+ Lives alone (unsafe)
+ ADL assistance needed
= MEMORY CARE REQUIRED

5.3 FINANCIAL ANALYSIS

Assets:
- Checking: $1,500
- Savings: $1,500
- Home: ~$250,000 (exempt)
- Vehicle: ~$8,000 (exempt)
- COUNTABLE ASSETS: $3,000

Income:
- Social Security: $1,850/month
- Survivor Pension: $450/month
- TOTAL INCOME: $2,300/month

5.4 BENEFIT ELIGIBILITY

MEDICAID ICP:
- Assets: $1,000 over limit (spend-down needed)
- Income: Under cap (no Miller Trust)
- Medical: Meets nursing facility level
- Look-back: Clean
- STATUS: ELIGIBLE AFTER SPEND-DOWN

VA SURVIVORS PENSION WITH A&A:
- Veteran service: Vietnam era, honorable
- Marriage: 55 years
- Medical need: Meets A&A criteria
- Net worth: Under limit
- STATUS: ELIGIBLE FOR $1,432/MONTH

5.5 RECOMMENDED ACTION PLAN

IMMEDIATE (Days 1-7):
1. Spend down $1,000 on prepaid funeral
2. Submit Medicaid application
3. Submit VA application
4. Secure Memory Care placement
5. Arrange private pay for bridge period

SHORT-TERM (Days 8-60):
1. Complete CARES assessment
2. Provide all requested documentation
3. Follow up weekly on applications
4. Manage private pay costs

MEDIUM-TERM (Days 61-120):
1. Receive Medicaid approval
2. Receive VA approval
3. Transition to benefit-covered care
4. Address home disposition

5.6 PROJECTED FINANCIAL OUTCOME

BEFORE BENEFITS:
- Memory Care cost: $7,500/month
- Income: $2,300/month
- MONTHLY SHORTFALL: $5,200

AFTER BENEFITS:
- Medicaid pays: Facility cost
- Patient responsibility: ~$2,170/month
- VA A&A: +$1,432/month
- NET COST TO FAMILY: $738/month

With proper planning, Margaret's care costs reduce from $5,200/month shortfall to $738/month - a savings of $4,462/month or $53,544/year.

Document Generated by CareNav AI
Decision Matrix Version: 2.0
Last Updated: February 2026""",
        "extracted_data": {
            "document_type": "AI Decision Matrix",
            "care_levels": ["Independent Living", "Assisted Living", "Memory Care", "Skilled Nursing"],
            "mmse_thresholds": {"normal": 24, "mild": 18, "moderate": 10, "severe": 0},
            "benefit_programs": ["Medicaid ICP", "VA A&A", "Medicare"],
            "margaret_care_level": "Memory Care",
            "margaret_medicaid_eligible": True,
            "margaret_va_eligible": True,
            "margaret_monthly_savings": 4462,
            "margaret_annual_savings": 53544
        },
        "ai_analysis": "Comprehensive AI decision matrix for elder care navigation. For Margaret Thompson: MMSE 16 + wandering = Memory Care required. Financial analysis shows $1,000 spend-down needed for Medicaid, VA A&A eligible for $1,432/month. Optimal strategy: simultaneous Medicaid and VA applications with prepaid funeral spend-down. Projected outcome: $4,462/month savings compared to private pay."
    },
]


async def create_demo_documents_for_patient(patient_id: int):
    """Create demo documents for a patient and index them in ChromaDB."""
    session_maker = get_async_session_maker()
    
    async with session_maker() as session:
        # Check if patient exists
        result = await session.execute(
            select(Patient).where(Patient.id == patient_id)
        )
        patient = result.scalar_one_or_none()
        if not patient:
            return {"error": "Patient not found"}
        
        # Check if documents already exist
        result = await session.execute(
            select(Document).where(Document.patient_id == patient_id)
        )
        existing_docs = result.scalars().all()
        if len(existing_docs) > 5:
            return {"message": "Documents already exist", "count": len(existing_docs)}
        
        # Create documents
        created_count = 0
        for doc_data in DEMO_DOCUMENTS:
            doc = Document(
                patient_id=patient_id,
                name=doc_data["name"],
                category=doc_data["category"],
                doc_type=doc_data["doc_type"],
                content=doc_data["content"],
                extracted_data=doc_data["extracted_data"],
                ai_analysis=doc_data["ai_analysis"],
                status="generated",
                uploaded_at=datetime.utcnow(),
            )
            session.add(doc)
            created_count += 1
        
        await session.commit()
        
        # Index in ChromaDB
        try:
            kb_service = get_knowledge_base_service()
            if not kb_service.disabled:
                for doc_data in DEMO_DOCUMENTS:
                    kb_service.add_document(
                        "patient_documents",
                        f"patient_{patient_id}_{doc_data['doc_type']}",
                        doc_data["content"],
                        {
                            "patient_id": patient_id,
                            "category": doc_data["category"],
                            "doc_type": doc_data["doc_type"],
                        }
                    )
        except Exception:
            pass  # ChromaDB may be disabled
        
        return {"message": "Documents created", "count": created_count}
