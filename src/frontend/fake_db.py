"""
Fake database module to simulate data access patterns without a real database.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

products = [
    "Laptop",
    "Smartphone",
    "Tablet",
    "Headphones",
    "Monitor",
    "Keyboard",
    "Mouse",
]
categories = [
    "Electronics",
    "Electronics",
    "Electronics",
    "Audio",
    "Display",
    "Peripherals",
    "Peripherals",
]
regions = ['North', 'South', 'East', 'West', 'Central']

class FakeDatabase:

    def __init__(self):
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=90)
        dates = pd.date_range(start=start_date, end=end_date, freq='D')

        records = []
        for product, category in zip(products, categories):
            for date in dates:
                for region in regions:
                    # Create some realistic patterns
                    base_sales = np.random.randint(5, 50)
                    
                    # Add some seasonality - higher sales on weekends
                    if date.dayofweek >= 5:  # Weekend
                        base_sales = int(base_sales * 1.5)
                    
                    # Add regional variations
                    if region == 'North':
                        regional_factor = 0.9
                    elif region == 'South':
                        regional_factor = 1.2
                    elif region == 'East':
                        regional_factor = 1.1
                    elif region == 'West':
                        regional_factor = 1.3
                    else:  # Central
                        regional_factor = 1.0
                    
                    sales = int(base_sales * regional_factor)
                    price = np.random.choice([299, 899, 499, 129, 249, 69, 49])
                    
                    records.append({
                        'date': date,
                        'product': product,
                        'category': category,
                        'region': region,
                        'sales': sales,
                        'price': price,
                        'revenue': sales * price
                    })

        self.sales_df = pd.DataFrame(records)
    
    def get_sales_data(self, start_date=None, end_date=None, product=None, region=None):
        filtered_df = self.sales_df.copy()
        
        if start_date:
            filtered_df = filtered_df[filtered_df['date'] >= start_date]
        
        if end_date:
            filtered_df = filtered_df[filtered_df['date'] <= end_date]
        
        if product:
            if isinstance(product, list):
                filtered_df = filtered_df[filtered_df['product'].isin(product)]
            else:
                filtered_df = filtered_df[filtered_df['product'] == product]
        
        if region:
            if isinstance(region, list):
                filtered_df = filtered_df[filtered_df['region'].isin(region)]
            else:
                filtered_df = filtered_df[filtered_df['region'] == region]
        
        return filtered_df
    
    def get_products(self):
        """Get list of all products"""
        return self.sales_df['product'].unique().tolist()
    
    def get_regions(self):
        """Get list of all regions"""
        return self.sales_df['region'].unique().tolist()
    
    def get_sales_by_product(self):
        """Aggregate sales by product"""
        return self.sales_df.groupby('product')['sales'].sum().reset_index()
    
    def get_sales_by_region(self):
        """Aggregate sales by region"""
        return self.sales_df.groupby('region')['sales'].sum().reset_index()
    
    def get_sales_by_date(self):
        """Aggregate sales by date"""
        return self.sales_df.groupby('date')['sales'].sum().reset_index()
    
    def get_revenue_by_product(self):
        """Aggregate revenue by product"""
        return self.sales_df.groupby('product')['revenue'].sum().reset_index()
    
    def get_revenue_by_category(self):
        """Aggregate revenue by category"""
        return self.sales_df.groupby('category')['revenue'].sum().reset_index()

# Global instance that can be imported and used across the app
fake_db = FakeDatabase()
