import pandas as pd

# 1. Crear la variable path con la URL de GitHub (usa tu URL Raw aquí)
path = "https://raw.githubusercontent.com/GordoomHub/Manejo-Datos/refs/heads/main/pipol_dataset.csv"

# 2. Leer el archivo utilizando el comando para el tipo de archivo (.csv)
df = pd.read_csv(path)

# 3. Mostrar la estructura o información del archivo
print("--- Información del DataFrame ---")
df.info()

# 4. Mostrar los primeros 5 elementos con head
print("\n--- Primeros 5 elementos ---")
print(df.head())

# 5. Muestre las columnas con los datos: Nombre y País
print("\n--- Columnas Nombre y País ---")
print(df[['name', 'country']])

# 6. Muestre por medio de índices (3 índices) lo que contienen dichas filas
#Ejemplo: mostramos las filas con índice 0, 1 y 2
print("\n--- Filas por índices (0, 1, 2) ---")
print(df.iloc[0:3])

# 7. Filtrar por país todos los que pertenecen a México
print("\n--- Personas de México ---")
mexico_df = df[df['country'] == 'Mexico']
print(mexico_df)

# 8. Filtrar por país México y que viven en Dusty City
print("\n--- Personas de México en Dusty City ---")
filtro_especifico = df[(df['country'] == 'Mexico') & (df['city'] == 'Dusty City')]
print(filtro_especifico)