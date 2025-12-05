#!/usr/bin/env python3
"""
forecast_promo_mix.py

Usage examples:
  python forecast_promo_mix.py
  python forecast_promo_mix.py --csv path/to/q-excel-multivariate-regression.csv
  python forecast_promo_mix.py --coef-file coeffs.json    # compute forecast only using provided coefficients

Notes:
- By default the script expects the CSV to contain columns:
    Weekly_Sales_Units, Average_price, Discount_depth, Digital_ads_spend, In_store_event
  (adjust --ycol / --xcols if your column names differ).
- Discount depth in the prompt is "16.6%" and by default the script will convert 16.6 -> 0.166
  to match common regression practice. If your CSV already stores discount as percent (16.6),
  set --discount-as-percent to True (default). If your CSV stores discount as decimal (0.166),
  run with --discount-as-percent False so the script will interpret the provided 16.6 as decimal.
- Requires: pandas, numpy, statsmodels, matplotlib, openpyxl (optional for Excel output)
"""

import argparse
import json
import os
import sys

import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt

def fit_regression(df, ycol, xcols):
    # drop NA and build X, y
    df2 = df[[ycol] + xcols].dropna()
    y = df2[ycol].astype(float)
    X = df2[xcols].astype(float)
    X = sm.add_constant(X)  # adds intercept
    model = sm.OLS(y, X).fit()
    return model, df2

def plot_diagnostics(model, df2, xcols, out_prefix="reg_diag"):
    fitted = model.fittedvalues
    resid = model.resid

    # Residuals vs Fitted
    plt.figure(figsize=(6,4))
    plt.scatter(fitted, resid)
    plt.axhline(0, color='grey', linewidth=0.8)
    plt.xlabel('Fitted values')
    plt.ylabel('Residuals')
    plt.title('Residuals vs Fitted')
    plt.tight_layout()
    plt.savefig(f"{out_prefix}_resid_vs_fitted.png", dpi=150)
    plt.close()

    # QQ plot
    fig = sm.qqplot(resid, line='45', fit=True)
    fig.suptitle('Normal Q-Q')
    fig.savefig(f"{out_prefix}_qq.png", dpi=150)
    plt.close()

    # Histogram of residuals
    plt.figure(figsize=(6,4))
    plt.hist(resid, bins=30)
    plt.xlabel('Residual')
    plt.ylabel('Frequency')
    plt.title('Residuals histogram')
    plt.tight_layout()
    plt.savefig(f"{out_prefix}_resid_hist.png", dpi=150)
    plt.close()

    # Optional: residuals over time / index
    plt.figure(figsize=(6,4))
    plt.plot(resid)
    plt.axhline(0, color='grey', linewidth=0.8)
    plt.xlabel('Observation index')
    plt.ylabel('Residual')
    plt.title('Residuals over index')
    plt.tight_layout()
    plt.savefig(f"{out_prefix}_resid_index.png", dpi=150)
    plt.close()

def compute_forecast_from_coeffs(coeffs_dict, input_values):
    """
    coeffs_dict: dict with keys matching input_values keys and 'const' for intercept (or 'Intercept')
    input_values: dict of regressor_name -> value
    """
    # Normalize key names: accept 'const' or 'Intercept' or 'const' key from statsmodels
    intercept = 0.0
    for k in ('const', 'Const', 'CONST', 'Intercept', 'intercept'):
        if k in coeffs_dict:
            intercept = float(coeffs_dict[k])
            break

    total = intercept
    missing = []
    for k, v in input_values.items():
        if k in coeffs_dict:
            total += float(coeffs_dict[k]) * float(v)
        else:
            missing.append(k)
    return total, missing

def main():
    p = argparse.ArgumentParser(description="Fit regression and forecast weekly sales for a proposed promo mix.")
    p.add_argument("--csv", default="q-excel-multivariate-regression.csv", help="Path to CSV file")
    p.add_argument("--ycol", default="Weekly_Sales_Units", help="Name of dependent variable column")
    p.add_argument("--xcols", default="Average_price,Discount_depth,Digital_ads_spend,In_store_event",
                   help="Comma-separated independent variable column names in the CSV in the same order")
    p.add_argument("--discount-as-percent", action="store_true", default=True,
                   help="If set, the script will interpret the provided discount depth (e.g. 16.6) as percent and convert to 0.166 for regression input. Default: True")
    p.add_argument("--coef-file", help="If you have regression coefficients already (json file mapping column->coef, include intercept as 'const' or 'Intercept'), script will skip fitting and only compute forecast.")
    p.add_argument("--out-prefix", default="brightcart", help="Prefix for output files (plots, summary)")
    args = p.parse_args()

    xcols = [c.strip() for c in args.xcols.split(",")]

    # Proposed campaign mix (hard-coded from user's brief)
    proposed = {
        "Average_price": 28.59,
        # user gave "16.6%" -> represent consistent with CSV units:
        "Discount_depth": 16.6,   # interpretation depends on --discount-as-percent
        "Digital_ads_spend": 15790,
        "In_store_event": 0
    }

    # If discount-as-percent True, convert 16.6 -> 0.166
    if args.discount_as_percent:
        proposed["Discount_depth"] = proposed["Discount_depth"] / 100.0

    # If user provided coefficients file, compute forecast directly
    if args.coef_file:
        if not os.path.exists(args.coef_file):
            print(f"Coefficient file {args.coef_file} not found.", file=sys.stderr)
            sys.exit(2)
        with open(args.coef_file, "r") as fh:
            coeffs = json.load(fh)
        forecast, missing = compute_forecast_from_coeffs(coeffs, proposed)
        print("Forecast computed from provided coefficients file.")
        print(f"Input values used (after potential percent->decimal conversion):\n{proposed}")
        print(f"Missing regressors not found in coefficient file: {missing}")
        print(f"Forecasted Weekly_Sales_Units = {forecast:.2f}")
        # write to a tiny JSON and text file
        with open(f"{args.out_prefix}_forecast_from_coeffs.json", "w") as fh:
            json.dump({"forecast": forecast, "inputs": proposed, "missing_regressors": missing}, fh, indent=2)
        print(f"Wrote results to {args.out_prefix}_forecast_from_coeffs.json")
        return

    # Fit regression using CSV
    if not os.path.exists(args.csv):
        print(f"CSV file {args.csv} not found in current folder. Provide correct path with --csv", file=sys.stderr)
        sys.exit(2)
    df = pd.read_csv(args.csv)
    print(f"Loaded CSV {args.csv} with shape {df.shape}")

    # If Discount_depth column is in percent in CSV but you converted proposed to decimal,
    # you should ensure both are consistent. We assume user will set flag appropriately.
    try:
        model, df2 = fit_regression(df, args.ycol, xcols)
    except Exception as e:
        print("Error fitting regression:", e, file=sys.stderr)
        sys.exit(3)

    # Print concise regression outputs similar to Excel's Regression output
    print("\n===== Regression summary (statsmodels OLS) =====\n")
    print(model.summary())  # full summary
    # Save summary to text
    with open(f"{args.out_prefix}_regression_summary.txt", "w") as fh:
        fh.write(model.summary().as_text())
    print(f"\nSaved regression summary to {args.out_prefix}_regression_summary.txt")

    # Diagnostics
    adj_r2 = model.rsquared_adj
    print(f"\nAdjusted R-squared: {adj_r2:.4f}")
    print("Coefficients:")
    coeffs = model.params.to_dict()
    for name, val in coeffs.items():
        print(f"  {name}: {val:.6g}")

    # Residual diagnostics plots
    plot_diagnostics(model, df2, xcols, out_prefix=args.out_prefix)
    print(f"Saved diagnostic plots with prefix '{args.out_prefix}_*png'")

    # Build input vector in the same unit convention as the X columns.
    # Key assumption: xcols names match proposed keys (case-sensitive). If not, user must map names.
    input_values = {}
    for name in xcols:
        if name not in proposed:
            print(f"Warning: proposed inputs do not contain column '{name}'. Trying to find a close match...", file=sys.stderr)
            # try case-insensitive match
            matched = None
            for k in proposed.keys():
                if k.lower() == name.lower():
                    matched = k
                    break
            if matched:
                input_values[name] = proposed[matched]
                print(f"  Matched {name} -> using proposed['{matched}'] = {proposed[matched]}")
            else:
                print(f"  No match found for '{name}'. Setting to 0.0")
                input_values[name] = 0.0
        else:
            input_values[name] = proposed[name]

    # Compute forecast using fitted coefficients (model.params)
    # model.params includes 'const' if add_constant used
    coef_dict = model.params.to_dict()
    forecast, missing = compute_forecast_from_coeffs(coef_dict, input_values)
    print("\n===== Forecast =====")
    print("Inputs (as used):")
    for k, v in input_values.items():
        print(f"  {k}: {v}")
    if missing:
        print(f"Missing regressors in model coefficients: {missing}")
    print(f"\nForecasted Weekly_Sales_Units = {forecast:.2f}")

    # Write forecast to a small CSV / excel
    out_df = pd.DataFrame([{
        "Weekly_Sales_Forecast_Units": float(forecast),
        **{f"input_{k}": float(v) for k, v in input_values.items()}
    }])
    out_df.to_csv(f"{args.out_prefix}_forecast.csv", index=False)
    try:
        out_df.to_excel(f"{args.out_prefix}_forecast.xlsx", index=False)
    except Exception:
        # openpyxl may not be installed; ignore if fails
        pass
    print(f"Wrote forecast to {args.out_prefix}_forecast.csv (and .xlsx if possible)")

    print("\nIf you want exact parity with Excel's Data Analysis output, export the regression summary text file and compare the coefficients, standard errors, t-stats and p-values printed above with Excel's output.")

if __name__ == "__main__":
    main()
