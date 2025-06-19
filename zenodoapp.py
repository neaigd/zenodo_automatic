import requests
import json
import os
import argparse
import shutil
from datetime import datetime
import time
import dotenv  # Added for .env support

# --- Load environment variables ---
dotenv.load_dotenv()  # Load .env file if exists

# --- CONFIGURAÇÃO ---
# Pasta para mover os arquivos após o upload bem-sucedido.
ARCHIVE_FOLDER = "uploaded_files"  # Caminho relativo ao diretório do script

# Get access token from environment
ACCESS_TOKEN = os.getenv("ZENODO_TOKEN")
if not ACCESS_TOKEN:
    raise EnvironmentError("ZENODO_TOKEN não encontrado. Crie um arquivo .env com ZENODO_TOKEN=seu_token")

# Configure API URL - use sandbox as default
ZENODO_API_URL = os.getenv("ZENODO_API_URL", "https://zenodo.org/api/deposit/depositions")

print(f"Usando URL da API: {ZENODO_API_URL}")
print(f"Token {'encontrado' if ACCESS_TOKEN else 'NÃO encontrado'}")

# Headers for API requests
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

# Tipos de submissão permitidos pela API do Zenodo
UPLOAD_TYPES = [
    'publication', 'poster', 'presentation', 'dataset', 'image',
    'video', 'software', 'lesson', 'physicalobject', 'other'
]

# --- FUNÇÕES DA API ---

def create_new_deposition():
    """Passo 1: Cria um novo rascunho (deposition) no Zenodo."""
    print(" PASSO 1: Criando novo rascunho no Zenodo...")
    try:
        response = requests.post(ZENODO_API_URL, headers=HEADERS, json={})
        response.raise_for_status()
        deposition_data = response.json()
        print(f"-> Sucesso! Rascunho criado com ID: {deposition_data['id']}")
        return deposition_data
    except requests.exceptions.HTTPError as err:
        print(f"!!! Erro HTTP ao criar rascunho ({err.response.status_code}): {err.response.text}")
        return None
    except json.JSONDecodeError:
        print("!!! Erro: Resposta inválida da API")
        return None

def upload_file(deposition_data, file_path):
    """Passo 2: Faz o upload de um arquivo para o 'bucket' do rascunho."""
    print(f"\n PASSO 2: Fazendo upload do arquivo '{os.path.basename(file_path)}'...")
    if not os.path.exists(file_path):
        print(f"!!! Erro: O arquivo '{file_path}' não foi encontrado.")
        return False
        
    bucket_url = deposition_data['links']['bucket']
    file_name = os.path.basename(file_path)
    
    try:
        with open(file_path, "rb") as fp:
            # Use bucket URL directly with auth token in headers
            response = requests.put(
                f"{bucket_url}/{file_name}", 
                data=fp,
                headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
            )
            response.raise_for_status()
        print("-> Sucesso! Upload do arquivo concluído.")
        return True
    except requests.exceptions.HTTPError as err:
        print(f"!!! Erro HTTP no upload do arquivo ({err.response.status_code}): {err.response.text}")
        return False
    except Exception as e:
        print(f"!!! Erro inesperado no upload: {str(e)}")
        return False

def add_metadata(deposition_data, metadata):
    """Passo 3: Adiciona os metadados ao rascunho."""
    print("\n PASSO 3: Adicionando metadados...")
    url = f"{ZENODO_API_URL}/{deposition_data['id']}"
    try:
        response = requests.put(
            url, 
            data=json.dumps({'metadata': metadata}), 
            headers=HEADERS
        )
        response.raise_for_status()
        print("-> Sucesso! Metadados adicionados.")
        return True
    except requests.exceptions.HTTPError as err:
        print(f"!!! Erro HTTP ao adicionar metadados ({err.response.status_code}): {err.response.text}")
        return False
    except Exception as e:
        print(f"!!! Erro inesperado ao adicionar metadados: {str(e)}")
        return False

def publish_deposition(deposition_data):
    """Passo 4: Publica o rascunho, tornando-o um registro permanente com DOI."""
    print("\n PASSO 4: Publicando o registro...")
    publish_url = deposition_data['links']['publish']
    try:
        response = requests.post(publish_url, headers=HEADERS)
        response.raise_for_status()
        published_record = response.json()
        print("-" * 50)
        print(" SUCESSO! Registro publicado.")
        print(f" DOI: {published_record.get('doi', 'DOI não disponível')}")
        print(f" Link: {published_record['links']['latest_html']}")
        print("-" * 50)
        return published_record
    except requests.exceptions.HTTPError as err:
        print(f"!!! Erro HTTP ao publicar ({err.response.status_code}): {err.response.text}")
        return None
    except json.JSONDecodeError:
        print("!!! Erro: Resposta inválida da API após publicação")
        return None

# --- FUNÇÕES DE PROCESSAMENTO ---

def process_file_for_upload(file_path, metadata, archive_folder_path):
    """
    Orquestra o processo de upload de um único arquivo para o Zenodo,
    incluindo a movimentação para o arquivo após o sucesso.
    """
    print("\n--- INICIANDO PROCESSO DE UPLOAD ---")
    print(f"Arquivo: {file_path}")
    print(f"Metadados: {json.dumps(metadata, indent=2, ensure_ascii=False)}")

    # Executa a sequência de passos da API
    rascunho = create_new_deposition()
    if rascunho:
        if upload_file(rascunho, file_path):
            if add_metadata(rascunho, metadata):
                print("\nO rascunho foi criado e os dados enviados com sucesso.")
                # No fluxo atual, publicamos imediatamente a primeira versão
                published_record = publish_deposition(rascunho)
                if published_record:
                    doi = published_record.get('doi')
                    if doi:
                        print(f"DOI obtido: {doi}")

                        # --- Lógica de Modificação do Arquivo Local e Versionamento ---
                        print(f"\n--- Próximos Passos (Ainda Não Implementados) ---")
                        print(f"1. Tentar incluir o DOI ({doi}) no arquivo local original: {file_path}")
                        print("   !!! NOTA: A modificação automática de PDF é complexa e requer bibliotecas adicionais.")
                        print("   !!! Alternativas: renomear o arquivo local, criar um arquivo .txt com o DOI, ou atualizar a fonte do documento.")
                        print(f"2. Se a modificação for bem-sucedida, criar uma NOVA VERSÃO do depósito ID {rascunho['id']} via API.")
                        print("3. Uploadar o arquivo LOCAL MODIFICADO (com DOI) para esta nova versão.")
                        print("4. Publicar a NOVA VERSÃO.")
                        print("--------------------------------------------------")
                        # --- Fim Lógica de Modificação/Versionamento ---


                    # --- Mover e Renomear o arquivo processado para o arquivo ---
                    try:
                        # Verifique se o arquivo original ainda existe antes de mover
                        if os.path.exists(file_path):
                            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                            original_filename = os.path.basename(file_path)
                            new_filename = f"{timestamp}_{original_filename}"
                            destination_path = os.path.join(archive_folder_path, new_filename)

                            print(f"\nMovendo arquivo para arquivo: {original_filename} -> {destination_path}")
                            shutil.move(file_path, destination_path)
                            print("-> Arquivo movido com sucesso.")

                            # Opcional: Remover o arquivo metadata.json associado na pasta de origem
                            # Supondo que o metadata.json está na mesma pasta do arquivo original
                            metadata_file_path = os.path.join(os.path.dirname(file_path), "metadata.json")
                            if os.path.exists(metadata_file_path):
                                 print(f"Removendo arquivo de metadados: {metadata_file_path}")
                                 os.remove(metadata_file_path)
                        else:
                            print(f"!!! Aviso: Arquivo original não encontrado para mover para o arquivo: {file_path}")


                    except Exception as e:
                        print(f"!!! Erro ao mover o arquivo para o arquivo: {e}")


                else:
                    print("Falha ao publicar o registro.")

            else:
                print("Falha ao adicionar metadados.")
        else:
            print("Falha no upload do arquivo.")
    else:
        print("Falha ao criar novo rascunho.")

# --- FUNÇÕES DE INTERAÇÃO COM O USUÁRIO (mantidas para o modo interativo existente) ---

def get_user_inputs():
    """Coleta os dados do usuário de forma interativa."""

    # Caminho do Arquivo
    file_path = ""
    while not os.path.exists(file_path):
        file_path = input("? Digite o caminho completo para o arquivo: ")
        if not os.path.exists(file_path):
            print("! Arquivo não encontrado. Tente novamente.")

    # Título
    title = input("? Título da publicação: ")

    # Descrição
    description = input("? Descrição/resumo: ")

    # Criadores
    creators = []
    while True:
        creator_name = input("? Nome do criador (ex: Silva, João da). Deixe em branco para finalizar: ")
        if not creator_name:
            break
        affiliation = input(f"? Afiliação de '{creator_name}': ")
        creators.append({'name': creator_name, 'affiliation': affiliation})

    # Tipo de Upload
    print("\nSelecione o tipo de submissão:")
    for i, type_name in enumerate(UPLOAD_TYPES):
        print(f"  [{i+1}] {type_name}\n", end="") # Use end="" to avoid extra newline

    choice = 0
    while not (1 <= choice <= len(UPLOAD_TYPES)):
        try:
            choice = int(input(f"? Escolha uma opção [1-{len(UPLOAD_TYPES)}]: "))
        except ValueError:
            print("! Entrada inválida. Digite o número correspondente.")
            pass # Keep looping

    upload_type = UPLOAD_TYPES[choice - 1]

    # Adicionando licença CC BY 4.0 por padrão
    metadata = {
        'title': title,
        'upload_type': upload_type,
        'description': description,
        'creators': creators,
        'access_right': 'open', # Defaulting to open access
        'license': 'cc-by-4.0' # Setting default license
    }


    return {
        'file_path': file_path,
        'metadata': metadata
    }


# --- FUNÇÃO PRINCIPAL ---

def main():
    """Configura e executa o modo CLI ou o modo de monitoramento de pasta."""
    parser = argparse.ArgumentParser(description="Script para automatizar uploads no Zenodo.")
    parser.add_argument("--file", help="Caminho do arquivo para upload.")
    parser.add_argument("--title", help="Título da publicação.")
    parser.add_argument("--desc", help="Descrição da publicação.")
    # Permite múltiplos criadores: --creator "Silva, J" --creator "Souza, M"
    parser.add_argument("--creator", action='append', help="Criador no formato 'Nome, Sobrenome'. Use múltiplos para adicionar mais de um.")
    parser.add_argument("--type", choices=UPLOAD_TYPES, help="Tipo de publicação.")
    # Adicionado argumento para ativar o modo de monitoramento de pasta
    parser.add_argument("--monitor", action='store_true', help="Ativa o modo de monitoramento da pasta 'upload_queue'.")


    args = parser.parse_args()

    # Defina o caminho da pasta de monitoramento (magic folder)
    upload_queue_folder = os.path.join(os.path.dirname(__file__), "upload_queue")
    # Defina o caminho da pasta de arquivos enviados
    archive_folder_path = os.path.join(os.path.dirname(__file__), ARCHIVE_FOLDER)

    # Certifique-se de que a pasta de arquivos enviados exista
    os.makedirs(archive_folder_path, exist_ok=True)

    # Modo CLI (se --file e outros argumentos forem fornecidos)
    if args.file and args.title and args.creator and args.type:
        print("Modo não-interativo (via argumentos de linha de comando) detectado.")
        user_data = {
            'file_path': args.file,
            'metadata': {
                'title': args.title,
                'upload_type': args.type,
                'description': args.desc or "N/A",
                'creators': [{'name': name, 'affiliation': ''} for name in args.creator],
                'access_right': 'open', # Defaulting to open access for CLI mode
                'license': 'cc-by-4.0' # Setting default license for CLI mode
            }
        }
        process_file_for_upload(user_data['file_path'], user_data['metadata'], archive_folder_path)

    # Modo Monitoramento de Pasta (se --monitor for ativado)
    elif args.monitor:
        print(f"Iniciando monitoramento da pasta mágica: {upload_queue_folder}")
        # !!! IMPLEMENTAÇÃO DO WATCHDOG VIRÁ AQUI !!!
        # Por enquanto, processa arquivos existentes e depois fica inativo ou espera por nova implementação.
        print("!!! A funcionalidade de monitoramento em tempo real com 'watchdog' não está totalmente implementada nesta versão. !!!")
        print("!!! O script irá apenas processar arquivos .pdf existentes na pasta 'upload_queue' e sair. !!!")


        # Processar arquivos existentes na pasta 'upload_queue' (exemplo simples)
        files_in_queue = [f for f in os.listdir(upload_queue_folder) if f.lower().endswith('.pdf') and not f.startswith('.')] # Only process PDFs, ignore hidden files
        if not files_in_queue:
            print(f"Nenhum arquivo .pdf encontrado na pasta de monitoramento '{upload_queue_folder}'.")

        for filename in files_in_queue:
            file_path_to_process = os.path.join(upload_queue_folder, filename)
            metadata_file_path = os.path.join(upload_queue_folder, "metadata.json") # Assumes metadata.json is generated here

            print(f"\nProcessando arquivo: {file_path_to_process}")

            # --- Gerar Metadados via Fabric (Etapa que você já implementou externamente) ---
            # Esta parte conceitualmente chama seu comando fabric.
            # Exemplo (descomente e ajuste conforme sua configuração):
            # try:
            #     print(f"Executando comando fabric para gerar metadados para {filename}...")
            #     # Assumes 'fabric' command is in your PATH
            #     # Assumes 'create_zenodo_json' is the task name in your tasks.py/fabfile.py
            #     # You might need to pass file_path_to_process to your fabric task
            #     subprocess.run(['fabric', '-ps', 'create_zenodo_json', file_path_to_process], 
            #                    stdout=open(metadata_file_path, 'w'), check=True)
            #     print("Comando fabric executado com sucesso.")
            # except FileNotFoundError:
            #     print("!!! Erro: Comando 'fabric' não encontrado. Certifique-se de que o fabric esteja instalado e acessível no PATH.")
            #     continue # Skip this file
            # except subprocess.CalledProcessError as e:
            #     print(f"!!! Erro ao executar comando fabric: {e}")
            #     print("!!! Verifique sua tarefa 'create_zenodo_json' e a saída gerada.")
            #     continue # Skip this file
            # except Exception as e:
            #      print(f"!!! Erro inesperado ao chamar fabric: {e}")
            #      continue # Skip this file

            # --- Carregar metadados do arquivo JSON gerado ---
            # Adicionado um pequeno delay para garantir que o arquivo metadata.json seja salvo após a chamada externa do fabric
            time.sleep(1) # Adjust delay if needed

            try:
                with open(metadata_file_path, 'r', encoding='utf-8') as f:
                    metadata_from_file = json.load(f)
                # Garantir que a licença seja CC BY 4.0, sobrescrevendo se necessário
                metadata_from_file['license'] = 'cc-by-4.0'
                print("Metadados carregados e licença definida para CC BY 4.0.")
            except FileNotFoundError:
                print(f"!!! Erro: metadata.json não encontrado para {filename} após a chamada do fabric. Pulando este arquivo.")
                continue # Skip this file
            except json.JSONDecodeError:
                print(f"!!! Erro: metadata.json inválido para {filename}. Verifique o conteúdo gerado pelo fabric. Pulando este arquivo.")
                continue # Skip this file
            except Exception as e:
                 print(f"!!! Erro inesperado ao carregar metadados: {e}. Pulando este arquivo.")
                 continue # Skip this file


            # --- Processar o arquivo e metadados ---
            process_file_for_upload(file_path_to_process, metadata_from_file, archive_folder_path)

        print("\nProcessamento de arquivos existentes na pasta de monitoramento concluído.")
        print("Para monitoramento contínuo, a implementação com 'watchdog' é necessária.")


    # Modo Interativo (se nenhum argumento for fornecido)
    else:
        print("Iniciando modo interativo...")
        user_data = get_user_inputs()
        process_file_for_upload(user_data['file_path'], user_data['metadata'], archive_folder_path)


if __name__ == '__main__':
    main()