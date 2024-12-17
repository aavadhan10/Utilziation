import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import calendar

# Must be the first Streamlit command
st.set_page_config(layout="wide", page_title="Law Firm Analytics Dashboard")

# Custom CSS for better styling
st.markdown("""
    <style>
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 0.125rem 0.25rem rgba(0,0,0,0.075);
    }
    </style>
""", unsafe_allow_html=True)

def check_password():
    """Returns `True` if the user had the correct password."""
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    
    if not st.session_state["password_correct"]:
        st.markdown("## Dashboard Login")
        password = st.text_input("Please enter the dashboard password", type="password")
        if password == "Scale2025":
            st.session_state["password_correct"] = True
        elif password:
            st.error("Incorrect password")
        return st.session_state["password_correct"]
    
    return True

def load_and_process_data():
    # Create the dataframe structure with two years of data
    current_year_data = {
        'Month': [], 'Practice Group': [], 'Billable Hours': [],
        'Non-Billable Hours': [], 'Billed Hours': [], 'Revenue': [], 'Year': []
    }
    
    previous_year_data = {
        'Month': [], 'Practice Group': [], 'Billable Hours': [],
        'Non-Billable Hours': [], 'Billed Hours': [], 'Revenue': [], 'Year': []
    }
    
    months = ['January', 'February', 'March', 'April', 'May', 'June', 
              'July', 'August', 'September', 'October', 'November']
              
    practice_groups = [
        'Corporate & Securities',
        'Fintech & Financial Services',
        'Intellectual Property',
        'Litigation',
        'Real Estate & Land Use'
    ]
    
    # Sample data for January 2024
    january_data = {
        'Corporate & Securities': [1421.10, 0, 994.5, 889180.84],
        'Fintech & Financial Services': [170.30, 0, 114.40, 152508.27],
        'Intellectual Property': [530.10, 0, 384.50, 343759.88],
        'Litigation': [604.00, 0, 594.00, 357942.29],
        'Real Estate & Land Use': [242.80, 0, 153.20, 122155.65]
    }
    
    # Generate data for both years
    for year_data, year in [(current_year_data, 2024), (previous_year_data, 2023)]:
        for month in months:
            for pg in practice_groups:
                year_data['Month'].append(month)
                year_data['Practice Group'].append(pg)
                year_data['Year'].append(year)
                
                if year == 2024 and month == 'January':
                    metrics = january_data[pg]
                    year_data['Billable Hours'].append(metrics[0])
                    year_data['Non-Billable Hours'].append(metrics[1])
                    year_data['Billed Hours'].append(metrics[2])
                    year_data['Revenue'].append(metrics[3])
                else:
                    # Generate sample data with year-over-year patterns
                    base_billable = float(np.random.randint(100, 2000))
                    if year == 2023:
                        multiplier = 0.9
                    else:
                        multiplier = 1.0
                    
                    year_data['Billable Hours'].append(base_billable * multiplier)
                    year_data['Non-Billable Hours'].append(float(np.random.randint(0, 200)))
                    year_data['Billed Hours'].append(base_billable * multiplier * 0.8)
                    year_data['Revenue'].append(base_billable * multiplier * np.random.randint(500, 800))
    
    # Combine the data
    df = pd.concat([pd.DataFrame(current_year_data), pd.DataFrame(previous_year_data)])
    
    # Calculate additional metrics
    df['Total Hours'] = df['Billable Hours'] + df['Non-Billable Hours']
    df['Utilization Rate'] = (df['Billable Hours'] / df['Total Hours'] * 100).round(2)
    df['Realization Rate'] = (df['Billed Hours'] / df['Billable Hours'] * 100).round(2)
    df['Average Hourly Rate'] = (df['Revenue'] / df['Billable Hours']).round(2)
    df['Year-Month'] = df.apply(lambda x: f"{x['Year']}-{x['Month']}", axis=1)
    
    return df
    y=year_data['Utilization Rate'],
                    name=f'Utilization Rate {year}',
                    mode='lines+markers'
                ))
                fig_metrics.add_trace(go.Scatter(
                    x=year_data['Month'],
                    y=year_data['Realization Rate'],
                    name=f'Realization Rate {year}',
                    mode='lines+markers'
                ))
            
            fig_metrics.update_layout(
                title='Efficiency Metrics Trends',
                height=400
            )
            st.plotly_chart(fig_metrics, use_container_width=True)
    
    # YoY Comparisons Tab
    with tab5:
        st.header("Year-over-Year Comparisons")
        
        st.subheader("Revenue Comparison")
        yoy_revenue = filtered_df.pivot_table(
            values='Revenue',
            index='Month',
            columns='Year',
            aggfunc='sum'
        ).reset_index()
        
        fig_yoy_revenue = go.Figure()
        for year in selected_years:
            fig_yoy_revenue.add_trace(go.Bar(
                name=str(year),
                x=yoy_revenue['Month'],
                y=yoy_revenue[year],
                text=yoy_revenue[year].apply(lambda x: f'${x:,.0f}'),
                textposition='auto',
            ))
        
        fig_yoy_revenue.update_layout(
            title='Monthly Revenue by Year',
            barmode='group',
            height=400
        )
        st.plotly_chart(fig_yoy_revenue, use_container_width=True)
        
        col5, col6 = st.columns(2)
        
        with col5:
            # Calculate YoY growth rates
            yoy_growth = pd.DataFrame()
            for metric in ['Revenue', 'Billable Hours', 'Average Hourly Rate']:
                current_year = filtered_df[filtered_df['Year'] == max(selected_years)].groupby('Month')[metric].sum()
                previous_year = filtered_df[filtered_df['Year'] == min(selected_years)].groupby('Month')[metric].sum()
                growth = ((current_year - previous_year) / previous_year * 100).round(2)
                yoy_growth[f'{metric} Growth'] = growth
            
            fig_growth = px.bar(
                yoy_growth.reset_index(),
                x='Month',
                y=yoy_growth.columns,
                title='Year-over-Year Growth Rates',
                barmode='group',
                height=400
            )
            st.plotly_chart(fig_growth, use_container_width=True)
        
        with col6:
            # Practice Group YoY Comparison
            practice_yoy = filtered_df.pivot_table(
                values='Revenue',
                index='Practice Group',
                columns='Year',
                aggfunc='sum'
            ).reset_index()
            
            fig_practice_yoy = go.Figure()
            for year in selected_years:
                fig_practice_yoy.add_trace(go.Bar(
                    name=str(year),
                    x=practice_yoy['Practice Group'],
                    y=practice_yoy[year],
                    text=practice_yoy[year].apply(lambda x: f'${x:,.0f}'),
                    textposition='auto',
                ))
            
            fig_practice_yoy.update_layout(
                title='Practice Group Revenue by Year',
                barmode='group',
                height=400,
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig_practice_yoy, use_container_width=True)
    def main():
    if not check_password():
        st.stop()
    
    create_dashboard()

if __name__ == "__main__":
    main()
