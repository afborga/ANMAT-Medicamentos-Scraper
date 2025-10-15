"""
ANMAT Vademécum Scraper
Extrae todos los medicamentos del vademécum oficial de ANMAT
"""

import time
import csv
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import itertools
import string


class ANMATScraper:
    def __init__(self, output_file='medicamentos_anmat.csv', headless=False, delay=2):
        """
        Inicializa el scraper

        Args:
            output_file: Nombre del archivo CSV de salida
            headless: Si True, ejecuta Chrome en modo sin interfaz gráfica
            delay: Tiempo de espera en segundos entre solicitudes
        """
        self.url = "https://servicios.pami.org.ar/vademecum/views/consultaPublica/listado.zul"
        self.output_file = output_file
        self.delay = delay
        self.results_count = 0

        # Configurar opciones de Chrome
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")

        # Inicializar driver
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 15)

        # Crear archivo CSV con encabezados
        self._init_csv()

    def _init_csv(self):
        """Inicializa el archivo CSV con encabezados"""
        with open(self.output_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Nombre_Comercial_Presentacion',
                'Monodroga_Generico',
                'Laboratorio',
                'Forma_Farmaceutica',
                'Numero_Certificado',
                'GTIN',
                'Disponibilidad',
                'Timestamp_Extraccion'
            ])

    def generate_search_terms(self, length=3):
        """
        Genera todas las combinaciones posibles de letras

        Args:
            length: Longitud de las combinaciones (mínimo 3 según la página)

        Yields:
            Combinaciones de letras
        """
        letters = string.ascii_uppercase
        for combo in itertools.product(letters, repeat=length):
            yield ''.join(combo)

    def search_by_commercial_name(self, search_term):
        """
        Realiza una búsqueda por nombre comercial

        Args:
            search_term: Término de búsqueda (mínimo 3 caracteres)

        Returns:
            Lista de medicamentos encontrados
        """
        try:
            # Navegar a la página
            self.driver.get(self.url)
            time.sleep(2)

            # Esperar a que cargue el campo de búsqueda de nombre comercial
            nombre_comercial_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@maxlength='255']"))
            )

            # Encontrar todos los inputs con maxlength='255' (genérico y comercial)
            inputs = self.driver.find_elements(By.XPATH, "//input[@maxlength='255']")

            # El segundo input es el de Nombre Comercial
            if len(inputs) >= 2:
                nombre_comercial_input = inputs[1]

            # Limpiar el campo y escribir el término de búsqueda
            nombre_comercial_input.clear()
            nombre_comercial_input.send_keys(search_term)
            time.sleep(0.5)

            # Hacer clic en el botón Buscar
            buscar_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn-default') and contains(., 'Buscar')]"))
            )
            buscar_btn.click()

            # Esperar a que carguen los resultados
            time.sleep(self.delay)

            # Verificar si hay resultados
            try:
                empty_msg = self.driver.find_element(By.XPATH, "//*[contains(text(), 'No se han encontrado resultados')]")
                print(f"  No hay resultados para: {search_term}")
                return []
            except NoSuchElementException:
                pass

            # Extraer resultados
            return self._extract_results(search_term)

        except TimeoutException:
            print(f"  Timeout en búsqueda: {search_term}")
            return []
        except Exception as e:
            print(f"  Error en búsqueda {search_term}: {str(e)}")
            return []

    def _extract_results(self, search_term):
        """
        Extrae los resultados de la tabla de medicamentos

        Returns:
            Lista de diccionarios con datos de medicamentos
        """
        results = []

        try:
            # Esperar a que aparezca la tabla de resultados
            time.sleep(2)

            # Procesar todas las páginas de resultados
            page_num = 1
            while True:
                print(f"    Procesando página {page_num} de resultados...")

                # Extraer filas de la tabla
                rows = self.driver.find_elements(By.XPATH, "//div[@class='z-grid-body']//tr[contains(@class, 'z-row')]")

                if not rows:
                    break

                for row in rows:
                    try:
                        cells = row.find_elements(By.TAG_NAME, "td")

                        if len(cells) >= 8:
                            # Extraer datos de cada celda
                            numero_certificado = cells[1].text.strip()
                            laboratorio = cells[2].text.strip()
                            nombre_comercial = cells[3].text.strip()
                            forma_farmaceutica = cells[4].text.strip()
                            presentacion = cells[5].text.strip()
                            generico = cells[7].text.strip()

                            # GTIN puede estar oculto
                            try:
                                gtin = cells[6].text.strip()
                            except:
                                gtin = ""

                            # Disponibilidad
                            try:
                                disponibilidad_icon = cells[9].find_element(By.TAG_NAME, "img")
                                disponibilidad = "Disponible" if "eye" in disponibilidad_icon.get_attribute("src") else "No disponible"
                            except:
                                disponibilidad = ""

                            # Combinar nombre comercial con presentación
                            nombre_completo = f"{nombre_comercial} - {presentacion}"

                            resultado = {
                                'Nombre_Comercial_Presentacion': nombre_completo,
                                'Monodroga_Generico': generico,
                                'Laboratorio': laboratorio,
                                'Forma_Farmaceutica': forma_farmaceutica,
                                'Numero_Certificado': numero_certificado,
                                'GTIN': gtin,
                                'Disponibilidad': disponibilidad,
                                'Timestamp_Extraccion': datetime.now().isoformat()
                            }

                            results.append(resultado)

                    except Exception as e:
                        print(f"      Error extrayendo fila: {str(e)}")
                        continue

                # Verificar si hay más páginas
                try:
                    # Buscar el botón "Siguiente"
                    next_button = self.driver.find_element(By.XPATH, "//button[@title='Next Page' or contains(@class, 'z-paging-next')]")

                    # Verificar si está deshabilitado
                    if 'z-paging-disabled' in next_button.get_attribute('class'):
                        break

                    next_button.click()
                    time.sleep(self.delay)
                    page_num += 1

                except NoSuchElementException:
                    break

            return results

        except Exception as e:
            print(f"    Error extrayendo resultados: {str(e)}")
            return results

    def save_results(self, results):
        """
        Guarda los resultados en el archivo CSV

        Args:
            results: Lista de diccionarios con datos de medicamentos
        """
        if not results:
            return

        with open(self.output_file, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'Nombre_Comercial_Presentacion',
                'Monodroga_Generico',
                'Laboratorio',
                'Forma_Farmaceutica',
                'Numero_Certificado',
                'GTIN',
                'Disponibilidad',
                'Timestamp_Extraccion'
            ])

            for result in results:
                writer.writerow(result)
                self.results_count += 1

    def run(self, start_from=None, max_searches=None):
        """
        Ejecuta el scraper con todas las combinaciones

        Args:
            start_from: Término desde el cual empezar (para reanudar)
            max_searches: Número máximo de búsquedas a realizar (None = todas)
        """
        print("=" * 60)
        print("ANMAT Vademécum Scraper")
        print("=" * 60)
        print(f"URL: {self.url}")
        print(f"Archivo de salida: {self.output_file}")
        print(f"Delay entre solicitudes: {self.delay}s")
        print("=" * 60)

        search_count = 0
        start_searching = start_from is None

        try:
            for search_term in self.generate_search_terms(length=3):
                # Si hay un punto de inicio, esperar hasta llegar a él
                if not start_searching:
                    if search_term == start_from:
                        start_searching = True
                    else:
                        continue

                search_count += 1
                print(f"\n[{search_count}] Buscando: {search_term}")

                results = self.search_by_commercial_name(search_term)

                if results:
                    print(f"  ✓ Encontrados {len(results)} medicamentos")
                    self.save_results(results)
                    print(f"  Total acumulado: {self.results_count} medicamentos")

                # Verificar límite de búsquedas
                if max_searches and search_count >= max_searches:
                    print(f"\nAlcanzado límite de {max_searches} búsquedas")
                    break

                # Pequeña pausa entre búsquedas
                time.sleep(0.5)

        except KeyboardInterrupt:
            print("\n\n⚠ Interrupción detectada. Guardando progreso...")
            print(f"Última búsqueda: {search_term}")
            print(f"Para reanudar, usa: start_from='{search_term}'")

        finally:
            print("\n" + "=" * 60)
            print(f"Scraping finalizado")
            print(f"Total de medicamentos extraídos: {self.results_count}")
            print(f"Archivo guardado: {self.output_file}")
            print("=" * 60)
            self.close()

    def close(self):
        """Cierra el navegador"""
        if self.driver:
            self.driver.quit()


if __name__ == "__main__":
    # Configuración
    scraper = ANMATScraper(
        output_file='medicamentos_anmat.csv',
        headless=False,  # Cambiar a True para ejecutar sin ventana visible
        delay=2  # Segundos de espera entre solicitudes
    )

    # Ejecutar scraper
    # Para hacer una prueba limitada, descomentar la siguiente línea:
    # scraper.run(max_searches=10)

    # Para ejecutar completo (todas las combinaciones AAA-ZZZ):
    scraper.run()

    # Para reanudar desde un punto específico:
    # scraper.run(start_from='ABC')
