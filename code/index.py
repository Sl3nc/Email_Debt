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
from os import path, renames
import sys
from copy import deepcopy
from time import sleep

from sqlite3 import connect

from smtp2go.core import Smtp2goClient

from PySide6.QtWidgets import (
    QMainWindow, QApplication, QRadioButton, QVBoxLayout, QWidget, QCheckBox
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
        self.query_enedereco = (
            f'SELECT endereco FROM {self.TABELA_EMAIL} '
            'WHERE id_emp = '
            f'(SELECT id_emp FROM {self.TABELA_EMPRESA} '
            'WHERE nome = "{0}")'
        )

        self.insert_endereco = (
            f'INSERT INTO {self.TABELA_EMAIL} '
            '(nome, id_emp)'
            ' VALUES '
            '(?,?)'
        )

        self.connection = connect(self.ARQUIVO_DB)
        self.cursor = self.connection.cursor()
        pass

    def emails_empresa(self, nome_empresa: str) -> list[str]:
        self.cursor.execute(
            self.query_enedereco.format(nome_empresa)
        )
        return self.cursor.fetchall()

class Email:
    def __init__(self):
        self.client = Smtp2goClient(api_key='api-57285302C4594921BD70EB19882D320B')
        self.base_titulo = ' - HONORÁRIOS CONTÁBEIS EM ABERTO'

    def criar(self, destinatario, nome_empresa, conteudo):
        print(f'Destinatario: {destinatario}')
        self.payload = {
            'sender': 'financeiro@deltaprice.com.br',
            'recipients': ['deltapricepedro@gmail.com'],
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

    def add_linha(self, row: pd.Series):
        valor_pag = float(row['Valor'].replace(',', '', 1).replace(',', '.', 1))

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

class Arquivo(QObject):
    fim = Signal()
    nomes = Signal(list)
    conteudos = Signal(dict)

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
        arquivo = tb.read_pdf(
            self.caminho, pages='all',relative_area=True, area=[20,16,90,40]
        )
        tabelas = pd.concat(arquivo, ignore_index=True)
        tabelas.fillna('', inplace=True)
        tabelas = tabelas[tabelas[self.col_titulo] != '']
        tabelas = tabelas.loc[tabelas.apply(lambda row: row[self.col_titulo][1] != '/', axis=1)]
        self.nomes.emit(tabelas[self.col_titulo].values.tolist())
        self.fim.emit()

    def ler(self):
        arquivo = tb.read_pdf(self.caminho, pages="all", relative_area=True, area=[20,16,90,100])
        for tabelas in arquivo:
            tabelas.columns = ["Titulo/Competencia", "", "","", "","","","","","","","","Valor"]
        tabelas = pd.concat(arquivo, ignore_index=True)
        tabelas = tabelas.drop('', axis=1)
        tabelas = tabelas.drop(0).reset_index(drop=True)

        tabelas.fillna('', inplace=True)
        self.conteudos.emit(self.filtro_conteudo(tabelas))
        self.fim.emit()

    def filtro_conteudo(self, tabelas):
        dict_conteudos = {}
        for index, row in tabelas.iterrows():
            if row.Valor != '' and row["Titulo/Competencia"] != '':
                vencimento = row["Titulo/Competencia"].replace('1/1 ','')
                
                competencia = datetime.strptime(vencimento[3:],'%m/%Y')
                competencia = competencia.replace(month= competencia.month - 1).strftime('%m/%Y')
                
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

class Cobrador(QObject):
    novo_endereco = Signal(str)
    inicio = Signal()
    progress = Signal(int)
    fim = Signal(bool)
    resume = Signal(list[str])

    def __init__(self, dict_content: dict[str,str]):
        super().__init__()
        self.dict_content = dict_content
        self.db = DataBase()
        self.enderecos_novos = ''

    #TODO EXECUTAR
    def executar(self):
        email = Email()
        count = 0
        for nome_empresa, conteudo in self.dict_content.items():
            enderecos_email = self.db.emails_empresa(nome_empresa)
            if enderecos_email == None:
                enderecos_email = self.registro(nome_empresa, enderecos_email)
            
            for endereco in enderecos_email:
                email.criar(endereco, nome_empresa, conteudo)
                email.enviar()
            
            count = count + 1
            self.progress.emit(count)
        self.fim.emit(False)
        self.resume.emit(self.dict_content.keys())

    def registro(self, nome_empresa):
        self.novo_endereco.emit(nome_empresa)
        while self.enderecos_novos == '':
            sleep(2)

        id_empresa = self.db.registrar_empresa(nome_empresa)
        enderecos_email = self.enderecos_novos.split(';')
        self.enderecos_novos = ''

        for endereco in enderecos_email:
            self.db.registrar_endereco(endereco, id_empresa)
        return enderecos_email
    
    def set_novo_endereco(self, valor: str):
        self.enderecos_novos == valor

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        self.MAX_PROGRESS = 100
        self.coeficiente_progress = 0
        self.arquivo = Arquivo()
        self.options = []


        self.setWindowIcon(QIcon(resource_path('src\\imgs\\mail-icon.ico')))

        self.movie = QMovie(resource_path("src\\imgs\\load.gif"))
        self.label_load_gif.setMovie(self.movie)
        self.label_loading_empresas.setMovie(self.movie)

        icon = QIcon()
        icon.addFile(resource_path("src\\imgs\\upload-icon.png"), QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_body_relatorio_anexar.setIcon(icon)

        #Logo
        self.label_header_logo.setPixmap(QPixmap
        (resource_path('src\\imgs\\mail-hori.png')))

        self.pushButton_endereco.clicked.connect(
            self.enviar_valor
        )

        self.pushButton_body_relatorio_anexar.clicked.connect(
            self.inserir_relatorio
        )

        self.pushButton_body_executar.clicked.connect(
            self.executar
        )

        self._thread = QThread()
        self.arquivo.moveToThread(self._thread)
        self.arquivo.fim.connect(self._thread.quit)

    #TODO THREADS
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
            traceback.print_exc()
            messagebox.showwarning(title='Aviso', message= e)

    def pesquisar_empresas(self):
        if self.label_empresas_aviso.isVisible() == True:
            self.label_empresas_aviso.hide()
        else:
            self._thread.disconnect(self.inicio)
            self.arquivo.disconnect(self.conexao_nome)

            for widget in self.options:
                self.gridLayout_empresas.removeWidget(widget)
                widget.hide()
                widget.destroy()

        self.pushButton_body_executar.setEnabled(False)
        self.stackedWidget_empresas.setCurrentIndex(1)
        self.movie.start()
        
        self.inicio = self._thread.started.connect(self.arquivo.nomes_empresas)
        # self.arquivo.fim.connect(self._thread.deleteLater)
        self.conexao_nome = self.arquivo.nomes.connect(self.exibir_opcoes)

        self._thread.start()

    def exibir_opcoes(self, nomes):
        self.options.clear()
        for nome in nomes:
            cb = QCheckBox(nome)
            cb.setChecked(True)
            self.options.append(cb)
            self.gridLayout_empresas.addWidget(cb)

        self.pushButton_body_executar.setEnabled(True)
        self.stackedWidget_empresas.setCurrentIndex(0)
        self.movie.stop()

    def executar(self):
        if self.pushButton_body_relatorio_anexar.text() == '':
            raise Exception ('Insira algum relatório de vencidos')
        self.exec_load(True)

        self.conexao_ler = self._thread.started.connect(self.arquivo.ler)
        # self.arquivo.fim.connect(self._thread.deleteLater)
        self.conexao_cobrar = self.arquivo.conteudos.connect(self.cobrar)

        self._thread.start()

    def cobrar(self, dict_content):
        try:
            self._thread.disconnect(self.conexao_ler)
            self.arquivo.disconnect(self.conexao_cobrar)

            content_filtred = self.filtro(dict_content)
            self.coeficiente_progress = self.MAX_PROGRESS / len(content_filtred)
            self._cobrador = Cobrador(content_filtred)
            self._thread_cobrador = QThread()

            self._cobrador.moveToThread(self._thread_cobrador)
            self._thread_cobrador.started.connect(self._cobrador.executar)
            self._cobrador.novo_endereco.connect(self.acess_cadastro)
            self._cobrador.fim.connect(self._thread_cobrador.quit)
            self._cobrador.fim.connect(self._thread_cobrador.deleteLater)
            self._cobrador.fim.connect(self.exec_load)
            self._cobrador.resume.connect(self.conclusion)
            self._thread_cobrador.finished.connect(self._cobrador.deleteLater)
            self._thread_cobrador.start()
        except Exception as e:
            traceback.print_exc()
            messagebox.showwarning(title='Aviso', message= e)

    def filtro(self, dict_content : dict[str,str]):
        filtred_content = deepcopy(dict_content)
        for i in self.options:
            if i.isChecked() == False:
                del filtred_content[i.text()]
        return filtred_content

    def enviar_valor(self):
        try:
            resp = self.lineEdit_endereco.text()
            #Validar envio
            if resp == '':
                raise Exception('Endereço de email inválido')

            #Confirmar envio
            self._cobrador.set_novo_endereco(resp)
        except Exception as e:
            messagebox.showwarning(title='Aviso', message= e)

    def to_progress(self, valor):
        self.progressBar.setValue(self.coeficiente_progress * valor)

    def conclusion(self, nomes_empresas: list[str]):
        messagebox.showinfo(title='Aviso', message= f'Email enviado com sucesso para: {'\n- '.join(nomes_empresas)}')

    def acess_cadastro(self, nome_empresa):
        self.label_endereco_empresa.setText(nome_empresa)
        self.exec_load(False, 3)

    def exec_load(self, action: bool, to = 0):
        if action == True:
            self.movie.start()
            self.stackedWidget_body.setCurrentIndex(1)
        else:
            self.movie.stop()
            self.stackedWidget_body.setCurrentIndex(to)

if __name__ == '__main__':
    app = QApplication()
    window = MainWindow()
    window.show()
    app.exec()