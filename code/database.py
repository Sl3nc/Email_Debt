from pymysql import connect
from os import getenv

class DataBase:
    """
    Classe responsável por gerenciar a conexão e as operações com o banco de dados MySQL.
    Permite consultar, inserir, atualizar e remover empresas e endereços de e-mail.
    """
    TABELA_EMPRESA = 'Empresa'
    TABELA_USUARIO = 'Usuario'
    TABELA_EMAIL = 'Email'

    def __init__(self) -> None:
        # Inicializa a conexão com o banco de dados e define as queries SQL utilizadas.
        self.connection = connect(
                host= getenv('IP_HOST'),
                port= int(getenv('PORT_HOST')),
                user= getenv('USER_DB'),
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
        """
        Retorna a lista de e-mails cadastrados para uma empresa.
        """
        with self.connection.cursor() as cursor:
            cursor.execute(
                self.query_endereco, (nome_empresa,)
            )
            return [i for sub in cursor.fetchall() for i in sub]
    
    def remover_empresa(self, id_empresa: str):
        """
        Remove uma empresa do banco de dados pelo seu ID.
        """
        with self.connection.cursor() as cursor:
            cursor.execute(
                self.delete_empresa, (id_empresa, )
            )
            self.connection.commit()

    def remover_endereco(self, id_empresa: str, endereco: str):
        """
        Remove um endereço de e-mail específico de uma empresa.
        """
        with self.connection.cursor() as cursor:
            cursor.execute(
                self.delete_endereco, (id_empresa, endereco)
            )
            self.connection.commit()

    def remover_enderecos(self, id_empresa: str):
        """
        Remove todos os endereços de e-mail de uma empresa.
        """
        with self.connection.cursor() as cursor:
            cursor.execute(
                self.delete_enderecos, (id_empresa,)
            )
            self.connection.commit()
    
    def atualizar_endereco(self, end_novo: str, end_antigo: str, id_emp: str):
        """
        Atualiza um endereço de e-mail de uma empresa.
        """
        with self.connection.cursor() as cursor:
            cursor.execute(
                self.update_endereco, (end_novo, end_antigo, id_emp)
            )
            self.connection.commit()

    def registrar_empresa(self, nome_empresa: str) -> None:
        """
        Registra uma nova empresa no banco de dados.
        """
        with self.connection.cursor() as cursor:
            cursor.execute(
                self.insert_empresa, (nome_empresa,)
            )
            self.connection.commit()
    
    def empresas(self) -> list[str]:
        """
        Retorna a lista de nomes de todas as empresas cadastradas.
        """
        with self.connection.cursor() as cursor:
            cursor.execute(
                self.query_empresas
            )
            return [i for sub in cursor.fetchall() for i in sub]

    def registrar_enderecos(self, enderecos: list[str], id_empresa: str) -> None:
        """
        Registra múltiplos endereços de e-mail para uma empresa.
        """
        with self.connection.cursor() as cursor:
            cursor.executemany(
                self.insert_endereco, 
                ([endereco, id_empresa] for endereco in enderecos)
            )
            self.connection.commit()

    def identificador_empresa(self, nome_empresa: str) -> str:
        """
        Retorna o identificador (ID) de uma empresa pelo nome.
        """
        with self.connection.cursor() as cursor:
            cursor.execute(
                self.query_empresa, (nome_empresa,)
            )
            return cursor.fetchone()[0]

    def user_acessorias(self, nome_func: str):
        """
        Retorna as credenciais de acesso ao sistema Acessorias para um usuário.
        """
        with self.connection.cursor() as cursor:
            cursor.execute(
                self.query_acessorias, (nome_func,)
            )
            return cursor.fetchone()
    