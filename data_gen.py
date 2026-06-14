import pandas as pd
import numpy as np
from faker import Faker
import random

fake = Faker('en_IN')
random.seed(42)
np.random.seed(42)

categories = {
    'Supplements': ['Whey Protein 1kg', 'Creatine 500g', 'Multivitamin 60tab', 'Omega-3 90cap', 'Vitamin D3 60tab',
                    'BCAA Powder 400g', 'Pre-Workout 300g', 'Magnesium 60tab', 'Zinc 60tab', 'Collagen 250g'],
    'Personal Care': ['Face Wash 150ml', 'Shampoo 300ml', 'Body Lotion 200ml', 'Sunscreen SPF50 100ml',
                      'Beard Oil 30ml', 'Hair Serum 50ml', 'Conditioner 300ml', 'Toner 200ml', 'Eye Cream 30ml', 'Lip Balm 10g'],
    'Health Devices': ['BP Monitor', 'Pulse Oximeter', 'Weighing Scale', 'Thermometer', 'Glucometer',
                       'Nebulizer', 'Heating Pad', 'Massager', 'TENS Unit', 'Sleep Tracker'],
    'Wellness Drinks': ['Green Tea 100bags', 'Apple Cider Vinegar 500ml', 'Turmeric Latte Mix 200g',
                        'Protein Shake RTD', 'Electrolyte Powder 500g', 'Ashwagandha Latte 200g',
                        'Coconut Water 330ml', 'Kombucha 250ml', 'Collagen Drink 250ml', 'Immunity Shots 30ml'],
    'Medicines': ['Paracetamol 500mg', 'Antacid Syrup 200ml', 'Cough Syrup 100ml', 'Vitamin C 1000mg',
                  'Iron Supplement', 'B-Complex', 'Probiotic 30cap', 'Melatonin 5mg', 'Digestive Enzyme', 'Fish Oil 60cap']
}

suppliers = {
    'Supplements': 'NutriSource Pvt Ltd',
    'Personal Care': 'CareWell Distributors',
    'Health Devices': 'MedTech Supplies',
    'Wellness Drinks': 'WellBev India',
    'Medicines': 'PharmaCo Wholesale'
}

lead_times = {'Supplements': 7, 'Personal Care': 5, 'Health Devices': 14, 'Wellness Drinks': 4, 'Medicines': 3}
holding_costs = {'Supplements': 15, 'Personal Care': 12, 'Health Devices': 8, 'Wellness Drinks': 10, 'Medicines': 20}
order_costs = {'Supplements': 800, 'Personal Care': 600, 'Health Devices': 1200, 'Wellness Drinks': 500, 'Medicines': 400}

skus = []
sku_id = 1
for cat, items in categories.items():
    for item in items:
        skus.append({
            'sku_id': f'SKU{str(sku_id).zfill(3)}',
            'sku_name': item,
            'category': cat,
            'supplier': suppliers[cat],
            'lead_time_days': lead_times[cat],
            'holding_cost_pct': holding_costs[cat],
            'order_cost_inr': order_costs[cat],
            'unit_price_inr': round(random.uniform(80, 1800), 2),
            'current_stock': random.randint(10, 300)
        })
        sku_id += 1

sku_df = pd.DataFrame(skus)

dates = pd.date_range('2023-01-01', '2024-12-31', freq='D')
sales_rows = []

for _, sku in sku_df.iterrows():
    base = random.uniform(5, 40)
    for d in dates:
        dow = d.dayofweek
        month = d.month
        seasonal = 1.0
        if sku['category'] == 'Supplements':
            seasonal = 1.3 if month in [1, 2] else (0.85 if month in [6, 7] else 1.0)
        elif sku['category'] == 'Wellness Drinks':
            seasonal = 1.4 if month in [10, 11] else (0.9 if month in [3, 4] else 1.0)
        elif sku['category'] == 'Medicines':
            seasonal = 1.3 if month in [7, 8, 9] else 1.0
        elif sku['category'] == 'Personal Care':
            seasonal = 1.2 if month in [3, 4, 5] else 1.0
        weekend_mult = 1.25 if dow >= 5 else 1.0
        noise = np.random.normal(1, 0.15)
        qty = max(0, round(base * seasonal * weekend_mult * noise))
        sales_rows.append({'date': d, 'sku_id': sku['sku_id'], 'qty_sold': qty})

sales_df = pd.DataFrame(sales_rows)
sku_df.to_csv('sku_master.csv', index=False)
sales_df.to_csv('sales_history.csv', index=False)
print(f"Generated {len(sku_df)} SKUs and {len(sales_df)} sales rows.")
print("Files saved: sku_master.csv, sales_history.csv")
