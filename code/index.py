from PySide6.QtWidgets import (
    QMainWindow, QApplication, QCheckBox, QTreeWidgetItem, QPushButton, QHBoxLayout, QFrame, QSizePolicy
)
from selenium.common.exceptions import NoSuchElementException, SessionNotCreatedException
from PySide6.QtCore import QThread, QObject, Signal, QSize
from selenium.webdriver.chrome.service import Service
from os import renames, getenv, startfile, remove
from dateutil.relativedelta import relativedelta
from PySide6.QtGui import QPixmap, QIcon, QMovie
from tkinter.filedialog import askopenfilename
from src.window_cobranca import Ui_MainWindow
from selenium.webdriver.common.by import By
from smtp2go.core import Smtp2goClient
from pymysql import err, connect
from unidecode import unidecode
from traceback import print_exc
from shutil import rmtree, move
from tkinter import messagebox
from dotenv import load_dotenv
from selenium import webdriver
from datetime import datetime
from zipfile import ZipFile
from copy import deepcopy
from pathlib import Path
from requests import get
from json import loads
from time import sleep
import pandas as pd
import tabula as tb

load_dotenv(Path(__file__).parent / 'src' / 'env' / '.env')

class DataBase:
    TABELA_EMPRESA = 'Empresa'
    TABELA_USUARIO = 'Usuario'
    TABELA_EMAIL = 'Email'

    def __init__(self) -> None:
        self.connection = connect(
                host= getenv('IP_HOST'),
                port= int(getenv('PORT_HOST')),
                user= getenv('USER'),
                password= getenv('PASSWORD'),
                database= getenv('DB'),
            )

        self.query_endereco = (
            f'SELECT endereco FROM {self.TABELA_EMAIL} '
            'WHERE id_emp IN '
            f'(SELECT id_emp FROM {self.TABELA_EMPRESA} '
            'WHERE nome = %s)'
        )

        self.update_endereco = (
            f'UPDATE {self.TABELA_EMAIL} SET '
            'endereco = %s '
            'WHERE endereco = %s AND  id_emp = %s'
        )

        self.insert_endereco = (
            f'INSERT INTO {self.TABELA_EMAIL} '
            '(endereco, id_emp)'
            ' VALUES (%s, %s) '
        )

        self.delete_endereco = (
            f'DELETE FROM {self.TABELA_EMAIL} '
            'WHERE id_emp = %s AND endereco = %s'
        )

        self.delete_enderecos = (
            f'DELETE FROM {self.TABELA_EMAIL} '
            'WHERE id_emp = %s'
        )

        self.query_empresa = (
            f'SELECT id_emp FROM {self.TABELA_EMPRESA} '
            'WHERE nome = %s'
        )

        self.query_empresas = (
            f'SELECT nome FROM {self.TABELA_EMPRESA} '
        )

        self.insert_empresa = (
            f'INSERT INTO {self.TABELA_EMPRESA} '
            '(nome) VALUES (%s) '
        )

        self.delete_empresa = (
            f'DELETE FROM {self.TABELA_EMPRESA} '
            'WHERE id_emp = %s'
        )
        
        self.query_ass = (
            f'SELECT assinatura FROM {self.TABELA_USUARIO} '
            'WHERE nome = %s'
        )

        self.query_acessorias = (
            'SELECT email_acessorias, senha_acessorias'
            f' FROM {self.TABELA_USUARIO} '
            'WHERE nome = %s'
        )
        pass

    def emails_empresa(self, nome_empresa: str) -> list[str]:
        with self.connection.cursor() as cursor:
            cursor.execute(
                self.query_endereco, (nome_empresa,)
            )
            return [i for sub in cursor.fetchall() for i in sub]
    
    def remover_empresa(self, id_empresa: str):
        with self.connection.cursor() as cursor:
            cursor.execute(
                self.delete_empresa, (id_empresa, )
            )
            self.connection.commit()

    def remover_endereco(self, id_empresa: str, endereco: str):
        with self.connection.cursor() as cursor:
            cursor.execute(
                self.delete_endereco, (id_empresa, endereco)
            )
            self.connection.commit()

    def remover_enderecos(self, id_empresa: str):
        with self.connection.cursor() as cursor:
            cursor.execute(
                self.delete_enderecos, (id_empresa,)
            )
            self.connection.commit()
    
    def atualizar_endereco(self, end_novo: str, end_antigo: str, id_emp: str):
        with self.connection.cursor() as cursor:
            cursor.execute(
                self.update_endereco, (end_novo, end_antigo, id_emp)
            )
            self.connection.commit()

    def registrar_empresa(self, nome_empresa: str) -> None:
        with self.connection.cursor() as cursor:
            cursor.execute(
                self.insert_empresa, (nome_empresa,)
            )
            self.connection.commit()
    
    def empresas(self) -> list[str]:
        with self.connection.cursor() as cursor:
            cursor.execute(
                self.query_empresas
            )
            return [i for sub in cursor.fetchall() for i in sub]

    def registrar_enderecos(self, enderecos: list[str], id_empresa: str) -> None:
        with self.connection.cursor() as cursor:
            cursor.executemany(
                self.insert_endereco, 
                ([endereco, id_empresa] for endereco in enderecos)
            )
            self.connection.commit()

    def identificador_empresa(self, nome_empresa: str) -> str:
        with self.connection.cursor() as cursor:
            cursor.execute(
                self.query_empresa, (nome_empresa,)
            )
            return cursor.fetchone()[0]

    def user_acessorias(self, nome_func: str):
        with self.connection.cursor() as cursor:
            cursor.execute(
                self.query_acessorias, (nome_func,)
            )
            return cursor.fetchone()
    
class Email:
    def __init__(self):
        self.client = Smtp2goClient(api_key= getenv('API_SMTP'))
        self.base_titulo = ' - HONORÁRIOS CONTÁBEIS EM ABERTO'
        self.sender = getenv('SENDER_EMAIL')

    def criar(self, destinatarios: list[str], nome_empresa: str, conteudo: str):
        destinatarios.append(self.sender)
        self.payload = {
            'sender': self.sender,
            'recipients': destinatarios,
            'subject': nome_empresa  + self.base_titulo,
            'html': conteudo,
        }

    def enviar(self):
        response = self.client.send(**self.payload)
        if response.success == False:
            raise Exception('Endereço de email inválido')

#https://i.imgur.com/dTUNLTy.jpeg
class Conteudo:
    def __init__(self):
        self.VALOR_JUROS = 0.02
        self.text = ''
        self.valores_totais = []
        self.CONTENT_BASE = Path(__file__).parent / 'src' / 'html' / 'content_email.html'
        with open (self.CONTENT_BASE, 'r', encoding='utf-8') as file:
            self.body = file.read()

    def add_linha(self, row: pd.Series):
        valor_pag = float(row['Valor'].replace('.','').replace(',', '.'))

        dia_atual = datetime.now()
        dia_vencimento = datetime.strptime(row['Vencimento'], '%d/%m/%Y')
        dias_atraso = (dia_atual - dia_vencimento).days

        multa = round(valor_pag * self.VALOR_JUROS , 2)

        juros = round(((valor_pag * self.VALOR_JUROS) / 30) * dias_atraso , 2)
        
        total = round(valor_pag + multa + juros , 2)

        self.valores_totais.append(total)

        self.text = self.text + """
            <tr>
                <th style="border: 1px solid black; padding: 8px 10px;">{0}</th>
                <td style="border: 1px solid black; padding: 8px 10px;">{1}</td>
                <td style="text-align: center; border: 1px solid black; padding: 8px 10px;">{2}</td>
                <td style="color: red; border: 1px solid black; padding: 8px 10px;">R$ {3}</td>
                <td style="border: 1px solid black; padding: 8px 10px;">R$ {4}</td>
                <td style="border: 1px solid black; padding: 8px 10px;">R$ {5}</td>
                <td style="border: 1px solid black; padding: 8px 10px;"><span style="color: red;">R$ {6}</span></td>\
            </tr>\n
            """.format(
                    str(row['Competência']), 
                    str(row['Vencimento']), 
                    dias_atraso, str(row['Valor']), 
                    f'{multa:_.2f}'.replace('.',',').replace('_','.'), 
                    f'{juros:_.2f}'.replace('.',',').replace('_','.'), 
                    f'{total:_.2f}'.replace('.',',').replace('_','.')
                )

    def valor_geral(self):
        valor = f'{sum(self.valores_totais):_.2f}'\
            .replace('.',',').replace('_','.')
        return f'<td><b><span style="color: red;">\
            R$ {valor} </span></b></td>'
    
    def cumprimento(self):
        hora_atual = datetime.now().hour
        if hora_atual < 12:
            return 'bom dia!'
        elif hora_atual >= 12 and hora_atual < 18:
            return 'boa tarde!'
        return 'boa noite!'

    def to_string(self):
        return self.body.replace('$text', self.text)\
            .replace('$cumprimento', self.cumprimento())\
                .replace('$valor_geral', self.valor_geral())

class Arquivo(QObject):
    fim = Signal(int)
    nomes = Signal(list)
    conteudos = Signal(dict)
    error = Signal(bool)
    preview = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.caminho = ''
        self.col_titulo = "rcela Vencimento"

    def set_caminho(self, caminho):
        if caminho == '':
            return None
        self.validar_tipo(caminho)
        caminho = self.validar_uni(caminho)
        self.caminho = caminho
        return caminho[caminho.rfind('/') +1:]

    def validar_uni(self, caminho):
        caminho_uni = unidecode(caminho)
        if caminho != caminho_uni:
            renames(caminho, caminho_uni)
            caminho = caminho_uni
            messagebox.showinfo(title='Aviso', message='O caminho do arquivo precisou ser mudado, para encontrá-lo novamente siga o caminho a seguir: \n' + caminho)
        return caminho

    def validar_tipo(self, caminho: str):
        tipo = caminho[len(caminho) - 3 :]
        if tipo.lower() != 'pdf':
            raise Exception('Formato de arquivo inválido') 

    def nomes_empresas(self):
        try:
            arquivo = tb.read_pdf(
                self.caminho, pages='all',relative_area=True, area=[20,16,90,40], encoding="ISO-8859-1"
            )
            tabelas = pd.concat(arquivo, ignore_index=True)
            tabelas.fillna('', inplace=True)
            tabelas = tabelas[tabelas[self.col_titulo] != '']
            tabelas = tabelas.loc[tabelas.apply(lambda row: row[self.col_titulo][1] != '/', axis=1)]
            self.nomes.emit(tabelas[self.col_titulo].values.tolist())
            self.fim.emit(1)
        except Exception as error:
            self.error.emit(False)
            messagebox.showerror(title='Aviso', message= f"Erro em ler as empresas do arquivo, favor comunique o desenvolvedor \n\n- erro do tipo: {error}")

    def ler(self):
        try:
            arquivo = tb.read_pdf(self.caminho, pages="all", relative_area=True, area=[20,10,96,100], encoding="ISO-8859-1")
            for tabelas in arquivo:
                tabelas.columns = ["Num. Dominio", "Titulo/Competencia", "", "","", "","","","","","","","","Valor"]
            tabelas = pd.concat(arquivo, ignore_index=True)
            tabelas = tabelas.drop('', axis=1)
            tabelas = tabelas.drop(0).reset_index(drop=True)

            for i , r in tabelas.iterrows():
                if pd.isnull(r).all():
                    tabelas.drop(i,inplace = True)
            tabelas.fillna('', inplace=True)
            self.conteudos.emit(self.filtro_conteudo(tabelas))
            self.fim.emit(2)
        except Exception as error:
            self.error.emit(False)
            messagebox.showerror(title='Aviso', message= f"Erro em ler as empresas do arquivo, favor comunique o desenvolvedor \n\n- erro do tipo: {error}")

    def filtro_conteudo(self, tabelas: pd.Series):
        dict_conteudos = {}
        for index, row in tabelas.iterrows():
            if row.Valor != '' and row["Titulo/Competencia"] != '':
                vencimento = row["Titulo/Competencia"].replace('1/1 ','')
                
                competencia = datetime.strptime(vencimento[3:],'%m/%Y')
                competencia = (competencia - relativedelta(months=1)).strftime('%m/%Y')
                
                conteudo_atual.add_linha(pd.Series(data= {
                    'Competência': competencia,
                    'Vencimento': vencimento,
                    'Valor': row.Valor
                }))
            elif row.Valor == '':
                #Abrir conteudo
                num_domin = row["Num. Dominio"].replace(' Nome:','')
                nome_atual = row["Titulo/Competencia"]
                conteudo_atual = Conteudo()
                dict_valores = {}
            else:
                #Fecha conteudo
                dict_valores['mensagem'] = conteudo_atual.to_string()
                dict_valores['numero'] = num_domin
                dict_conteudos[nome_atual] = dict_valores

        return dict_conteudos
    
class DriverMaintenance:
    URL = 'https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json'
    query_parameters = {"downloadformat": "zip"}
    zip_path = Path(__file__).parent / 'src' / 'drivers' / "chomedriver.zip"
    zip_extract_path = Path(__file__).parent / 'src' / 'drivers'
    exe_dir_path = Path(__file__).parent / 'src' / 'drivers' / 'chromedriver-win64' / 'chromedriver.exe'
    exe_path = Path(__file__).parent / 'src' / 'drivers' / 'chromedriver.exe'

    def __init__(self):
        pass

    def upgrade(self):
        try:
            self._zip()
            self._extract_move()
            print("Arquivo movido com sucesso!")
        except FileNotFoundError:
            print("O arquivo de origem não foi encontrado.")
        except Exception as e:
            print(f"Ocorreu um erro: {e}")

    def _zip(self):
        object_json = self._download_json()
        response = self._driver_response(object_json)
        print(response.ok)
        with open(self.zip_path, mode="wb") as file:
            file.write(response.content)

    def _download_json(self):
        response = get(self.URL)
        return loads(response.text)

    def _driver_response(self, object_json):
        latest_driver_url = object_json['channels']['Stable']\
                                ['downloads']['chromedriver'][4]['url']
        return get(latest_driver_url, self.query_parameters)

    def _extract_move(self):
        with ZipFile(self.zip_path, 'r') as zObject: 
            zObject.extractall(path= self.zip_extract_path) 

        move(self.exe_dir_path, self.exe_path)

        rmtree(self.exe_dir_path.parent)
        remove(self.zip_path)

class Acessorias:
    ROOT_FOLDER = Path(__file__).parent
    CHROME_DRIVER_PATH = ROOT_FOLDER / 'src' / 'drivers' / 'chromedriver.exe'
    URL_MAIN = 'https://app.acessorias.com/sysmain.php'
    URL_DETALHES = 'https://app.acessorias.com/sysmain.php?m=105&act=e&i={0}&uP=14&o=EmpNome,EmpID|Asc'


    INPUT_EMAIL = 'mailAC'
    INPUT_PASSWORD= 'passAC'
    BTN_ENTRAR = '#site-corpo > section.secao.secao-login > div > form > div.botoes > button'

    def __init__(self) -> None:
        self.rowContato = 'divCtt_0_{0}'
        self.campo_nome = 'CttNome_0_{0}'
        self.campo_email = 'CttEMail_0_{0}'

        self.browser = self.make_chrome_browser(hide=True)
        self.browser.get(self.URL_MAIN)
        pass

    def make_chrome_browser(self,*options: str, hide = True) -> webdriver.Chrome:
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
        self.browser.find_element(By.NAME, self.INPUT_EMAIL).send_keys(usuario)
        self.browser.find_element(By.NAME, self.INPUT_PASSWORD).send_keys(senha)

        self.browser.find_element(By.CSS_SELECTOR, self.BTN_ENTRAR).click()
        sleep(4)

    def pesquisar(self, num_empresa: str):
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
        try:
            self.browser.find_element(By.ID, self.rowContato.format(id))
            return True
        except NoSuchElementException:
            return False

    def close(self):
        self.browser.close()

class Cobrador(QObject):
    novo_endereco = Signal(str)
    progress = Signal(int)
    fim = Signal()
    resume = Signal(dict)
    confirm_enderecos = Signal(dict)
    empty_enderecos = Signal(list)
    error = Signal(bool)
    progress_bar = Signal(int)

    def __init__(self, dict_content: dict[str,dict], db: DataBase):
        super().__init__()
        self.dict_content = dict_content
        self.db = db
        self.enderecos_novos = {}

    #TODO EXECUTAR
    def executar(self):
        try:
            dict_faltantes = self.filtro_faltantes()
            if dict_faltantes != {}:
                self.exec_registro(dict_faltantes)
            self.progress.emit(0)
            self.enviar()
        except Exception as error:
            self.progress.emit(0)
            messagebox.showerror(title='Aviso', message= f"Erro na etapa em questão, favor comunique o desenvolvedor \n\n- erro do tipo: {error}")

    def filtro_faltantes(self):
        dict_faltantes = {}
        self.progress.emit(-3)
        for nome_empresa, conteudo in self.dict_content.items():
            enderecos_email = self.db.emails_empresa(nome_empresa)
            if enderecos_email == []: #Sem email cadastrado da empresa
                dict_faltantes[nome_empresa] = conteudo['numero']
                continue

        return dict_faltantes

    def exec_registro(self, dict_faltantes):
        list_restantes = []
        self.progress.emit(-2)
        dict_contato, list_empty = self.registro_acessorias(dict_faltantes)
        if dict_contato != {}:
            self.confirm_enderecos.emit(dict_contato)
            self.enderecos_novos = {}
            list_restantes = list_restantes + self.registro()

        if list_empty != []:
            self.empty_enderecos.emit(list_empty)
            list_restantes = list_restantes + list_empty

        self.progress.emit(-1)
        if list_restantes != []:
            self.registro_manual(list_restantes)

    #TODO REGISTRO
    def registro_acessorias(self, dict_faltante: dict[str,str]):
        dict_contato = {}
        acessorias = Acessorias()
        usuario = getenv('USER_ACESSORIAS')
        senha = getenv('PASSWORD_ACESSORIAS') 
        acessorias.login(usuario, senha)
        for nome_empresa, num_dominio in dict_faltante.items():
            dict_contato[nome_empresa] = acessorias.pesquisar(num_dominio)
        acessorias.close()
        dict_contato, list_empty = self.filter_empty(dict_contato)
        return dict_contato, list_empty
     
    def filter_empty(self, dict_contato):
        list_empty = []
        filtered_dict = deepcopy(dict_contato)
        for key, value in dict_contato.items():
            if value == {}:
                list_empty.append(key)
                del filtered_dict[key]
        return filtered_dict, list_empty

    def registro_manual(self, list_restantes: list[str]):
        for nome_empresa in list_restantes:
            self.novo_endereco.emit(nome_empresa)
            self.enderecos_novos = {}
            self.registro()

    def registro(self):
        list_restantes = []
        while self.enderecos_novos == {}:
                sleep(2)
        for nome_empresa, enderecos in self.enderecos_novos.items():
            if enderecos == '':
                list_restantes.append(nome_empresa)
                continue
            self.db.registrar_empresa(nome_empresa)
            id_empresa = self.db.identificador_empresa(nome_empresa)
            enderecos_email = enderecos.split(';')
            self.db.registrar_enderecos(enderecos_email, id_empresa)
        return list_restantes
    
    def set_novo_endereco(self, valor: dict[str,str]):
        self.enderecos_novos = valor

    def enviar(self):
        email = Email()
        dict_contatos = {}
        count_content = len(self.dict_content)
        count = 1

        for nome_empresa, conteudo in self.dict_content.items():
            enderecos_email = self.db.emails_empresa(nome_empresa)
            dict_contatos[nome_empresa] = enderecos_email
            
            email.criar(enderecos_email, nome_empresa, conteudo['mensagem'])
            email.enviar()
            count = count + 1
            self.progress_bar.emit((count / count_content) * 100)

        self.fim.emit()
        self.resume.emit(dict_contatos)

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.try_conection()
        self.setupUi(self)

        self.arquivo = Arquivo()
        self.options = []
        self.preview_btn = []
        self.option_checada = False
        self.widget_enderecos = {}
        self.empresa_preview = ''
        self.PATH_MESSAGE = 'base_message.html'

        self.setWindowIcon(
            QIcon(
                (Path(__file__).parent / 'src' / 'imgs' / 'mail-icon.ico').__str__())
        )

        self.movie = QMovie(
            (Path(__file__).parent / 'src' / 'imgs' / 'load.gif').__str__()
        )
        self.label_load_gif.setMovie(self.movie)
        self.label_loading_empresas.setMovie(self.movie)

        icon = QIcon()
        icon.addFile(
            (Path(__file__).parent / 'src' / 'imgs' / 'upload-icon.png').__str__(),
            QSize(),
            QIcon.Mode.Normal,
            QIcon.State.Off
        )
        self.pushButton_body_relatorio_anexar.setIcon(icon)

        #Logo
        self.label_header_logo.setPixmap(
            QPixmap(Path(__file__).parent / 'src' / 'imgs' / 'mail-hori.png'))

        self.pushButton_body_relatorio_anexar.clicked.connect(
            self.inserir_relatorio
        )

        self.pushButton_body_executar.clicked.connect(
            self.executar
        )

        self.pushButton_empresas_marcar.clicked.connect(
            self.marcar_options
        )

        self.pushButton_cadastros_back.clicked.connect(
            lambda: self.stackedWidget_body.setCurrentIndex(0)
        )

        self.pushButton_cadastros_visualizar.clicked.connect(
            self.acess_infos
        )

        self.pushButton_cadastro_adcionar.clicked.connect(
            self.adcionar_info
        )

        self.pushButton_cadastro_editar.clicked.connect(
            self.editar_info
        )

        self.pushButton_cadastro_remover.clicked.connect(
            self.remover_info
        )

        self.pushButton.clicked.connect(
            self.enviar_contatos
        )

        self.pushButton_empresas_marcar.hide()

        self._thread = QThread()
        self.arquivo.moveToThread(self._thread)
        self.arquivo.fim.connect(self._thread.quit)

        # self.confirmar_registro(
        #     {
        #         'Empresa':
        #         {
        #             'Contato': 'Endereço e-mail',
        #             'Outro Contato': 'Outro Endereco'
        #         },
        #         'Outra Empresa':
        #         {
        #             'Contato2': 'Endereco e-mail2'
        #         }
        #     }
        # )

    def try_conection(self):
        try:
            self.db = DataBase()
        except err.OperationalError as e:
            messagebox.showerror('Aviso!', f'Falha na conexão com o banco de dados. Favor verificar se o aplicativo "DOCKER" está inicializado no servidor, caso constrário, entre em contato com o suporte disponível\n\n{e}')
            raise Exception('')

    def inserir_relatorio(self):
        try:
            caminho_reduzido = self.arquivo.set_caminho(askopenfilename())
            if caminho_reduzido == None:
                return None
            self.pushButton_body_relatorio_anexar.setText(caminho_reduzido)
            self.pushButton_body_relatorio_anexar.setIcon(QIcon())
            self.pesquisar_empresas()
        # except FileNotFoundError:
        #     messagebox.showwarning(title='Aviso', message= 'Operação cancelada')
        except Exception as e:
            print_exc()
            messagebox.showwarning(title='Aviso', message= e)

    def pesquisar_empresas(self):
        if self.label_empresas_aviso.isVisible() == True:
            self.label_empresas_aviso.hide()
        else:
            for widget in self.options:
                self.gridLayout_empresas.removeWidget(widget)
                widget.hide()
                widget.destroy()

        self.pushButton_empresas_marcar.hide()
        self.pushButton_body_executar.setEnabled(False)
        self.exec_load_empresas(True)
        
        self.inicio = self._thread.started.connect(self.arquivo.nomes_empresas)
        self.arquivo.fim.connect(self.reset_thread)
        self.arquivo.error.connect(self.exec_load_empresas)
        self.conexao_nome = self.arquivo.nomes.connect(self.exibir_opcoes)

        self._thread.start()

    def exec_load_empresas(self, action: bool):
        if action == True:
            self.movie.start()
            self.stackedWidget_empresas.setCurrentIndex(1)
        else:
            self.movie.stop()
            self.stackedWidget_empresas.setCurrentIndex(0)
        
    #TODO OPCOES
    def exibir_opcoes(self, nomes: list):
        self.options.clear()
        for nome in nomes:
            layout = QHBoxLayout()
            frame = QFrame()
            sp = frame.sizePolicy()
            sp.setVerticalPolicy(QSizePolicy.Maximum)
            frame.setSizePolicy(sp)
            
            cb = QCheckBox(nome, frame)
            cb.setChecked(True)
            self.options.append(cb)
            layout.addWidget(cb)

            btn = QPushButton(frame)
            btn.setText('prévia')
            btn.setProperty('empresa', nome)
            btn.clicked.connect(self.carregar_mensagem)
            self.preview_btn.append(btn)
            layout.addWidget(btn)

            frame.setLayout(layout)
            self.gridLayout_empresas.addWidget(frame)

        self.pushButton_empresas_marcar.show()
        self.pushButton_body_executar.setEnabled(True)
        self.exec_load_empresas(False)

    def carregar_mensagem(self):
        for i in self.preview_btn:
            if i.hasFocus():
                empresa = i.property('empresa')
                break
        if self.empresa_preview != '':
            remove(self.PATH_MESSAGE)
        self.empresa_preview = empresa
        self.pushButton_empresas_marcar.hide()
        self.pushButton_body_executar.setEnabled(False)
        self.exec_load_empresas(True)
        
        self.conexao_ler = self._thread.started.connect(self.arquivo.ler)
        self.arquivo.fim.connect(self.reset_thread)
        self.arquivo.error.connect(self.exec_load_empresas)
        self.conexao_cobrar = self.arquivo.conteudos.connect(self.exibir_mensagem)

        self._thread.start()

    def exibir_mensagem(self, dict_conteudos):
        html = dict_conteudos[self.empresa_preview]['mensagem']
        with open (self.PATH_MESSAGE, 'w', encoding='utf-8') as file:
           file.write(''.join(x for x in html))

        startfile(self.PATH_MESSAGE)

        self.pushButton_empresas_marcar.show()
        self.pushButton_body_executar.setEnabled(True)
        self.exec_load_empresas(False)

    def marcar_options(self):
        for i in self.options:
            i.setChecked(self.option_checada)

        if self.option_checada == False:
            self.pushButton_empresas_marcar.setText('Marcar todos')
        else:
            self.pushButton_empresas_marcar.setText('Desmarcar todos')
        self.option_checada = not self.option_checada

    def executar(self):
        if self.pushButton_body_relatorio_anexar.text() == '':
            raise Exception ('Insira algum relatório de vencidos')
        if self.empresa_preview != '':
            remove(self.PATH_MESSAGE)
        
        self.to_progress(-4)
        self.exec_load(True)

        self.conexao_ler = self._thread.started.connect(self.arquivo.ler)
        self.arquivo.fim.connect(self.reset_thread)
        self.arquivo.error.connect(self.exec_load)
        self.conexao_cobrar = self.arquivo.conteudos.connect(self.cobrar)

        self._thread.start()

    def reset_thread(self, option: int):
        if option == 1:
            self._thread.disconnect(self.inicio)
            self.arquivo.disconnect(self.conexao_nome)
        elif option == 2:
            self._thread.disconnect(self.conexao_ler)
            self.arquivo.disconnect(self.conexao_cobrar)
    
    #TODO COBRAR
    def cobrar(self, dict_content: dict[str,dict]):
        try:
            content_filtred = self.filtro(dict_content)

            self._cobrador = Cobrador(
                content_filtred,
                self.db
                )
            self._thread_cobrador = QThread()

            self._cobrador.moveToThread(self._thread_cobrador)
            self._thread_cobrador.started.connect(self._cobrador.executar)
            self._cobrador.novo_endereco.connect(self.acess_cadastro)
            self._cobrador.fim.connect(self._thread_cobrador.quit)
            self._cobrador.fim.connect(self._thread_cobrador.deleteLater)
            self._cobrador.progress.connect(self.to_progress)
            self._cobrador.confirm_enderecos.connect(self.confirmar_registro)
            self._cobrador.empty_enderecos.connect(self.empty_enderecos)
            self._cobrador.resume.connect(self.conclusion)
            self._cobrador.error.connect(self.exec_load)
            self._cobrador.progress_bar.connect(self.to_progress_bar)
            self._thread_cobrador.finished.connect(self._cobrador.deleteLater)
            self._thread_cobrador.start()
        except ZeroDivisionError:
            self.exec_load(False)
            messagebox.showwarning(title='Aviso', message= "Sem empresas selecionadas")
        except Exception as e:
            self.exec_load(False)
            print_exc()
            messagebox.showwarning(title='Aviso', message= e)

    def filtro(self, dict_content : dict[str,dict]):
        filtred_content = deepcopy(dict_content)
        for i in self.options:
            if i.isChecked() == False:
                del filtred_content[i.text()]
        
        return filtred_content
    
    def confirmar_registro(self, dict_contato: dict[str,dict[str,str]]):
        self.stackedWidget_body.setCurrentIndex(4)
        self.widget_enderecos.clear()
        for empresa, contato in dict_contato.items():
            for nome, endereco in contato.items():
                item = QTreeWidgetItem(self.treeWidget_contatos)
                item.setText(0, empresa)
                item.setText(1, nome)
                cb = QCheckBox(endereco)
                cb.setChecked(True)
                self.widget_enderecos[item] = cb
                self.treeWidget_contatos.setItemWidget(item, 2, cb)

    def empty_enderecos(self, list_empty: list[str]):
        messagebox.showwarning(title='Aviso', message=f'O endereço de e-mail das seguintes empresas não foram encontrados no acessórias: \n\n{'\n -'.join(list_empty)}\n\nFavor inseri-los manualmente')

    def enviar_contatos(self):
        contatos_filtrados = {}
        empresa_atual = ''
        for item, cb in self.widget_enderecos.items():
            if item.text(0) != empresa_atual:
                empresa_atual = item.text(0)
                contatos_filtrados[empresa_atual] = ''

            if cb.isChecked() == True:
                contatos_filtrados[empresa_atual] = \
                    contatos_filtrados[empresa_atual] + ';' + cb.text()
                
        for nome_emp in contatos_filtrados.keys():
            contatos_filtrados[nome_emp] =\
                contatos_filtrados[nome_emp].replace(';', '', 1)
            
        print(contatos_filtrados)
        self._cobrador.set_novo_endereco(contatos_filtrados)
        self.to_progress(-1)
        self.exec_load(True)
        self.treeWidget_contatos.clear()

    def to_progress(self, valor):
        if valor == -4:
            self.progressBar.hide()
            self.label_load_title.setText('Gerando mensagem...')
        if valor == -3:
            self.label_load_title.setText('Carregando endereços registrados...')
        elif valor == -2:
            self.label_load_title.setText('Buscando endereços no Acessórias...')
        elif valor == -1:
            self.label_load_title.setText('Registrando endereços...')
        elif valor == 0:
            self.progressBar.show()
            self.label_load_title.setText('Enviando e-mails...')

    def to_progress_bar(self, value):
        self.progressBar.setValue(value)

    def conclusion(self, dict_contatos: dict[str, list[str]]):
        self.exec_load(False, 0)
        text = ''
        for nome_empresa, enderecos in dict_contatos.items():
            text = f'{text}\n-{nome_empresa}\n'
            for endereco in enderecos:
                text = f'{text}|=>{endereco}\n'

        messagebox.showinfo(title='Aviso', message= f'Email enviado com sucesso para: \n{text}')

    def acess_cadastro(self, nome_empresa: str):
        self.lineEdit_endereco.setText('')
        self.label_endereco_title.setText('Empresa abaixo não cadastrada:')
        self.label_endereco_empresa.setText(nome_empresa)
        self.conexao_envio = self.pushButton_endereco.clicked.connect(
            lambda: self.enviar_valor(nome_empresa)
        )
        self.exec_load(False, 2)

    def enviar_valor(self, nome_empresa: str):
        try:
            resp = self.lineEdit_endereco.text()

            if resp == '' or '@' not in resp or '.com' not in resp:
                raise Exception('Endereço de email inválido')

            self._cobrador.set_novo_endereco({nome_empresa: resp})
            self.pushButton_endereco.disconnect(self.conexao_envio)
            self.exec_load(True)
        except Exception as e:
            messagebox.showwarning(title='Aviso', message= e)

    def exec_load(self, action: bool, to = 0):
        if action == True:
            self.movie.start()
            self.stackedWidget_body.setCurrentIndex(1)
        else:
            self.movie.stop()
            self.stackedWidget_body.setCurrentIndex(to)

    def acess_infos(self):
        dict_informacoes = {}
        self.stackedWidget_body.setCurrentIndex(3)
        self.treeWidget_cadastros_infos.clear()

        for i in self.db.empresas():
            dict_informacoes[i] = self.db.emails_empresa(i)

        dict_informacoes_sorted = dict(sorted(dict_informacoes.items()))
        for empresa, enderecos in dict_informacoes_sorted.items():
            root = QTreeWidgetItem(self.treeWidget_cadastros_infos)
            root.setText(0, empresa)
            # root.setFont(0, QFont())
            self.treeWidget_cadastros_infos.addTopLevelItem(root)

            for endereco in enderecos:
                child = QTreeWidgetItem()
                child.setText(0, endereco)
                root.addChild(child)

    def adcionar_info(self):
        try:
            items = self.treeWidget_cadastros_infos.selectedItems()
            if len(items) == 0:
                raise Exception("Escolha um e-mail para adcionar")
            atual = items[0]
            parente = atual.parent()
            if parente != None:
                raise Exception("Selecione a empresa que deseja adcionar o e-mail")
                
            self.label_endereco_title.setText('Adcionar e-mail na empresa abaixo:')
            self.label_endereco_empresa.setText(atual.text(0))
            self.stackedWidget_body.setCurrentIndex(2)
            self.conexao_add = self.pushButton_endereco.clicked.connect(
                self.operacao_adcionar
            )
        except Exception as e:
            messagebox.showwarning('Aviso', e)

    def operacao_adcionar(self):
        atual = self.treeWidget_cadastros_infos.selectedItems()[0]
        enderecos = self.lineEdit_endereco.text().split(';')

        id_emp = self.db.identificador_empresa(atual.text(0))
        self.db.registrar_enderecos(enderecos, id_emp)

        for endereco in enderecos:
            child = QTreeWidgetItem()
            child.setText(0, endereco)
            atual.addChild(child)

        self.pushButton_endereco.disconnect(self.conexao_add)
        self.stackedWidget_body.setCurrentIndex(3)

    def editar_info(self):
        try:
            items = self.treeWidget_cadastros_infos.selectedItems()
            if len(items) == 0:
                raise Exception("Escolha um e-mail para editar")
            parente = items[0].parent()
            escolhido = items[0]
            if parente == None:
                raise Exception("Em pró do funcionamento do programa, edite apenas endereços de e-mail. O nome atual das empresas é fundamental para execução")
                
            self.label_endereco_input_subtitle.hide()
            self.actual_text = self.label_endereco_input_title.text()
            self.label_endereco_input_title.setText(f"Favor, insira o endereço que substituirá o atual endereço: {escolhido.text(0)}")
            self.label_endereco_title.setText('Editar e-mail da empresa abaixo:')
            self.label_endereco_empresa.setText(parente.text(0))
            self.stackedWidget_body.setCurrentIndex(2)
            self.conexao_edit = self.pushButton_endereco.clicked.connect(
                self.operacao_editar
            )
        except Exception as e:
            messagebox.showwarning('Aviso', e)

    def operacao_editar(self):
        atual = self.treeWidget_cadastros_infos.selectedItems()[0]
        parente = atual.parent()
        novo_text = self.lineEdit_endereco.text()

        id_emp = self.db.identificador_empresa(parente.text(0))
        self.db.atualizar_endereco(novo_text, atual.text(0), id_emp)

        atual.setText(0, novo_text)
        self.label_endereco_input_subtitle.show()
        self.label_endereco_input_title.setText(self.actual_text)
        self.pushButton_endereco.disconnect(self.conexao_edit)
        self.stackedWidget_body.setCurrentIndex(3)

    def remover_info(self):
        # try:
            items = self.treeWidget_cadastros_infos.selectedItems()
            if len(items) == 0:
                raise Exception("Escolha um e-mail ou empresa para remover")
            escolhido = items[0]
            parente = escolhido.parent()

            if parente == None:
                if messagebox.askyesno('Atenção!', 'A remoção da empresa eliminará todos seus emails, tem certeza que deseja removê-la?') == False:
                    return None

                id_emp = self.db.identificador_empresa(escolhido.text(0))
                self.db.remover_enderecos(id_emp)
                self.db.remover_empresa(id_emp)
            else:
                id_emp = self.db.identificador_empresa(parente.text(0))
                self.db.remover_endereco(id_emp, escolhido.text(0))

            escolhido.setHidden(True)
            self.stackedWidget_body.setCurrentIndex(3)
        # except Exception as e:
        #     messagebox.showwarning('Aviso', e)

if __name__ == '__main__':
    app = QApplication()
    window = MainWindow()
    window.show()
    app.exec()
