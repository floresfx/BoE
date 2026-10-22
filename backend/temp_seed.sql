SELECT id, lot_code, quantity, unit_cost FROM stock_lots WHERE resource_id = 'c1241bfa-0687-4b40-aae4-ab5dfdfe9eef';
ON CONFLICT DO NOTHING;
