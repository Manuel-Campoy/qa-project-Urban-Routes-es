# Urban Routes — Automatización de Pruebas E2E

## Descripción del proyecto
Suite de pruebas automatizadas de extremo a extremo (End-to-End) para la aplicación web **Urban Routes**. El proyecto valida el flujo completo de solicitud de un taxi con tarifa **Comfort**, desde la configuración de las direcciones de origen y destino hasta la confirmación de asignación del conductor.

## Tecnologías y técnicas utilizadas
* **Python 3:** Lenguaje base para el desarrollo de las pruebas y aserciones.
* **Selenium WebDriver (Selenium 4):** Automatización de interacciones en Google Chrome (clics, ingreso de texto, envío de teclas `Keys.TAB` y desplazamiento en el DOM con JavaScript).
* **Pytest:** Ejecución estructurada de la suite de pruebas y reporte detallado en consola.
* **Page Object Model (POM):** Separación entre los localizadores e interacciones de interfaz (`UrbanRoutesPage`) y las verificaciones (`TestUrbanRoutes`).
* **Esperas explícitas (`WebDriverWait` + `expected_conditions`):** Sincronización con elementos asíncronos, modales y temporizadores de búsqueda.
* **Chrome DevTools Protocol (CDP):** Interceptación de registros de red (`performance` logs) mediante `retrieve_phone_code()` para obtener el código de confirmación SMS.
* **Validación de texto dinámico:** Verificación por subcadenas (`in`) para comprobar el mensaje de llegada del conductor sin depender de un valor fijo de minutos.

## Notas técnicas y adaptaciones de implementación

### Migración de `setup_class` de Selenium 3 a Selenium 4
La plantilla inicial del proyecto estaba configurada para **Selenium 3** utilizando `DesiredCapabilities` y el argumento `desired_capabilities` en `webdriver.Chrome()`, parámetro eliminado en **Selenium 4** (`TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'`).

Para mantener la compatibilidad con **Selenium 4** (y aprovechar la gestión automática del controlador mediante *Selenium Manager*) sin perder el acceso a los registros de red necesarios para `retrieve_phone_code()`, se actualizó `setup_class` en `TestUrbanRoutes` empleando `ChromeOptions`:

```python
from selenium.webdriver.chrome.options import Options

options = Options()
options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
cls.driver = webdriver.Chrome(options=options)
```

### Validación de tiempo dinámico en `test_driver_info_appears`
El tiempo estimado de llegada del conductor varía en cada ejecución (por ejemplo, `'El conductor llegará en 6 min.'` o `'El conductor llegará en 9 min'`). Para evitar falsos negativos sin importar módulos adicionales como `re`, la aserción verifica los fragmentos fijos del encabezado:

```python
assert 'El conductor llegará en' in header_text and 'min' in header_text
```

## Cobertura de pruebas (`TestUrbanRoutes`)
1. `test_set_route`: Configura las direcciones de origen y destino.
2. `test_select_comfort_tariff`: Abre el selector de tarifas y elige **Comfort**.
3. `test_fill_phone_number`: Registra el número de teléfono e intercepta el código SMS.
4. `test_add_credit_card`: Vincula una tarjeta de crédito desenfocando el campo CVV (`Keys.TAB`) para habilitar el botón de enlace.
5. `test_write_message_for_driver`: Ingresa un mensaje personalizado para el conductor.
6. `test_order_blanket_and_tissues`: Activa el interruptor de **Manta y pañuelos**.
7. `test_order_two_ice_creams`: Incrementa a `2` la cantidad de **Helado**.
8. `test_search_taxi_modal_appears`: Confirma el pedido y valida el modal de búsqueda (`Buscar automóvil`).
9. `test_driver_info_appears`: Espera la asignación del conductor y verifica el mensaje de tiempo estimado de llegada.

## Estructura del proyecto
* `data.py`: URL del entorno de pruebas y datos de entrada (direcciones, teléfono, tarjeta y mensaje).
* `main.py`: Función `retrieve_phone_code()`, clase `UrbanRoutesPage` (POM) y clase de pruebas `TestUrbanRoutes`.
* `README.md`: Documentación del proyecto e instrucciones de ejecución.

## Cómo ejecutar las pruebas

1. **Clonar el repositorio y entrar al directorio del proyecto:**
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd <NOMBRE_DEL_DIRECTORIO>
   ```

2. **Instalar las dependencias:**
   ```bash
   pip install selenium pytest
   ```

3. **Verificar la URL activa en `data.py`:**
   Confirma que la variable `urban_routes_url` contenga la URL vigente del servidor de pruebas.

4. **Ejecutar la suite de pruebas:**
   * **Desde la terminal:**
```bash
pytest main.py -v
```
   * **Desde PyCharm:** Crear una configuración de ejecución de tipo **pytest**, seleccionar `script` apuntando a `main.py`, añadir `-v` en *Additional arguments* y establecer la carpeta raíz del proyecto como *Working directory*.