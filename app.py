import streamlit as st
import pandas as pd
import plotly.express as px

# PAGE CONFIG

st.set_page_config(
    page_title="🚚 Factory-to-Customer Shipping Route Efficiency Analysis for Nassau Candy Distributor 📦",
    layout="wide"
)

# CUSTOM CSS

st.markdown("""
<style>
.stApp {
    background: linear-gradient(to bottom, #0b0617, #14091f);
    color: white;
}

.glass {
    background: rgba(255,255,255,0.05);
    border-radius: 20px;
    padding: 20px;
    backdrop-filter: blur(15px);
    box-shadow: 0px 0px 20px rgba(168,85,247,0.25);
    margin-bottom: 20px;
}

.kpi-value {
    font-size: 30px;
    font-weight: bold;
    color: #c084fc;
}

.kpi-label {
    color: #d1d5db;
    font-size: 14px;
}

table {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)


# LOAD DATA

@st.cache_data
def load_data():
    df = pd.read_csv(r"C:\Users\venne\Downloads\Final Nassau Candy Distributor Project-2.csv")
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["ship_date"] = pd.to_datetime(df["ship_date"])
     # Calculate lead time in full days
    df["lead_time_days"] = pd.to_numeric(
        (df["ship_date"] - df["order_date"]).dt.days, downcast='integer'
    )
    return df

df = load_data()

# STATE ABBREVIATIONS

state_abbrev = {
    'Alabama':'AL','Arizona':'AZ','Arkansas':'AR','California':'CA',
    'Colorado':'CO','Connecticut':'CT','Delaware':'DE','Florida':'FL',
    'Georgia':'GA','Idaho':'ID','Illinois':'IL','Indiana':'IN',
    'Iowa':'IA','Kansas':'KS','Kentucky':'KY','Louisiana':'LA',
    'Maine':'ME','Maryland':'MD','Massachusetts':'MA','Michigan':'MI',
    'Minnesota':'MN','Mississippi':'MS','Missouri':'MO','Montana':'MT',
    'Nebraska':'NE','Nevada':'NV','New Hampshire':'NH','New Jersey':'NJ',
    'New Mexico':'NM','New York':'NY','North Carolina':'NC',
    'North Dakota':'ND','Ohio':'OH','Oklahoma':'OK','Oregon':'OR',
    'Pennsylvania':'PA','Rhode Island':'RI','South Carolina':'SC',
    'South Dakota':'SD','Tennessee':'TN','Texas':'TX','Utah':'UT',
    'Vermont':'VT','Virginia':'VA','Washington':'WA',
    'West Virginia':'WV','Wisconsin':'WI','Wyoming':'WY'
}

# SIDEBAR FILTERS
st.sidebar.title("🎛️ Dashboard Filters")

# Date range filter
min_date = df["order_date"].min()
max_date = df["order_date"].max()

date_filter = st.sidebar.date_input(
    "📅 Date Range",
    [min_date, max_date]
)

region_filter = st.sidebar.multiselect(
    "🌍 Region",
    df["region"].unique(),
    default=df["region"].unique()
)

state_filter = st.sidebar.multiselect(
    "📍State",
    df["state/province"].unique(),
    default=df["state/province"].unique()
)

ship_mode_filter = st.sidebar.multiselect(
    "🚚 Ship Mode",
    df["ship_mode"].unique(),
    default=df["ship_mode"].unique()
)

lead_threshold = st.sidebar.slider(
    "⏱️ Lead Time Threshold",
    int(df["lead_time_days"].min()),
    int(df["lead_time_days"].max()),
    int(df["lead_time_days"].max())
)


# FILTER DATA

filtered_df = df[
    (df["order_date"] >= pd.to_datetime(date_filter[0])) &
    (df["order_date"] <= pd.to_datetime(date_filter[1])) &
    (df["region"].isin(region_filter)) &
    (df["state/province"].isin(state_filter)) &
    (df["ship_mode"].isin(ship_mode_filter)) &
    (df["lead_time_days"] <= lead_threshold)
]


# KPI METRICS

avg_lead = round(filtered_df["lead_time_days"].mean(), 2)
total_orders = filtered_df.shape[0]
total_profit = round(filtered_df["gross_profit"].sum(), 2)
total_sales = round(filtered_df["sales"].sum(), 2)
delay_orders = filtered_df[filtered_df["lead_time_days"] > 4].shape[0]

delay_rate = round(
    (delay_orders / total_orders) * 100, 2
) if total_orders else 0


# HEADER

st.title("🚚 Factory-to-Customer Shipping Route Efficiency Analysis for Nassau Candy Distributor📦")


# KPI CARDS

k1, k2, k3, k4, k5 = st.columns(5)

metrics = [
    (avg_lead, "⏳ Avg Lead Time"),
    (total_orders, "📦 Total Orders"),
    (delay_rate, "🚨 Delay Rate %"),
    (total_profit, "💰 Total Profit"),
    (total_sales, "📈 Total Sales")
]

for col, (value, label) in zip([k1, k2, k3, k4, k5], metrics):
    with col:
        st.markdown(f"""
        <div class="glass">
            <div class="kpi-value">{value}</div>
            <div class="kpi-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

theme_color = "#9247d7"  # Tailwind's purple-500


# 1. ROUTE EFFICIENCY OVERVIEW

st.subheader("📊 Route Efficiency Overview")

route_df = filtered_df.groupby(
    "state/province"
)["lead_time_days"].mean().round(2).reset_index()

fig1 = px.bar(
    route_df,
    x="state/province",
    y="lead_time_days",
    title="Average Lead Time by Route"
)

fig1.update_traces(marker_color=theme_color)
fig1.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="white"
)

st.plotly_chart(fig1, use_container_width=True)

# Leaderboard
st.subheader("🏆 Route Performance Leaderboard")

leaderboard = route_df.sort_values(
    by="lead_time_days"
).head(10)

st.dataframe(leaderboard, use_container_width=True)


# 2. GEOGRAPHIC SHIPPING MAP

st.subheader("🌍 US Shipping Efficiency Heatmap")

map_df = filtered_df.groupby(
    "state/province"
)["lead_time_days"].mean().round(2).reset_index()

map_df["state_code"] = map_df["state/province"].map(state_abbrev)

fig2 = px.choropleth(
    map_df,
    locations="state_code",
    locationmode="USA-states",
    color="lead_time_days",
    scope="usa"
)

fig2.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    font_color="white"
)

st.plotly_chart(fig2, use_container_width=True)

# Regional bottlenecks
st.subheader("🚨 Regional Bottleneck Visualization")

region_df = filtered_df.groupby(
    "region"
)["lead_time_days"].mean().round(2).reset_index()

fig3 = px.bar(
    region_df,
    x="region",
    y="lead_time_days"
)

fig3.update_traces(marker_color=theme_color)
fig3.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="white"
)

st.plotly_chart(fig3, use_container_width=True)


# 3. SHIP MODE COMPARISON

st.subheader("🚛 Ship Mode Comparison")

ship_mode_df = filtered_df.groupby(
    "ship_mode"
)["lead_time_days"].mean().round(2).reset_index()

fig4 = px.bar(
    ship_mode_df,
    x="ship_mode",
    y="lead_time_days"
)

fig4.update_traces(marker_color=theme_color)
fig4.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="white"
)

st.plotly_chart(fig4, use_container_width=True)


# 4. ROUTE DRILL-DOWN

st.subheader("📍 State-Level Performance Insights")

state_drill = filtered_df.groupby(
    ["state/province", "shipment_status"]
)["lead_time_days"].mean().round(2).reset_index()

st.dataframe(state_drill, use_container_width=True)

st.subheader("📦 Order-Level Shipment Timeline")

fig5 = px.timeline(
    filtered_df,
    x_start="order_date",
    x_end="ship_date",
    y="order_id",
    color="ship_mode"
)

fig5.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="white"
)

st.plotly_chart(fig5, use_container_width=True)