from dateutil.relativedelta import relativedelta
from PySide6.QtCore import Signal, QObject
from unidecode import unidecode
from tkinter import messagebox
from datetime import datetime
from content import Conteudo
from os import renames
import tabula as tb
import pandas as pd

class Arquivo(QObject):
    """
    Classe responsável por ler e processar arquivos PDF de relatórios, extraindo nomes de empresas e dados de cobrança.
    """
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
        """
        Define e valida o caminho do arquivo a ser processado.
        """
        if caminho == () or '':
            return None
        self.validar_tipo(caminho)
        caminho = self.validar_uni(caminho)
        self.caminho = caminho
        return caminho[caminho.rfind('/') +1:]

    def validar_uni(self, caminho):
        """
        Remove acentuação do caminho do arquivo, se necessário.
        """
        caminho_uni = unidecode(caminho)
        if caminho != caminho_uni:
            renames(caminho, caminho_uni)
            caminho = caminho_uni
            messagebox.showinfo(title='Aviso', message='O caminho do arquivo precisou ser mudado, para encontrá-lo novamente siga o caminho a seguir: \n' + caminho)
        return caminho

    def validar_tipo(self, caminho: str):
        """
        Verifica se o arquivo é do tipo PDF.
        """
        tipo = caminho[len(caminho) - 3 :]
        if tipo.lower() != 'pdf':
            raise Exception('Formato de arquivo inválido') 

    def nomes_empresas(self):
        """
        Lê o PDF e emite os nomes das empresas encontradas.
        """
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
        """
        Lê o PDF e emite os conteúdos das cobranças.
        """
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
        """
        Filtra e organiza os dados extraídos do PDF.
        """
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