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
    def __init__(self):
        self.arquivo = ''
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

    def inserir(self, label):
        caminho = askopenfilename()
        ultima_barra = caminho.rfind('/')
        self.nome = caminho[ultima_barra+1:]
        label['text'] = self.nome

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
        self.arquivo = Arquivo()
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
        self.index = Frame(self.window, bd=4, bg='lightblue')
        self.index.place(relx=0.05,rely=0.05,relwidth=0.9,relheight=0.9)

        #Titulo
        Label(self.index, text='Conversor de Extrato', background='lightblue', font=('arial',30,'bold')).place(relx=0.23,rely=0.2,relheight=0.15)

        # #Logo
        # self.logo = PhotoImage(file='C:/Users/DELTAASUS/Documents/GitHub/Extrato_Auto/code/imgs/deltaprice-hori.png')
        
        # self.logo = self.logo.subsample(4,4)
        
        # Label(self.window, image=self.logo, background='lightblue')\
        #     .place(relx=0.175,rely=0.05,relwidth=0.7,relheight=0.2)
        
        #Labels e Entrys
        ###########Arquivo
        Label(self.index, text='Insira aqui o arquivo:',\
            background='lightblue', font=(10))\
                .place(relx=0.15,rely=0.4)

        self.nome_arq = ''
        self.arqLabel = Label(self.index)
        self.arqLabel.config(font=("Arial", 8, 'bold italic'))
        self.arqLabel.place(relx=0.21,rely=0.47,relwidth=0.35, relheight=0.055)
        
        Button(self.index, text='Enviar',\
            command= lambda: self.arquivo.inserir(self.arqLabel))\
                .place(relx=0.15,rely=0.47,relwidth=0.06,relheight=0.055)
        
        #Botão enviar
        Button(self.index, text='Gerar Extrato',\
            command= lambda: self.executar(self.endereco_email))\
                .place(relx=0.35,rely=0.8,relwidth=0.35,relheight=0.12)
        
    def executar(self):
        arquivo = Arquivo(self.pdf)
        empresa = arquivo.nomeEmpresa()
        conteudo = Arquivo.gerar_text(arquivo)
        self.email.criar(destinatario= 'deltapricepedro@gmail.com', titulo=empresa, conteudo=conteudo)
        self.email.enviar()

    


App()