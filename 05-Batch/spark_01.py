from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, count, unix_timestamp, max

def size_files():
    import os

    directorio = "datos_reparticionado.parquet"
    archivos_parquet = [
        os.path.join(directorio, archivo)
        for archivo in os.listdir(directorio)
        if archivo.endswith(".parquet")
    ]
    
    if not archivos_parquet:
        print("No se encontraron archivos Parquet en el directorio.")
    else:
        tamaños = [os.path.getsize(archivo) for archivo in archivos_parquet]
        tamaño_total_bytes = sum(tamaños)
        num_archivos = len(archivos_parquet)
        tamaño_promedio_bytes = tamaño_total_bytes / num_archivos
    
        # Convertir a MB
        tamaño_promedio_mb = tamaño_promedio_bytes / (1024 * 1024)
    
        print(f"Número de archivos Parquet: {num_archivos}")
        print(f"Tamaño promedio de los archivos Parquet: {tamaño_promedio_mb:.2f} MB")

# Inicializar SparkSession
spark = SparkSession.builder.appName("AnalisisUnificado").getOrCreate()

# Leer los archivos de datos una sola vez
df_viajes = spark.read.parquet("yellow_tripdata_2024-10.parquet") # o spark.read.csv("tu_archivo_de_datos.csv", header=True)
df_zonas = spark.read.csv("taxi_zone_lookup.csv", header=True)

print(f'Versión de pyspark: {pyspark.__version__}')

# --- 0 Reparticionar DataFrame en 4 particiones
df_reparticionado = df_viajes.repartition(4)

# Guardar el DataFrame reparticionado en formato Parquet
df_reparticionado.write.parquet("datos_reparticionado.parquet")

size_files()

# --- 1. ¿Cuántos viajes en taxi hubo el 15 de octubre de 2024? ---
df_viajes_fecha = df_viajes.withColumn("pickup_date", to_date(col("tpep_pickup_datetime")))
viajes_15_oct = df_viajes_fecha.filter(col("pickup_date") == "2024-10-15")
num_viajes_15_oct = viajes_15_oct.agg(count("*")).collect()[0][0]
print(f"Número de viajes el 15 de octubre de 2024: {num_viajes_15_oct}")

# --- 2. ¿Cuál es la duración del viaje más largo en horas? ---
df_duracion = df_viajes.withColumn("pickup_timestamp", unix_timestamp(col("tpep_pickup_datetime"))) \
                          .withColumn("dropoff_timestamp", unix_timestamp(col("tpep_dropoff_datetime"))) \
                          .withColumn("duracion_segundos", col("dropoff_timestamp") - col("pickup_timestamp")) \
                          .withColumn("duracion_horas", col("duracion_segundos") / 3600)
duracion_maxima = df_duracion.agg(max("duracion_horas")).collect()[0][0]
print(f"Duración máxima del viaje: {duracion_maxima:.2f} horas")

# --- 3. ¿Cuál es la zona de recogida MENOS frecuente en octubre de 2024? ---
df_octubre_2024 = df_viajes_fecha.filter(col("pickup_date").between("2024-10-01", "2024-10-31"))
df_unido = df_octubre_2024.join(df_zonas, df_octubre_2024.PULocationID == df_zonas.LocationID, "left")
frecuencia_zonas = df_unido.groupBy("Zone").agg(count("*").alias("frecuencia"))
zona_menos_frecuente = frecuencia_zonas.orderBy(col("frecuencia")).first()
print(f"Zona de recogida menos frecuente en octubre de 2024: {zona_menos_frecuente.Zone}")

# Detener SparkSession una sola vez al final
spark.stop()
