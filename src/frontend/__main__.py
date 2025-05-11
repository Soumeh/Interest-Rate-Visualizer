import dash
from dash import dcc, html, callback, Output, Input
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from django_plotly_dash import DjangoDash
from .fake_db import fake_db

# Create a DjangoDash application
app = DjangoDash('ExampleDashApp')

# Get data from our fake database
products = fake_db.get_products()
regions = fake_db.get_regions()

# Default date range (last 30 days)
end_date = datetime.now().date()
start_date = end_date - timedelta(days=30)

# Define the app layout with interactive components
app.layout = html.Div([
    html.Div([
        html.H1('Sales Dashboard'),
        html.P('Analyze product sales across regions and time periods'),
    ], style={'textAlign': 'center', 'marginBottom': '30px'}),
    
    html.Div([
        html.Div([
            html.Label('Date Range:'),
            dcc.DatePickerRange(
                id='date-picker-range',
                start_date=start_date,
                end_date=end_date,
                display_format='YYYY-MM-DD'
            ),
        ], style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div([
            html.Label('Products:'),
            dcc.Dropdown(
                id='product-dropdown',
                options=[{'label': product, 'value': product} for product in products],
                multi=True,
                placeholder='Select products...'
            ),
        ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'}),
    ], style={'marginBottom': '20px'}),
    
    html.Div([
        html.Label('Regions:'),
        dcc.Checklist(
            id='region-checklist',
            options=[{'label': region, 'value': region} for region in regions],
            value=regions,  # Default to all regions selected
            inline=True
        ),
    ], style={'marginBottom': '20px'}),
    
    html.Div([
        html.Div([
            dcc.Graph(id='sales-by-product-graph')
        ], style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Graph(id='sales-by-region-graph')
        ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'}),
    ]),
    
    html.Div([
        dcc.Graph(id='sales-trend-graph')
    ]),
    
    html.Div([
        html.Div([
            dcc.Graph(id='revenue-by-product-graph')
        ], style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Graph(id='revenue-by-category-graph')
        ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'}),
    ]),
], style={'padding': '20px'})

# Define callbacks to update graphs based on filters

@callback(
    Output('sales-by-product-graph', 'figure'),
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('region-checklist', 'value')]
)
def update_sales_by_product(start_date, end_date, regions):
    # Get filtered data from fake DB
    filtered_data = fake_db.get_sales_data(
        start_date=start_date,
        end_date=end_date,
        region=regions
    )
    
    # Aggregate data
    product_sales = filtered_data.groupby('product')['sales'].sum().reset_index()
    
    # Create figure
    fig = px.bar(
        product_sales, 
        x='product', 
        y='sales',
        title='Sales by Product',
        labels={'product': 'Product', 'sales': 'Total Sales'},
        color='product'
    )
    
    # Update layout
    fig.update_layout(xaxis_title='Product', yaxis_title='Sales')
    
    return fig

@callback(
    Output('sales-by-region-graph', 'figure'),
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('product-dropdown', 'value')]
)
def update_sales_by_region(start_date, end_date, products):
    # Get filtered data from fake DB
    filtered_data = fake_db.get_sales_data(
        start_date=start_date,
        end_date=end_date,
        product=products
    )
    
    # Aggregate data
    region_sales = filtered_data.groupby('region')['sales'].sum().reset_index()
    
    # Create figure
    fig = px.pie(
        region_sales, 
        values='sales', 
        names='region',
        title='Sales by Region',
        hole=0.3
    )
    
    return fig

@callback(
    Output('sales-trend-graph', 'figure'),
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('product-dropdown', 'value'),
     Input('region-checklist', 'value')]
)
def update_sales_trend(start_date, end_date, products, regions):
    # Get filtered data from fake DB
    filtered_data = fake_db.get_sales_data(
        start_date=start_date,
        end_date=end_date,
        product=products,
        region=regions
    )
    
    # Aggregate data by date
    daily_sales = filtered_data.groupby('date')['sales'].sum().reset_index()
    
    # Create figure
    fig = px.line(
        daily_sales, 
        x='date', 
        y='sales',
        title='Sales Trend Over Time',
        labels={'date': 'Date', 'sales': 'Sales'}
    )
    
    # Add rolling average
    if len(daily_sales) > 7:
        daily_sales['7_day_avg'] = daily_sales['sales'].rolling(window=7).mean()
        fig.add_scatter(
            x=daily_sales['date'], 
            y=daily_sales['7_day_avg'],
            mode='lines',
            name='7-Day Moving Average',
            line=dict(color='red', dash='dash')
        )
    
    # Update layout
    fig.update_layout(xaxis_title='Date', yaxis_title='Sales')
    
    return fig

@callback(
    Output('revenue-by-product-graph', 'figure'),
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('region-checklist', 'value')]
)
def update_revenue_by_product(start_date, end_date, regions):
    # Get filtered data from fake DB
    filtered_data = fake_db.get_sales_data(
        start_date=start_date,
        end_date=end_date,
        region=regions
    )
    
    # Aggregate data
    product_revenue = filtered_data.groupby('product')['revenue'].sum().reset_index()
    product_revenue = product_revenue.sort_values('revenue', ascending=False)
    
    # Create figure
    fig = px.bar(
        product_revenue, 
        x='product', 
        y='revenue',
        title='Revenue by Product',
        labels={'product': 'Product', 'revenue': 'Total Revenue ($)'},
        color='product'
    )
    
    # Format y-axis as currency
    fig.update_layout(
        xaxis_title='Product', 
        yaxis_title='Revenue ($)',
        yaxis=dict(tickprefix='$')
    )
    
    return fig

@callback(
    Output('revenue-by-category-graph', 'figure'),
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('region-checklist', 'value'),
     Input('product-dropdown', 'value')]
)
def update_revenue_by_category(start_date, end_date, regions, products):
    # Get filtered data from fake DB
    filtered_data = fake_db.get_sales_data(
        start_date=start_date,
        end_date=end_date,
        region=regions,
        product=products
    )
    
    # Aggregate data
    category_revenue = filtered_data.groupby('category')['revenue'].sum().reset_index()
    
    # Create figure
    fig = px.pie(
        category_revenue, 
        values='revenue', 
        names='category',
        title='Revenue by Category',
        color_discrete_sequence=px.colors.sequential.Plasma
    )
    
    # Add total revenue in the center
    total_revenue = category_revenue['revenue'].sum()
    fig.update_traces(
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Revenue: $%{value:,.0f}<br>Percentage: %{percent}'
    )
    
    # Add annotation for total revenue
    fig.add_annotation(
        text=f"Total Revenue:<br>${total_revenue:,.0f}",
        x=0.5, y=0.5,
        font_size=14,
        showarrow=False
    )
    
    return fig