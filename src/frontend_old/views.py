from django.shortcuts import render
from src.frontend_old.fake_db import fake_db

def dash_example(request):
    product_sales = fake_db.get_sales_by_product()
    top_product = product_sales.sort_values('sales', ascending=False).iloc[0]['product']
    total_sales = product_sales['sales'].sum()
    
    # Create context with summary stats
    context = {
        'top_product': top_product,
        'total_sales': total_sales,
        'product_count': len(fake_db.get_products()),
        'region_count': len(fake_db.get_regions())
    }

    return render(request, 'dashboard.html', context)
