from PySide6.QtCore import QObject, Signal
from acessorias import Acessorias
from tkinter import messagebox
from database import DataBase
from copy import deepcopy
from delta_email import Email
from time import sleep
from os import getenv

class Cobrador(QObject):
    """
    Classe responsável por orquestrar o processo de cobrança: filtra empresas sem e-mail, busca contatos, registra e envia e-mails.
    """
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
        """
        Executa o fluxo principal de cobrança.
        """
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
        """
        Filtra empresas que não possuem e-mail cadastrado.
        """
        dict_faltantes = {}
        self.progress.emit(-3)
        for nome_empresa, conteudo in self.dict_content.items():
            enderecos_email = self.db.emails_empresa(nome_empresa)
            if enderecos_email == []: #Sem email cadastrado da empresa
                dict_faltantes[nome_empresa] = conteudo['numero']
                continue

        return dict_faltantes

    def exec_registro(self, dict_faltantes):
        """
        Executa o registro de e-mails faltantes, buscando no Acessorias e solicitando manualmente se necessário.
        """
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
        """
        Busca e-mails no sistema Acessorias.com.
        """
        dict_contato = {}
        acessorias = Acessorias()

        usuario = getenv('USER_ACESSORIAS')
        senha = getenv('PASSWORD_ACESSORIAS') 
        acessorias.login(usuario, senha)

        # esperar o captcha do usuário

        for nome_empresa, num_dominio in dict_faltante.items():
            dict_contato[nome_empresa] = acessorias.pesquisar(num_dominio)
        acessorias.close()
        dict_contato, list_empty = self.filter_empty(dict_contato)
        return dict_contato, list_empty
     
    def filter_empty(self, dict_contato):
        """
        Filtra contatos vazios.
        """
        list_empty = []
        filtered_dict = deepcopy(dict_contato)
        for key, value in dict_contato.items():
            if value == {}:
                list_empty.append(key)
                del filtered_dict[key]
        return filtered_dict, list_empty

    def registro_manual(self, list_restantes: list[str]):
        """
        Solicita manualmente o cadastro de e-mails para empresas sem contato.
        """
        for nome_empresa in list_restantes:
            self.novo_endereco.emit(nome_empresa)
            self.enderecos_novos = {}
            self.registro()

    def registro(self):
        """
        Registra os e-mails coletados no banco de dados.
        """
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
        """
        Define novos endereços de e-mail informados manualmente.
        """
        self.enderecos_novos = valor

    def enviar(self):
        """
        Envia os e-mails de cobrança para as empresas.
        """
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