import pandas as pd
all_items_df = pd.read_csv('sample_data.csv')
all_items_dump = all_items_df.to_dict(orient='records')