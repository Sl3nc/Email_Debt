from tkinter import messagebox
from tkinter.filedialog import askopenfilename

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

import tabula as tb
import pandas as pd
from unidecode import unidecode
import traceback
from datetime import datetime
import string
from os import path, rename
import sys

from sqlite3 import connect

from smtp2go.core import Smtp2goClient

from PySide6.QtWidgets import (
    QMainWindow, QApplication, QRadioButton, QVBoxLayout, QWidget
)
from PySide6.QtGui import QPixmap, QIcon, QMovie
from PySide6.QtCore import QThread, QObject, Signal, QSize
from src.window_cobranca import Ui_MainWindow

def resource_path(relative_path):
    base_path = getattr(
        sys,
        '_MEIPASS',
        path.dirname(path.abspath(__file__)))
    return path.join(base_path, relative_path)

class DataBase:
    NOME_DB = 'email_cobranca.sqlite3'
    ARQUIVO_DB = resource_path(f'src\\db\\{NOME_DB}')
    TABELA_EMPRESA = 'Empresa'
    TABELA_USUARIO = 'Usuario'
    TABELA_EMAIL = 'Email'

    def __init__(self) -> None:
        self.query_id_banco = 'SELECT id_banco FROM {0} WHERE nome = "{1}"'

        self.query_id_nome_emp = 'SELECT id_empresa, nome  FROM {0} WHERE id_banco = "{1}"'

        self.query_codEmp_keyBanco =  'SELECT codigo_emp, chave_banco FROM {0} WHERE id_banco = "{1}" AND id_empresa = "{2}"'

        self.connection = connect(self.ARQUIVO_DB)
        self.cursor = self.connection.cursor()
        pass

    def clientes_do_banco(self, nome_empresa: str) -> str:
        self.cursor.execute(
            self.query_id_nome_emp.format(
                self.TABELA_EMPRESA, id_banco
            )
        )
        return { id: nome for id, nome in self.cursor.fetchall() }

class Email:
    def __init__(self):
        self.client = Smtp2goClient(api_key='api-57285302C4594921BD70EB19882D320B')
        self.base_titulo = ' - HONORÁRIOS CONTÁBEIS EM ABERTO'

    def criar(self, destinatario, nome_empresa, conteudo):
        self.payload = {
            'sender': 'financeiro@deltaprice.com.br',
            'recipients': [destinatario],
            'subject': nome_empresa  + self.base_titulo,
            'html': conteudo,
        }

    def enviar(self):
        response = self.client.send(**self.payload)
        if response.success == False:
            raise Exception('Endereço de email inválido')

class Conteudo:
    def __init__(self):
        self.VALOR_JUROS = 0.02
        self.text = ''
        self.valores_totais = []
        self.body = """
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body>
            <p>
                Prezado cliente, $cumprimento <br><br>Não acusamos o recebimento do(s) honorário(s) relacionado(s) abaixo:
            </p>
            <table style="border: 1px solid black;">
                <thead>
                    <tr>
                        <th style="padding: 8px 10px;">COMP.</th>
                        <th style="padding: 8px 10px;">VENC.</th>
                        <th style="padding: 8px 10px;">Dias Atraso</th>
                        <th style="padding: 8px 10px;">Principal</th>
                        <th style="padding: 8px 10px;">Multa</th>
                        <th style="padding: 8px 10px;">Juros</th>
                        <th style="padding: 8px 10px;">Total</th>
                    </tr>
                </thead>
                <tbody>
                    $text
                </tbody>
                <tfoot>
                    <tr>
                        <th colspan="6" style="text-align: right;">Total em aberto: </th>
                        $valor_geral
                    </tr>
                </tfoot>
            </table>
            <p>Pedimos gentilmente que regularize sua situação financeira conosco:</p>
            <h3>
                Chave PIX: <span style="font-weight: 100"> 10.620.061/0001-05 </span><br>
                Favorecido: Deltaprice Serviços Contábeis<br>
                CNPJ: 10.620.061/0001-05<br>
                <span style="background-color: yellow;">Banco Itau 341 Ag 1582 conta  98.000-7</span>
            </h3>
            <p>
                Assim que efetuar o pagamento/transferência, gentileza nos enviar o comprovante para baixa do(s) título(s) em aberto.
            </p>
            <b style="color: rgb(87, 86, 86);">Atenciosamente,</b>
            <br>
            <img src="https://i.imgur.com/dTUNLTy.jpeg" style="width: 50%;">
            <p>
                Esta mensagem, incluindo seus anexos, tem caráter confidencial e seu conteúdo é restrito ao destinatário da mensagem. Caso você tenha recebido esta mensagem por engano, queira, por favor, retorná-la ao destinatário e apagá-la de seus arquivos. Qualquer uso não autorizado, replicação ou disseminação desta mensagem ou parte dela, incluindo seus anexos, é expressamente proibido. 
                <br><br>
                This message is intended only for the use of the addressee(s) named herein. The information contained in this message is confidential and may constitute proprietary or inside information. Unauthorized review, dissemination, distribution, copying or other use of this message, including all attachments, is strictly prohibited and may be unlawful. If you have received this message in error, please notify us immediately by return e-mail and destroy this message and all copies thereof, including all attachments.
            </p>
        </body>
        </html>
        """

    def add_linha(self, row):
        valor_pag = float(row['Em aberto'].replace(',','.'))

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
                dias_atraso, str(row['Em aberto']), 
                f'{multa:,.2f}'.replace('.',','), 
                f'{juros:,.2f}'.replace('.',','), 
                f'{total:,.2f}'.replace('.',',').replace('_','.'))

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

class Arquivo:
    def __init__(self):
        self.caminho = ''

    def inserir(self, label):
        try:
            self.caminho = askopenfilename()

            if self.caminho =='':
                raise FileNotFoundError()

            if any(c not in string.ascii_letters for c in self.caminho):
                caminho_uni = unidecode(self.caminho)
                rename(self.caminho, caminho_uni)
                self.caminho = caminho_uni

            self.tipo = self.definir_tipo()
            ultima_barra = self.caminho.rfind('/')
            label['text'] = self.caminho[ultima_barra+1:]

        except FileNotFoundError:
            messagebox.showwarning(title='Aviso', message= 'Operação cancelada')
        except Exception as e:
            messagebox.showwarning(title='Aviso', message= e)

    def ler(self):
        arquivo = tb.read_pdf(self.caminho, pages="all",)
        for tabelas in arquivo:
            tabelas.columns = ["Titulo/Competencia", "", "","", "","","","","","","","","Valor"]
        tabelas = pd.concat(arquivo, ignore_index=True)
        tabelas = tabelas.drop('', axis=1)
        tabelas = tabelas.drop(0).reset_index(drop=True)

        tabelas.fillna('', inplace=True)
        dict_conteudos = {}
        for index, row in arquivo.iterrows():
            if row.Valor != '' and row["Titulo/Competencia"] != '':
                #Cria series com: Competência, Vencimento e Valor em aberto
                vencimento = row["Titulo/Competencia"].replace('1/1 ','')
                
                competencia = datetime.strptime(vencimento[7:],'%m/%Y')
                competencia = competencia.replace(month= -1).strftime('%m/%Y')
                
                conteudo_atual.add_linha(pd.Series(data= {
                    'Competência': competencia,
                    'Vencimento': vencimento,
                    'Valor': row.Valor
                }))
            elif row.Valor == '':
                #Abrir conteudo
                nome_atual = row["Titulo/Competencia"]
                conteudo_atual = Conteudo()
            else:
                #Fecha conteudo
                dict_conteudos[nome_atual] = conteudo_atual.to_string()
            
        return dict_conteudos
    
    def definir_tipo(self):
        tamanho = len(self.caminho)
        tipo = self.caminho[tamanho-3 :]
        if 'pdf' == tipo or 'lsx' == tipo:
            return tipo    
        self.caminho = ''
        raise Exception('Formato de arquivo inválido') 

class DataBase:
    def __init__(self):
        pass

class Cobrador(QObject):
    def __init__(self, dict_content: dict[str,str]):
        super().__init__()
        self.dict_content = dict_content

    def executar(self):
        db = DataBase()
        email = Email()
        for nome_empresa, conteudo in self.dict_conteudo.items():
            endereco_email = db.query_endereco(nome_empresa)
            if endereco_email == None:
                endereco_email = db.registrar_endereco(nome_empresa)
                
            email.criar(endereco_email, nome_empresa, conteudo)
            email.enviar()

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.arquivo = Arquivo()

    def executar(self):
        if self.endereco_email.get() == '':
                raise Exception ('Insira algum endereço de email')
        self._thread = QThread()

        self.arquivo.moveToThread(self._thread)
        self._thread.started.connect(self.arquivo.ler)
        self.arquivo.fim.connect(self._thread.quit)
        self.arquivo.fim.connect(self._thread.deleteLater)
        self.arquivo.fim.connect(self.cobrar)
        self.arquivo.inicio.connect(self.alter_estado)
        self._thread.finished.connect(self.arquivo.deleteLater)
        self._thread.start()

    #TODO EXECUTAR
    def cobrar(self, dict_content):
        try:
            self._cobrador = Cobrador(dict_content)
            self._thread = QThread()

            self._cobrador.moveToThread(self._thread)
            self._thread.started.connect(self._cobrador.executar)
            self._cobrador.fim.connect(self._thread.quit)
            self._cobrador.fim.connect(self._thread.deleteLater)
            self._cobrador.fim.connect(self.alter_estado)
            self._thread.finished.connect(self._cobrador.deleteLater)
            self._thread.start()
        except Exception as e:
            traceback.print_exc()
            messagebox.showwarning(title='Aviso', message= e)

    def to_progress(self, nome_empresa):
        messagebox.showinfo(title='Aviso', message= f'Email enviado com sucesso para: {nome_empresa}')