import os;
import re;
import requests;
import shutil;
from zipfile import ZipFile;
from datetime import date;

base_path = "data/years"

# Criar pastas para os anos se elas não existerem
def create_base_folders(base_path):
        if not (os.path.exists(base_path)):
            os.makedirs(base_path);
            print(f">> Pasta criadas com sucesso: {base_path}")

# Fazer o download dos dados do INMET
def download_inmet_data(base_path, years):
    print("============== Baixando Dados ================\n")
    
    for year in years:
        year_path = os.path.join(base_path, str(year))
        
        if not (os.path.exists(year_path)) or not (os.listdir(year_path)):
            current_url = f"https://portal.inmet.gov.br/uploads/dadoshistoricos/{year}.zip";
            response = requests.get(current_url);
            
            if (response.status_code == 200): # status OK
                zip_path = os.path.join(base_path, f"{year}.zip");
                
                with open(zip_path, 'wb') as file:
                    file.write(response.content);
                    print(f"Download {zip_path} concluido!")
                extract_file(base_path, year, zip_path);
            else:
                print(f"[ERROR] Falha ao tentar baixar o arquivo do ano {year}")
        else:
            print(f">> Arquivos ja baixados para o ano: {year}")
        
        organize_file(os.listdir(year_path), year_path)

            
    print(">> Downloads concluidos!")
    print("==============================================\n")
    
# Descompactar os arquivos ZIP
# Remover os arquivos ZIP
def extract_file(base_path, year, zip_path):
    extract_path = os.path.join(base_path, str(year))
    
    with ZipFile(zip_path, 'r') as zip_file:
        # Listar todos os arquivos e diretórios no ZIP
        zip_files = zip_file.namelist()
        
        # Verificar se há um diretório principal com o mesmo nome do ano
        if any(file.startswith(f"{year}/") for file in zip_files):
            # Extrair todos os arquivos do ZIP
            for file_info in zip_file.infolist():
                # Se o caminho do arquivo começa com o ano, extrai para o diretório do ano
                target_path = os.path.join(extract_path, os.path.relpath(file_info.filename, f"{year}/"))
                if file_info.is_dir():
                    os.makedirs(target_path, exist_ok=True)
                else:
                    with zip_file.open(file_info) as source, open(target_path, 'wb') as target:
                        shutil.copyfileobj(source, target)
        else:
            # Se não houver diretório principal, extrair diretamente no diretório do ano
            zip_file.extractall(extract_path)
        
        print(f"Arquivo extraído para {extract_path}\n")
    
    os.remove(zip_path)

def create_directory_region_state(path):
    if not (os.path.exists(path)):
        os.makedirs(path)
        
def parse_filename(filename):
    # Padrão revisado para capturar todos os detalhes
    pattern = r'^INMET_(\w{1,2})_(\w{2})_(\w{4})_([^_]+?)_(\d{2}-\d{2}-\d{4})_A_(\d{2}-\d{2}-\d{4})\.CSV$'
    
    match = re.fullmatch(pattern, filename)
    
    if match:
        return {
            'region': match.group(1),
            'state': match.group(2),
            'station_code': match.group(3),
            'station_name': match.group(4),
            'start_date': match.group(5),
            'end_date': match.group(6)
        }
    return None
     
        
def organize_file(file_list, base_path):
    for file in file_list:
        current_file_data = parse_filename(file)
        if current_file_data:
            # Define o caminho para os diretórios de região e estado
            region_dir = os.path.join(base_path, current_file_data['region'])
            state_dir = os.path.join(region_dir, current_file_data['state'])
            
            # Cria os diretórios se não existirem
            create_directory_region_state(state_dir)
            
            # Move o arquivo para o diretório apropriado
            src_path = os.path.join(base_path, file)
            dest_path = os.path.join(state_dir, file)
            shutil.move(src_path, dest_path)
        else:
            print(f'Nome de arquivo inválido: {file}')    


#Escolher um intervalo existente de acordo com a base de dados do inmet
current_year = date.today().year
years = range(2004, current_year + 1);

create_base_folders(base_path);
download_inmet_data(base_path, years);