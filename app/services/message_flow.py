# from datetime import datetime, timedelta

# async def obtener_citas_desde_conn(conn):
#     hoy = datetime.today().date()
#     dias_a_generar = 6
#     fecha_inicial = hoy

#     rango_fechas = [fecha_inicial + timedelta(days=i) for i in range(dias_a_generar + 1)]

#     print(rango_fechas)
#     placeholders = ', '.join(['%s'] * len(rango_fechas))

#     async with conn.cursor() as cur:
#         query = f"SELECT DISTINCT fecha FROM dmty_citas WHERE fecha IN ({placeholders}) ORDER BY fecha;"
#         await cur.execute(query, rango_fechas)
#         result = await cur.fetchall()

#     return result