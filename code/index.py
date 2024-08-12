from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askopenfilename, asksaveasfilename

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

import tabula as tb

window = Tk()

class Email:
    def __init__(self):
        self.server_smtp = 'smtp.gmail.com'
        self.port = 587
        self.server = smtplib.SMTP(self.server_smtp, self.port)

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
            self.server.starttls()

            self.server.login(self.address, self.password)

            self.server.sendmail(self.address, 'deltapricepedro@gmail.com',self.msg.as_string())
            print('Deu')
        except Exception as e:
            print(f'Ocorreu um erro: {e}')
        finally:
            self.server.quit()

class Arquivo:
    def __init__(self, arquivo):
        self.arquivo = arquivo
        self.body = """"
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Document</title>
        </head>
        <body>
            <p>Não acusamos o recebimento do(s) honorário(s) relacionado(s) abaixo:</p>
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
        </body>
        </html>''
        """

    def gerar_text(self):
        text = ''
        valorGeral = ''
        arquivo = tb.read_pdf(self.arquivo, pages="all")

        arquivo = arquivo[0].drop([0,1,4])

        for index, row in arquivo.iterrows():
            if 'Total geral:' in str(row['Competência']):
                self.valorGeral =  'Total em aberto: '+ str(row['Em aberto'])
                break
            arquivo.loc[[index],['Vencimento']] = str(row['Vencimento']).replace('1/1 ','')
            text = text + 'Período: {0} - Vencimento: {1} - Valor: {2}\n'\
                .format(str(row['Competência']), str(row['Vencimento']), str(row['Em aberto']))

        text = text + valorGeral
        return self.body.replace('$text', text)
    
    def nomeEmpresa():
        return 'Sesas'

class App:
    def __init__(self):
        self.window = window
        self.email = Email()
        self.tela()
        self.index()
        window.mainloop()

    def tela(self):
        self.window.configure(background='darkblue')
        self.window.resizable(False,False)
        self.window.geometry('860x500')
        #self.window.iconbitmap('C:/Users/DELTAASUS/Documents/GitHub/Extrato_Auto/code/imgs/delta-icon.ico')
        self.window.title('Emails')

    def index(self):

        #Botão enviar
        Button(self.index, text='Gerar Extrato',\
            command= lambda: self.ler_arq(self.nome_arq,self.bancoEntry, self.rdButton))\
                .place(relx=0.35,rely=0.8,relwidth=0.35,relheight=0.12)
        
    def executar(self):
        arquivo = Arquivo(self.pdf)
        empresa = arquivo.nomeEmpresa()
        conteudo = Arquivo.gerar_text(arquivo)
        self.email.criar(destinatario= 'deltapricepedro@gmail.com', titulo=empresa, conteudo=conteudo)
        self.email.enviar()


App()