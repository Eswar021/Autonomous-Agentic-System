import pandas as pd
from pathlib import Path
from tools._paths import find_data_dir


def product_category_mapping() -> pd.DataFrame:
    """Creates a mapping between product_id and a product category.

    The mapping is based on product_id ranges. The function reads a CSV file
    containing the mapping from product_id to product category. The file is
    located in the same directory as the script.

    Returns:
        pandas.DataFrame: A DataFrame containing the product_id to product category mapping.
    """
    data_dir = find_data_dir(Path(__file__))
    mapping_file = data_dir / "product_category_mapping.csv"

    try:
        df = pd.read_csv(mapping_file)
        # Data quality checks: Ensures that product_id is an integer and product_category is a string
        df['product_id'] = df['product_id'].astype(int)
        df['product_category'] = df['product_category'].astype(str)

        # Validations: Checks if the product_category is one of the allowed values
        allowed_categories = ['flagship', 'mid-range', 'entry-level', 'accessory']
        df = df[df['product_category'].isin(allowed_categories)]

        return df

    except FileNotFoundError:
        print(f"Error: Mapping file not found at {mapping_file}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error reading or processing mapping file: {e}")
        return pd.DataFrame()


if __name__ == '__main__':
    # Create a dummy product_category_mapping.csv for testing
    # This part is only executed when the script is run directly
    # and won't affect the tool's functionality when called from other scripts.
    data = {
        'product_id': [100, 200, 300, 400],
        'product_category': ['flagship', 'mid-range', 'entry-level', 'accessory']
    }
    df = pd.DataFrame(data)
    data_dir = find_data_dir(Path(__file__))
    filepath = data_dir / 'product_category_mapping.csv'
    df.to_csv(filepath, index=False)

    # Example usage
    mapping_df = product_category_mapping()
    if not mapping_df.empty:
        print(mapping_df)
    else:
        print("No product category mapping available.")