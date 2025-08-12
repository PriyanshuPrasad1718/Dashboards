import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import numpy as np

# Set page config to increase dashboard width
st.set_page_config(layout="wide")

# Load the data (replace 'data.csv' with your actual data file)
df = pd.read_csv(r"C:\Users\priya\ALGO8 AI PRIVATE LIMITED\Pwani Digital - Modern Trade additional data\nielsen_data_pipeline\__databases\FinalNielsenData.csv")

# Start with the original DataFrame
filtered_df_global = df.copy()

# Function to remove NaN and check if only NaN remains
def get_valid_options(column, df_subset):
    options = df_subset[column].dropna().unique()
    return options.tolist() if len(options) > 0 else []

# Global filters (applied to entire page)
col1, col2, col3, col4 = st.columns(4)

with col1:
    category_options = get_valid_options("Category", filtered_df_global)
    categories = st.multiselect("Category", category_options, key="cat_global")
    if categories:
        filtered_df_global = filtered_df_global[filtered_df_global["Category"].isin(categories)]

with col2:
    manufacturer_options = get_valid_options("Manufacturer", filtered_df_global)
    manufacturers = st.multiselect("Manufacturer", manufacturer_options, key="man_global")
    if manufacturers:
        filtered_df_global = filtered_df_global[filtered_df_global["Manufacturer"].isin(manufacturers)]

with col3:
    facts_options = get_valid_options("Facts", filtered_df_global)
    facts = st.multiselect("Facts", facts_options, key="fac_global")
    if facts:
        filtered_df_global = filtered_df_global[filtered_df_global["Facts"].isin(facts)]

with col4:
    calculation = st.selectbox("Calculation", ["Year", "Half-Yearly", "Month", "Quarter", "Monthly Average", "Quarterly Average"], key="calc_global")

# Additional global filters
col5, col6 = st.columns(2)

with col5:
    usp_options = get_valid_options("USP", filtered_df_global)
    usps = st.multiselect("USP", usp_options, key="usp_global")
    if usps:
        filtered_df_global = filtered_df_global[filtered_df_global["USP"].isin(usps)]

with col6:
    type_options = get_valid_options("Type", filtered_df_global)
    types = st.multiselect("Type", type_options, key="typ_global")
    if types:
        filtered_df_global = filtered_df_global[filtered_df_global["Type"].isin(types)]

# First part: Top 10 Brands and Sales Comparison
filtered_df_part1 = filtered_df_global.copy()

# Channel, Area, Region together for first part (mutually exclusive)
col7, col8, col9 = st.columns(3)

channel_selection = st.session_state.get("chan_part1", [])
area_selection = st.session_state.get("area_part1", [])
region_selection = st.session_state.get("reg_part1", [])
any_selected_part1 = bool(channel_selection) or bool(area_selection) or bool(region_selection)

with col7:
    channel_options_part1 = get_valid_options("Channel", filtered_df_part1)
    channel_disabled_part1 = any_selected_part1 and not channel_selection
    channels_part1 = st.multiselect("Channel", channel_options_part1, key="chan_part1", disabled=channel_disabled_part1 or len(channel_options_part1) == 0)
    if channels_part1:
        filtered_df_part1 = filtered_df_part1[filtered_df_part1["Channel"].isin(channels_part1)]

with col8:
    area_options_part1 = get_valid_options("Area", filtered_df_part1)
    area_disabled_part1 = any_selected_part1 and not area_selection
    areas_part1 = st.multiselect("Area", area_options_part1, key="area_part1", disabled=area_disabled_part1 or len(area_options_part1) == 0)
    if areas_part1:
        filtered_df_part1 = filtered_df_part1[filtered_df_part1["Area"].isin(areas_part1)]

with col9:
    region_options_part1 = get_valid_options("Region", filtered_df_part1)
    region_disabled_part1 = any_selected_part1 and not region_selection
    regions_part1 = st.multiselect("Region", region_options_part1, key="reg_part1", disabled=region_disabled_part1 or len(region_options_part1) == 0)
    if regions_part1:
        filtered_df_part1 = filtered_df_part1[filtered_df_part1["Region"].isin(regions_part1)]

# Aggregate data by Brand for first part
brand_sales_part1 = filtered_df_part1.groupby("Brand").sum(numeric_only=True).reset_index()

# Handle the Calculation filter for first part
if calculation == "Year":
    prev_col, curr_col = "Previous Year", "Current Year"
elif calculation == "Half-Yearly":
    prev_col, curr_col = "Previous Half Year", "Current Half Year"
elif calculation == "Month":
    prev_col, curr_col = "Previous Month", "Current Month"
elif calculation == "Quarter":
    prev_col, curr_col = "Previous Quarter", "Current Quarter"
elif calculation == "Monthly Average":
    brand_sales_part1["Previous Sales"] = brand_sales_part1["Previous Year"] / 12
    brand_sales_part1["Current Sales"] = brand_sales_part1["Current Year"] / 12
    prev_col, curr_col = "Previous Sales", "Current Sales"
elif calculation == "Quarterly Average":
    brand_sales_part1["Previous Sales"] = brand_sales_part1["Previous Year"] / 4
    brand_sales_part1["Current Sales"] = brand_sales_part1["Current Year"] / 4
    prev_col, curr_col = "Previous Sales", "Current Sales"

# Extract sales if not averaging
if calculation not in ["Monthly Average", "Quarterly Average"]:
    brand_sales_part1["Previous Sales"] = brand_sales_part1[prev_col]
    brand_sales_part1["Current Sales"] = brand_sales_part1[curr_col]

# Calculate metrics for first part
brand_sales_part1["% Growth in Sales"] = (
    (brand_sales_part1["Current Sales"] - brand_sales_part1["Previous Sales"]) / 
    brand_sales_part1["Previous Sales"].replace(0, float("nan")) * 100
).fillna(0)

total_prev_sales_part1 = brand_sales_part1["Previous Sales"].sum()
total_curr_sales_part1 = brand_sales_part1["Current Sales"].sum()

brand_sales_part1["Previous Market Share"] = (brand_sales_part1["Previous Sales"] / total_prev_sales_part1 * 100).fillna(0)
brand_sales_part1["Current Market Share"] = (brand_sales_part1["Current Sales"] / total_curr_sales_part1 * 100).fillna(0)

# Identify top 10 brands for first part
top_10_brands_part1 = brand_sales_part1.sort_values("Current Sales", ascending=False).head(10)

# Prepare table data for first part (full sales values)
table_df_part1 = top_10_brands_part1[["Brand", "Previous Sales", "Current Sales", 
                                     "% Growth in Sales", "Previous Market Share", "Current Market Share"]].copy()
table_df_part1["Previous Sales"] = table_df_part1["Previous Sales"].apply(lambda x: f"{x:,.2f}")
table_df_part1["Current Sales"] = table_df_part1["Current Sales"].apply(lambda x: f"{x:,.2f}")
table_df_part1["% Growth in Sales"] = table_df_part1["% Growth in Sales"].apply(lambda x: f"{x:.3f}%")
table_df_part1["Previous Market Share"] = table_df_part1["Previous Market Share"].apply(lambda x: f"{x:.3f}%")
table_df_part1["Current Market Share"] = table_df_part1["Current Market Share"].apply(lambda x: f"{x:.3f}%")

# Toggle for first chart
view_part1 = st.radio("View", ["Sales", "Market Share"], horizontal=True, key="view_part1")

# Create bar chart for first part
fig_part1 = go.Figure()
if view_part1 == "Sales":
    fig_part1.add_trace(go.Bar(
        y=top_10_brands_part1["Brand"],
        x=top_10_brands_part1["Previous Sales"],
        name="Previous (Apr 2023 - Mar 2024)",
        orientation="h",
        marker_color="lightblue",
        text=[f"{x:,.0f}" for x in top_10_brands_part1["Previous Sales"]],
        textposition="auto"
    ))
    fig_part1.add_trace(go.Bar(
        y=top_10_brands_part1["Brand"],
        x=top_10_brands_part1["Current Sales"],
        name="Current (Apr 2024 - Mar 2025)",
        orientation="h",
        marker_color="darkblue",
        text=[f"{x:,.0f}" for x in top_10_brands_part1["Current Sales"]],
        textposition="auto"
    ))
    yaxis_title = "Sales"
else:
    fig_part1.add_trace(go.Bar(
        y=top_10_brands_part1["Brand"],
        x=top_10_brands_part1["Previous Market Share"],
        name="Previous Market Share",
        orientation="h",
        marker_color="lightblue",
        text=[f"{x:.1f}%" for x in top_10_brands_part1["Previous Market Share"]],
        textposition="auto"
    ))
    fig_part1.add_trace(go.Bar(
        y=top_10_brands_part1["Brand"],
        x=top_10_brands_part1["Current Market Share"],
        name="Current Market Share",
        orientation="h",
        marker_color="darkblue",
        text=[f"{x:.1f}%" for x in top_10_brands_part1["Current Market Share"]],
        textposition="auto"
    ))
    yaxis_title = "Market Share (%)"

fig_part1.update_layout(
    barmode="group",
    xaxis_title=yaxis_title,
    yaxis_title="Brand",
    legend=dict(x=0.7, y=1.1, orientation="h"),
    height=400,
    template="plotly_white",
    margin=dict(l=50, r=50, t=50, b=50),
    font=dict(size=12)
)

# Display first part
col_left1, col_right1 = st.columns(2)
with col_left1:
    st.subheader("Top 10 Brands")
    st.dataframe(table_df_part1)
with col_right1:
    st.subheader("Sales Comparison")
    st.radio("", [], key="dummy1")  # Placeholder for alignment
    st.plotly_chart(fig_part1)

# Second part: Sales By table with specific filters
st.subheader("Sales By")
col10, col11 = st.columns(2)

with col10:
    value_options = ["Channel", "Area", "Region", "Variant", "SKUs"]
    selected_value = st.selectbox("Value", value_options, key="value_select")

with col11:
    brand_options = get_valid_options("Brand", filtered_df_global)
    selected_brands = st.multiselect("Brand", brand_options, key="brand_select")
    if selected_brands:
        filtered_df_global = filtered_df_global[filtered_df_global["Brand"].isin(selected_brands)]

# Filter data for second part based on selected value
filtered_df_part2 = filtered_df_global.copy()
if selected_value == "Channel":
    channel_options_part2 = get_valid_options("Channel", filtered_df_part2)
    channels_part2 = st.multiselect("Channel", channel_options_part2, key="chan_part2")
    if channels_part2:
        filtered_df_part2 = filtered_df_part2[filtered_df_part2["Channel"].isin(channels_part2)]
elif selected_value == "Area":
    area_options_part2 = get_valid_options("Area", filtered_df_part2)
    areas_part2 = st.multiselect("Area", area_options_part2, key="area_part2")
    if areas_part2:
        filtered_df_part2 = filtered_df_part2[filtered_df_part2["Area"].isin(areas_part2)]
elif selected_value == "Region":
    region_options_part2 = get_valid_options("Region", filtered_df_part2)
    regions_part2 = st.multiselect("Region", region_options_part2, key="reg_part2")
    if regions_part2:
        filtered_df_part2 = filtered_df_part2[filtered_df_part2["Region"].isin(regions_part2)]
elif selected_value == "Variant":
    variant_options_part2 = get_valid_options("Variant", filtered_df_part2)
    variants_part2 = st.multiselect("Variant", variant_options_part2, key="var_part2")
    if variants_part2:
        filtered_df_part2 = filtered_df_part2[filtered_df_part2["Variant"].isin(variants_part2)]
elif selected_value == "SKUs":
    sku_options_part2 = get_valid_options("SKU", filtered_df_part2)
    skus_part2 = st.multiselect("SKUs", sku_options_part2, key="sku_part2")
    if skus_part2:
        filtered_df_part2 = filtered_df_part2[filtered_df_part2["SKU"].isin(skus_part2)]

# Aggregate data by the selected value for second part
brand_sales_part2 = filtered_df_part2.groupby(selected_value).sum(numeric_only=True).reset_index()

# Handle the Calculation filter for second part
if calculation == "Year":
    prev_col, curr_col = "Previous Year", "Current Year"
elif calculation == "Half-Yearly":
    prev_col, curr_col = "Previous Half Year", "Current Half Year"
elif calculation == "Month":
    prev_col, curr_col = "Previous Month", "Current Month"
elif calculation == "Quarter":
    prev_col, curr_col = "Previous Quarter", "Current Quarter"
elif calculation == "Monthly Average":
    brand_sales_part2["Previous Sales"] = brand_sales_part2["Previous Year"] / 12
    brand_sales_part2["Current Sales"] = brand_sales_part2["Current Year"] / 12
    prev_col, curr_col = "Previous Sales", "Current Sales"
elif calculation == "Quarterly Average":
    brand_sales_part2["Previous Sales"] = brand_sales_part2["Previous Year"] / 4
    brand_sales_part2["Current Sales"] = brand_sales_part2["Current Year"] / 4
    prev_col, curr_col = "Previous Sales", "Current Sales"

# Extract sales if not averaging
if calculation not in ["Monthly Average", "Quarterly Average"]:
    brand_sales_part2["Previous Sales"] = brand_sales_part2[prev_col]
    brand_sales_part2["Current Sales"] = brand_sales_part2[curr_col]

# Calculate metrics for second part
brand_sales_part2["% Growth in Sales"] = (
    (brand_sales_part2["Current Sales"] - brand_sales_part2["Previous Sales"]) / 
    brand_sales_part2["Previous Sales"].replace(0, float("nan")) * 100
).fillna(0)

total_prev_sales_part2 = brand_sales_part2["Previous Sales"].sum()
total_curr_sales_part2 = brand_sales_part2["Current Sales"].sum()

brand_sales_part2["Previous Market Share"] = (brand_sales_part2["Previous Sales"] / total_prev_sales_part2 * 100).fillna(0)
brand_sales_part2["Current Market Share"] = (brand_sales_part2["Current Sales"] / total_curr_sales_part2 * 100).fillna(0)

# Prepare table data for second part
table_df_part2 = brand_sales_part2[[selected_value, "Previous Sales", "Current Sales", 
                                   "% Growth in Sales", "Previous Market Share", "Current Market Share"]].copy()
table_df_part2.columns = ["Value", "Previous Sales", "Current Sales", 
                         "% Growth in Sales", "Previous Market Share", "Current Market Share"]
table_df_part2["Previous Sales"] = table_df_part2["Previous Sales"].apply(lambda x: f"{x:,.2f}")
table_df_part2["Current Sales"] = table_df_part2["Current Sales"].apply(lambda x: f"{x:,.2f}")
table_df_part2["% Growth in Sales"] = table_df_part2["% Growth in Sales"].apply(lambda x: f"{x:.3f}%")
table_df_part2["Previous Market Share"] = table_df_part2["Previous Market Share"].apply(lambda x: f"{x:.3f}%")
table_df_part2["Current Market Share"] = table_df_part2["Current Market Share"].apply(lambda x: f"{x:.3f}%")

# Toggle for second chart
view_part2 = st.radio("View", ["Sales", "Market Share"], horizontal=True, key="view_part2")

# Create bar chart for second part
fig_part2 = go.Figure()
if view_part2 == "Sales":
    fig_part2.add_trace(go.Bar(
        y=table_df_part2["Value"],
        x=table_df_part2["Previous Sales"].str.replace(',', '').astype(float),
        name="Previous (Apr 2023 - Mar 2024)",
        orientation="h",
        marker_color="lightblue",
        text=table_df_part2["Previous Sales"],
        textposition="auto"
    ))
    fig_part2.add_trace(go.Bar(
        y=table_df_part2["Value"],
        x=table_df_part2["Current Sales"].str.replace(',', '').astype(float),
        name="Current (Apr 2024 - Mar 2025)",
        orientation="h",
        marker_color="darkblue",
        text=table_df_part2["Current Sales"],
        textposition="auto"
    ))
    yaxis_title_part2 = "Sales"
else:
    fig_part2.add_trace(go.Bar(
        y=table_df_part2["Value"],
        x=table_df_part2["Previous Market Share"].str.replace('%', '').astype(float),
        name="Previous Market Share",
        orientation="h",
        marker_color="lightblue",
        text=table_df_part2["Previous Market Share"],
        textposition="auto"
    ))
    fig_part2.add_trace(go.Bar(
        y=table_df_part2["Value"],
        x=table_df_part2["Current Market Share"].str.replace('%', '').astype(float),
        name="Current Market Share",
        orientation="h",
        marker_color="darkblue",
        text=table_df_part2["Current Market Share"],
        textposition="auto"
    ))
    yaxis_title_part2 = "Market Share (%)"

fig_part2.update_layout(
    barmode="group",
    xaxis_title=yaxis_title_part2,
    yaxis_title=selected_value,
    legend=dict(x=0.7, y=1.1, orientation="h"),
    height=400,
    template="plotly_white",
    margin=dict(l=50, r=50, t=50, b=50),
    font=dict(size=12)
)

# Display second part
col_left2, col_right2 = st.columns(2)
with col_left2:
    st.dataframe(table_df_part2)
with col_right2:
    st.plotly_chart(fig_part2)

# Third part: Matrices with row and column selection
st.subheader("Matrices")
col12, col13 = st.columns(2)

with col12:
    row_options = ["Brand", "Area", "Region", "Channel", "Variant", "SKU"]  # Corrected to "Brand" and "SKU"
    selected_row = st.selectbox("Rows", row_options, index=row_options.index("Brand"), key="row_select")

with col13:
    col_options = ["Area", "Region", "Channel", "Variant", "SKU", "Brand"]  # Corrected to "Brand" and "SKU"
    selected_col = st.selectbox("Columns", col_options, index=col_options.index("Area"), key="col_select")

# Filter data for third part (using global filtered data)
filtered_df_part3 = filtered_df_global.copy()

# Aggregate data by selected row and column
pivot_data = filtered_df_part3.groupby([selected_row, selected_col]).sum(numeric_only=True).reset_index()

# Pivot the data for sales
pivot_table_sales = pivot_data.pivot_table(index=selected_row, columns=selected_col, values="Current Year", aggfunc="sum", fill_value=0)

# Calculate totals for sales
pivot_table_sales["Total"] = pivot_table_sales.sum(axis=1)
pivot_table_sales.loc["Market Total"] = pivot_table_sales.sum()

# For market share, normalize each column to percentage
pivot_table_ms = pivot_table_sales.drop("Total", axis=1).drop("Market Total", axis=0)
for col in pivot_table_ms.columns:
    pivot_table_ms[col] = (pivot_table_ms[col] / pivot_table_ms[col].sum() * 100).fillna(0)

# Toggle for third chart
view_part3 = st.radio("View", ["Sales", "Market Share"], horizontal=True, key="view_part3")

# Prepare table data with formatted sales (always show sales in table)
table_df_part3 = pivot_table_sales.copy()
for col in table_df_part3.columns:
    table_df_part3[col] = table_df_part3[col].apply(lambda x: f"{x:,.2f}")

# Create bar chart for third part (grouped bar)
fig_part3 = go.Figure()
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']  # Consistent colors

if view_part3 == "Sales":
    pivot_df = pivot_table_sales.drop("Market Total", axis=0).drop("Total", axis=1)
    yaxis_title_part3 = "Sales"
else:
    pivot_df = pivot_table_ms
    yaxis_title_part3 = "Market Share (%)"

for i, col in enumerate(pivot_df.columns):
    fig_part3.add_trace(go.Bar(
        x=pivot_df.index,
        y=pivot_df[col],
        name=col,
        marker_color=colors[i % len(colors)],
        text=[f"{y:.1f}" if view_part3 == "Sales" else f"{y:.1f}%" for y in pivot_df[col]],
        textposition="auto"
    ))

fig_part3.update_layout(
    barmode="group",
    xaxis_title=selected_row,
    yaxis_title=yaxis_title_part3,
    legend=dict(x=0.7, y=1.1, orientation="h"),
    height=400,
    template="plotly_white",
    margin=dict(l=50, r=50, t=50, b=50),
    font=dict(size=12)
)

# Display third part
col_left3, col_right3 = st.columns(2)
with col_left3:
    st.dataframe(table_df_part3)
with col_right3:
    st.plotly_chart(fig_part3)