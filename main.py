import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import calendar

# Must be the first Streamlit command
st.set_page_config(layout="wide", page_title="Utilization Report")

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
        if password == "Scale2025":  # Hardcoded for demonstration
            st.session_state["password_correct"] = True
        elif password:  # If password is wrong
            st.error("Incorrect password")
        return st.session_state["password_correct"]
    
    return True

def load_and_process_data():
    # Create the dataframe structure
    months = ['January', 'February', 'March', 'April', 'May', 'June', 
              'July', 'August', 'September', 'October', 'November']
    practice_groups = [
        'Corporate & Securities',
        'Fintech & Financial Services',
        'Intellectual Property',
        'Litigation',
        'Real Estate & Land Use'
    ]
    
    # Initialize data dictionary
    data = {
        'Month': [],
        'Practice Group': [],
        'Billable Hours': [],
        'Non-Billable Hours': [],
        'Billed Hours': [],
        'Revenue': []
    }
    
    # Sample data for January
    january_data = {
        'Corporate & Securities': [1421.10, 0, 994.5, 889180.84],
        'Fintech & Financial Services': [170.30, 0, 114.40, 152508.27],
        'Intellectual Property': [530.10, 0, 384.50, 343759.88],
        'Litigation': [604.00, 0, 594.00, 357942.29],
        'Real Estate & Land Use': [242.80, 0, 153.20, 122155.65]
    }
    
    # Add data for each month and practice group
    for month in months:
        for pg in practice_groups:
            data['Month'].append(month)
            data['Practice Group'].append(pg)
            if month == 'January':
                metrics = january_data[pg]
                data['Billable Hours'].append(metrics[0])
                data['Non-Billable Hours'].append(metrics[1])
                data['Billed Hours'].append(metrics[2])
                data['Revenue'].append(metrics[3])
            else:
                # Add sample data for other months using numpy's random
                data['Billable Hours'].append(float(np.random.randint(100, 2000)))
                data['Non-Billable Hours'].append(float(np.random.randint(0, 200)))
                data['Billed Hours'].append(float(np.random.randint(100, 1500)))
                data['Revenue'].append(float(np.random.randint(100000, 1200000)))
    
    df = pd.DataFrame(data)
    
    # Calculate additional metrics
    df['Total Hours'] = df['Billable Hours'] + df['Non-Billable Hours']
    df['Utilization Rate'] = (df['Billable Hours'] / df['Total Hours'] * 100).round(2)
    df['Realization Rate'] = (df['Billed Hours'] / df['Billable Hours'] * 100).round(2)
    df['Average Hourly Rate'] = (df['Revenue'] / df['Billable Hours']).round(2)
    
    return df

def create_dashboard():
    st.title("Law Firm Analytics Dashboard")
    
    # Load data
    df = load_and_process_data()
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Date range filter
    selected_months = st.sidebar.multiselect(
        "Select Months",
        options=df['Month'].unique(),
        default=df['Month'].unique()
    )
    
    # Practice group filter
    selected_practice_groups = st.sidebar.multiselect(
        "Select Practice Groups",
        options=df['Practice Group'].unique(),
        default=df['Practice Group'].unique()
    )
    
    # Metric selection
    metric_options = {
        'Billable Hours': 'Billable Hours',
        'Revenue': 'Revenue ($)',
        'Utilization Rate': 'Utilization Rate (%)',
        'Realization Rate': 'Realization Rate (%)'
    }
    selected_metric = st.sidebar.selectbox(
        "Select Primary Metric",
        options=list(metric_options.keys()),
        format_func=lambda x: metric_options[x]
    )
    
    # Filter data
    filtered_df = df[
        (df['Month'].isin(selected_months)) &
        (df['Practice Group'].isin(selected_practice_groups))
    ]
    
    # Key Metrics Row
    st.header("Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_revenue = filtered_df['Revenue'].sum()
        st.metric(
            "Total Revenue",
            f"${total_revenue:,.2f}",
            delta=f"{(total_revenue / len(selected_months)):,.2f} per month"
        )
    
    with col2:
        avg_utilization = filtered_df['Utilization Rate'].mean()
        st.metric(
            "Average Utilization Rate",
            f"{avg_utilization:.1f}%",
            delta=f"{avg_utilization - df['Utilization Rate'].mean():.1f}% vs all time"
        )
    
    with col3:
        avg_realization = filtered_df['Realization Rate'].mean()
        st.metric(
            "Average Realization Rate",
            f"{avg_realization:.1f}%",
            delta=f"{avg_realization - df['Realization Rate'].mean():.1f}% vs all time"
        )
    
    with col4:
        avg_rate = filtered_df['Average Hourly Rate'].mean()
        st.metric(
            "Average Hourly Rate",
            f"${avg_rate:.2f}",
            delta=f"${avg_rate - df['Average Hourly Rate'].mean():.2f} vs all time"
        )
    
    # Main visualizations
    st.header("Detailed Analysis")
    
    # Interactive visualization tabs
    tab1, tab2, tab3 = st.tabs(["Time Series Analysis", "Practice Group Analysis", "Performance Metrics"])
    
    with tab1:
        # Time series chart
        st.subheader(f"{selected_metric} Over Time")
        fig1 = px.line(
            filtered_df,
            x='Month',
            y=selected_metric,
            color='Practice Group',
            markers=True,
            height=400
        )
        fig1.update_layout(yaxis_title=metric_options[selected_metric])
        st.plotly_chart(fig1, use_container_width=True)
        
        # Monthly comparison
        st.subheader("Monthly Comparison")
        fig2 = px.bar(
            filtered_df,
            x='Month',
            y=selected_metric,
            color='Practice Group',
            barmode='group',
            height=400
        )
        fig2.update_layout(yaxis_title=metric_options[selected_metric])
        st.plotly_chart(fig2, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Practice group distribution
            st.subheader("Practice Group Distribution")
            fig3 = px.pie(
                filtered_df.groupby('Practice Group')[selected_metric].sum().reset_index(),
                values=selected_metric,
                names='Practice Group',
                height=400
            )
            st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            # Practice group performance heatmap
            st.subheader("Performance Heatmap")
            pivot_data = filtered_df.pivot_table(
                values=selected_metric,
                index='Practice Group',
                columns='Month',
                aggfunc='sum'
            )
            fig4 = px.imshow(
                pivot_data,
                aspect='auto',
                color_continuous_scale='RdYlBu_r',
                height=400
            )
            st.plotly_chart(fig4, use_container_width=True)
    
    with tab3:
        # Scatter plot of relationships
        st.subheader("Metric Relationships")
        fig5 = px.scatter(
            filtered_df,
            x='Utilization Rate',
            y='Revenue',
            color='Practice Group',
            size='Billable Hours',
            hover_data=['Month'],
            height=500
        )
        st.plotly_chart(fig5, use_container_width=True)
        
        # Performance metrics table
        st.subheader("Detailed Metrics Table")
        metric_table = filtered_df.groupby('Practice Group').agg({
            'Billable Hours': 'sum',
            'Revenue': 'sum',
            'Utilization Rate': 'mean',
            'Realization Rate': 'mean',
            'Average Hourly Rate': 'mean'
        }).round(2)
        
        st.dataframe(
            metric_table.style.format({
                'Revenue': '${:,.2f}',
                'Utilization Rate': '{:.1f}%',
                'Realization Rate': '{:.1f}%',
                'Average Hourly Rate': '${:.2f}'
            }),
            height=400
        )

def main():
    if not check_password():
        st.stop()
    
    create_dashboard()

if __name__ == "__main__":
    main()
