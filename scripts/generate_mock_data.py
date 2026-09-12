"""
FreshBite PoC: Mock Data Generator

Generates a star-schema dataset for a multi-tenant QSR franchise chain.
Output: 6 CSV files ready to load into Amazon Redshift.

Usage:
    python generate_mock_data.py [--output-dir ./data]
"""

import argparse
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def generate_mock_data(output_dir: str = "./data"):
    """Generate all mock data CSVs."""
    np.random.seed(42)
    os.makedirs(output_dir, exist_ok=True)

    # --- DIMENSION: Franchises ---
    franchises = pd.DataFrame({
        'franchise_id': [f'FR-{i:03d}' for i in range(1, 11)],
        'franchise_name': [
            'FreshBite North', 'FreshBite South', 'FreshBite East', 'FreshBite West',
            'FreshBite Central', 'FreshBite Metro', 'FreshBite Coastal',
            'FreshBite Mountain', 'FreshBite Valley', 'FreshBite Lakes'
        ],
        'owner_name': [
            'Sarah Johnson', 'Marcus Chen', 'Priya Patel', 'David Rodriguez',
            'Emma Thompson', 'James Wilson', 'Aisha Mohammed', 'Robert Kim',
            'Lisa Garcia', "Michael O'Brien"
        ],
        'owner_email': [
            'sarah.johnson@freshbite-north.example.com', 'marcus.chen@freshbite-south.example.com',
            'priya.patel@freshbite-east.example.com', 'david.rodriguez@freshbite-west.example.com',
            'emma.thompson@freshbite-central.example.com', 'james.wilson@freshbite-metro.example.com',
            'aisha.mohammed@freshbite-coastal.example.com', 'robert.kim@freshbite-mountain.example.com',
            'lisa.garcia@freshbite-valley.example.com', 'michael.obrien@freshbite-lakes.example.com'
        ],
        'region': ['Northeast', 'Southeast', 'East', 'West', 'Central',
                   'Metro', 'Coastal', 'Mountain', 'Valley', 'Great Lakes']
    })

    # --- DIMENSION: Locations (5 per franchise = 50 total) ---
    cities = [
        ('Boston', 'MA'), ('Hartford', 'CT'), ('Portland', 'ME'), ('Burlington', 'VT'), ('Providence', 'RI'),
        ('Atlanta', 'GA'), ('Charlotte', 'NC'), ('Nashville', 'TN'), ('Jacksonville', 'FL'), ('Richmond', 'VA'),
        ('New York', 'NY'), ('Philadelphia', 'PA'), ('Baltimore', 'MD'), ('Newark', 'NJ'), ('Washington', 'DC'),
        ('Los Angeles', 'CA'), ('San Francisco', 'CA'), ('Seattle', 'WA'), ('Portland', 'OR'), ('San Diego', 'CA'),
        ('Chicago', 'IL'), ('Detroit', 'MI'), ('Indianapolis', 'IN'), ('Columbus', 'OH'), ('Milwaukee', 'WI'),
        ('Miami', 'FL'), ('Tampa', 'FL'), ('Orlando', 'FL'), ('Fort Lauderdale', 'FL'), ('West Palm Beach', 'FL'),
        ('Virginia Beach', 'VA'), ('Savannah', 'GA'), ('Charleston', 'SC'), ('Wilmington', 'NC'), ('Myrtle Beach', 'SC'),
        ('Denver', 'CO'), ('Salt Lake City', 'UT'), ('Boise', 'ID'), ('Albuquerque', 'NM'), ('Colorado Springs', 'CO'),
        ('Phoenix', 'AZ'), ('Tucson', 'AZ'), ('Las Vegas', 'NV'), ('Sacramento', 'CA'), ('Fresno', 'CA'),
        ('Cleveland', 'OH'), ('Minneapolis', 'MN'), ('Madison', 'WI'), ('Grand Rapids', 'MI'), ('Buffalo', 'NY')
    ]

    locations_data = []
    for i, franchise_id in enumerate(franchises['franchise_id']):
        for j in range(5):
            idx = i * 5 + j
            city, state = cities[idx]
            open_date = datetime(2020, 1, 1) + timedelta(days=np.random.randint(0, 1500))
            locations_data.append({
                'location_id': f'LOC-{idx+1:03d}',
                'franchise_id': franchise_id,
                'location_name': f'FreshBite {city}',
                'city': city,
                'state': state,
                'open_date': open_date.strftime('%Y-%m-%d')
            })
    locations = pd.DataFrame(locations_data)

    # --- DIMENSION: Products ---
    products = pd.DataFrame({
        'product_id': [f'P-{i:03d}' for i in range(1, 21)],
        'category': ['Bowls']*5 + ['Wraps']*4 + ['Salads']*4 + ['Smoothies']*4 + ['Sides']*3,
        'product_name': [
            'Chicken Power Bowl', 'Veggie Buddha Bowl', 'Salmon Poke Bowl', 'Steak Burrito Bowl', 'Tofu Teriyaki Bowl',
            'Grilled Chicken Wrap', 'Falafel Wrap', 'BBQ Pulled Pork Wrap', 'Mediterranean Wrap',
            'Caesar Salad', 'Greek Salad', 'Asian Sesame Salad', 'Harvest Salad',
            'Green Detox Smoothie', 'Berry Blast Smoothie', 'Tropical Mango Smoothie', 'Protein Power Smoothie',
            'Sweet Potato Fries', 'Quinoa Side', 'Soup of the Day'
        ],
        'unit_price': [12.99, 11.49, 14.99, 13.49, 11.99,
                       10.99, 10.49, 11.99, 10.99,
                       9.99, 9.49, 10.49, 10.99,
                       7.99, 7.49, 7.99, 8.49,
                       4.99, 4.49, 5.99]
    })

    # --- FACT: Daily Sales ---
    print("Generating daily sales data...")
    date_range = pd.date_range('2026-01-01', '2026-06-30')
    sales_records = []

    for loc_id in locations['location_id']:
        loc_multiplier = np.random.uniform(0.7, 1.4)
        for date in date_range:
            dow_factor = 1.2 if date.dayofweek >= 5 else 1.0
            seasonal = 1 + (date.month - 1) * 0.02
            n_products = np.random.randint(8, 16)
            chosen_products = np.random.choice(products['product_id'].values, n_products, replace=False)
            for prod_id in chosen_products:
                price = products.loc[products['product_id'] == prod_id, 'unit_price'].values[0]
                quantity = int(np.random.poisson(lam=25 * loc_multiplier * dow_factor * seasonal))
                if quantity == 0:
                    quantity = 1
                revenue = round(quantity * price, 2)
                cost = round(revenue * np.random.uniform(0.28, 0.38), 2)
                sales_records.append({
                    'sale_date': date.strftime('%Y-%m-%d'),
                    'location_id': loc_id,
                    'product_id': prod_id,
                    'quantity': quantity,
                    'revenue': revenue,
                    'cost': cost
                })

    fact_sales = pd.DataFrame(sales_records)
    print(f"  Sales records: {len(fact_sales):,}")

    # --- FACT: Customer Feedback ---
    print("Generating customer feedback data...")
    feedback_records = []
    for loc_id in locations['location_id']:
        base_rating = np.random.uniform(3.5, 4.8)
        for date in date_range:
            n_reviews = np.random.poisson(lam=3)
            for _ in range(n_reviews):
                rating = min(5, max(1, round(np.random.normal(base_rating, 0.5), 1)))
                response_time = max(1, int(np.random.exponential(scale=15)))
                feedback_records.append({
                    'feedback_date': date.strftime('%Y-%m-%d'),
                    'location_id': loc_id,
                    'rating': rating,
                    'response_time_mins': response_time
                })

    fact_feedback = pd.DataFrame(feedback_records)
    print(f"  Feedback records: {len(fact_feedback):,}")

    # --- RLS Permissions ---
    rls_permissions = [{'user_email': 'admin@freshbite-corp.example.com', 'franchise_id': 'ALL'}]
    for _, row in franchises.iterrows():
        rls_permissions.append({'user_email': row['owner_email'], 'franchise_id': row['franchise_id']})
    rls_df = pd.DataFrame(rls_permissions)

    # --- Save CSVs ---
    franchises.to_csv(f"{output_dir}/dim_franchises.csv", index=False)
    locations.to_csv(f"{output_dir}/dim_locations.csv", index=False)
    products.to_csv(f"{output_dir}/dim_products.csv", index=False)
    fact_sales.to_csv(f"{output_dir}/fact_daily_sales.csv", index=False)
    fact_feedback.to_csv(f"{output_dir}/fact_customer_feedback.csv", index=False)
    rls_df.to_csv(f"{output_dir}/rls_user_permissions.csv", index=False)

    print(f"\nAll files saved to: {output_dir}")
    print(f"  Franchises:  {len(franchises)}")
    print(f"  Locations:   {len(locations)}")
    print(f"  Products:    {len(products)}")
    print(f"  Sales:       {len(fact_sales):,}")
    print(f"  Feedback:    {len(fact_feedback):,}")
    print(f"  RLS rules:   {len(rls_df)}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate FreshBite mock data')
    parser.add_argument('--output-dir', default='./data', help='Output directory for CSV files')
    args = parser.parse_args()
    generate_mock_data(args.output_dir)
