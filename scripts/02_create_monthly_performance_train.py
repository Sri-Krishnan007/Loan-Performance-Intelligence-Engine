import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
"""
Intain Loan Performance Intelligence Engine
Synthetic Data Generator - Monthly Training Performance

Generates:
    data/synthetic/loan_monthly_performance_train.csv

Design:
    - One row per loan per month
    - Uses loan_static_attributes.csv as the source of origination data
    - Generates realistic monthly loan behavior
    - Creates future-looking target variables
    - Uses 2026 as the latest reporting period

IMPORTANT:
    This is synthetic DEVELOPMENT data.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm


# ============================================================
# CONFIGURATION
# ============================================================

SEED = 42
END_DATE = pd.Timestamp("2026-07-01")

INPUT_FILE = Path(__file__).resolve().parent.parent / "data/synthetic/loan_static_attributes.csv"

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data/synthetic"

OUTPUT_FILE = (
    OUTPUT_DIR /
    "loan_monthly_performance_train.csv"
)

rng = np.random.default_rng(SEED)


# ============================================================
# REFERENCE VALUES
# ============================================================

STATUSES = [
    "Current",
    "Delinquent",
    "Default",
    "Prepaid"
]

LOSS_SEVERITY_BANDS = [
    "None",
    "Low",
    "Medium",
    "High"
]

SOURCE_SYSTEMS = [
    "ServicingCore",
    "LoanPlatform",
    "RiskSystem"
]

DOCUMENT_STATUSES = [
    "Complete",
    "Complete",
    "Complete",
    "Pending",
    "Missing"
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def band_to_midpoint(value: str) -> float:
    """
    Convert categorical bands into representative numeric values.
    Used only internally for probability generation.
    """

    if value == "580-619":
        return 600

    if value == "620-659":
        return 640

    if value == "660-699":
        return 680

    if value == "700-739":
        return 720

    if value == "740-779":
        return 760

    if value == "780+":
        return 790

    return 700


def ltv_midpoint(value: str) -> float:

    mapping = {
        "0-60": 55,
        "60-70": 65,
        "70-80": 75,
        "80-90": 85,
        "90-100": 95
    }

    return mapping[value]


def dti_midpoint(value: str) -> float:

    mapping = {
        "0-20": 15,
        "20-30": 25,
        "30-40": 35,
        "40-50": 45
    }

    return mapping[value]


def logistic(x: float) -> float:
    """Numerically stable logistic function."""

    x = np.clip(x, -20, 20)

    return 1.0 / (1.0 + np.exp(-x))


def monthly_payment(
    principal: float,
    annual_rate: float,
    term_months: int
) -> float:
    """
    Standard fixed-rate mortgage payment approximation.
    """

    monthly_rate = annual_rate / 100 / 12

    if monthly_rate == 0:
        return principal / term_months

    payment = (
        principal
        * monthly_rate
        * (1 + monthly_rate) ** term_months
        / (
            (1 + monthly_rate) ** term_months - 1
        )
    )

    return payment


def generate_balance(
    original_balance: float,
    annual_rate: float,
    age_months: int,
    term_months: int
) -> float:
    """
    Approximate remaining mortgage balance.
    """

    if age_months <= 0:
        return original_balance

    age_months = min(
        age_months,
        term_months
    )

    payment = monthly_payment(
        original_balance,
        annual_rate,
        term_months
    )

    monthly_rate = annual_rate / 100 / 12

    if monthly_rate == 0:
        balance = (
            original_balance
            - payment * age_months
        )
    else:
        balance = (
            original_balance
            * (1 + monthly_rate) ** age_months
            - payment
            * (
                ((1 + monthly_rate) ** age_months - 1)
                / monthly_rate
            )
        )

    return max(
        0,
        min(
            original_balance,
            balance
        )
    )


def risk_score(row: pd.Series) -> float:
    """
    Calculate a latent credit-risk score.

    Higher score = higher risk.
    """

    credit_score = band_to_midpoint(
        row["credit_score_band"]
    )

    ltv = ltv_midpoint(
        row["ltv_band"]
    )

    dti = dti_midpoint(
        row["dti_band"]
    )

    # Normalize components
    credit_risk = (720 - credit_score) / 120

    ltv_risk = (ltv - 60) / 40

    dti_risk = (dti - 20) / 30

    risk = (
        0.45 * credit_risk
        + 0.30 * ltv_risk
        + 0.25 * dti_risk
    )

    return float(
        np.clip(risk, -1, 2)
    )


def determine_status(
    risk: float,
    age_months: int,
    previous_status: str,
    previous_dpd: int
) -> tuple[str, int, int, bool, bool]:

    """
    Generate monthly performance state using realistic roll-rate credit transition logic.

    Returns:
        status
        days_past_due
        modification_flag
        prepayment_flag
        default_flag
    """

    # --------------------------------------------------------
    # Already terminal
    # --------------------------------------------------------

    if previous_status in {
        "Default",
        "Prepaid"
    }:

        if previous_status == "Default":

            return (
                "Default",
                90,
                0,
                False,
                True
            )

        return (
            "Prepaid",
            0,
            0,
            True,
            False
        )

    # --------------------------------------------------------
    # Age and risk effects
    # --------------------------------------------------------

    seasoning_effect = (
        0.15
        if age_months > 24
        else 0
    )

    # If the loan is already delinquent, default is much more likely
    # (a current loan rarely jumps straight to default, it rolls through delinquency first)
    default_base = -5.0
    if previous_status == "Delinquent":
        if previous_dpd == 90:
            default_base = -1.2  # Very high risk of rolling to default
        elif previous_dpd == 60:
            default_base = -2.5
        else:
            default_base = -4.0

    default_probability = logistic(
        default_base
        + 2.0 * risk
        + seasoning_effect
    )

    prepayment_probability = logistic(
        -3.2
        - 0.7 * risk
        + (0.4 if age_months > 18 else 0)
    )

    # Delinquency probability depends on previous status
    delinquency_probability = logistic(
        -3.8
        + 1.8 * risk
        + (1.5 if previous_status == "Delinquent" else 0)
    )

    random_value = rng.random()

    # --------------------------------------------------------
    # Default
    # --------------------------------------------------------

    if random_value < default_probability:

        return (
            "Default",
            90,
            int(rng.random() < 0.10),
            False,
            True
        )

    # --------------------------------------------------------
    # Prepayment
    # --------------------------------------------------------
    # Prepaid loans pay off their remaining balance. 
    # Severely delinquent loans rarely prepay (refinancing is blocked by bad credit score/status)
    if previous_status != "Delinquent" or previous_dpd <= 30:
        if (
            rng.random()
            < prepayment_probability * 0.15
        ):

            return (
                "Prepaid",
                0,
                0,
                True,
                False
            )

    # --------------------------------------------------------
    # Delinquency
    # --------------------------------------------------------

    if random_value < (
        default_probability
        + delinquency_probability
    ):

        # Roll-rate logic: DPD flow transitions logically
        if previous_status == "Current":
            dpd = 30  # Can only enter delinquency at 30 DPD
        else:
            # Already delinquent: roll forward, stay, or roll back (partial cure)
            roll_rand = rng.random()
            if previous_dpd == 30:
                if roll_rand < 0.60:
                    dpd = 60  # Roll forward to 60 DPD
                elif roll_rand < 0.90:
                    dpd = 30  # Stay at 30 DPD
                else:
                    # Fully cure to Current
                    return (
                        "Current",
                        0,
                        int(rng.random() < 0.02),
                        False,
                        False
                    )
            elif previous_dpd == 60:
                if roll_rand < 0.70:
                    dpd = 90  # Roll forward to 90 DPD
                elif roll_rand < 0.90:
                    dpd = 60  # Stay at 60 DPD
                else:
                    dpd = 30  # Partial cure back to 30 DPD
            else:  # previous_dpd == 90
                if roll_rand < 0.80:
                    dpd = 90  # Stay at 90 DPD
                else:
                    dpd = 60  # Roll back to 60 DPD

        return (
            "Delinquent",
            dpd,
            int(rng.random() < 0.05),
            False,
            False
        )

    # --------------------------------------------------------
    # Current
    # --------------------------------------------------------

    return (
        "Current",
        0,
        int(rng.random() < 0.02),
        False,
        False
    )


# ============================================================
# GENERATE ONE LOAN
# ============================================================

def generate_loan_history(
    loan: pd.Series
) -> list[dict]:

    loan_id = loan["loan_id"]

    origination_month = pd.Timestamp(
        loan["origination_month"]
    )

    original_balance = float(
        loan["original_balance"]
    )

    interest_rate = float(
        loan["interest_rate"]
    )

    # Typical mortgage term
    term_months = int(
        rng.choice(
            [180, 240, 300, 360],
            p=[0.05, 0.15, 0.15, 0.65]
        )
    )

    reporting_months = pd.date_range(
        start=origination_month,
        end=END_DATE,
        freq="MS"
    )

    records = []

    previous_status = "Current"
    previous_dpd = 0

    for month_index, reporting_month in enumerate(
        reporting_months
    ):

        age_months = month_index

        remaining_term = max(
            0,
            term_months - age_months
        )

        # Stop after loan term
        if remaining_term == 0:
            break

        current_balance = generate_balance(
            original_balance=original_balance,
            annual_rate=interest_rate,
            age_months=age_months,
            term_months=term_months
        )

        latent_risk = risk_score(loan)

        (
            current_status,
            days_past_due,
            modification_flag,
            prepayment_flag,
            default_flag
        ) = determine_status(
            risk=latent_risk,
            age_months=age_months,
            previous_status=previous_status,
            previous_dpd=previous_dpd
        )

        # ----------------------------------------------------
        # Balance adjustment for terminal events
        # ----------------------------------------------------

        if prepayment_flag:

            # Small remaining balance before payoff
            current_balance = max(
                0,
                current_balance
                * rng.uniform(0.00, 0.10)
            )

        elif default_flag:

            current_balance = max(
                0,
                current_balance
            )

        # ----------------------------------------------------
        # Loss severity
        # ----------------------------------------------------

        if default_flag:

            severity = rng.choice(
                LOSS_SEVERITY_BANDS[1:],
                p=[0.35, 0.45, 0.20]
            )

        else:

            severity = "None"

        # ----------------------------------------------------
        # Source / documentation
        # ----------------------------------------------------

        source_system = rng.choice(
            SOURCE_SYSTEMS,
            p=[0.60, 0.25, 0.15]
        )

        document_status = rng.choice(
            DOCUMENT_STATUSES
        )

        # ----------------------------------------------------
        # Last update timestamp
        # ----------------------------------------------------

        last_updated_at = (
            reporting_month
            + pd.Timedelta(
                days=int(
                    rng.integers(
                        1,
                        28
                    )
                )
            )
            + pd.Timedelta(
                hours=int(
                    rng.integers(
                        0,
                        24
                    )
                )
            )
        )

        records.append({

            "loan_id": loan_id,

            "month_index": month_index,

            "reporting_month": reporting_month,

            "origination_month": origination_month,

            "loan_age_months": age_months,

            "remaining_term_months": remaining_term,

            "original_balance": round(
                original_balance,
                2
            ),

            "current_balance": round(
                current_balance,
                2
            ),

            "interest_rate": round(
                interest_rate,
                3
            ),

            "credit_score_band":
                loan["credit_score_band"],

            "ltv_band":
                loan["ltv_band"],

            "dti_band":
                loan["dti_band"],

            "state":
                loan["state"],

            "loan_purpose":
                loan["loan_purpose"],

            "occupancy_type":
                loan["occupancy_type"],

            "property_type":
                loan["property_type"],

            "servicer_name":
                loan["servicer_name"],

            "current_status":
                current_status,

            "days_past_due":
                days_past_due,

            "modification_flag":
                modification_flag,

            "prepayment_flag":
                int(prepayment_flag),

            "default_flag":
                int(default_flag),

            "loss_severity_band":
                severity,

            "last_updated_at":
                last_updated_at,

            "source_system":
                source_system,

            "document_status":
                document_status
        })

        previous_status = current_status
        previous_dpd = days_past_due

        # ----------------------------------------------------
        # Terminal loan states
        # ----------------------------------------------------

        if current_status in {
            "Default",
            "Prepaid"
        }:

            break

    return records


# ============================================================
# ADD FUTURE TARGETS
# ============================================================

def add_future_targets(
    df: pd.DataFrame
) -> pd.DataFrame:

    df = df.sort_values(
        ["loan_id", "reporting_month"]
    ).reset_index(drop=True)

    grouped = df.groupby(
        "loan_id",
        group_keys=False
    )

    # --------------------------------------------------------
    # Future delinquency
    # --------------------------------------------------------

    df["future_delinquency"] = (
        df["current_status"]
        .eq("Delinquent")
        .astype(int)
    )

    df["next_3m_delinquency_flag"] = (
        grouped["future_delinquency"]
        .transform(
            lambda x:
            x.shift(-1)
            .rolling(
                window=3,
                min_periods=1
            )
            .max()
        )
        .fillna(0)
        .astype(int)
    )

    df["next_6m_delinquency_flag"] = (
        grouped["future_delinquency"]
        .transform(
            lambda x:
            x.shift(-1)
            .rolling(
                window=6,
                min_periods=1
            )
            .max()
        )
        .fillna(0)
        .astype(int)
    )

    # --------------------------------------------------------
    # Future default
    # --------------------------------------------------------

    df["next_12m_default_flag"] = (
        grouped["default_flag"]
        .transform(
            lambda x:
            x.shift(-1)
            .rolling(
                window=12,
                min_periods=1
            )
            .max()
        )
        .fillna(0)
        .astype(int)
    )

    # --------------------------------------------------------
    # Future prepayment
    # --------------------------------------------------------

    df["next_12m_prepayment_flag"] = (
        grouped["prepayment_flag"]
        .transform(
            lambda x:
            x.shift(-1)
            .rolling(
                window=12,
                min_periods=1
            )
            .max()
        )
        .fillna(0)
        .astype(int)
    )

    # --------------------------------------------------------
    # Next state
    # --------------------------------------------------------

    df["next_state"] = (
        grouped["current_status"]
        .shift(-1)
        .fillna("Current")
    )

    # --------------------------------------------------------
    # Exception logic
    # --------------------------------------------------------

    exception_condition = (
        (df["days_past_due"] >= 60)
        | (df["document_status"] == "Missing")
        | (df["modification_flag"] == 1)
        | (df["current_status"] == "Default")
    )

    df["exception_required"] = (
        exception_condition
        .astype(int)
    )

    df["exception_type"] = np.select(
        [
            df["days_past_due"] >= 60,
            df["document_status"] == "Missing",
            df["modification_flag"] == 1,
            df["current_status"] == "Default"
        ],
        [
            "Severe Delinquency",
            "Documentation Gap",
            "Loan Modification",
            "Default Review"
        ],
        default="None"
    )

    # --------------------------------------------------------
    # Remove helper column
    # --------------------------------------------------------

    df = df.drop(
        columns=["future_delinquency"]
    )

    return df


# ============================================================
# VALIDATION
# ============================================================

def validate_dataset(
    df: pd.DataFrame
):

    print("\nRunning validation...")

    # Required columns
    required_columns = [
        "loan_id",
        "month_index",
        "reporting_month",
        "origination_month",
        "loan_age_months",
        "remaining_term_months",
        "original_balance",
        "current_balance",
        "interest_rate",
        "credit_score_band",
        "ltv_band",
        "dti_band",
        "state",
        "loan_purpose",
        "occupancy_type",
        "property_type",
        "servicer_name",
        "current_status",
        "days_past_due",
        "modification_flag",
        "prepayment_flag",
        "default_flag",
        "loss_severity_band",
        "last_updated_at",
        "source_system",
        "document_status",
        "next_3m_delinquency_flag",
        "next_6m_delinquency_flag",
        "next_12m_default_flag",
        "next_12m_prepayment_flag",
        "next_state",
        "exception_required",
        "exception_type"
    ]

    missing_columns = set(
        required_columns
    ) - set(df.columns)

    assert not missing_columns, (
        f"Missing columns: {missing_columns}"
    )

    # No negative monetary values
    assert (
        df["original_balance"] > 0
    ).all()

    assert (
        df["current_balance"] >= 0
    ).all()

    # Current balance cannot exceed original
    assert (
        df["current_balance"]
        <= df["original_balance"]
    ).all()

    # Valid interest rate
    assert (
        df["interest_rate"]
        .between(0, 15)
        .all()
    )

    # Valid DPD
    assert (
        df["days_past_due"]
        .isin([0, 30, 60, 90])
        .all()
    )

    # Binary fields
    binary_columns = [
        "modification_flag",
        "prepayment_flag",
        "default_flag",
        "next_3m_delinquency_flag",
        "next_6m_delinquency_flag",
        "next_12m_default_flag",
        "next_12m_prepayment_flag",
        "exception_required"
    ]

    for column in binary_columns:

        assert set(
            df[column].unique()
        ).issubset({0, 1}), (
            f"Invalid binary values in {column}"
        )

    # Dates
    assert (
        df["reporting_month"]
        >= df["origination_month"]
    ).all()

    assert (
        df["reporting_month"]
        <= END_DATE
    ).all()

    # Age
    assert (
        df["loan_age_months"] >= 0
    ).all()

    # Remaining term
    assert (
        df["remaining_term_months"] >= 0
    ).all()

    # Prepaid loans should have prepayment flag
    prepaid_rows = (
        df["current_status"] == "Prepaid"
    )

    assert (
        df.loc[
            prepaid_rows,
            "prepayment_flag"
        ] == 1
    ).all()

    # Default loans should have default flag
    default_rows = (
        df["current_status"] == "Default"
    )

    assert (
        df.loc[
            default_rows,
            "default_flag"
        ] == 1
    ).all()

    print("Validation PASSED.")


# ============================================================
# MAIN
# ============================================================

def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print("=" * 70)
    print("INTAIN SYNTHETIC MONTHLY PERFORMANCE GENERATOR")
    print("=" * 70)

    # --------------------------------------------------------
    # Load static data
    # --------------------------------------------------------

    static_df = pd.read_csv(
        INPUT_FILE,
        parse_dates=[
            "origination_month"
        ]
    )

    print(
        f"Static loans loaded: "
        f"{len(static_df):,}"
    )

    # --------------------------------------------------------
    # Generate monthly records
    # --------------------------------------------------------

    all_records = []

    print("\nProcessing loan historical paths...")
    for index, loan in tqdm(static_df.iterrows(), total=len(static_df), desc="Generating Monthly Performance", bar_format="{l_bar}{bar:30}{r_bar}"):

        records = generate_loan_history(
            loan
        )

        all_records.extend(
            records
        )

    df = pd.DataFrame(
        all_records
    )

    print(
        f"\nMonthly records generated: "
        f"{len(df):,}"
    )

    # --------------------------------------------------------
    # Add future targets
    # --------------------------------------------------------

    print(
        "Generating future targets..."
    )

    df = add_future_targets(
        df
    )

    # --------------------------------------------------------
    # Sort
    # --------------------------------------------------------

    df = df.sort_values(
        [
            "loan_id",
            "reporting_month"
        ]
    ).reset_index(drop=True)

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    validate_dataset(
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
    print("TRAIN DATA GENERATED SUCCESSFULLY")
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
        f"Date range    : "
        f"{df['reporting_month'].min().date()} "
        f"→ "
        f"{df['reporting_month'].max().date()}"
    )

    print(
        f"Output        : {OUTPUT_FILE}"
    )

    print("\nTarget distribution:")

    target_columns = [
        "next_3m_delinquency_flag",
        "next_6m_delinquency_flag",
        "next_12m_default_flag",
        "next_12m_prepayment_flag"
    ]

    for column in target_columns:

        print(
            f"{column:<35}"
            f"{df[column].mean():.3%}"
        )

    print("\nStatus distribution:")

    print(
        df["current_status"]
        .value_counts(
            normalize=True
        )
        .mul(100)
        .round(2)
    )


if __name__ == "__main__":
    main()