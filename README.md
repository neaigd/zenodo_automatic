# Zenodo Automatic Upload Script

Este projeto contém um script Python (`zenodoapp.py`) para automatizar o processo de upload de arquivos para o Zenodo, facilitando a publicação e o arquivamento de seus dados e publicações.

## Funcionalidades

O script `zenodoapp.py` permite:

*   Criar novos depósitos (rascunhos) no Zenodo.
*   Fazer upload de arquivos para um depósito.
*   Adicionar metadados (título, autores, descrição, tipo, etc.) a um depósito.
*   Publicar um depósito para obter um DOI permanente.
*   Mover arquivos processados com sucesso para uma pasta de arquivo local (`uploaded_files`).
*   Suporta diferentes modos de operação: interativo, linha de comando (CLI) e monitoramento básico de pasta.

## Pré-requisitos

*   Python 3.6+ instalado.
*   Conta no Zenodo (ou Zenodo Sandbox para testes).
*   Uma chave de API do Zenodo com os escopos `deposit:write` e `deposit:actions`. Veja a seção [Configuração da Chave de API](#configuração-da-chave-de-api-do-zenodo) para obter instruções.

## Configuração

### Configuração da Chave de API do Zenodo

Obtenha sua chave de API seguindo os passos descritos na documentação [referência_api.md](referência_api.md).

O script espera encontrar sua chave de API na variável de ambiente `ZENODO_TOKEN`. Você pode configurá-la temporariamente no seu terminal:

```bash
export ZENODO_TOKEN="SEU_TOKEN_DE_ACESSO_AQUI"
```

Ou configurá-la permanentemente (adicione ao seu arquivo shell de inicialização, como `~/.bashrc` ou `~/.zshrc`):

```bash
echo 'export ZENODO_TOKEN="SEU_TOKEN_DE_ACESSO_AQUI"' >> ~/.bashrc
source ~/.bashrc
```

Substitua `"SEU_TOKEN_DE_ACESSO_AQUI"` pela sua chave real.

### Instalação das Dependências

Recomenda-se usar um ambiente virtual para isolar as dependências do projeto.

1.  Navegue até o diretório do projeto:
    ```bash
    cd /media/peixoto/stuff/zenodo_automatic
    ```
2.  Crie um ambiente virtual (se ainda não tiver):
    ```bash
    python3 -m venv venv
    ```
3.  Ative o ambiente virtual:
    ```bash
    source venv/bin/activate
    ```
4.  Instale as dependências listadas em `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

## Uso

O script pode ser executado em diferentes modos:

### Modo Interativo (Padrão)

Execute o script sem argumentos. Ele solicitará as informações do arquivo e metadados interativamente.

```bash
python zenodoapp.py
```

### Modo CLI (Argumentos de Linha de Comando)

Forneça todos os detalhes como argumentos para um upload não interativo:

```bash
python zenodoapp.py \
  --file "/caminho/para/seu/arquivo.pdf" \
  --title "Título da Minha Publicação" \
  --desc "Descrição detalhada do conteúdo." \
  --creator "Silva, João" \
  --creator "Souza, Maria" \
  --type "publication" # Veja zenodoapp.py para tipos válidos
```

Use `--creator` multiple times para adicionar vários autores.

### Modo Monitoramento de Pasta (`--monitor`)

Este modo processa arquivos `.pdf` encontrados na pasta `upload_queue/`. Ele espera que um arquivo `metadata.json` com os metadados correspondentes esteja presente na mesma pasta para cada PDF.

```bash
python zenodoapp.py --monitor
```

Os arquivos PDF e seus respectivos `metadata.json` são movidos para a pasta `uploaded_files/` após um upload bem-sucedido. Note que o monitoramento contínuo em tempo real não está totalmente implementado e requer desenvolvimento adicional (ex: uso da biblioteca `watchdog`).

## Estrutura de Pastas do Projeto

*   `.env`: Arquivo (ignorada pelo git) para configurar variáveis de ambiente, como `ZENODO_TOKEN`.
*   `.gitignore`: Lista de arquivos e pastas a serem ignorados pelo Git (inclui `venv/`, `uploaded_files/`, `.env`).
*   `requirements.txt`: Lista as dependências Python do projeto (`requests`).
*   `upload_queue/`: Pasta para colocar arquivos (`.pdf`) e seus `metadata.json` associados para processamento no modo monitoramento.
*   `uploaded_files/`: Pasta para onde os arquivos e metadados processados com sucesso são movidos.
*   `venv/`: Ambiente virtual Python (ignorada pelo git).
*   `zenodoapp.py`: O script principal da aplicação.
*   `referência_api.md`: Documentação detalhada sobre a obtenção da chave de API e o uso das funções do script.

## Desenvolvimento Futuro

*   Implementação completa do monitoramento contínuo de pasta com `watchdog`.
*   Adicionar tratamento de erros mais robusto.
*   Expandir as opções de metadados suportadas.
*   Implementar a funcionalidade de versionamento de arquivos (upload de novas versões de registros existentes).

---

Lembre-se de usar a Sandbox do Zenodo para testes: `https://sandbox.zenodo.org/`
