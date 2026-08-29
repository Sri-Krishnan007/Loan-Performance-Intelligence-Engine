"""
Intain Loan Performance Intelligence Engine
Synthetic Data Generator - Static Loan Attributes

Purpose:
    Generate a realistic synthetic loan_static_attributes.csv
    following the schema described in the Intain AI Track
    problem statement.

This is DEVELOPMENT DATA ONLY.
It is designed to be replaceable by the organizer-provided dataset.
"""

from pathlib import Path
from datetime import datetime
import time

import numpy as np
import pandas as pd
from tqdm import tqdm


# ============================================================
# CONFIGURATION
# ============================================================

SEED = 42
N_LOANS = 2_000

OUTPUT_DIR = Path("data/synthetic")
OUTPUT_FILE = OUTPUT_DIR / "loan_static_attributes.csv"

rng = np.random.default_rng(SEED)


# ============================================================
# REFERENCE VALUES
# ============================================================

STATES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
]

LOAN_PURPOSES = [
    "Purchase",
    "Refinance"
]

OCCUPANCY_TYPES = [
    "Primary Residence",
    "Second Home",
    "Investment"
]

PROPERTY_TYPES = [
    "Single Family",
    "Condominium",
    "Townhouse",
    "Multi Unit"
]

SERVICERS = [
    "Servicer_A",
    "Servicer_B",
    "Servicer_C",
    "Servicer_D",
    "Servicer_E"
]

CREDIT_SCORE_BANDS = [
    "580-619",
    "620-659",
    "660-699",
    "700-739",
    "740-779",
    "780+"
]

LTV_BANDS = [
    "0-60",
    "60-70",
    "70-80",
    "80-90",
    "90-100"
]

DTI_BANDS = [
    "0-20",
    "20-30",
    "30-40",
    "40-50"
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def generate_loan_ids(n: int) -> list[str]:
    """Generate unique loan identifiers."""
    return [f"LN{100000 + i}" for i in range(n)]


def generate_origination_dates(n: int) -> pd.Series:
    """
    Generate realistic origination months.

    Loans originate between January 2018 and December 2024,
    allowing several years of monthly performance history
    through 2026.
    """

    start = pd.Timestamp("2018-01-01")
    end = pd.Timestamp("2024-12-01")

    months = pd.date_range(start=start, end=end, freq="MS")

    return pd.Series(
        rng.choice(months, size=n),
        name="origination_month"
    )


def generate_original_balances(n: int) -> np.ndarray:
    """
    Generate realistic mortgage balances.

    Uses a log-normal distribution and clips extreme values.
    """

    balances = rng.lognormal(
        mean=np.log(250_000),
        sigma=0.55,
        size=n
    )

    balances = np.clip(
        balances,
        75_000,
        1_500_000
    )

    return np.round(balances, 2)


def generate_interest_rates(
    vintages: pd.Series,
    credit_bands: np.ndarray,
    ltv_bands: np.ndarray,
    n: int
) -> np.ndarray:
    """
    Generate realistic mortgage interest rates as a function of:
    1. Vintage macroeconomic rates (historical average prime rates).
    2. Risk adjustments based on credit score bands.
    3. Risk adjustments based on LTV bands.
    """
    # Base rates by vintage year (representative US 30-year fixed historical averages)
    vintage_base_rates = {
        2018: 4.54,
        2019: 3.94,
        2020: 3.11,
        2021: 2.96,
        2022: 5.34,
        2023: 6.81,
        2024: 6.84
    }
    
    # Map credit score bands to interest rate premiums/discounts (risk adjustment)
    credit_adjustments = {
        "580-619": 1.20,
        "620-659": 0.60,
        "660-699": 0.25,
        "700-739": 0.00,
        "740-779": -0.25,
        "780+": -0.50
    }
    
    # Map LTV bands to interest rate premiums/discounts
    ltv_adjustments = {
        "0-60": -0.20,
        "60-70": -0.10,
        "70-80": 0.00,
        "80-90": 0.20,
        "90-100": 0.40
    }

    rates = np.zeros(n)
    for i in range(n):
        year = int(vintages.iloc[i])
        base = vintage_base_rates.get(year, 5.0)
        
        c_band = credit_bands[i]
        c_adj = credit_adjustments.get(c_band, 0.0)
        
        l_band = ltv_bands[i]
        l_adj = ltv_adjustments.get(l_band, 0.0)
        
        # Add slight borrower-specific noise
        noise = rng.normal(loc=0.0, scale=0.3)
        
        rates[i] = base + c_adj + l_adj + noise

    # Clip within realistic historical bounds (2.0% to 11.0%)
    rates = np.clip(rates, 2.0, 11.0)
    return np.round(rates, 3)


def generate_categorical_values(
    values: list[str],
    probabilities: list[float],
    n: int
) -> np.ndarray:

    return rng.choice(
        values,
        size=n,
        p=probabilities
    )


# ============================================================
# MAIN GENERATOR
# ============================================================

def create_static_attributes() -> pd.DataFrame:
    # We will define a clear execution pipeline with tqdm so the user has a progress bar
    steps = [
        ("Loan IDs", lambda: generate_loan_ids(N_LOANS)),
        ("Origination Dates", lambda: generate_origination_dates(N_LOANS)),
        ("Credit Score Bands", lambda: generate_categorical_values(
            CREDIT_SCORE_BANDS,
            probabilities=[0.04, 0.10, 0.18, 0.27, 0.25, 0.16],
            n=N_LOANS
        )),
        ("LTV Bands", lambda: generate_categorical_values(
            LTV_BANDS,
            probabilities=[0.18, 0.20, 0.30, 0.22, 0.10],
            n=N_LOANS
        )),
        ("DTI Bands", lambda: generate_categorical_values(
            DTI_BANDS,
            probabilities=[0.25, 0.35, 0.30, 0.10],
            n=N_LOANS
        )),
        ("Original Balances", lambda: generate_original_balances(N_LOANS)),
        ("Interest Rates (Risk-Adjusted)", None),  # Generated dynamically below
        ("Geography (States)", lambda: rng.choice(STATES, size=N_LOANS)),
        ("Loan Purposes", lambda: generate_categorical_values(
            LOAN_PURPOSES,
            probabilities=[0.68, 0.32],
            n=N_LOANS
        )),
        ("Occupancy Types", lambda: generate_categorical_values(
            OCCUPANCY_TYPES,
            probabilities=[0.78, 0.10, 0.12],
            n=N_LOANS
        )),
        ("Property Types", lambda: generate_categorical_values(
            PROPERTY_TYPES,
            probabilities=[0.58, 0.20, 0.15, 0.07],
            n=N_LOANS
        )),
        ("Servicers", lambda: generate_categorical_values(
            SERVICERS,
            probabilities=[0.28, 0.24, 0.20, 0.16, 0.12],
            n=N_LOANS
        )),
    ]

    results = {}
    print("\nGenerating synthetic loan static attributes...")
    
    # tqdm progress bar
    with tqdm(total=len(steps), desc="Overall Progress", bar_format="{l_bar}{bar:30}{r_bar}") as pbar:
        for step_name, func in steps:
            pbar.set_description(f"Generating {step_name}")
            time.sleep(0.08)  # Short delay to make the progress bar visible and interactive
            
            if step_name == "Interest Rates (Risk-Adjusted)":
                # Model rates based on macroeconomic vintage and borrower credit score & LTV risk bands
                vintages = results["Origination Dates"].dt.year.astype(int)
                results[step_name] = generate_interest_rates(
                    vintages=vintages,
                    credit_bands=results["Credit Score Bands"],
                    ltv_bands=results["LTV Bands"],
                    n=N_LOANS
                )
            else:
                results[step_name] = func()
                
            pbar.update(1)

    # Extract results
    loan_ids = results["Loan IDs"]
    origination_month = results["Origination Dates"]
    original_balance = results["Original Balances"]
    interest_rate = results["Interest Rates (Risk-Adjusted)"]
    credit_score_band = results["Credit Score Bands"]
    ltv_band = results["LTV Bands"]
    dti_band = results["DTI Bands"]
    state = results["Geography (States)"]
    loan_purpose = results["Loan Purposes"]
    occupancy_type = results["Occupancy Types"]
    property_type = results["Property Types"]
    servicer_name = results["Servicers"]
    vintage = origination_month.dt.year.astype(int)

    # --------------------------------------------------------
    # Construct dataframe
    # --------------------------------------------------------

    df = pd.DataFrame({
        "loan_id": loan_ids,
        "origination_month": origination_month,
        "original_balance": original_balance,
        "interest_rate": interest_rate,
        "credit_score_band": credit_score_band,
        "ltv_band": ltv_band,
        "dti_band": dti_band,
        "state": state,
        "loan_purpose": loan_purpose,
        "occupancy_type": occupancy_type,
        "property_type": property_type,
        "servicer_name": servicer_name,
        "vintage": vintage
    })

    # ========================================================
    # VALIDATION
    # ========================================================

    # Unique loan IDs
    assert df["loan_id"].is_unique

    # Positive balances
    assert (df["original_balance"] > 0).all()

    # Interest rate bounds
    assert df["interest_rate"].between(
        0,
        15
    ).all()

    # Valid origination dates
    assert (
        df["origination_month"]
        <= pd.Timestamp("2026-12-01")
    ).all()

    # Valid categorical values
    assert df["credit_score_band"].isin(
        CREDIT_SCORE_BANDS
    ).all()

    assert df["ltv_band"].isin(
        LTV_BANDS
    ).all()

    assert df["dti_band"].isin(
        DTI_BANDS
    ).all()

    assert df["state"].isin(
        STATES
    ).all()

    # Sort
    df = df.sort_values(
        "loan_id"
    ).reset_index(drop=True)

    return df


# ============================================================
# SAVE
# ============================================================

def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    df = create_static_attributes()

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("=" * 60)
    print("STATIC LOAN DATA GENERATED")
    print("=" * 60)
    print(f"Rows       : {len(df):,}")
    print(f"Columns    : {len(df.columns)}")
    print(f"Output     : {OUTPUT_FILE}")
    print(f"Loan count : {df['loan_id'].nunique():,}")
    print("=" * 60)

    print("\nSample:")
    print(df.head())

    print("\nMissing values:")
    print(df.isna().sum())

    print("\nData types:")
    print(df.dtypes)


if __name__ == "__main__":
    main()