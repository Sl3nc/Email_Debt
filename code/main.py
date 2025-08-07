from PySide6.QtWidgets import (
    QMainWindow, QApplication, QCheckBox, QTreeWidgetItem, QPushButton, QHBoxLayout, QFrame, QSizePolicy, QFileDialog
)
from PySide6.QtGui import QPixmap, QIcon, QMovie
from src.window_cobranca import Ui_MainWindow
from PySide6.QtCore import QThread, QSize
from os import remove
from traceback import print_exc
from tkinter import messagebox
from dotenv import load_dotenv
from collector import Cobrador
from database import DataBase
from copy import deepcopy
from pathlib import Path
from file import Arquivo
from pymysql import err
from startfile import startfile

load_dotenv(Path(__file__).parent / 'src' / 'env' / '.env')

class MainWindow(QMainWindow, Ui_MainWindow):
    """
    Classe principal da interface gráfica do sistema, responsável por interagir com o usuário e orquestrar as operações.
    """
    def __init__(self, parent = None) -> None:
        """
        Inicializa a janela principal e conecta os sinais aos slots.
        """
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
        self.frames = []

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

    def try_conection(self):
        """
        Tenta conectar ao banco de dados e exibe mensagem de erro caso falhe.
        """
        try:
            self.db = DataBase()
        except err.OperationalError as e:
            messagebox.showerror('Aviso!', f'Falha na conexão com o banco de dados. Favor verificar se o aplicativo "DOCKER" está inicializado no servidor, caso constrário, entre em contato com o suporte disponível\n\n{e}')
            raise Exception('')

    def inserir_relatorio(self):
        """
        Permite ao usuário selecionar e inserir um relatório PDF.
        """
        try:
            caminho_reduzido = self.arquivo.set_caminho( 
                QFileDialog.getOpenFileName(
                    caption= "Favor, inserir o relatório",
                    filter= "Arquivo PDF (*pdf)",
                )[0]
            )
            if caminho_reduzido == None:
                return
            self.pushButton_body_relatorio_anexar.setText(caminho_reduzido)
            self.pushButton_body_relatorio_anexar.setIcon(QIcon())
            self.pesquisar_empresas()
        # except FileNotFoundError:
        #     messagebox.showwarning(title='Aviso', message= 'Operação cancelada')
        except Exception as e:
            print_exc()
            messagebox.showwarning(title='Aviso', message= e)

    def pesquisar_empresas(self):
        """
        Pesquisa e exibe as empresas presentes no relatório.
        """
        if self.label_empresas_aviso.isVisible() == True:
            self.label_empresas_aviso.hide()
        else:
            for widget in self.frames:
                self.gridLayout_empresas.removeWidget(widget)
                widget.destroy()
                widget.hide()

        self.pushButton_empresas_marcar.hide()
        self.pushButton_body_executar.setEnabled(False)
        self.exec_load_empresas(True)
        
        self.inicio = self._thread.started.connect(self.arquivo.nomes_empresas)
        self.arquivo.fim.connect(self.reset_thread)
        self.arquivo.error.connect(self.exec_load_empresas)
        self.conexao_nome = self.arquivo.nomes.connect(self.exibir_opcoes)

        self._thread.start()

    def exec_load_empresas(self, action: bool):
        """
        Controla a exibição do carregamento das empresas.
        """
        if action == True:
            self.movie.start()
            self.stackedWidget_empresas.setCurrentIndex(1)
        else:
            self.movie.stop()
            self.stackedWidget_empresas.setCurrentIndex(0)
        
    #TODO OPCOES
    def exibir_opcoes(self, nomes: list):
        """
        Exibe as opções de empresas para seleção.
        """
        self.options.clear()
        self.preview_btn.clear()
        self.frames.clear()
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

            self.frames.append(frame)
            frame.setLayout(layout)
            self.gridLayout_empresas.addWidget(frame)

        self.pushButton_empresas_marcar.show()
        self.pushButton_body_executar.setEnabled(True)
        self.exec_load_empresas(False)

    def carregar_mensagem(self):
        """
        Carrega a prévia da mensagem de cobrança para uma empresa.
        """
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
        """
        Exibe a mensagem de cobrança gerada em HTML.
        """
        html = dict_conteudos[self.empresa_preview]['mensagem']
        with open (self.PATH_MESSAGE, 'w', encoding='utf-8') as file:
           file.write(''.join(x for x in html))

        startfile(self.PATH_MESSAGE)

        self.pushButton_empresas_marcar.show()
        self.pushButton_body_executar.setEnabled(True)
        self.exec_load_empresas(False)

    def marcar_options(self):
        """
        Marca ou desmarca todas as opções de empresas.
        """
        for i in self.options:
            i.setChecked(self.option_checada)

        if self.option_checada == False:
            self.pushButton_empresas_marcar.setText('Marcar todos')
        else:
            self.pushButton_empresas_marcar.setText('Desmarcar todos')
        self.option_checada = not self.option_checada

    def executar(self):
        """
        Inicia o processo de cobrança para as empresas selecionadas.
        """
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
        """
        Reseta as conexões de thread conforme a etapa.
        """
        if option == 1:
            self._thread.disconnect(self.inicio)
            self.arquivo.disconnect(self.conexao_nome)
        elif option == 2:
            self._thread.disconnect(self.conexao_ler)
            self.arquivo.disconnect(self.conexao_cobrar)
    
    #TODO COBRAR
    def cobrar(self, dict_content: dict[str,dict]):
        """
        Inicia o processo de cobrança, criando e enviando os e-mails.
        """
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
        """
        Filtra o conteúdo das empresas selecionadas.
        """
        filtred_content = deepcopy(dict_content)
        for i in self.options:
            if i.isChecked() == False:
                del filtred_content[i.text()]
        
        return filtred_content
    
    def confirmar_registro(self, dict_contato: dict[str,dict[str,str]]):
        """
        Exibe a tela de confirmação dos endereços de e-mail encontrados.
        """
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
        """
        Exibe aviso para empresas sem e-mail encontrado.
        """
        b = '\n -'.join(list_empty)
        a = f'O endereço de e-mail das seguintes empresas não foram encontrados no acessórias:\n\n{b}\n\nFavor inseri-los manualmente'
        messagebox.showwarning(
            title='Aviso', 
            message=a)

    def enviar_contatos(self):
        """
        Envia os contatos confirmados para registro.
        """
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
        """
        Atualiza o texto e a barra de progresso conforme a etapa.
        """
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
        """
        Atualiza o valor da barra de progresso.
        """
        self.progressBar.setValue(value)

    def conclusion(self, dict_contatos: dict[str, list[str]]):
        """
        Exibe mensagem de conclusão após o envio dos e-mails.
        """
        self.exec_load(False, 0)
        text = ''
        for nome_empresa, enderecos in dict_contatos.items():
            text = f'{text}\n-{nome_empresa}\n'
            for endereco in enderecos:
                text = f'{text}|=>{endereco}\n'

        messagebox.showinfo(title='Aviso', message= f'Email enviado com sucesso para: \n{text}')

    def acess_cadastro(self, nome_empresa: str):
        """
        Solicita manualmente o cadastro de e-mail para empresa sem contato.
        """
        self.lineEdit_endereco.setText('')
        self.label_endereco_title.setText('Empresa abaixo não cadastrada:')
        self.label_endereco_empresa.setText(nome_empresa)
        self.conexao_envio = self.pushButton_endereco.clicked.connect(
            lambda: self.enviar_valor(nome_empresa)
        )
        self.exec_load(False, 2)

    def enviar_valor(self, nome_empresa: str):
        """
        Envia o valor informado manualmente para registro.
        """
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
        """
        Controla a exibição do carregamento geral.
        """
        if action == True:
            self.movie.start()
            self.stackedWidget_body.setCurrentIndex(1)
        else:
            self.movie.stop()
            self.stackedWidget_body.setCurrentIndex(to)

    def acess_infos(self):
        """
        Exibe as informações cadastradas no banco de dados.
        """
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
        """
        Adiciona um novo e-mail para uma empresa.
        """
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
        """
        Realiza a operação de adição de e-mail.
        """
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
        """
        Permite editar um e-mail cadastrado.
        """
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
        """
        Realiza a operação de edição de e-mail.
        """
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
        """
        Remove um e-mail ou empresa do banco de dados.
        """
        try:
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
        except Exception as e:
            messagebox.showwarning('Aviso', e)

if __name__ == '__main__':
    # Inicializa a aplicação Qt.
    app = QApplication()
    window = MainWindow()
    window.show()
    app.exec()
