from selenium import webdriver
from bs4 import BeautifulSoup

# Configuración de Selenium
options = webdriver.ChromeOptions()
options.add_argument('headless')  # Para no abrir una ventana del navegador
driver = webdriver.Chrome(options=options)

# URL de la página que quieres scrapear
url = 'https://www.donostia.eus/kirola/betetzemaila/Gimnasios_es#'

# Cargar la página con Selenium
driver.get(url)

# Obtener el contenido HTML después de que JavaScript haya cargado los datos
html = driver.page_source

# Cerrar el navegador Selenium
driver.quit()

# Parsear el contenido HTML con BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

# Buscar todos los elementos de interés
zones = soup.find_all('div', class_='zona-list')
print('eeeeeeeeeeeeeeeeeeeeeeeeeeeee',zones)

# Iterar sobre cada elemento encontrado y extraer la información deseada
for zone in zones:
    zone_name = zone.find('div', class_='zone-name').text.strip()
    zone_occupancy = zone.find('div', class_='zone-ocupation').text.strip()
    
    # Imprimir los resultados
    print("Nombre de la zona:", zone_name)
    print("Ocupación:", zone_occupancy)
    print()  # Para una línea en blanco entre cada resultado
