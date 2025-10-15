# ANMAT Vademécum Scraper

Herramienta automatizada para extraer la lista completa de medicamentos registrados en Argentina desde el Vademécum Nacional de Medicamentos de ANMAT.

## Descripción

Este scraper automatiza la búsqueda y extracción de medicamentos desde el sitio oficial de consulta pública de ANMAT (https://servicios.pami.org.ar/vademecum/views/consultaPublica/listado.zul).

Dado que la página requiere un mínimo de 3 caracteres en el campo de búsqueda por nombre comercial, el script genera y prueba todas las combinaciones posibles de 3 letras (AAA, AAB, AAC, ..., ZZX, ZZY, ZZZ) para obtener una cobertura completa.

## Características

- Búsqueda automatizada por todas las combinaciones posibles (17,576 combinaciones)
- Extracción de múltiples páginas de resultados por búsqueda
- Manejo de errores y timeout
- Capacidad de pausar y reanudar el scraping
- Exportación directa a formato CSV
- Opción de modo headless (sin interfaz gráfica)
- Control de velocidad de solicitudes para no sobrecargar el servidor

## Datos Extraídos

Para cada medicamento se extrae:

- **Nombre Comercial y Presentación**: Nombre del producto y su presentación
- **Monodroga/Genérico**: Principio activo o nombre genérico
- **Laboratorio**: Fabricante del medicamento
- **Forma Farmacéutica**: Cápsula, comprimido, jarabe, etc.
- **Número de Certificado**: Número de certificación ANMAT
- **GTIN**: Código de barras del producto
- **Disponibilidad**: Estado de disponibilidad comercial
- **Timestamp**: Fecha y hora de extracción

## Requisitos

- Python 3.7 o superior
- Google Chrome instalado
- ChromeDriver (se maneja automáticamente)

## Instalación

1. Clonar o descargar este repositorio:
```bash
cd MedicamentosANMAT
```

2. Crear un entorno virtual (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Uso

### Uso Básico

Para ejecutar el scraper completo (todas las combinaciones):

```bash
python anmat_scraper.py
```

### Configuración en el código

Editar las siguientes variables en `anmat_scraper.py`:

```python
scraper = ANMATScraper(
    output_file='medicamentos_anmat.csv',  # Nombre del archivo de salida
    headless=False,  # True para ejecutar sin ventana visible
    delay=2  # Segundos de espera entre solicitudes
)
```

### Modo de prueba (búsquedas limitadas)

Para probar con un número limitado de búsquedas:

```python
scraper.run(max_searches=10)  # Solo las primeras 10 combinaciones
```

### Reanudar desde un punto específico

Si el proceso se interrumpe, puedes reanudarlo desde donde quedó:

```python
scraper.run(start_from='ABC')  # Reanudar desde la combinación 'ABC'
```

### Modo headless (sin interfaz gráfica)

Para ejecutar en un servidor o en segundo plano:

```python
scraper = ANMATScraper(
    output_file='medicamentos_anmat.csv',
    headless=True,  # No abre ventana del navegador
    delay=2
)
```

## Salida

El script genera un archivo CSV con el siguiente formato:

```csv
Nombre_Comercial_Presentacion,Monodroga_Generico,Laboratorio,Forma_Farmaceutica,Numero_Certificado,GTIN,Disponibilidad,Timestamp_Extraccion
"CREON 25000 - 1 FRASCO por 20 UNIDADES","AMILASA 18000 U PH EUR + LIPASA 25000 U PH EUR + PROTEASA 1000 U PH EUR",ABBOTT LABORATORIES ARGENTINA S.A.,CAPSULA,41928,,"Disponible",2025-10-10T10:30:00
```

## Tiempo Estimado

Con 17,576 combinaciones posibles y un delay de 2 segundos:
- **Tiempo mínimo estimado**: ~10 horas
- **Tiempo real**: Puede ser mayor dependiendo de:
  - Velocidad de respuesta del servidor
  - Cantidad de resultados por búsqueda
  - Número de páginas de resultados

## Consideraciones Importantes

1. **Uso Ético**: Este scraper debe usarse de manera responsable
2. **Delay entre solicitudes**: El delay de 2 segundos ayuda a no sobrecargar el servidor
3. **Datos Públicos**: Los datos son de acceso público según el sitio de ANMAT
4. **Actualizaciones**: El vademécum se actualiza periódicamente, se recomienda ejecutar el scraper periódicamente

## Solución de Problemas

### ChromeDriver no encontrado

Si aparece error de ChromeDriver, asegurarse de que Chrome está instalado o instalar ChromeDriver manualmente.

### Elementos no encontrados

Si la página de ANMAT cambia su estructura, es posible que los selectores XPath necesiten actualizarse en el código.

### Timeout errors

Aumentar el valor de timeout en la configuración:

```python
self.wait = WebDriverWait(self.driver, 30)  # Aumentar de 15 a 30 segundos
```

### Memoria insuficiente

Para sesiones muy largas, considerar dividir el scraping en bloques usando `start_from` y `max_searches`.

## Estructura del Proyecto

```
MedicamentosANMAT/
│
├── anmat_scraper.py          # Script principal
├── requirements.txt          # Dependencias
├── README.md                 # Este archivo
└── medicamentos_anmat.csv    # Archivo de salida (generado)
```

## Licencia

Este proyecto es de código abierto para uso educativo y de investigación.

## Descargo de Responsabilidad

Esta herramienta accede a datos públicos del sitio web de ANMAT. Los usuarios son responsables del uso que le den a los datos extraídos y deben cumplir con todas las leyes y regulaciones aplicables.

## Autor

Creado para facilitar el acceso programático al Vademécum Nacional de Medicamentos de Argentina.

## Versión

1.0.0 - Octubre 2024

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue primero para discutir los cambios que te gustaría realizar.

## Contacto

Para preguntas o sugerencias, por favor abre un issue en este repositorio.
