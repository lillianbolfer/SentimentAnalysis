import csv
import pandas as pd

df =pd.read_csv("Data\TwitterAnalysis.csv")

print(df["Text"][1])