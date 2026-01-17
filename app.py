# ============================================================================
# RETAIL SALES ANALYTICS - INTERACTIVE DASHBOARD
# Streamlit Web Application
# ============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="Sales Analytics", page_icon="📊", layout="wide")

st.markdown("""
    <style>
    .main {padding: 2rem;}
    .stMetric {
        background-color: #f0f2f6; 
        padding: 1rem; 
        border-radius: 0.5rem;
    }
    /* Fix text color visibility in metrics */
    .stMetric label {
        color: #31333F !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #31333F !important;
    }
    .stMetric [data-testid="stMetricDelta"] {
        color: #09AB3B !important;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# LOAD DATA
# ============================================================================

@st.cache_data
def load_data():
    try:
        sales_df = pd.read_csv('retail_sales_data.csv')
        sales_df['Order_Date'] = pd.to_datetime(sales_df['Order_Date'])
        
        rfm_df = pd.read_csv('customer_rfm_segments.csv')
        associations_df = pd.read_csv('product_associations.csv')
        forecast_df = pd.read_csv('sales_forecast.csv')
        forecast_df['Month'] = pd.to_datetime(forecast_df['Month'])
        
        return sales_df, rfm_df, associations_df, forecast_df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None, None

sales_df, rfm_df, associations_df, forecast_df = load_data()

# ============================================================================
# HEADER
# ============================================================================

st.title("📊 Retail Sales Analytics Dashboard")
st.markdown("### Business Intelligence & Forecasting Platform")
st.markdown("---")

# ============================================================================
# SIDEBAR
# ============================================================================

st.sidebar.header("Navigation")
page = st.sidebar.selectbox("Select Dashboard", 
    ["Executive Overview", "Sales Trends & Forecast", "Product Analytics", 
     "Customer Segmentation", "Recommendations"])

st.sidebar.markdown("---")
st.sidebar.markdown("### 📅 Data Summary")
if sales_df is not None:
    st.sidebar.metric("Total Transactions", f"{len(sales_df):,}")
    st.sidebar.metric("Date Range", f"{sales_df['Order_Date'].min().date()}")
    st.sidebar.markdown(f"to {sales_df['Order_Date'].max().date()}")

# ============================================================================
# PAGE 1: EXECUTIVE OVERVIEW
# ============================================================================

if page == "Executive Overview":
    st.header("Executive Overview")
    
    if sales_df is not None:
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_sales = sales_df['Sales'].sum()
        total_profit = sales_df['Profit'].sum()
        total_orders = sales_df['Order_ID'].nunique()
        avg_order_value = total_sales / total_orders
        
        col1.metric("Total Revenue", f"${total_sales:,.0f}")
        col2.metric("Total Profit", f"${total_profit:,.0f}", 
                   f"{(total_profit/total_sales)*100:.1f}%")
        col3.metric("Total Orders", f"{total_orders:,}")
        col4.metric("Avg Order Value", f"${avg_order_value:.2f}")
        
        st.markdown("---")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Sales by Category")
            category_sales = sales_df.groupby('Category')['Sales'].sum().sort_values(ascending=True)
            fig = go.Figure(go.Bar(
                x=category_sales.values,
                y=category_sales.index,
                orientation='h',
                marker_color='steelblue',
                text=category_sales.values,
                texttemplate='$%{text:,.0f}',
                textposition='outside'
            ))
            fig.update_layout(height=400, showlegend=False,
                            xaxis_title="Sales ($)", yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Regional Performance")
            region_sales = sales_df.groupby('Region')['Sales'].sum()
            fig = go.Figure(go.Pie(
                labels=region_sales.index,
                values=region_sales.values,
                hole=0.4
            ))
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Monthly Trend
        st.subheader("Monthly Sales Trend")
        monthly = sales_df.groupby(sales_df['Order_Date'].dt.to_period('M')).agg({
            'Sales': 'sum',
            'Profit': 'sum'
        }).reset_index()
        monthly['Order_Date'] = monthly['Order_Date'].dt.to_timestamp()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly['Order_Date'],
            y=monthly['Sales'],
            name='Sales',
            line=dict(color='navy', width=3)
        ))
        fig.add_trace(go.Scatter(
            x=monthly['Order_Date'],
            y=monthly['Profit'],
            name='Profit',
            line=dict(color='green', width=3)
        ))
        fig.update_layout(height=400, hovermode='x unified',
                         xaxis_title="Month", yaxis_title="Amount ($)")
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PAGE 2: SALES TRENDS & FORECAST
# ============================================================================

elif page == "Sales Trends & Forecast":
    st.header("Sales Trends & Forecasting")
    
    if sales_df is not None and forecast_df is not None:
        # Historical + Forecast
        st.subheader("Sales Forecast - Next 3 Months")
        
        monthly = sales_df.groupby(sales_df['Order_Date'].dt.to_period('M'))['Sales'].sum().reset_index()
        monthly['Order_Date'] = monthly['Order_Date'].dt.to_timestamp()
        
        fig = go.Figure()
        
        # Historical data
        fig.add_trace(go.Scatter(
            x=monthly['Order_Date'],
            y=monthly['Sales'],
            name='Actual Sales',
            mode='lines+markers',
            line=dict(color='navy', width=3),
            marker=dict(size=6)
        ))
        
        # Forecast
        fig.add_trace(go.Scatter(
            x=forecast_df['Month'],
            y=forecast_df['Forecasted_Sales'],
            name='Forecasted Sales',
            mode='lines+markers',
            line=dict(color='red', width=3, dash='dash'),
            marker=dict(size=8, symbol='diamond')
        ))
        
        fig.update_layout(
            height=500,
            hovermode='x unified',
            xaxis_title="Month",
            yaxis_title="Sales ($)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Forecast Details
        st.subheader("Detailed Forecast")
        col1, col2, col3 = st.columns(3)
        
        for i, (idx, row) in enumerate(forecast_df.iterrows()):
            with [col1, col2, col3][i]:
                st.metric(
                    row['Month'].strftime('%B %Y'),
                    f"${row['Forecasted_Sales']:,.0f}",
                    f"+{((row['Forecasted_Sales'] / monthly['Sales'].iloc[-1]) - 1) * 100:.1f}%"
                )
        
        # Seasonal Analysis
        st.markdown("---")
        st.subheader("Seasonal Patterns")
        
        sales_df['Month'] = sales_df['Order_Date'].dt.month_name()
        monthly_avg = sales_df.groupby('Month')['Sales'].mean().reindex([
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ])
        
        fig = go.Figure(go.Bar(
            x=monthly_avg.index,
            y=monthly_avg.values,
            marker_color=['#e74c3c' if v == monthly_avg.max() else 
                         '#2ecc71' if v == monthly_avg.min() else '#3498db' 
                         for v in monthly_avg.values],
            text=monthly_avg.values,
            texttemplate='$%{text:,.0f}',
            textposition='outside'
        ))
        fig.update_layout(height=400, showlegend=False,
                         xaxis_title="Month", yaxis_title="Average Sales ($)")
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PAGE 3: PRODUCT ANALYTICS
# ============================================================================

elif page == "Product Analytics":
    st.header("Product Analytics & Recommendations")
    
    if sales_df is not None:
        # Top Products
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Top 10 Best Sellers")
            top_products = sales_df.groupby('Product')['Sales'].sum().sort_values(ascending=False).head(10)
            
            fig = go.Figure(go.Bar(
                x=top_products.values,
                y=top_products.index,
                orientation='h',
                marker_color='coral',
                text=top_products.values,
                texttemplate='$%{text:,.0f}',
                textposition='outside'
            ))
            fig.update_layout(height=400, showlegend=False, xaxis_title="Sales ($)")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Profit Margin Analysis")
            product_margin = sales_df.groupby('Product').agg({
                'Sales': 'sum',
                'Profit': 'sum'
            })
            product_margin['Margin'] = (product_margin['Profit'] / product_margin['Sales']) * 100
            top_margin = product_margin.nlargest(10, 'Margin')['Margin']
            
            fig = go.Figure(go.Bar(
                x=top_margin.values,
                y=top_margin.index,
                orientation='h',
                marker_color='gold',
                text=top_margin.values,
                texttemplate='%{text:.1f}%',
                textposition='outside'
            ))
            fig.update_layout(height=400, showlegend=False, xaxis_title="Profit Margin (%)")
            st.plotly_chart(fig, use_container_width=True)
        
        # Product Associations
        if associations_df is not None:
            st.markdown("---")
            st.subheader("🛍️ Frequently Bought Together")
            st.markdown("*Products customers purchase in the same order*")
            
            col1, col2, col3 = st.columns(3)
            
            for i in range(min(6, len(associations_df))):
                with [col1, col2, col3][i % 3]:
                    row = associations_df.iloc[i]
                    st.info(f"""
                    **Bundle #{i+1}**
                    
                    {row['Product_1']} + {row['Product_2']}
                    
                    Purchased together: **{row['Frequency']} times**
                    """)

# ============================================================================
# PAGE 4: CUSTOMER SEGMENTATION
# ============================================================================

elif page == "Customer Segmentation":
    st.header("Customer Segmentation (RFM Analysis)")
    
    if rfm_df is not None:
        # Segment Overview
        st.subheader("Customer Segments Overview")
        
        segment_stats = rfm_df.groupby('Segment').agg({
            'Customer_ID': 'count',
            'Monetary': ['sum', 'mean'],
            'Frequency': 'mean',
            'Recency': 'mean'
        }).round(2)
        
        col1, col2, col3, col4 = st.columns(4)
        
        segments = ['Champions', 'Loyal', 'Potential', 'At Risk']
        colors = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c']
        
        for i, segment in enumerate(segments):
            if segment in segment_stats.index:
                count = segment_stats.loc[segment, ('Customer_ID', 'count')]
                revenue = segment_stats.loc[segment, ('Monetary', 'sum')]
                
                with [col1, col2, col3, col4][i]:
                    st.markdown(f"""
                    <div style='padding: 1rem; background-color: {colors[i]}22; 
                                border-radius: 0.5rem; border-left: 4px solid {colors[i]}'>
                        <h3 style='color: {colors[i]}; margin: 0;'>{segment}</h3>
                        <p style='font-size: 2rem; margin: 0.5rem 0;'>{count}</p>
                        <p style='margin: 0;'>customers</p>
                        <p style='font-size: 1.2rem; margin: 0.5rem 0;'>${revenue:,.0f}</p>
                        <p style='margin: 0;'>total revenue</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # RFM Distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Customer Distribution")
            segment_counts = rfm_df['Segment'].value_counts()
            
            fig = go.Figure(go.Pie(
                labels=segment_counts.index,
                values=segment_counts.values,
                marker_colors=colors[:len(segment_counts)]
            ))
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Revenue by Segment")
            segment_revenue = rfm_df.groupby('Segment')['Monetary'].sum().sort_values()
            
            fig = go.Figure(go.Bar(
                x=segment_revenue.values,
                y=segment_revenue.index,
                orientation='h',
                marker_color=colors[:len(segment_revenue)],
                text=segment_revenue.values,
                texttemplate='$%{text:,.0f}',
                textposition='outside'
            ))
            fig.update_layout(height=400, showlegend=False, xaxis_title="Revenue ($)")
            st.plotly_chart(fig, use_container_width=True)
        
        # RFM Scatter
        st.subheader("Customer Value Matrix")
        fig = go.Figure()
        
        for segment in segments:
            if segment in rfm_df['Segment'].values:
                seg_data = rfm_df[rfm_df['Segment'] == segment]
                fig.add_trace(go.Scatter(
                    x=seg_data['Frequency'],
                    y=seg_data['Monetary'],
                    mode='markers',
                    name=segment,
                    marker=dict(size=8, opacity=0.6)
                ))
        
        fig.update_layout(
            height=500,
            xaxis_title="Purchase Frequency",
            yaxis_title="Total Spend ($)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PAGE 5: RECOMMENDATIONS
# ============================================================================

elif page == "Recommendations":
    st.header("Business Recommendations")
    
    if sales_df is not None:
        st.markdown("### 🎯 Key Strategic Recommendations")
        
        # Forecast-based
        if forecast_df is not None:
            avg_forecast = forecast_df['Forecasted_Sales'].mean()
            last_actual = sales_df.groupby(sales_df['Order_Date'].dt.to_period('M'))['Sales'].sum().iloc[-1]
            growth = ((avg_forecast - last_actual) / last_actual) * 100
            
            st.success(f"""
            **📈 Sales Forecast**
            - Expected growth: **{growth:+.1f}%** over next quarter
            - Average monthly forecast: **${avg_forecast:,.0f}**
            - Recommendation: {"Increase inventory by 15-20%" if growth > 0 else "Optimize stock levels"}
            """)
        
        # Product bundles
        if associations_df is not None:
            st.info(f"""
            **🛍️ Product Bundling Opportunities**
            - Identified {len(associations_df)} strong product associations
            - Top bundle: **{associations_df.iloc[0]['Product_1']}** + **{associations_df.iloc[0]['Product_2']}**
            - Recommendation: Create "Frequently Bought Together" promotions to increase AOV by 10-15%
            """)
        
        # Customer segments
        if rfm_df is not None:
            champions = len(rfm_df[rfm_df['Segment'] == 'Champions'])
            at_risk = len(rfm_df[rfm_df['Segment'] == 'At Risk'])
            
            st.warning(f"""
            **👥 Customer Retention Strategy**
            - Champions: **{champions}** customers - Reward with VIP benefits
            - At Risk: **{at_risk}** customers - Launch win-back campaign
            - Recommendation: Implement targeted email campaigns to reduce churn by 20%
            """)
        
        # Seasonal
        sales_df['Month'] = sales_df['Order_Date'].dt.month_name()
        monthly_avg = sales_df.groupby('Month')['Sales'].mean()
        best_month = monthly_avg.idxmax()
        worst_month = monthly_avg.idxmin()
        
        st.info(f"""
        **📅 Seasonal Marketing Strategy**
        - Peak month: **{best_month}** - Maximize marketing spend
        - Low month: **{worst_month}** - Run clearance promotions
        - Recommendation: Adjust inventory levels seasonally to reduce holding costs by 10%
        """)
        
        # Category optimization
        category_margin = sales_df.groupby('Category').agg({
            'Sales': 'sum',
            'Profit': 'sum'
        })
        category_margin['Margin'] = (category_margin['Profit'] / category_margin['Sales']) * 100
        best_margin_cat = category_margin['Margin'].idxmax()
        
        st.success(f"""
        **📊 Category Optimization**
        - Highest margin category: **{best_margin_cat}** ({category_margin.loc[best_margin_cat, 'Margin']:.1f}%)
        - Recommendation: Increase shelf space and promotions for high-margin categories
        """)

st.markdown("---")
st.markdown("<div style='text-align: center; color: #7f8c8d;'><p>Retail Sales Analytics Platform | Data-Driven Business Intelligence</p></div>", 
            unsafe_allow_html=True)