from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askopenfilename

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

import tabula as tb
from unidecode import unidecode
from datetime import datetime
import string
import os

window = Tk()

class Email:
    def __init__(self):
        self.server_smtp = 'smtp.gmail.com'
        self.port = 587

        self.address = 'deltapricepedro@gmail.com'
        self.password = 'yogbduxcsmwaocfe'

    def criar(self, destinatario, titulo, conteudo):
        self.msg = MIMEMultipart()

        self.msg['From'] = self.address
        self.msg['To'] = destinatario

        self.msg['Subject'] = titulo
        self.msg.attach(MIMEText(conteudo, 'html'))

    def enviar(self):
        try:
            self.server = smtplib.SMTP(self.server_smtp, self.port)

            self.server.starttls()

            self.server.login(self.address, self.password)
            print(self.msg['To'])
            self.server.sendmail(self.address, self.msg['To'], self.msg.as_string())
        except Exception:
            raise Exception('O endereço de email não é valido!')
        finally:
            self.server.quit()

class Arquivo:
    def __init__(self):
        self.caminho = ''
        self.body = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Document</title>
        </head>
        <body>
            <p>Prezado cliente, $comprimento <br><br>Não acusamos o recebimento do(s) honorário(s) relacionado(s) abaixo:</p>
            <ul>
                $text
            </ul>
            <p>Você conseguiria regularizar a situação de sua empresa conosco?<br><u>Para que não ocorra cobrança de encargos como multa e juros</u>, abaixo encontra-se nossos dados bancários para transferência:
            </p>
            <h3>Chave PIX Deltaprice:</h3> 10620061000105
            <h3>
                Deltaprice Serviços Contábeis<br>
                CNPJ: 10.620.061/0001-05<br>
                <span style="background-color: yellow;">Banco Itau 341 Ag 1582 conta  98.000-7</span><br>
            </h3>
            <p>Gentileza nos enviar o comprovante para que possamos realizar a baixa dos títulos.</p>
            <b style="color: rgb(87, 86, 86);">Atenciosamente,</b>
            <br>
            <img src="https://i.imgur.com/CmnqM3L.png" style="width: 30%;">
            <p>
                Esta mensagem, incluindo seus anexos, tem caráter confidencial e seu conteúdo é restrito ao destinatário da mensagem. Caso você tenha recebido esta mensagem por engano, queira, por favor, retorná-la ao destinatário e apagá-la de seus arquivos. Qualquer uso não autorizado, replicação ou disseminação desta mensagem ou parte dela, incluindo seus anexos, é expressamente proibido. 
                <br><br>
                This message is intended only for the use of the addressee(s) named herein. The information contained in this message is confidential and may constitute proprietary or inside information. Unauthorized review, dissemination, distribution, copying or other use of this message, including all attachments, is strictly prohibited and may be unlawful. If you have received this message in error, please notify us immediately by return e-mail and destroy this message and all copies thereof, including all attachments.
            </p>
        </body>
        </html>
        """

    def inserir(self, label):
        try:
            self.caminho = askopenfilename()

            if any(c not in string.ascii_letters for c in self.caminho):
                caminho_uni = unidecode(self.caminho)
                os.rename(self.caminho, caminho_uni)
                self.caminho = caminho_uni

            self.tipo = self.definir_tipo()
            ultima_barra = self.caminho.rfind('/')
            label['text'] = self.caminho[ultima_barra+1:]
        except Exception:
            messagebox.showwarning(title='Aviso', message= 'Formato do arquivo inválido')

    def gerar_text(self):
        text = ''
        valorGeral = ''
        arquivo = tb.read_pdf(self.caminho, pages="all",)

        arquivo = arquivo[0].drop([0,1])

        for index, row in arquivo.iterrows():
            if 'Total geral:' in str(row['Competência']):
                valorGeral =  '<b>Total em aberto: <span style="color: red;">'+ str(row['Em aberto']) + '</span></b>'
                break
            elif 'Total do cliente:' in str(row['Competência']):
                continue

            row['Vencimento'] = str(row['Vencimento']).replace('1/1 ','')
            text = text + '<li><b>Período:</b> {0} <b>- Vencimento:</b> {1} <b>- Valor:</b><span style="color: red;"> {2} </span></li>\n'\
                .format(str(row['Competência']), str(row['Vencimento']), str(row['Em aberto']))

        text = text + valorGeral
        return self.body.replace('$text', text).replace('$comprimento', self.comprimento())
    
    def titulo_email(self):
        arquivo = tb.read_pdf(self.caminho, pages="all",)
        return arquivo[0].loc[[1],['Vencimento']].values[0][0] + ' - HONORÁRIOS CONTÁBEIS EM ABERTO'
    
    def comprimento(self):
        hora_atual = datetime.now().hour
        if hora_atual < 12:
            return 'bom dia!'
        elif hora_atual >= 12 and hora_atual < 18:
            return 'boa tarde!'
        return 'boa noite!'

    def definir_tipo(self):
        tamanho = len(self.caminho)
        tipo = self.caminho[tamanho-3 :]
        if 'pdf' == tipo or 'lsx' == tipo:
            return tipo    
        self.caminho = ''
        raise Exception('Formato de arquivo inválido') 

class App:
    def __init__(self):
        self.window = window
        self.email = Email()
        self.arquivo = Arquivo()
        self.tela()
        self.index()
        window.mainloop()

    def tela(self):
        self.window.configure(background='darkblue')
        self.window.resizable(False,False)
        self.window.geometry('860x500')
        self.window.iconbitmap('C:/Users/DELTAASUS/Documents/GitHub/Email_Debt/code/imgs/delta-icon.ico')
        self.window.title('Emails')

    def index(self):
        self.index = Frame(self.window, bd=4, bg='lightblue')
        self.index.place(relx=0.05,rely=0.05,relwidth=0.9,relheight=0.9)

        #Titulo
        Label(self.index, text='Gerador de Cobrança', background='lightblue', font=('arial',30,'bold')).place(relx=0.23,rely=0.3,relheight=0.15)

        #Logo
        self.logo = PhotoImage(file='C:/Users/DELTAASUS/Documents/GitHub/Email_Debt/code/imgs/deltaprice-hori.png')
        
        self.logo = self.logo.subsample(4,4)
        
        Label(self.window, image=self.logo, background='lightblue')\
            .place(relx=0.175,rely=0.1,relwidth=0.7,relheight=0.2)
        
        #Labels e Entrys
        ###########Arquivo
        Label(self.index, text='Insira aqui o arquivo:',\
            background='lightblue', font=(10))\
                .place(relx=0.15,rely=0.5)

        self.nome_arq = ''
        self.arqLabel = Label(self.index)
        self.arqLabel.config(font=("Arial", 8, 'bold italic'))
        self.arqLabel.place(relx=0.21,rely=0.57,relwidth=0.7, relheight=0.055)
        
        Button(self.index, text='Enviar',\
            command= lambda: self.arquivo.inserir(self.arqLabel))\
                .place(relx=0.15,rely=0.57,relwidth=0.06,relheight=0.055)
        

        #######Endereco email
        self.endereco_email = StringVar()

        Label(self.index, text='Endereço Email',\
            background='lightblue', font=(10))\
                .place(relx=0.15,rely=0.7)

        Entry(self.index,textvariable=self.endereco_email, justify='center')\
            .place(relx=0.15,rely=0.77,relwidth=0.35,relheight=0.05)

        Label(self.index, text='Para mais de um email, os separe com " ; "',\
            background='lightblue', font=("Arial", 10, 'bold italic'))\
                .place(relx=0.15,rely=0.85)

        #Botão enviar
        Button(self.index, text='Enviar Email',\
            command= lambda: self.executar())\
                .place(relx=0.55,rely=0.7,relwidth=0.35,relheight=0.12)
        
    def executar(self):
        try:
            if self.endereco_email.get() == '':
                raise Exception ('Insira algum endereço de email')

            titulo = self.arquivo.titulo_email()

            totalEmails = self.endereco_email.get().split(';')

            for enderecos in totalEmails:
                conteudo = self.arquivo.gerar_text()

                self.email.criar(enderecos.strip(), titulo, conteudo)
                self.email.enviar()

                messagebox.showinfo(title='Aviso', message= 'Email enviado com sucesso')
        except FileNotFoundError as e:
            messagebox.showwarning(title='Aviso', message= 'Insira um arquivo válido ou remova os acentos de seu nome')
        except Exception as e:
            messagebox.showwarning(title='Aviso', message= e)

    def mudarLabel(self, text):
        self.arqLabel['text'] = text
        
App()