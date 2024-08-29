from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askopenfilename

from smtp2go.core import Smtp2goClient

import tabula as tb
from unidecode import unidecode
from datetime import datetime
import string
import os

window = Tk()

class Email:
    def __init__(self):
        self.client = Smtp2goClient(api_key='api-57285302C4594921BD70EB19882D320B')

    def criar(self, destinatario, titulo, conteudo):
        self.payload = {
            'sender': 'financeiro@deltaprice.com.br',
            'recipients': [destinatario],
            'subject': titulo,
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
            <img src="https://i.imgur.com/CmnqM3L.png" style="width: 50%;">
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
        self.caminho = askopenfilename()

        if self.caminho =='':
            raise FileNotFoundError('Operação cancelada')

        if any(c not in string.ascii_letters for c in self.caminho):
            caminho_uni = unidecode(self.caminho)
            os.rename(self.caminho, caminho_uni)
            self.caminho = caminho_uni

        self.tipo = self.definir_tipo()
        ultima_barra = self.caminho.rfind('/')
        label['text'] = self.caminho[ultima_barra+1:]

    def ler(self):
        conteudo = Conteudo()
        arquivo = tb.read_pdf(self.caminho, pages="all",)

        arquivo = arquivo[0].drop([0,1])

        for index, row in arquivo.iterrows():
            if 'Total do cliente:' in str(row['Competência']):
                break

            row['Vencimento'] = str(row['Vencimento']).replace('1/1 ','')
            conteudo.add_linha(row)
            
        return conteudo.to_string()
    
    def titulo_email(self):
        arquivo = tb.read_pdf(self.caminho, pages="all",)
        return arquivo[0].loc[[1],['Vencimento']].values[0][0] + ' - HONORÁRIOS CONTÁBEIS EM ABERTO'

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
        #self.window.iconbitmap('Z:\\18 - PROGRAMAS DELTA\\code\\imgs\\delta-icon.ico')
        self.window.title('Cobrança Automática')

    def index(self):
        self.index = Frame(self.window, bd=4, bg='lightblue')
        self.index.place(relx=0.05,rely=0.05,relwidth=0.9,relheight=0.9)

        #Titulo
        Label(self.index, text='Atualiação e Cobrança\n de Honorários Vencidos', background='lightblue', font=('arial',25,'bold')).place(relx=0.23,rely=0.25,relheight=0.15)

        #Logoo
        #self.logo = PhotoImage(file='Z:\\18 - PROGRAMAS DELTA\\code\\imgs\\deltaprice-hori.png')
        
        # self.logo = self.logo.subsample(4,4)
        
        # Label(self.window, image=self.logo, background='lightblue')\
        #     .place(relx=0.175,rely=0.05,relwidth=0.7,relheight=0.2)
        
        #Labels e Entrys
        ###########Arquivo
        Label(self.index, text='Insira aqui o arquivo:',\
            background='lightblue', font=(10))\
                .place(relx=0.15,rely=0.47)

        self.nome_arq = ''
        self.arqLabel = Label(self.index)
        self.arqLabel.config(font=("Arial", 8, 'bold italic'))
        self.arqLabel.place(relx=0.21,rely=0.54,relwidth=0.7, relheight=0.055)
        
        Button(self.index, text='Enviar',\
            command= lambda: self.arquivo.inserir(self.arqLabel))\
                .place(relx=0.15,rely=0.54,relwidth=0.06,relheight=0.055)
        

        #######Endereco email
        self.endereco_email = StringVar()

        Label(self.index, text='Endereços de Email:',\
            background='lightblue', font=(10))\
                .place(relx=0.15,rely=0.65)

        Entry(self.index,textvariable=self.endereco_email, justify='center')\
            .place(relx=0.15,rely=0.72,relwidth=0.75,relheight=0.05)

        Label(self.index, text='Para mais de um email, os separe com " ; "',\
            background='lightblue', font=("Arial", 10, 'bold italic'))\
                .place(relx=0.15,rely=0.8)

        #Botão enviar
        Button(self.index, text='Enviar Email',\
            command= lambda: self.executar())\
                .place(relx=0.55,rely=0.8,relwidth=0.35,relheight=0.12)
        
    def executar(self):
        try:
            if self.endereco_email.get() == '':
                raise Exception ('Insira algum endereço de email')

            titulo = self.arquivo.titulo_email()

            totalEmails = self.endereco_email.get().split(';')
            
            for enderecos in totalEmails:
                conteudo = self.arquivo.ler()

                self.email.criar(enderecos.strip(), titulo, conteudo)
                self.email.enviar()

                messagebox.showinfo(title='Aviso', message= 'Email enviado com sucesso')

        except FileNotFoundError:
            messagebox.showwarning(title='Aviso', message= 'Insira algum arquivo')
        except Exception as e:
            messagebox.showwarning(title='Aviso', message= e)

    def mudarLabel(self, text):
        self.arqLabel['text'] = text
        
App()