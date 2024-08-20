import os
import re
from bs4 import BeautifulSoup
from time import sleep
from datetime import date, timedelta, datetime
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


service_chrome = Service(ChromeDriverManager().install())

driver = webdriver.Chrome(service=service_chrome)
driver_wait = WebDriverWait(driver, 20)

base_path = "data/years"
current_data = date.today()
current_year = current_data.year

"""
    Data relativa a ultima atualização dos dados de 2024 dos dados do: https://portal.inmet.gov.br/dadoshistoricos
    A data precisa escrita separados por '-'
"""
last_updated_date = '31-07-2024' 

# Ler os arquivos de acordo com o ano atual
path_of_current_year = os.path.join(base_path, str(current_year))

# Ler os arquivos de acordo com a região
def get_folder_region(path: str, region: str) -> str:
    current_path = os.path.join(path, region)
    if os.path.exists(current_path):
        return current_path
    else:
        print(f"A pasta {current_path} não existe. Caso o problema persista, rode o arquivo 'config.py'.")
    return None

# Ler os arquivos de acordo com o estado
def get_folder_state(path: str, state: str) -> str:
    current_path = os.path.join(path, state)
    if os.path.exists(current_path):
        return current_path
    else:
        print(f"A pasta {current_path} não existe. Caso o problema persista, rode o arquivo 'config.py'.")
    return None

# Ler a formatação dos arquivos (Usar regex para pegar: CODIGO_ESTACAO, NOME, ULTIMA_DATA)
def parse_filename(filename: str):
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

# Coletar dados atuais do INMET
def collect_current_inmet_data(path: str):
    regions = os.listdir(path)
    last_date = datetime.strptime(last_updated_date, '%d-%m-%Y').date() + timedelta(days=1)
    
    for region in regions:
        path_states = os.path.join(path, region)
        states = os.listdir(path_states)
        
        for state in states:
            path_files_datas = os.path.join(path_states, state)
            files_datas = os.listdir(path_files_datas)
            
            for file_path_name in files_datas:
                file_info = parse_filename(file_path_name)
                
                if file_info:
                    station_code = file_info['station_code']
                    station_name = file_info['station_name']
                    end_date = file_info['end_date']
                    
                    current_URL = f'https://tempo.inmet.gov.br/TabelaEstacoes/{station_code}'
                    
                    driver.get(current_URL)

                    if (last_date > current_data):
                        last_date = end_date
                    
                    try:    
                        button_menu = driver_wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[1]/div[1]/i')))

                        sleep(1)
                        button_menu.click()
                        
                        input_started_date = driver_wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/div[1]/div[2]/div[4]/input')))
                        
                        input_started_date.send_keys(last_date.strftime('%d-%m-%Y'))
                        
                        button_generate_table = driver_wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[2]/div[1]/div[2]/button')))
                        
                        button_generate_table.click()
                        
                        main_table = driver_wait.until(EC.visibility_of_element_located((By.TAG_NAME, 'table')))
                        
                        browser = driver.page_source
                        
                        page_content = BeautifulSoup(browser, 'html.parser')
                        
                        # table = page_content.find('table', attrs={'class':'ui blue celled striped unstackable table'})
                        
                        # table_body = table.find('tbody', attrs={'class':'tabela-body'})
                        # table_rows = table_body.find_all('tr', attrs={'class':'tabela-row'})
                        # rows = table_body.find_all('td')
                        
                        # print(table_body.prettify())
                        # print("===========================")
                        # print(table_rows)
                        
                        # for row in rows:
                        #     print(row.text)
                        # sleep(5)
                        # break;
                        print(f">> Dados da estacao {station_code} - {station_name} foram extraidos com sucesso!\n")
                    except TimeoutException:
                        print(f"[ERROR] Nao foi possivel extrair os dados da estacao: {station_code} - {station_name}")
                    print("Extraindo proxima estacao...\n")
        
    
# Reescrever os meus dados de acordo com os a coleta de dados
# Salvar o meu arquivo para a data atual de alteração do arquivo(current_data)
# Repitir o processo de hora em hora

"""
    ATENÇÃO!!!
    MELHORAR O SISTEMA DE TIME PARA ENCONTRAR OS ELEMENTOS! ELES PODEM DAR CONFITOS!
"""

collect_current_inmet_data(path_of_current_year)