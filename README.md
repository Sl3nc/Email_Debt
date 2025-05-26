# Email Debt

## Descrição

O **Email Debt** é um sistema automatizado para envio de cobranças de honorários contábeis em aberto para empresas. Ele integra leitura de relatórios em PDF, extração de dados, busca automática de e-mails de contato em sistemas externos (Acessorias.com), gerenciamento de cadastro de empresas e endereços de e-mail, e envio de mensagens personalizadas via e-mail.

O sistema possui uma interface gráfica desenvolvida em PySide6 (Qt), permitindo ao usuário selecionar relatórios, visualizar e editar informações, e acompanhar o progresso do envio das cobranças.

## Funcionalidades

- **Leitura de relatórios PDF:** Extração automática dos dados de cobrança e nomes das empresas.
- **Busca automática de e-mails:** Integração com o sistema Acessorias.com para buscar e-mails de contato das empresas.
- **Cadastro e edição de empresas e e-mails:** Gerenciamento completo dos dados no banco de dados MySQL.
- **Envio de e-mails em massa:** Geração de mensagens personalizadas em HTML e envio via SMTP2GO.
- **Interface gráfica intuitiva:** Seleção de empresas, visualização de prévias, confirmação de contatos e acompanhamento do progresso.
- **Atualização automática do driver Chrome:** Para garantir a compatibilidade do Selenium com o navegador.

## Requisitos

- Python 3.9+
- MySQL Server (pode ser via Docker)
- Google Chrome instalado
- [Selenium WebDriver](https://chromedriver.chromium.org/)
- SMTP2GO API Key
- Bibliotecas Python:
  - PySide6
  - selenium
  - python-dotenv
  - pandas
  - tabula-py
  - pymysql
  - unidecode
  - requests
  - python-dateutil
  - shutil
  - tkinter
  - smtp2go
  - outros (ver `requirements.txt`)

## Instalação

1. Clone este repositório.
2. Instale as dependências Python:
   ```
   pip install -r requirements.txt
   ```
3. Configure o arquivo `.env` com as credenciais do banco de dados, SMTP2GO e Acessorias.com.
4. Certifique-se de que o banco de dados está rodando e as tabelas necessárias estão criadas.
5. Execute o programa:
   ```
   python code/index.py
   ```

## Uso

1. Abra o sistema e selecione um relatório PDF de cobranças.
2. O sistema irá extrair os nomes das empresas e permitir a seleção de quais serão cobradas.
3. Visualize a prévia das mensagens, confirme ou edite os e-mails de contato.
4. Inicie o envio das cobranças. O progresso será exibido na interface.
5. Gerencie empresas e e-mails cadastrados pelo menu de informações.

## Observações

- O sistema automatiza o acesso ao site Acessorias.com para buscar e-mails. É necessário fornecer as credenciais no `.env`.
- O envio de e-mails utiliza a API do SMTP2GO.
- O driver do Chrome é atualizado automaticamente se necessário.
- O sistema foi desenvolvido para uso interno em escritórios de contabilidade.

## Licença

Este projeto é de uso restrito e não possui licença aberta.