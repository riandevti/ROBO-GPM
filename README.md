# ROBO-GPM

Automação desenvolvida em Python para gerar, baixar e processar relatórios do sistema GPM de forma automática.

O robô realiza login no sistema, solicita a exportação do relatório de obras, aguarda o download do arquivo ZIP, extrai o CSV, renomeia o arquivo e o move para uma pasta de destino configurada.

## Funcionalidades

* Login automatizado no sistema GPM
* Exportação automática de relatórios
* Download de arquivos ZIP
* Extração automática do CSV
* Renomeação padronizada para `OBRAS.csv`
* Movimentação do arquivo para uma pasta definida pelo usuário
* Registro de logs de execução
* Agendamento de execuções em horários específicos
* Empacotamento como executável Windows (`.exe`)

## Tecnologias utilizadas

* Python 3
* Selenium
* ChromeDriver
* python-dotenv
* schedule
* PyInstaller

## Estrutura do projeto

```text
ROBO-GPM/

├── automation.py
├── scheduler.py
├── logger.py
├── config.json
├── .env
├── downloads/
├── logs/
└── README.md
```

## Configuração

Crie um arquivo `.env` na raiz do projeto:

```env
ADMIN_USERNAME=seu_usuario
ADMIN_PASSWORD=sua_senha
```

Configure o arquivo `config.json`:

```json
{
  "login_url": "URL_DO_LOGIN",
  "export_url": "URL_DA_EXPORTACAO",
  "initial_date": "07/05/2023",
  "contract_id": "17",
  "download_folder": "downloads",
  "destination_folder": "C:\\Destino",
  "log_folder": "logs"
}
```

## Instalação

Clone o repositório:

```bash
git clone <URL_DO_REPOSITORIO>
cd ROBO-GPM
```

Crie o ambiente virtual:

```bash
python -m venv .venv
```

Ative o ambiente virtual:

Windows:

```bash
.venv\Scripts\activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

## Execução

Para executar manualmente:

```bash
python automation.py
```

Para utilizar o agendamento automático:

```bash
python scheduler.py
```

## Gerando o executável

```bash
pyinstaller --onefile --noconsole --name GPM_BOT automation.py
```

O executável será gerado na pasta:

```text
dist/
```

## Logs

Todos os eventos da automação são registrados na pasta `logs/`, incluindo:

* data e hora da execução;
* usuário da máquina;
* início e término da automação;
* falhas e exceções;
* arquivos processados.

## Aviso

Este projeto foi desenvolvido para fins internos de automação de processos.

Credenciais de acesso não devem ser armazenadas diretamente no código-fonte.

Utilize sempre variáveis de ambiente através do arquivo `.env`.
