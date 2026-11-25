import data
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


# no modificar
def retrieve_phone_code(driver) -> str:
    """Este código devuelve un número de confirmación de teléfono y lo devuelve como un string.
    Utilízalo cuando la aplicación espere el código de confirmación para pasarlo a tus pruebas.
    El código de confirmación del teléfono solo se puede obtener después de haberlo solicitado en la aplicación."""

    import json
    import time
    from selenium.common import WebDriverException
    code = None
    for i in range(10):
        try:
            logs = [log["message"] for log in driver.get_log('performance') if log.get("message")
                    and 'api/v1/number?number' in log.get("message")]
            for log in reversed(logs):
                message_data = json.loads(log)["message"]
                body = driver.execute_cdp_cmd('Network.getResponseBody',
                                              {'requestId': message_data["params"]["requestId"]})
                code = ''.join([x for x in body['body'] if x.isdigit()])
        except WebDriverException:
            time.sleep(1)
            continue
        if not code:
            raise Exception("No se encontró el código de confirmación del teléfono.\n"
                            "Utiliza 'retrieve_phone_code' solo después de haber solicitado el código en tu aplicación.")
        return code


class UrbanRoutesPage:
    # Ruta y selección de tarifa
    from_field = (By.ID, 'from')
    to_field = (By.ID, 'to')
    order_taxi_button = (By.CSS_SELECTOR, 'button.button.round')
    comfort_tariff_card = (By.XPATH, "//div[@class='tcard-title' and text()='Comfort']/..")

    # Teléfono y confirmación SMS
    phone_button = (By.CLASS_NAME, 'np-button')
    phone_input = (By.ID, 'phone')
    phone_next_button = (By.XPATH, "//div[@class='section active']//button[@type='submit']")
    sms_code_input = (By.XPATH, "//div[@class='section active']//input[@id='code']")
    sms_confirm_button = (By.XPATH, "//div[@class='section active']//button[text()='Confirmar']")
    phone_value_text = (By.CLASS_NAME, 'np-text')

    # Método de pago / tarjeta de crédito
    payment_method_button = (By.CLASS_NAME, 'pp-button')
    add_card_button = (By.CLASS_NAME, 'pp-plus-container')
    card_number_input = (By.ID, 'number')
    card_code_input = (By.XPATH, "//input[@id='code' and @class='card-input']")
    link_card_button = (By.XPATH, "//div[@class='pp-buttons']//button[@type='submit']")
    close_payment_modal_button = (By.XPATH, "//div[@class='payment-picker open']//button[@class='close-button section-close']")
    payment_value_text = (By.CLASS_NAME, 'pp-value-text')

    # Mensaje y requisitos del pedido
    driver_message_input = (By.ID, 'comment')
    blanket_and_tissues_switch = (By.XPATH, "//div[@class='r-sw-label' and text()='Manta y pañuelos']/..//span[@class='slider round']")
    blanket_and_tissues_checkbox = (By.XPATH, "//div[@class='r-sw-label' and text()='Manta y pañuelos']/..//input[@class='switch-input']")
    ice_cream_plus_button = (By.XPATH, "//div[@class='r-counter-label' and text()='Helado']/..//div[@class='counter-plus']")
    ice_cream_counter_value = (By.XPATH, "//div[@class='r-counter-label' and text()='Helado']/..//div[@class='counter-value']")

    # Modal de búsqueda y asignación de conductor
    place_order_button = (By.CLASS_NAME, 'smart-button')
    order_modal = (By.CLASS_NAME, 'order-body')
    order_header_title = (By.CLASS_NAME, 'order-header-title')
    driver_rating = (By.CLASS_NAME, 'order-btn-rating')

    def __init__(self, driver):
        self.driver = driver

    def set_from(self, from_address):
        WebDriverWait(self.driver, 10).until(
            expected_conditions.visibility_of_element_located(self.from_field)
        ).send_keys(from_address)

    def set_to(self, to_address):
        WebDriverWait(self.driver, 10).until(
            expected_conditions.visibility_of_element_located(self.to_field)
        ).send_keys(to_address)

    def set_route(self, from_address, to_address):
        self.set_from(from_address)
        self.set_to(to_address)

    def get_from(self):
        return self.driver.find_element(*self.from_field).get_property('value')

    def get_to(self):
        return self.driver.find_element(*self.to_field).get_property('value')

    def click_order_taxi(self):
        WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable(self.order_taxi_button)
        ).click()

    def select_comfort_tariff(self):
        card = WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable(self.comfort_tariff_card)
        )
        if 'active' not in card.get_attribute('class'):
            card.click()

    def is_comfort_tariff_selected(self):
        card = WebDriverWait(self.driver, 10).until(
            expected_conditions.visibility_of_element_located(self.comfort_tariff_card)
        )
        return 'active' in card.get_attribute('class')

    def set_phone_number(self, phone_number):
        WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable(self.phone_button)
        ).click()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.visibility_of_element_located(self.phone_input)
        ).send_keys(phone_number)
        WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable(self.phone_next_button)
        ).click()

        code = retrieve_phone_code(self.driver)
        WebDriverWait(self.driver, 10).until(
            expected_conditions.visibility_of_element_located(self.sms_code_input)
        ).send_keys(code)
        WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable(self.sms_confirm_button)
        ).click()

    def get_phone_number(self):
        return WebDriverWait(self.driver, 10).until(
            expected_conditions.visibility_of_element_located(self.phone_value_text)
        ).text

    def add_credit_card(self, card_number, card_code):
        WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable(self.payment_method_button)
        ).click()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable(self.add_card_button)
        ).click()

        WebDriverWait(self.driver, 10).until(
            expected_conditions.visibility_of_element_located(self.card_number_input)
        ).send_keys(card_number)

        cvv_field = WebDriverWait(self.driver, 10).until(
            expected_conditions.visibility_of_element_located(self.card_code_input)
        )
        cvv_field.send_keys(card_code)
        # Quitar el enfoque del campo CVV para habilitar el botón 'Enlace'
        cvv_field.send_keys(Keys.TAB)

        WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable(self.link_card_button)
        ).click()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable(self.close_payment_modal_button)
        ).click()

    def get_payment_method(self):
        return WebDriverWait(self.driver, 10).until(
            expected_conditions.visibility_of_element_located(self.payment_value_text)
        ).text

    def set_driver_message(self, message):
        message_field = WebDriverWait(self.driver, 10).until(
            expected_conditions.visibility_of_element_located(self.driver_message_input)
        )
        message_field.clear()
        message_field.send_keys(message)

    def get_driver_message(self):
        return WebDriverWait(self.driver, 10).until(
            expected_conditions.visibility_of_element_located(self.driver_message_input)
        ).get_property('value')

    def toggle_blanket_and_tissues(self):
        switch = WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable(self.blanket_and_tissues_switch)
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", switch)
        switch.click()

    def is_blanket_and_tissues_selected(self):
        return self.driver.find_element(*self.blanket_and_tissues_checkbox).is_selected()

    def add_ice_cream(self, quantity=2):
        plus_button = WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable(self.ice_cream_plus_button)
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", plus_button)
        for _ in range(quantity):
            plus_button.click()

    def get_ice_cream_count(self):
        return int(WebDriverWait(self.driver, 10).until(
            expected_conditions.visibility_of_element_located(self.ice_cream_counter_value)
        ).text)

    def click_place_order(self):
        WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable(self.place_order_button)
        ).click()

    def is_order_modal_displayed(self):
        return WebDriverWait(self.driver, 10).until(
            expected_conditions.visibility_of_element_located(self.order_modal)
        ).is_displayed()

    def get_order_header_text(self):
        return WebDriverWait(self.driver, 10).until(
            expected_conditions.visibility_of_element_located(self.order_header_title)
        ).text

    def wait_for_driver_info(self, timeout=45):
        WebDriverWait(self.driver, timeout).until(
            expected_conditions.visibility_of_element_located(self.driver_rating)
        )
        return WebDriverWait(self.driver, 10).until(
            expected_conditions.visibility_of_element_located(self.order_header_title)
        ).text


class TestUrbanRoutes:

    driver = None

    @classmethod
    def setup_class(cls):
        # no lo modifiques, ya que necesitamos un registro adicional habilitado para recuperar el código de confirmación del teléfono
        from selenium.webdriver.chrome.options import Options
        options = Options()
        options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        cls.driver = webdriver.Chrome(options=options)

    def test_set_route(self):
        self.driver.get(data.urban_routes_url)
        routes_page = UrbanRoutesPage(self.driver)
        address_from = data.address_from
        address_to = data.address_to
        routes_page.set_route(address_from, address_to)
        assert routes_page.get_from() == address_from
        assert routes_page.get_to() == address_to

    def test_select_comfort_tariff(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.click_order_taxi()
        routes_page.select_comfort_tariff()
        assert routes_page.is_comfort_tariff_selected()

    def test_fill_phone_number(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.set_phone_number(data.phone_number)
        assert routes_page.get_phone_number() == data.phone_number

    def test_add_credit_card(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.add_credit_card(data.card_number, data.card_code)
        assert routes_page.get_payment_method() == 'Tarjeta'

    def test_write_message_for_driver(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.set_driver_message(data.message_for_driver)
        assert routes_page.get_driver_message() == data.message_for_driver

    def test_order_blanket_and_tissues(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.toggle_blanket_and_tissues()
        assert routes_page.is_blanket_and_tissues_selected()

    def test_order_two_ice_creams(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.add_ice_cream(2)
        assert routes_page.get_ice_cream_count() == 2

    def test_search_taxi_modal_appears(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.click_place_order()
        assert routes_page.is_order_modal_displayed()
        assert 'Buscar automóvil' in routes_page.get_order_header_text()

    def test_driver_info_appears(self):
        routes_page = UrbanRoutesPage(self.driver)
        header_text = routes_page.wait_for_driver_info(timeout=45)
        assert 'El conductor llegará en' in header_text and 'min' in header_text

    @classmethod
    def teardown_class(cls):
        cls.driver.quit()