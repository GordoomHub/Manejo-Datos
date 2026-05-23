"""
data_practica.py
Práctica de ETL con pandas, SQLite3 y Expresiones Regulares
Fuente de datos: members.csv
"""

import os
import re
import sqlite3
import pandas as pd
from datetime import datetime


CREAR AMBIENTE VIRTUAL (instrucciones)

# Para crear el ambiente virtual ejecuta en terminal:
#   python -m venv venv_mlearning
#   source venv_mlearning/bin/activate        (Linux/Mac)
#   venv_mlearning\Scripts\activate           (Windows)
#   pip install pandas

CSV_PATH = "members.csv"
DB_PATH  = "members.db"


df = pd.read_csv(CSV_PATH)
print(f"[INFO] CSV cargado: {len(df)} filas, {len(df.columns)} columnas")


conn = sqlite3.connect(DB_PATH)
df.to_sql("members", conn, if_exists="replace", index=False)
print(f"[INFO] Tabla 'members' creada en {DB_PATH}")


cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM members")
print(f"[INFO] Registros en SQLite3: {cursor.fetchone()[0]}")

def extract_postal_code(series: pd.Series) -> pd.Series:
    """
    Extrae el código postal numérico de 5 dígitos al final de la dirección.
    Patrón RegEx: \\b\\d{5}\\b
      \\b  → límite de palabra
      \\d{5} → exactamente 5 dígitos
      \\b  → límite de palabra
    Retorna una Serie con el código postal (str) o NaN si no se encuentra.
    """
    pattern = r"\b(\d{5})\b"
    return series.str.extract(pattern, expand=False)


df["postal_code"] = extract_postal_code(df["address"])
print("\n[EXTRACCIÓN] Códigos postales extraídos (primeras 5 filas):")
print(df[["address", "postal_code"]].head())
print(f"  → Nulos encontrados: {df['postal_code'].isna().sum()}")

def clean_phone_number(series: pd.Series) -> pd.Series:
    """
    Elimina del número telefónico los caracteres no numéricos:
      +  →  símbolo de código de país
      (  )  →  paréntesis
      -  →  guiones
      \\s  →  espacios en blanco
    Patrón RegEx: [+()\\-\\s]
    Retorna la serie con números sólo dígitos.
    """
    pattern = r"[+()\-\s]"
    return series.str.replace(pattern, "", regex=True)


df["phone_clean"] = clean_phone_number(df["phone_number"])
print("\n[TRANSFORMACIÓN] Teléfonos formateados (primeras 5 filas):")
print(df[["phone_number", "phone_clean"]].head())

MONTHS = {
    "jan": "01", "feb": "02", "mar": "03", "apr": "04",
    "may": "05", "jun": "06", "jul": "07", "aug": "08",
    "sep": "09", "oct": "10", "nov": "11", "dec": "12",
    "ene": "01", "abr": "04", "ago": "08",
}

PATTERN_TEXT_DATE = re.compile(
    r"(\d{1,2})[\s\-]([a-zA-Z]{3})[\s\-](\d{2,4})",
    re.IGNORECASE
)


def format_birth_date(series: pd.Series) -> pd.Series:
    """
    Normaliza la columna birth_date a formato DD/MM/YYYY.
    Soporta formatos:
      - "05-feb-91"   (día-mes_texto-año2d)
      - "11 Jan 1993" (día mes_texto año4d)
    RegEx usada: (\\d{1,2})[\\s\\-]([a-zA-Z]{3})[\\s\\-](\\d{2,4})
    """
    def convert(value: str) -> str:
        match = PATTERN_TEXT_DATE.search(str(value))
        if not match:
            return None
        day, month_txt, year = match.groups()
        month_num = MONTHS.get(month_txt.lower(), "00")
        # Normalizar año de 2 dígitos
        if len(year) == 2:
            year = "19" + year if int(year) > 25 else "20" + year
        return f"{int(day):02d}/{month_num}/{year}"

    return series.apply(convert)

df["birth_date_fmt"] = format_birth_date(df["birth_date"])
print("\n[NACIMIENTO] Fechas formateadas a DD/MM/YYYY (primeras 5 filas):")
print(df[["birth_date", "birth_date_fmt"]].head())

def calculate_age(birth_fmt_series: pd.Series,
                  ref_unix_series: pd.Series) -> pd.Series:
    """
    Calcula la edad en años a partir de:
      birth_date_fmt  → fecha de nacimiento en DD/MM/YYYY
      register_time   → timestamp Unix del registro

    Pasos:
      1. Convertir register_time (Unix epoch) a datetime.
      2. Parsear birth_date_fmt con strptime.
      3. Restar y dividir por 365.25 para obtener años completos.
    """
    def age(row):
        try:
            ref_date = datetime.fromtimestamp(row["register_time"])
            born = datetime.strptime(row["birth_date_fmt"], "%d/%m/%Y")
            delta_days = (ref_date - born).days
            return int(delta_days / 365.25)
        except Exception:
            return None

    tmp = pd.DataFrame({
        "birth_date_fmt": birth_fmt_series,
        "register_time":  ref_unix_series,
    })
    return tmp.apply(age, axis=1)


df["age_at_register"] = calculate_age(df["birth_date_fmt"], df["register_time"])
print("\n[EDAD] Edad al momento del registro (primeras 5 filas):")
print(df[["birth_date_fmt", "register_time", "age_at_register"]].head())

df.to_sql("members_transformed", conn, if_exists="replace", index=False)
print("\n[INFO] Tabla 'members_transformed' guardada en SQLite3.")

print("\n─── Resumen final (primeras 5 filas) ───")
print(df[["first_name", "last_name", "postal_code",
          "phone_clean", "birth_date_fmt", "age_at_register"]].head().to_string())

conn.close()
print("\n[OK] Proceso ETL completado exitosamente.")
