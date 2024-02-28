# Web Scraper para trackear el resultado de la lotería miloto
# Importación de librerías necesarias para crear el Web Scraper
from bs4 import BeautifulSoup
import pandas
import pyarrow
import requests
import sys
import time
import openpyxl
import math

def guardar_en_excel():
	# Convertir la lista de balotas en columnas:

	new_data = []

	for _ in range(len(data)):
		sorteo_to_list = {
			"sorteo": data["sorteo"][_],
			"balota_1": data["balotas"][_][0],
			"balota_2": data["balotas"][_][1],
			"balota_3": data["balotas"][_][2],
			"balota_4": data["balotas"][_][3],
			"balota_5": data["balotas"][_][4],
			"acumulado": data["acumulado"][_],
			"fecha": data["fecha"][_]
		}

		new_data.append(sorteo_to_list)

	new_data = pandas.DataFrame(new_data)

	new_data.to_excel("output/sorteos.xlsx")


def obtener_numero_sorteos():
	pagina = requests.get("https://baloto.com/miloto/resultados")
	soup = BeautifulSoup(pagina.text, 'html.parser')

	strongs = soup.find_all('strong')

	global numero_sorteos

	for strong in strongs:
		strong_text_list = strong.text.split("#")

		if len(strong_text_list) > 1:
			numero_sorteos = int(strong_text_list[1])


def string_tiempo_empleado(ns):

	m = 0
	s = ns / 1000000000
	m = math.floor(s/60)
	s_restantes = s - m * 60

	if m > 0:
		en_texto = str(m) + " m, " + str(s_restantes) + " s"
	else:
		en_texto = str(s) + " s"

	return en_texto


# Variables necesarias
URLBASE = "https://baloto.com/miloto/resultados-miloto/"
N_SORTEOS_BASE = "SORTEO #"
BALOTAS_BASE = "yellow-ball"
ACUMULADO_BASE = "results-accumulated-number shadow-inner"
FECHA_BASE = "col-md-7 white-color text-center text-md-start text-lg-start"
numero_sorteos = 1
sorteos = []

# Para debugging
tiempo_inicial = time.time_ns()
tiempo_final = 0

mydivs = []

obtener_numero_sorteos()

for sorteo in range(numero_sorteos):
	print(f"Procesando sorteo N° {sorteo + 1}:")
	# Necesito una URL base para luego actualizar y trackear de una en una cada juego
	website = f"{URLBASE}{sorteo + 1}"
	print(f"\tWebsite: {website}")
	pagina = requests.get(website)
	soup = BeautifulSoup(pagina.text, 'html.parser')

	fecha_soup = soup.find("div", {"class": FECHA_BASE})
	fecha = fecha_soup.text.split("\n")[5]

	print(f"\tFecha: {fecha}")

	balotas_list = soup.find_all("div", {"class": BALOTAS_BASE})
	balotas = []

	print(f"\tBalotas: ", end="")

	for _ in balotas_list:
		new_balota = []
		_ = _.text.replace("<div class=\"yellow-ball\">", "")
		_ = _.replace(" ", "")
		_ = _.replace("\n", "")
		_ = _.replace("</div>", "")
		_ = _.strip()
		balotas.append(int(_))
		print(f"{_}", end=", ")

	acumulado_soup = soup.find("div", {"class": ACUMULADO_BASE})
	acumulado = acumulado_soup.text.replace(" ", "")
	acumulado = acumulado.replace("\n", "")
	acumulado = acumulado.replace("</div>", "")
	acumulado = acumulado.replace("$", "")
	acumulado = acumulado.strip()
	acumulado = int(acumulado)

	print(f"\n\tAcumulado: {acumulado} millones")

	sorteo_to_list = {
		"sorteo": sorteo + 1,
		"balotas": balotas,
		"acumulado": acumulado,
		"fecha": fecha
	}

	sorteos.append(sorteo_to_list)
	print("------------------------------------\n")

tiempo_final = time.time_ns()

print(f"Finalizado.\nSe procesaron {numero_sorteos} sorteos en un total de {string_tiempo_empleado((tiempo_final - tiempo_inicial))}")

on_running = True

while on_running:

	data = pandas.DataFrame(sorteos)

	print(f"¿Qué deseas realizar con los datos?")
	print("1. Guardar en un archivo .CSV")
	print("2. Guardar en un archivo de excel")
	print("3. Todos")
	print("Cualquier otra tecla para salir.")

	try:
		option = int(input("Ingrese la opción (Número): "))

		if option >= 4 or option <=0:
			sys.exit(0)

	except ValueError:
		sys.exit(0)

	if option == 1:
		print("Creando archivo .CSV...")
		data.to_csv("output/sorteos.csv")
		print("Archivo .CSV creado")
	elif option == 2:

		# Para excel, haremos que cada balota sea una columna

		print("Creando archivo de excel...")

		guardar_en_excel()

		print("Archivo de excel creado")
	elif option == 3:
		print("Creando archivo .CSV...")
		data.to_csv("output/sorteos.csv")
		print("Archivo .CSV creado")
		print("Creando archivo de excel...")
		guardar_en_excel()
		print("Archivo de excel creado")
	else:
		sys.exit(0)

	print("-----------------------------------------")
