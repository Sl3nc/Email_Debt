from selenium.common.exceptions import (
    NoSuchElementException, SessionNotCreatedException
)
from selenium.webdriver.chrome.service import Service
from driver_maintenanse import DriverMaintenance
from selenium.webdriver.common.by import By
from selenium import webdriver
from pathlib import Path
from time import sleep
from os import chmod

class Acessorias:
    """
    Classe responsável por automatizar o acesso ao sistema Acessorias.com para buscar e-mails de contato das empresas.
    """
    ROOT_FOLDER = Path(__file__).parent
    CHROME_DRIVER_PATH = ROOT_FOLDER / 'src' / 'drivers' / 'chromedriver'
    # CHROME_DRIVER_PATH = ROOT_FOLDER / 'src' / 'drivers' / 'chromedriver.exe'
    
    URL_MAIN = 'https://app.acessorias.com/sysmain.php'
    URL_DETALHES = 'https://app.acessorias.com/sysmain.php?m=105&act=e&i={0}&uP=14&o=EmpNome,EmpID|Asc'


    INPUT_EMAIL = 'mailAC'
    INPUT_PASSWORD= 'passAC'
    BTN_ENTRAR = '#site-corpo > section.secao.secao-login > div > form > div.botoes > button'

    def __init__(self) -> None:
        self.rowContato = 'divCtt_0_{0}'
        self.campo_nome = 'CttNome_0_{0}'
        self.campo_email = 'CttEMail_0_{0}'
        chmod(
            self.CHROME_DRIVER_PATH,
            755
        )

        self.browser = self.make_chrome_browser(hide=True)
        self.browser.get(self.URL_MAIN)
        pass

    def make_chrome_browser(self,*options: str, hide = True) -> webdriver.Chrome:
        """
        Cria uma instância do navegador Chrome para automação.
        """
        try:
            chrome_options = webdriver.ChromeOptions()

            if options is not None:
                for option in options:
                    chrome_options.add_argument(option)

            chrome_service = Service(
                executable_path=str(self.CHROME_DRIVER_PATH),
            )

            browser = webdriver.Chrome(
                service=chrome_service,
                options=chrome_options
            )

            if hide == True:
                browser.set_window_position(-10000,0)

            return browser
        except SessionNotCreatedException:
            DriverMaintenance().upgrade()
            return self.make_chrome_browser()

    
    def login(self, usuario: str, senha: str):
        """
        Realiza login no sistema Acessorias.com.
        """
        self.browser.find_element(By.NAME, self.INPUT_EMAIL).send_keys(usuario)
        self.browser.find_element(By.NAME, self.INPUT_PASSWORD).send_keys(senha)
        input()

        # self.browser.find_element(By.CSS_SELECTOR, self.BTN_ENTRAR).click()
        sleep(4)

    def pesquisar(self, num_empresa: str):
        """
        Pesquisa e retorna os contatos de uma empresa pelo número de domínio.
        """
        self.browser.get(self.URL_DETALHES.format(num_empresa))
        sleep(2)

        dict_contato = {}
        count = 1
        while self.contato_exists(count) == True:
            nome = self.browser.find_element(By.ID, self.campo_nome.format(count))\
                .get_attribute('value')
            email = self.browser.find_element(By.ID, self.campo_email.format(count))\
                .get_attribute('value')

            if email != '':
                dict_contato[nome] = email
            count = count + 1

        return dict_contato

    def contato_exists(self, id):
        """
        Verifica se existe um contato com determinado ID.
        """
        try:
            self.browser.find_element(By.ID, self.rowContato.format(id))
            return True
        except NoSuchElementException:
            return False

    def close(self):
        """
        Fecha o navegador automatizado.
        """
        self.browser.close()
