import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io

# Configure page
st.set_page_config(
    page_title="RAJENDRA BASTRALAY",
    page_icon="🏪",
    layout="wide"
)

# Initialize session state for storing sales data
if 'sales_data' not in st.session_state:
    st.session_state.sales_data = pd.DataFrame(columns=[
        'date', 'product_name', 'price', 'quantity', 'seller', 'total_amount'
    ])

# Initialize dashboard widget preferences
if 'dashboard_widgets' not in st.session_state:
    st.session_state.dashboard_widgets = {
        'total_revenue': True,
        'total_transactions': True,
        'avg_order_value': True,
        'top_seller': True,
        'daily_sales': True,
        'product_performance': True,
        'weekly_trend': True,
        'monthly_comparison': True
    }

def add_transaction(date, product_name, price, quantity, seller):
    """Add a new sales transaction to the data"""
    total_amount = price * quantity
    new_transaction = pd.DataFrame({
        'date': [date],
        'product_name': [product_name],
        'price': [price],
        'quantity': [quantity],
        'seller': [seller],
        'total_amount': [total_amount]
    })
    st.session_state.sales_data = pd.concat([st.session_state.sales_data, new_transaction], ignore_index=True)

def get_filtered_data(start_date=None, end_date=None, seller=None):
    """Filter sales data based on date range and seller"""
    data = st.session_state.sales_data.copy()
    
    if data.empty:
        return data
    
    # Convert date column to datetime if it's not already
    data['date'] = pd.to_datetime(data['date'])
    
    if start_date:
        data = data[data['date'] >= pd.to_datetime(start_date)]
    if end_date:
        data = data[data['date'] <= pd.to_datetime(end_date)]
    if seller and seller != "All":
        data = data[data['seller'] == seller]
    
    return data

def calculate_analytics(data, period='daily'):
    """Calculate analytics for different time periods"""
    if data.empty:
        return pd.DataFrame()
    
    data = data.copy()
    data['date'] = pd.to_datetime(data['date'])
    
    if period == 'daily':
        grouped = data.groupby(data['date'].dt.date).agg({
            'total_amount': 'sum',
            'quantity': 'sum',
            'product_name': 'count'
        }).rename(columns={'product_name': 'transaction_count'})
        grouped.index.name = 'date'
    elif period == 'weekly':
        data['week'] = data['date'].dt.to_period('W')
        grouped = data.groupby('week').agg({
            'total_amount': 'sum',
            'quantity': 'sum',
            'product_name': 'count'
        }).rename(columns={'product_name': 'transaction_count'})
        grouped.index = grouped.index.astype(str)
    elif period == 'monthly':
        data['month'] = data['date'].dt.to_period('M')
        grouped = data.groupby('month').agg({
            'total_amount': 'sum',
            'quantity': 'sum',
            'product_name': 'count'
        }).rename(columns={'product_name': 'transaction_count'})
        grouped.index = grouped.index.astype(str)
    
    return grouped.reset_index()

def calculate_business_metrics(data):
    """Calculate key business metrics for dashboard widgets"""
    if data.empty:
        return {}
    
    data = data.copy()
    data['date'] = pd.to_datetime(data['date'])
    
    # Basic metrics
    total_revenue = data['total_amount'].sum()
    total_transactions = len(data)
    avg_order_value = data['total_amount'].mean()
    total_quantity = data['quantity'].sum()
    
    # Top seller
    top_seller = data.groupby('seller')['total_amount'].sum().idxmax() if not data.empty else "N/A"
    top_seller_revenue = data.groupby('seller')['total_amount'].sum().max() if not data.empty else 0
    
    # Best selling product
    top_product = data.groupby('product_name')['quantity'].sum().idxmax() if not data.empty else "N/A"
    top_product_qty = data.groupby('product_name')['quantity'].sum().max() if not data.empty else 0
    
    # Daily sales (last 7 days)
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    recent_data = data[data['date'].dt.date >= week_ago]
    daily_avg = recent_data['total_amount'].sum() / 7 if not recent_data.empty else 0
    
    # Growth comparison (this week vs last week)
    last_week_start = week_ago - timedelta(days=7)
    last_week_data = data[(data['date'].dt.date >= last_week_start) & (data['date'].dt.date < week_ago)]
    this_week_revenue = recent_data['total_amount'].sum()
    last_week_revenue = last_week_data['total_amount'].sum()
    growth_rate = ((this_week_revenue - last_week_revenue) / last_week_revenue * 100) if last_week_revenue > 0 else 0
    
    # Monthly comparison
    current_month = data[data['date'].dt.month == datetime.now().month]
    monthly_revenue = current_month['total_amount'].sum()
    monthly_transactions = len(current_month)
    
    return {
        'total_revenue': total_revenue,
        'total_transactions': total_transactions,
        'avg_order_value': avg_order_value,
        'total_quantity': total_quantity,
        'top_seller': top_seller,
        'top_seller_revenue': top_seller_revenue,
        'top_product': top_product,
        'top_product_qty': top_product_qty,
        'daily_avg': daily_avg,
        'growth_rate': growth_rate,
        'monthly_revenue': monthly_revenue,
        'monthly_transactions': monthly_transactions
    }

def render_metric_widget(title, value, subtitle=None, delta=None, help_text=None):
    """Render a customizable metric widget"""
    with st.container():
        if delta is not None:
            st.metric(
                label=title,
                value=value,
                delta=delta,
                help=help_text
            )
        else:
            st.metric(
                label=title,
                value=value,
                help=help_text
            )
        if subtitle:
            st.caption(subtitle)

def main():
    st.title("🏪 RAJENDRA BASTRALAY")
    st.markdown("Track and analyze your cloth shop sales with ease")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page", ["Dashboard", "Add Transaction", "View Transactions", "Analytics", "Export Data"])
    
    if page == "Dashboard":
        st.header("📊 Business Dashboard")
        
        if st.session_state.sales_data.empty:
            st.info("No sales data available yet. Add some transactions to see your dashboard!")
            return
        
        # Dashboard customization sidebar
        st.sidebar.markdown("### 🎛️ Customize Dashboard")
        st.sidebar.markdown("Select which widgets to display:")
        
        # Widget selection checkboxes
        widgets = st.session_state.dashboard_widgets
        widgets['total_revenue'] = st.sidebar.checkbox("💰 Total Revenue", value=widgets['total_revenue'])
        widgets['total_transactions'] = st.sidebar.checkbox("🧾 Total Transactions", value=widgets['total_transactions'])
        widgets['avg_order_value'] = st.sidebar.checkbox("📈 Average Order Value", value=widgets['avg_order_value'])
        widgets['top_seller'] = st.sidebar.checkbox("👑 Top Seller", value=widgets['top_seller'])
        widgets['daily_sales'] = st.sidebar.checkbox("📅 Daily Average (7 days)", value=widgets['daily_sales'])
        widgets['product_performance'] = st.sidebar.checkbox("🏷️ Best Product", value=widgets['product_performance'])
        widgets['weekly_trend'] = st.sidebar.checkbox("📊 Weekly Growth", value=widgets['weekly_trend'])
        widgets['monthly_comparison'] = st.sidebar.checkbox("📆 Monthly Summary", value=widgets['monthly_comparison'])
        
        # Calculate business metrics
        metrics = calculate_business_metrics(st.session_state.sales_data)
        
        if not metrics:
            st.warning("Unable to calculate metrics. Please check your data.")
            return
        
        # Create responsive grid layout
        col1, col2, col3, col4 = st.columns(4)
        
        # Row 1: Basic Financial Metrics
        if widgets['total_revenue']:
            with col1:
                render_metric_widget(
                    "💰 Total Revenue", 
                    f"₹{metrics['total_revenue']:,.2f}",
                    help_text="Total revenue from all sales"
                )
        
        if widgets['total_transactions']:
            with col2:
                render_metric_widget(
                    "🧾 Total Transactions", 
                    f"{metrics['total_transactions']:,}",
                    help_text="Total number of sales transactions"
                )
        
        if widgets['avg_order_value']:
            with col3:
                render_metric_widget(
                    "📈 Average Order Value", 
                    f"₹{metrics['avg_order_value']:,.2f}",
                    help_text="Average value per transaction"
                )
        
        if widgets['daily_sales']:
            with col4:
                render_metric_widget(
                    "📅 Daily Average (7 days)", 
                    f"₹{metrics['daily_avg']:,.2f}",
                    help_text="Average daily sales over last 7 days"
                )
        
        # Row 2: Performance Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        if widgets['top_seller']:
            with col1:
                render_metric_widget(
                    "👑 Top Seller", 
                    metrics['top_seller'],
                    f"₹{metrics['top_seller_revenue']:,.2f} revenue",
                    help_text="Seller with highest total revenue"
                )
        
        if widgets['product_performance']:
            with col2:
                render_metric_widget(
                    "🏷️ Best Selling Product", 
                    metrics['top_product'],
                    f"{metrics['top_product_qty']} units sold",
                    help_text="Product with highest quantity sold"
                )
        
        if widgets['weekly_trend']:
            with col3:
                delta_value = f"{metrics['growth_rate']:+.1f}%" if metrics['growth_rate'] != 0 else "No change"
                render_metric_widget(
                    "📊 Weekly Growth", 
                    delta_value,
                    "vs last week",
                    help_text="Revenue growth compared to previous week"
                )
        
        if widgets['monthly_comparison']:
            with col4:
                render_metric_widget(
                    "📆 This Month", 
                    f"₹{metrics['monthly_revenue']:,.2f}",
                    f"{metrics['monthly_transactions']} transactions",
                    help_text="Current month performance"
                )
        
        # Charts section
        st.markdown("---")
        st.subheader("📈 Quick Analytics")
        
        # Create quick charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Last 7 days trend
            today = datetime.now().date()
            week_ago = today - timedelta(days=7)
            recent_data = st.session_state.sales_data.copy()
            recent_data['date'] = pd.to_datetime(recent_data['date'])
            recent_data = recent_data[recent_data['date'].dt.date >= week_ago]
            
            if not recent_data.empty:
                daily_trend = recent_data.groupby(recent_data['date'].dt.date)['total_amount'].sum().reset_index()
                fig_trend = px.line(
                    daily_trend, 
                    x='date', 
                    y='total_amount',
                    title="Last 7 Days Sales Trend",
                    labels={'total_amount': 'Revenue (₹)', 'date': 'Date'}
                )
                fig_trend.update_layout(showlegend=False, height=300)
                st.plotly_chart(fig_trend, use_container_width=True)
            else:
                st.info("No recent sales data for trend chart")
        
        with col2:
            # Top 5 products by revenue
            if not st.session_state.sales_data.empty:
                product_revenue = st.session_state.sales_data.groupby('product_name')['total_amount'].sum().sort_values(ascending=False).head(5)
                if not product_revenue.empty:
                    fig_products = px.bar(
                        x=product_revenue.values,
                        y=product_revenue.index,
                        orientation='h',
                        title="Top 5 Products by Revenue",
                        labels={'x': 'Revenue (₹)', 'y': 'Product'}
                    )
                    fig_products.update_layout(showlegend=False, height=300)
                    st.plotly_chart(fig_products, use_container_width=True)
                else:
                    st.info("No product data for chart")
            else:
                st.info("No product data available")
        
        # Quick actions
        st.markdown("---")
        st.subheader("⚡ Quick Actions")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("➕ Add New Sale", use_container_width=True):
                st.session_state.page = "Add Transaction"
                st.rerun()
        
        with col2:
            if st.button("📋 View All Sales", use_container_width=True):
                st.session_state.page = "View Transactions"
                st.rerun()
        
        with col3:
            if st.button("📊 Full Analytics", use_container_width=True):
                st.session_state.page = "Analytics"
                st.rerun()
        
        with col4:
            if st.button("📤 Export Data", use_container_width=True):
                st.session_state.page = "Export Data"
                st.rerun()
    
    elif page == "Add Transaction":
        st.header("📝 Add New Sales Transaction")
        
        with st.form("sales_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                date = st.date_input("Date of Sale", value=datetime.now().date())
                product_name = st.text_input("Product Name", placeholder="e.g., Cotton Shirt, Silk Saree")
                price = st.number_input("Price per Unit (₹)", min_value=0.0, step=0.01, format="%.2f")
            
            with col2:
                quantity = st.number_input("Quantity", min_value=1, step=1)
                seller = st.text_input("Seller Name", placeholder="e.g., John Doe")
                
            # Calculate and display total
            if price > 0 and quantity > 0:
                total = price * quantity
                st.info(f"Total Amount: ₹{total:.2f}")
            
            submitted = st.form_submit_button("Add Transaction", type="primary")
            
            if submitted:
                if product_name and seller and price > 0 and quantity > 0:
                    add_transaction(date, product_name, price, quantity, seller)
                    st.success("Transaction added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill all fields with valid values.")
    
    elif page == "View Transactions":
        st.header("📊 Sales Transactions")
        
        if st.session_state.sales_data.empty:
            st.info("No transactions recorded yet. Add some transactions to get started!")
            return
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            start_date = st.date_input("Start Date", value=None)
        with col2:
            end_date = st.date_input("End Date", value=None)
        with col3:
            sellers = ["All"] + list(st.session_state.sales_data['seller'].unique())
            selected_seller = st.selectbox("Seller", sellers)
        
        # Apply filters
        filtered_data = get_filtered_data(start_date, end_date, selected_seller)
        
        if filtered_data.empty:
            st.warning("No transactions found for the selected filters.")
            return
        
        # Display summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Revenue", f"₹{filtered_data['total_amount'].sum():.2f}")
        with col2:
            st.metric("Total Quantity", f"{filtered_data['quantity'].sum()}")
        with col3:
            st.metric("Total Transactions", f"{len(filtered_data)}")
        with col4:
            avg_order = filtered_data['total_amount'].mean() if len(filtered_data) > 0 else 0
            st.metric("Average Order Value", f"₹{avg_order:.2f}")
        
        # Display transactions table
        st.subheader("Transaction Details")
        
        # Format the data for display
        display_data = filtered_data.copy()
        display_data['date'] = pd.to_datetime(display_data['date']).dt.strftime('%Y-%m-%d')
        display_data['price'] = display_data['price'].apply(lambda x: f"₹{x:.2f}")
        display_data['total_amount'] = display_data['total_amount'].apply(lambda x: f"₹{x:.2f}")
        
        st.dataframe(
            display_data[['date', 'product_name', 'price', 'quantity', 'seller', 'total_amount']],
            column_config={
                'date': 'Date',
                'product_name': 'Product Name',
                'price': 'Price',
                'quantity': 'Quantity',
                'seller': 'Seller',
                'total_amount': 'Total Amount'
            },
            use_container_width=True
        )
    
    elif page == "Analytics":
        st.header("📈 Sales Analytics")
        
        if st.session_state.sales_data.empty:
            st.info("No transactions recorded yet. Add some transactions to view analytics!")
            return
        
        # Time period selection
        period = st.selectbox("Select Time Period", ["daily", "weekly", "monthly"])
        
        # Date range filter for analytics
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date for Analytics", value=None, key="analytics_start")
        with col2:
            end_date = st.date_input("End Date for Analytics", value=None, key="analytics_end")
        
        # Get filtered data
        filtered_data = get_filtered_data(start_date, end_date)
        
        if filtered_data.empty:
            st.warning("No data available for the selected date range.")
            return
        
        # Calculate analytics
        analytics_data = calculate_analytics(filtered_data, period)
        
        if analytics_data.empty:
            st.warning("No analytics data available.")
            return
        
        # Display charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Revenue chart
            fig_revenue = px.line(
                analytics_data, 
                x=analytics_data.columns[0], 
                y='total_amount',
                title=f"Revenue Trend ({period.title()})",
                labels={'total_amount': 'Revenue (₹)', analytics_data.columns[0]: period.title()}
            )
            fig_revenue.update_layout(showlegend=False)
            st.plotly_chart(fig_revenue, use_container_width=True)
        
        with col2:
            # Quantity chart
            fig_quantity = px.bar(
                analytics_data, 
                x=analytics_data.columns[0], 
                y='quantity',
                title=f"Quantity Sold ({period.title()})",
                labels={'quantity': 'Quantity Sold', analytics_data.columns[0]: period.title()}
            )
            st.plotly_chart(fig_quantity, use_container_width=True)
        
        # Transaction count chart
        fig_transactions = px.area(
            analytics_data, 
            x=analytics_data.columns[0], 
            y='transaction_count',
            title=f"Number of Transactions ({period.title()})",
            labels={'transaction_count': 'Transaction Count', analytics_data.columns[0]: period.title()}
        )
        st.plotly_chart(fig_transactions, use_container_width=True)
        
        # Summary table
        st.subheader(f"{period.title()} Summary")
        summary_display = analytics_data.copy()
        summary_display['total_amount'] = summary_display['total_amount'].apply(lambda x: f"₹{x:.2f}")
        
        st.dataframe(
            summary_display,
            column_config={
                analytics_data.columns[0]: period.title(),
                'total_amount': 'Revenue',
                'quantity': 'Quantity Sold',
                'transaction_count': 'Transactions'
            },
            use_container_width=True
        )
    
    elif page == "Export Data":
        st.header("📤 Export Sales Data")
        
        if st.session_state.sales_data.empty:
            st.info("No transactions to export. Add some transactions first!")
            return
        
        # Export options
        st.subheader("Export Options")
        
        col1, col2 = st.columns(2)
        with col1:
            export_start_date = st.date_input("Start Date for Export", value=None, key="export_start")
        with col2:
            export_end_date = st.date_input("End Date for Export", value=None, key="export_end")
        
        export_seller = st.selectbox("Select Seller", ["All"] + list(st.session_state.sales_data['seller'].unique()), key="export_seller")
        
        # Get filtered data for export
        export_data = get_filtered_data(export_start_date, export_end_date, export_seller)
        
        if export_data.empty:
            st.warning("No data available for export with the selected filters.")
            return
        
        # Preview data
        st.subheader("Preview Export Data")
        st.write(f"Total records to export: {len(export_data)}")
        
        preview_data = export_data.copy()
        preview_data['date'] = pd.to_datetime(preview_data['date']).dt.strftime('%Y-%m-%d')
        st.dataframe(preview_data, use_container_width=True)
        
        # Export buttons
        col1, col2 = st.columns(2)
        
        with col1:
            # CSV export
            csv_buffer = io.StringIO()
            export_data.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()
            
            st.download_button(
                label="Download as CSV",
                data=csv_data,
                file_name=f"sales_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col2:
            # Excel export
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                export_data.to_excel(writer, sheet_name='Sales Data', index=False)
            excel_data = excel_buffer.getvalue()
            
            st.download_button(
                label="Download as Excel",
                data=excel_data,
                file_name=f"sales_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**RAJENDRA BASTRALAY**")
    st.sidebar.markdown("Built with Streamlit")

if __name__ == "__main__":
    main()
