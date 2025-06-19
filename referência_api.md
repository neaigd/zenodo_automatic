Com certeza. Uma vez que o seu agente não consegue aceder à documentação, preparei uma série de notas interligadas com base no conteúdo de `https://developers.zenodo.org/`.

Estas notas foram concebidas para fornecer as especificações precisas e os exemplos de código de que necessita para o seu projeto.

---

### **Hub Central: Guia da API Zenodo para o Seu Projeto**

Bem-vindo ao seu guia de referência para a API do Zenodo. Estas notas estão interligadas para o guiar através do processo de automatização de submissões.

**Índice de Notas:**

1.  [Conceitos Fundamentais e Fluxo de Trabalho](#nota-1-conceitos-fundamentais-e-fluxo-de-trabalho)
2.  [Autenticação e Ambiente de Testes (Sandbox)](#nota-2-autenticacao-e-ambiente-de-testes-sandbox)
3.  [Passo 1: Criar uma Nova Submissão (Deposition)](#nota-3-passo-1-criar-uma-nova-submissao-deposition)
4.  [Passo 2: Upload de Ficheiros](#nota-4-passo-2-upload-de-ficheiros)
5.  [Passo 3: Adicionar e Atualizar Metadados](#nota-5-passo-3-adicionar-e-atualizar-metadados)
6.  [Passo 4: Publicar a Submissão](#nota-6-passo-4-publicar-a-submissao)
7.  [Referência Rápida de Metadados Essenciais](#nota-7-referencia-rapida-de-metadados-essenciais)

---

### **Nota 1: Conceitos Fundamentais e Fluxo de Trabalho**

O processo de submissão via API do Zenodo segue um fluxo de trabalho claro e transacional. O conceito central é o **"Deposition"**.

*   **O que é um "Deposition"?** Um *Deposition* é essencialmente um rascunho da sua submissão. É um contentor para os seus ficheiros e metadados que existe num estado `unsubmitted` (não submetido) até que decida publicá-lo. Uma vez publicado, torna-se um "Record" (registo) imutável.

**O Fluxo de Trabalho Padrão é:**

1.  **Criar um Deposition Vazio:** Envia um pedido `POST` para a API para criar um novo rascunho. A API devolve um `id` único para este deposition e um `bucket_url` para o upload de ficheiros.
2.  **Fazer Upload dos Ficheiros:** Utiliza o `bucket_url` fornecido para fazer o upload de um ou mais ficheiros (`.pdf`, `.zip`, `.csv`, etc.) através de um pedido `PUT`.
3.  **Adicionar Metadados:** Envia um pedido `PUT` para o endpoint do deposition com todos os metadados necessários (título, autores, descrição, etc.) em formato JSON.
4.  **Publicar:** Envia um pedido `POST` final para um endpoint de "ação" para publicar o deposition. Este passo é irreversível.

➡️ **Próximo Passo:** Antes de fazer qualquer pedido, precisa de se autenticar. Veja a **[Nota 2: Autenticação e Ambiente de Testes (Sandbox)](#nota-2-autenticacao-e-ambiente-de-testes-sandbox)**.

---

### **Nota 2: Autenticação e Ambiente de Testes (Sandbox)**

Toda a interação com a API requer um token de acesso. Para desenvolvimento, é **altamente recomendado** usar o ambiente Sandbox do Zenodo.

*   **Ambiente Sandbox:**
    *   **URL:** `https://sandbox.zenodo.org/`
    *   **URL Base da API:** `https://sandbox.zenodo.org/api/`
    *   Requer um registo e um token de acesso separados do site de produção.
    *   É um ambiente seguro para testar o seu código sem publicar registos permanentes.

*   **Obtenção do Token de Acesso:**
    1.  Crie uma conta no [Zenodo Sandbox](https://sandbox.zenodo.org/).
    2.  Navegue até **Applications** > **Personal access tokens** > **New token**.
    3.  Dê um nome ao token e selecione os `scopes` (permissões) necessários:
        *   `deposit:write`: Para criar e editar submissões.
        *   `deposit:actions`: Para publicar.
    4.  Copie e guarde o token. Ele não será mostrado novamente.

*   **Utilizar o Token em Python:**
    O token deve ser incluído em todos os pedidos como um parâmetro de URL.

    ```python
    import requests

    # É uma boa prática usar o sandbox para testes
    ACCESS_TOKEN = "SEU_TOKEN_DO_SANDBOX_AQUI"
    BASE_URL = "https://sandbox.zenodo.org/api"

    params = {'access_token': ACCESS_TOKEN}

    # Exemplo de teste de conexão
    r = requests.get(f"{BASE_URL}/deposit/depositions", params=params)

    # Um código 200 significa que a sua autenticação funcionou
    print(f"Status da Conexão: {r.status_code}")
    # Irá imprimir uma lista vazia se não tiver submissões
    print(f"Resposta: {r.json()}")
    ```

➡️ **Próximo Passo:** Vamos começar a usar a API. Veja a **[Nota 3: Passo 1: Criar uma Nova Submissão (Deposition)](#nota-3-passo-1-criar-uma-nova-submissao-deposition)**.

---

### **Nota 3: Passo 1: Criar uma Nova Submissão (Deposition)**

O primeiro passo é criar um contentor vazio para a sua submissão. Isto é feito com um pedido `POST`.

*   **Endpoint:** `POST /api/deposit/depositions`
*   **Cabeçalho Necessário:** `Content-Type: application/json`
*   **Corpo do Pedido:** Pode ser um JSON vazio `{}`.

**Exemplo em Python:**

```python
import requests
import json

ACCESS_TOKEN = "SEU_TOKEN_DO_SANDBOX_AQUI"
BASE_URL = "https://sandbox.zenodo.org/api"

headers = {"Content-Type": "application/json"}
params = {'access_token': ACCESS_TOKEN}

# Envia um pedido POST com um corpo JSON vazio para criar o deposition
r = requests.post(
    f'{BASE_URL}/deposit/depositions',
    params=params,
    json={} # Corpo do pedido vazio
)

if r.status_code == 201: # 201 Created é a resposta de sucesso
    deposition_data = r.json()
    deposition_id = deposition_data['id']
    bucket_url = deposition_data['links']['bucket']
    
    print(f"✅ Deposition criado com sucesso!")
    print(f"   ID do Deposition: {deposition_id}")
    print(f"   URL do Bucket para Upload: {bucket_url}")
else:
    print(f"❌ Erro ao criar deposition: {r.status_code} - {r.text}")

```
A resposta de sucesso contém duas informações cruciais que deve guardar: o `id` da submissão e o `links.bucket`, que é o URL para onde irá fazer o upload dos seus ficheiros.

➡️ **Próximo Passo:** Com um deposition criado, é hora de adicionar ficheiros. Veja a **[Nota 4: Passo 2: Upload de Ficheiros](#nota-4-passo-2-upload-de-ficheiros)**.

---

### **Nota 4: Passo 2: Upload de Ficheiros**

O Zenodo utiliza uma API de "bucket" para uploads de ficheiros, o que é mais eficiente para ficheiros grandes. O processo é fazer um pedido `PUT` para o `bucket_url` obtido no passo anterior.

*   **Endpoint:** `PUT {bucket_url}/{filename}`
    *   `{bucket_url}` é o URL obtido na criação do deposition.
    *   `{filename}` é o nome que o ficheiro terá no Zenodo.
*   **Cabeçalho:** O tipo de conteúdo do ficheiro (ex: `application/octet-stream`). A biblioteca `requests` geralmente trata disto automaticamente ao enviar dados de ficheiro.
*   **Corpo do Pedido:** Os dados binários do ficheiro.

**Exemplo em Python:**

```python
import requests

# --- Assumindo que já executou o código da Nota 3 ---
# deposition_id = 123456
# bucket_url = "https://sandbox.zenodo.org/api/files/some-uuid-string"
# ACCESS_TOKEN = "SEU_TOKEN_DO_SANDBOX_AQUI"
# params = {'access_token': ACCESS_TOKEN}

FILENAME = "meu-artigo.pdf"
FILE_PATH = "caminho/para/meu-artigo.pdf" # Mude para o caminho do seu ficheiro

# O alvo do upload é o URL do bucket + o nome do ficheiro desejado
target_url = f"{bucket_url}/{FILENAME}"

print(f"A fazer upload de '{FILENAME}' para o Zenodo...")

with open(FILE_PATH, "rb") as file_data:
    r = requests.put(
        target_url,
        data=file_data, # Envia os dados binários do ficheiro
        params=params
    )

if r.status_code == 200 or r.status_code == 201:
    print(f"✅ Ficheiro enviado com sucesso!")
    print(json.dumps(r.json(), indent=2))
else:
    print(f"❌ Erro no upload do ficheiro: {r.status_code} - {r.text}")
```
➡️ **Próximo Passo:** Agora que os ficheiros estão no rascunho, precisa de adicionar a descrição. Veja a **[Nota 5: Passo 3: Adicionar e Atualizar Metadados](#nota-5-passo-3-adicionar-e-atualizar-metadados)**.

---

### **Nota 5: Passo 3: Adicionar e Atualizar Metadados**

Os metadados (título, autores, etc.) são adicionados enviando um pedido `PUT` para o URL do próprio deposition.

*   **Endpoint:** `PUT /api/deposit/depositions/{deposition_id}`
*   **Cabeçalho Necessário:** `Content-Type: application/json`
*   **Corpo do Pedido:** Um objeto JSON dentro de uma chave `metadata`.

**Exemplo em Python:**
```python
import requests
import json

# --- Assumindo que já executou o código da Nota 3 ---
# deposition_id = 123456
# ACCESS_TOKEN = "SEU_TOKEN_DO_SANDBOX_AQUI"
# BASE_URL = "https://sandbox.zenodo.org/api"
# params = {'access_token': ACCESS_TOKEN}

headers = {"Content-Type": "application/json"}

# Construa o seu dicionário de metadados
# Veja a Nota 7 para mais detalhes sobre os campos
metadata_payload = {
    'metadata': {
        'title': 'Análise Automática de Padrões em PDFs Científicos',
        'upload_type': 'publication',
        'publication_type': 'article',
        'description': 'Este artigo descreve um método para automatizar a extração de dados. O HTML <b>simples</b> é permitido aqui.',
        'creators': [{'name': 'Silva, Ana', 'affiliation': 'Universidade de Lisboa'}],
        'keywords': ['automação', 'api', 'zenodo', 'python']
    }
}

r = requests.put(
    f'{BASE_URL}/deposit/depositions/{deposition_id}',
    params=params,
    data=json.dumps(metadata_payload), # O corpo deve ser uma string JSON
    headers=headers
)

if r.status_code == 200:
    print("✅ Metadados adicionados com sucesso!")
    print(json.dumps(r.json()['metadata'], indent=2))
else:
    print(f"❌ Erro ao adicionar metadados: {r.status_code} - {r.text}")
```➡️ **Próximo Passo:** O seu rascunho está completo. O passo final é torná-lo público. Veja a **[Nota 6: Passo 4: Publicar a Submissão](#nota-6-passo-4-publicar-a-submissao)**.

---

### **Nota 6: Passo 4: Publicar a Submissão**

Este é o passo final e **irreversível**. Uma vez publicado, um deposition não pode ser apagado. Apenas pode ser editado criando uma nova versão. A publicação é uma "ação" e tem o seu próprio endpoint.

*   **Endpoint:** `POST /api/deposit/depositions/{deposition_id}/actions/publish`
*   **Corpo do Pedido:** Nenhum.
*   **Scope do Token Necessário:** `deposit:actions`.

**Exemplo em Python:**

```python
import requests

# --- Assumindo que já executou o código das notas anteriores ---
# deposition_id = 123456
# ACCESS_TOKEN = "SEU_TOKEN_DO_SANDBOX_AQUI"
# BASE_URL = "https://sandbox.zenodo.org/api"
# params = {'access_token': ACCESS_TOKEN}

# AVISO: A execução deste código tornará a sua submissão pública permanentemente.
# Confirme no site do Zenodo Sandbox que o rascunho está correto antes de prosseguir.

user_input = input(f"Tem a certeza que deseja publicar o deposition ID {deposition_id}? (s/n): ")

if user_input.lower() == 's':
    print("A publicar...")
    r = requests.post(
        f'{BASE_URL}/deposit/depositions/{deposition_id}/actions/publish',
        params=params
    )

    # 202 Accepted significa que o Zenodo aceitou o pedido e está a processá-lo
    if r.status_code == 202:
        published_data = r.json()
        doi = published_data.get('doi')
        record_html_url = published_data.get('links', {}).get('record_html')
        
        print("🎉 Submissão publicada com sucesso!")
        print(f"   DOI: {doi}")
        print(f"   Ver em: {record_html_url}")
    else:
        print(f"❌ Erro ao publicar: {r.status_code} - {r.text}")
else:
    print("Publicação cancelada.")
```
➡️ **Próximo Passo:** Para preencher os seus metadados de forma correta, consulte a **[Nota 7: Referência Rápida de Metadados Essenciais](#nota-7-referencia-rapida-de-metadados-essenciais)**.

---

### **Nota 7: Referência Rápida de Metadados Essenciais**

Aqui estão os campos de metadados mais comuns e obrigatórios. Todos devem estar dentro de um objeto JSON principal chamado `"metadata"`.

| Campo | Obrigatório? | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| `title` | **Sim** | O título da sua submissão. | `"O Meu Título"` |
| `upload_type` | **Sim** | O tipo de conteúdo. Vocabulário controlado. | `"publication"`, `"dataset"`, `"software"`, `"image"`, etc. |
| `description` | **Sim** | O resumo/descrição. Permite HTML simples. | `"Esta é a descrição do meu projeto..."` |
| `creators` | **Sim** | Uma lista de autores/criadores. | `[{'name': 'Silva, Ana', 'affiliation': 'FCT'}]` |
| `publication_type` | Sim, se `upload_type` for `publication`. | O subtipo de publicação. | `"article"`, `"thesis"`, `"report"`, etc. |
| `access_right` | **Sim** | Controla o acesso. | `"open"`, `"embargoed"`, `"restricted"`, `"closed"` |
| `license` | Sim, se `access_right` for `open`. | O ID da licença. | `"cc-by-4.0"` (para trabalhos criativos), `"mit"` (para software) |
| `keywords` | Não | Uma lista de palavras-chave. | `["api", "python", "data"]` |
| `prereserve_doi` | Não | Coloque `true` para obter um DOI antes da publicação. | `true` |
| `related_identifiers` | Não | Para ligar a outros DOIs (ex: o artigo que descreve o dataset). | `[{'identifier': '10.5281/zenodo.12345', 'relation': 'isSupplementTo'}]` |