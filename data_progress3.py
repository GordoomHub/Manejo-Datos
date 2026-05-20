import pandas as pd
from datetime import date

df = pd.read_csv("pipol_dataset.csv")

df["birthday"] = pd.to_datetime(df["birthday"], format="%d/%m/%Y")
today = date.today()
df["age"] = df["birthday"].apply(
    lambda b: today.year - b.year - ((today.month, today.day) < (b.month, b.day))
)

# 4a) Agrupar por país y ciudad — obtener el grupo México / Dusty City
grupo = df.groupby(["country", "city"])
mexico_dusty = grupo.get_group(("Mexico", "Dusty City"))

print("4a) Personas en México - Dusty City:")
print(mexico_dusty[["name", "last_name", "city", "country", "age"]])
print()

# 4b) Edad promedio de cada país (agrupación multinivel país + ciudad, luego por país)
edad_por_pais_ciudad = df.groupby(["country", "city"]).agg(edad_promedio=("age", "mean")).round(1)
print("Edad promedio por país y ciudad:")
print(edad_por_pais_ciudad)
print()

edad_por_pais = df.groupby("country").agg(edad_promedio=("age", "mean")).round(1)
print("4b) Edad promedio por país:")
print(edad_por_pais)
