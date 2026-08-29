"""
Intain Loan Performance Intelligence Engine
Synthetic Data Generator - Servicer Updates

Generates:
    data/synthetic/servicer_updates.csv

Purpose:
    Create a second-source dataset containing:
        - normal matching records
        - partial updates
        - stale records
        - controlled conflicts

These records are designed for:
    Task 1 - Data Intelligence & Profiling
    Task 4 - Anomaly / Exception Detection

Development data only.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm


# ============================================================
# CONFIGURATION
# ============================================================

SEED = 2026

INPUT_FILE = Path(
    "data/synthetic/loan_monthly_performance_train.csv"
)

OUTPUT_DIR = Path(
    "data/synthetic"
)

OUTPUT_FILE = (
    OUTPUT_DIR /
    "servicer_updates.csv"
)

rng = np.random.default_rng(SEED)


# ============================================================
# CONFIGURATION FOR CONFLICT GENERATION
# ============================================================

# We don't want to corrupt everything.
# Real second-source data should mostly agree with the primary
# source, with a small percentage of exceptions.

NORMAL_RATE = 0.88
PARTIAL_UPDATE_RATE = 0.05
STALE_RECORD_RATE = 0.04
CONFLICT_RATE = 0.03


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def generate_update_type():

    return rng.choice(
        [
            "MATCH",
            "PARTIAL_UPDATE",
            "STALE",
            "CONFLICT"
        ],
        p=[
            NORMAL_RATE,
            PARTIAL_UPDATE_RATE,
            STALE_RECORD_RATE,
            CONFLICT_RATE
        ]
    )


def generate_timestamps(
    reporting_month,
    update_type
):

    base_date = pd.Timestamp(
        reporting_month
    )

    # Record is received 3 to 35 days after the end of the reporting month
    received_days = int(
        rng.integers(
            3,
            35
        )
    )
    record_received_at = base_date + pd.Timedelta(days=received_days)

    if update_type == "STALE":

        # System update occurred 60 to 180 days before receipt (stale)
        days_before = int(
            rng.integers(
                60,
                180
            )
        )

    else:

        # System update occurred recently before receipt
        days_before = int(
            rng.integers(
                1,
                5
            )
        )

    last_updated_at = record_received_at - pd.Timedelta(days=days_before)

    return last_updated_at, record_received_at


def generate_conflicting_balance(
    current_balance
):

    # Small but meaningful discrepancy.
    # Example:
    #
    # Primary = 250,000
    # Servicer = 254,500

    variation = rng.uniform(
        0.01,
        0.05
    )

    direction = rng.choice(
        [-1, 1]
    )

    new_balance = (
        current_balance
        * (
            1
            + direction * variation
        )
    )

    return round(
        max(
            0,
            new_balance
        ),
        2
    )


def generate_conflicting_dpd(
    days_past_due
):

    # Controlled DPD disagreement.

    possible_values = [
        0,
        30,
        60,
        90
    ]

    alternatives = [
        value
        for value in possible_values
        if value != days_past_due
    ]

    return int(
        rng.choice(
            alternatives
        )
    )


# ============================================================
# GENERATE SERVICER DATA
# ============================================================

def create_servicer_updates(
    train_df
):

    records = []

    # --------------------------------------------------------
    # Sample a subset of monthly records
    # --------------------------------------------------------

    # A second source does not necessarily contain every
    # monthly record.

    sample_size = int(
        len(train_df) * 0.45
    )

    sampled_df = train_df.sample(
        n=sample_size,
        random_state=SEED
    ).copy()

    # --------------------------------------------------------
    # Generate second-source records
    # --------------------------------------------------------

    print("\nProcessing and corrupting servicer updates...")
    for _, row in tqdm(sampled_df.iterrows(), total=len(sampled_df), desc="Generating Servicer Updates", bar_format="{l_bar}{bar:30}{r_bar}"):

        update_type = (
            generate_update_type()
        )

        primary_balance = float(
            row["current_balance"]
        )

        primary_dpd = int(
            row["days_past_due"]
        )

        # ----------------------------------------------------
        # Default: match primary record
        # ----------------------------------------------------

        servicer_balance = (
            primary_balance
        )

        servicer_dpd = (
            primary_dpd
        )

        servicer_status = (
            row["current_status"]
        )

        modification_flag = int(
            row["modification_flag"]
        )

        document_status = (
            row["document_status"]
        )

        # ----------------------------------------------------
        # Partial update
        # ----------------------------------------------------

        if update_type == "PARTIAL_UPDATE":

            # Some fields may be unavailable in the
            # second source.

            if rng.random() < 0.50:

                servicer_balance = np.nan

            if rng.random() < 0.50:

                servicer_dpd = np.nan

            if rng.random() < 0.30:

                modification_flag = np.nan

            if rng.random() < 0.30:

                document_status = np.nan

        # ----------------------------------------------------
        # Stale record
        # ----------------------------------------------------

        elif update_type == "STALE":

            # Keep old values while primary source has moved
            # forward.

            if rng.random() < 0.70:

                # Old balance slightly higher
                servicer_balance = round(
                    primary_balance
                    * rng.uniform(
                        1.01,
                        1.08
                    ),
                    2
                )

            if rng.random() < 0.60:

                # Old DPD state
                servicer_dpd = int(
                    rng.choice(
                        [0, 30, 60]
                    )
                )

        # ----------------------------------------------------
        # Explicit conflict
        # ----------------------------------------------------

        elif update_type == "CONFLICT":

            conflict_type = rng.choice(
                [
                    "BALANCE",
                    "DPD",
                    "STATUS",
                    "DOCUMENT"
                ]
            )

            if conflict_type == "BALANCE":

                servicer_balance = (
                    generate_conflicting_balance(
                        primary_balance
                    )
                )

            elif conflict_type == "DPD":

                servicer_dpd = (
                    generate_conflicting_dpd(
                        primary_dpd
                    )
                )

            elif conflict_type == "STATUS":

                status_options = [
                    "Current",
                    "Delinquent",
                    "Default",
                    "Prepaid"
                ]

                alternatives = [
                    value
                    for value in status_options
                    if value != servicer_status
                ]

                servicer_status = rng.choice(
                    alternatives
                )

            elif conflict_type == "DOCUMENT":

                document_options = [
                    "Complete",
                    "Pending",
                    "Missing"
                ]

                alternatives = [
                    value
                    for value in document_options
                    if value != document_status
                ]

                document_status = rng.choice(
                    alternatives
                )

        # ----------------------------------------------------
        # Timestamps
        # ----------------------------------------------------

        last_updated_at, record_received_at = generate_timestamps(
            row["reporting_month"],
            update_type
        )

        # ----------------------------------------------------
        # Source record ID
        # ----------------------------------------------------

        source_record_id = (
            f"SRV-"
            f"{row['loan_id']}-"
            f"{pd.Timestamp(row['reporting_month']).strftime('%Y%m')}"
        )

        # ----------------------------------------------------
        # Record
        # ----------------------------------------------------

        records.append({

            "source_record_id":
                source_record_id,

            "loan_id":
                row["loan_id"],

            "reporting_month":
                row["reporting_month"],

            "servicer_name":
                row["servicer_name"],

            "servicer_update_type":
                update_type,

            "servicer_current_balance":
                servicer_balance,

            "servicer_days_past_due":
                servicer_dpd,

            "servicer_status":
                servicer_status,

            "servicer_modification_flag":
                modification_flag,

            "servicer_document_status":
                document_status,

            "last_updated_at":
                last_updated_at,

            "source_system":
                "ServicerFeed",

            "record_received_at":
                record_received_at
        })

    return pd.DataFrame(
        records
    )


# ============================================================
# VALIDATION
# ============================================================

def validate_servicer_updates(
    df
):

    print(
        "\nRunning servicer update validation..."
    )

    required_columns = [

        "source_record_id",

        "loan_id",

        "reporting_month",

        "servicer_name",

        "servicer_update_type",

        "servicer_current_balance",

        "servicer_days_past_due",

        "servicer_status",

        "servicer_modification_flag",

        "servicer_document_status",

        "last_updated_at",

        "source_system",

        "record_received_at"
    ]

    missing_columns = (
        set(required_columns)
        - set(df.columns)
    )

    assert not missing_columns, (
        f"Missing columns: "
        f"{missing_columns}"
    )

    # --------------------------------------------------------
    # Unique source records
    # --------------------------------------------------------

    assert df[
        "source_record_id"
    ].is_unique

    # --------------------------------------------------------
    # Valid update types
    # --------------------------------------------------------

    valid_types = {
        "MATCH",
        "PARTIAL_UPDATE",
        "STALE",
        "CONFLICT"
    }

    assert set(
        df[
            "servicer_update_type"
        ].dropna().unique()
    ).issubset(
        valid_types
    )

    # --------------------------------------------------------
    # Balance cannot be negative
    # --------------------------------------------------------

    assert (
        df[
            "servicer_current_balance"
        ].dropna()
        >= 0
    ).all()

    # --------------------------------------------------------
    # Valid DPD
    # --------------------------------------------------------

    valid_dpd = {
        0,
        30,
        60,
        90
    }

    assert set(
        df[
            "servicer_days_past_due"
        ].dropna().astype(int).unique()
    ).issubset(
        valid_dpd
    )

    # --------------------------------------------------------
    # Dates
    # --------------------------------------------------------

    assert (
        pd.to_datetime(
            df["record_received_at"]
        )
        >= pd.to_datetime(
            df["reporting_month"]
        )
    ).all()

    print(
        "Validation PASSED."
    )


# ============================================================
# SUMMARY
# ============================================================

def print_summary(
    df
):

    print(
        "\nUpdate type distribution:"
    )

    print(
        df[
            "servicer_update_type"
        ]
        .value_counts(
            normalize=True
        )
        .mul(100)
        .round(2)
    )

    print(
        "\nMissing values:"
    )

    print(
        df.isna()
        .sum()
    )


# ============================================================
# MAIN
# ============================================================

def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print("=" * 70)
    print(
        "INTAIN SERVICER UPDATE GENERATOR"
    )
    print("=" * 70)

    # --------------------------------------------------------
    # Load training data
    # --------------------------------------------------------

    train_df = pd.read_csv(
        INPUT_FILE,
        parse_dates=[
            "reporting_month"
        ]
    )

    print(
        f"Training records loaded: "
        f"{len(train_df):,}"
    )

    # --------------------------------------------------------
    # Generate updates
    # --------------------------------------------------------

    df = create_servicer_updates(
        train_df
    )

    # --------------------------------------------------------
    # Sort
    # --------------------------------------------------------

    df = df.sort_values(
        [
            "loan_id",
            "reporting_month"
        ]
    ).reset_index(
        drop=True
    )

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    validate_servicer_updates(
        df
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\n" + "=" * 70)
    print(
        "SERVICER UPDATES GENERATED"
    )
    print("=" * 70)

    print(
        f"Rows          : {len(df):,}"
    )

    print(
        f"Columns       : {len(df.columns)}"
    )

    print(
        f"Unique loans  : "
        f"{df['loan_id'].nunique():,}"
    )

    print(
        f"Output        : {OUTPUT_FILE}"
    )

    print_summary(
        df
    )

    print(
        "\nSample:"
    )

    print(
        df.head(10).to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()