import pandas as pd
from src.db.connection import engine


def _read(table_name: str, store_id: str) -> pd.DataFrame:
    query = f"SELECT * FROM {table_name} WHERE store_id = %(store_id)s"
    return pd.read_sql(query, engine, params={"store_id": store_id})


def load_orders(store_id: str = "STORE_001"):
    df = _read("orders", store_id)
    df["price_clean"] = df["item_price"].str.replace(r"[\$,\s]", "", regex=True).astype(float)
    return df


def load_inventory(store_id: str = "STORE_001"):
    return _read("inventory", store_id)


def load_recipes(store_id: str = "STORE_001"):
    return _read("recipes", store_id)


def get_sales_summary(orders_df):
    summary = orders_df.groupby("item_name").agg(
        total_quantity=("quantity", "sum"),
        total_revenue=("price_clean", "sum"),
        num_orders=("order_id", "nunique")
    ).reset_index()
    return summary.sort_values("total_quantity", ascending=False)


def load_kitchen_orders(store_id: str = "STORE_001"):
    return _read("kitchen_orders", store_id)


def load_menu_prep_times(store_id: str = "STORE_001"):
    return _read("menu_prep_times", store_id)


def load_staff_schedule(store_id: str = "STORE_001"):
    return _read("staff_schedule", store_id)


def load_staff_performance(store_id: str = "STORE_001"):
    return _read("staff_performance", store_id)


def load_waste_log(store_id: str = "STORE_001"):
    return _read("waste_log", store_id)


def load_packaging_inventory(store_id: str = "STORE_001"):
    return _read("packaging_inventory", store_id)


def load_packaging_usage(store_id: str = "STORE_001"):
    return _read("packaging_usage", store_id)


def get_ingredient_usage(orders_df, recipes_df):
    orders_with_recipes = orders_df.merge(
        recipes_df,
        left_on="item_name",
        right_on="menu_item",
        how="inner"
    )
    orders_with_recipes["total_kg_used"] = (
        orders_with_recipes["quantity"] *
        orders_with_recipes["quantity_kg_per_serving"]
    )
    ingredient_usage = orders_with_recipes.groupby("ingredient").agg(
        total_kg_consumed=("total_kg_used", "sum"),
        total_orders=("order_id", "nunique")
    ).reset_index()
    return ingredient_usage.sort_values("total_kg_consumed", ascending=False)


def load_customers(store_id: str = "STORE_001"):
    return _read("customers", store_id)


def load_customer_orders(store_id: str = "STORE_001"):
    return _read("customer_orders", store_id)


def load_customer_feedback(store_id: str = "STORE_001"):
    return _read("customer_feedback", store_id)


def load_offers(store_id: str = "STORE_001"):
    return _read("offers", store_id)


def load_weather_log(store_id: str = "STORE_001"):
    return _read("weather_log", store_id)


def load_festivals(store_id: str = "STORE_001"):
    return _read("festivals", store_id)


def load_local_news(store_id: str = "STORE_001"):
    return _read("local_news", store_id)


def load_menu_pricing(store_id: str = "STORE_001"):
    return _read("menu_pricing", store_id)


def load_finance_summary(store_id: str = "STORE_001"):
    return _read("finance_summary", store_id)


def load_campaigns(store_id: str = "STORE_001"):
    return _read("campaigns", store_id)


def load_suppliers(store_id: str = "STORE_001"):
    return _read("suppliers", store_id)