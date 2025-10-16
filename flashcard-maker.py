import pandas as pd

excel_file = "arabic-vocabulary-master-list.xlsx"

df = pd.read_excel(excel_file)

df.to_csv("output.csv", index=False)

print(df.head())

# df.tosql