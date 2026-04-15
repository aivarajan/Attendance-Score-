# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 16:45:22 2026

@author: GITAA029
"""

# -*- coding: utf-8 -*-
"""
Updated Dataset Mapping Tool
Enhancements:
1. Handles duplicate keys → takes highest value
2. Removes invalid/unmapped values
"""

import streamlit as st
import pandas as pd
from io import BytesIO

st.title("Dataset Mapping Tool")

# Upload files
file1 = st.file_uploader("Upload Sheet1 (Source)", type=["csv", "xlsx"])
file2 = st.file_uploader("Upload Sheet2 (Target)", type=["csv", "xlsx"])

def read_file(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)

if file1 and file2:
    df1 = read_file(file1)
    df2 = read_file(file2)

    # Clean column names
    df1.columns = df1.columns.str.strip()
    df2.columns = df2.columns.str.strip()

    # Preview
    st.subheader("Sheet1 Columns")
    st.write(", ".join(df1.columns))

    st.subheader("Sheet2 Columns")
    st.write(", ".join(df2.columns))

    st.subheader("Sheet1 Preview")
    st.dataframe(df1.head())

    st.subheader("Sheet2 Preview")
    st.dataframe(df2.head())

    st.markdown("---")

    # Mapping inputs
    st.subheader("Enter Mapping Details")

    sheet1_key = st.text_input("Column in Sheet1 (e.g., Email_ID)")
    sheet2_key = st.text_input("Column in Sheet2 (e.g., Email)")
    source_col = st.text_input("Column to Copy from Sheet1 (e.g., Score)")
    target_col = st.text_input("Column to Paste in Sheet2")

    if st.button("Run Mapping"):
        try:
            # Normalize keys
            df1[sheet1_key] = df1[sheet1_key].astype(str).str.strip().str.lower()
            df2[sheet2_key] = df2[sheet2_key].astype(str).str.strip().str.lower()

            # Ensure numeric source column
            df1[source_col] = pd.to_numeric(df1[source_col], errors='coerce')

            # ✅ FIX 1: Handle duplicates → take highest value per key
            df1_agg = df1.groupby(sheet1_key)[source_col].max().reset_index()

            # Create mapping dictionary
            mapping_dict = df1_agg.set_index(sheet1_key)[source_col].to_dict()

            # Apply mapping
            df2[target_col] = df2[sheet2_key].map(mapping_dict)

            # Convert to numeric
            df2[target_col] = pd.to_numeric(df2[target_col], errors='coerce')

            # ✅ FIX 2: Remove unwanted / invalid values
            df2 = df2.dropna(subset=[target_col])

            # Round and convert
            df2[target_col] = df2[target_col].round(0).astype("Int64")

            st.success("Mapping Completed ✅")

            st.subheader("Updated Sheet2 Preview")
            st.dataframe(df2.head())

            # Download output
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df2.to_excel(writer, index=False)

            st.download_button(
                "Download Updated Excel",
                data=output.getvalue(),
                file_name="updated_sheet2.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:
            st.error(f"Error: {e}")