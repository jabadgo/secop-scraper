#SECOP Scraper
#Juan Pablo Abad Gomez
#github.com/jabadgo
#twitter.com/jabadgo
#https://sites.google.com/a/chromium.org/chromedriver/downloads


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import csv
import os
import pandas as pd
import numpy as np

#cambio de directorio
path = os.getcwd()+'\data'
os.chdir(path)

#Funcion para determinar un limite. Es importante seleccionar un limite porque el SECOP tiene miles de procesos y bajarlos todos haria que el tiempo de ejecucion sea demasiado largo
def set_limit():
    while True:
        try:
            limit = int(input("Por favor digite el maximo de procesos a buscar. Entre mas alto el limite, mayor el tiempo de ejecucion. \n Por favor escriba solo numeros \n"))
            break
        except ValueError:
            print("Por favor escriba solo numeros!")
    return limit


#la funcion que va a realizar la mayoria del trabajo
def Secop_scraper(url,xpath,query,limit):
    driver = webdriver.Chrome(path)
    data = []
    for i in query:
        urlwithQuery = 'https://community.secop.gov.co/Public/Tendering/ContractNoticeManagement/Index?Page=login&SkinName=CCE&requestStatus=50&currentLanguage=es-CO&Country=CO&allWords2Search='+i
        secop = urlwithQuery
        driver.get(secop)

        try:
            table = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME,'VortalGrid')))
            print('Tabla encontrada \n')
        except TimeoutException:
            print('Tabla no encontrada')

        row_count = len(driver.find_elements_by_xpath(xpath))
        #print(row_count)
        while True:
            try:
                button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'VortalGradualBindPaginatorButton')))
            except TimeoutException:
                break

            driver.execute_script("arguments[0].click();", button)
            time.sleep(1)

            try:
                WebDriverWait(driver, 10).until(lambda driver: len(driver.find_elements_by_xpath( xpath)) > row_count)
                time.sleep(1)
                row_count = len(driver.find_elements_by_xpath( xpath))
                for tr in driver.find_elements_by_xpath(xpath):
                    tds = tr.find_elements_by_tag_name('td')
                    data.append([td.text for td in tds])

                if row_count > limit:
                    print('Limite alcanzado. Total encontrado: %s procesos' % row_count)
                    break
            except TimeoutException:
                print('No existen mas filas. Total encontrado: ' + str(len(driver.find_elements_by_xpath( xpath))))
    return data


def write2csv(data): #Exportando a csv. Hace falta corregir el formato.
    while True:
        choice = input('\n\n Desea exportar la informacion como csv? (Y/N)\n')
        if choice.lower() in ('y','n'):
            if choice.lower() == 'y':
                with open("out.csv",'w') as f:
                    writer = csv.writer(f,delimiter=',')
                    writer.writerows(data)
            break
        else:
            print('Por favor escriba Y o N \n')
    return

def get_query():
    query = []

    def manual_query():
        while True:
            try:
                query_size = int(input('Cuantas palabras clave desea buscar? Escriba solo numeros.\n'))
                break
            except ValueError:
                print('Escriba solo numeros.\n')
        while True:
            if len(query) < query_size:
                while True:
                    try:
                        keyword = int(input('Escriba una palabra clave y presione Enter \n'))
                    except:
                        pass
                        break
                    else:
                        print('Escriba solo palabras.\n')
                query.append(keyword)
                print(len(query))
            else:
                break
        return query

    def auto_query():
        with open('query.txt',"r") as f:
            for line in f.readlines():
                li = line.lstrip()
                if not li.startswith("#"):
                    query.append(line.strip())
        return query

    while True:
        choice = input('Seleccione una opcion escribiendo A o B\n A. Escribir palabras clave\n B. Obtener las palabras clave del archivo "query" \n\n' )
        if choice.lower() in ('a','b'):
            if choice.lower() == 'a':
                    query = manual_query()
                    break
            else:
                query = auto_query()
                break
        else:
            print('Por favor escriba A o B para seleccionar una opcion.')

    return query


#Variables globales
url = 'https://community.secop.gov.co/Public/Tendering/ContractNoticeManagement/Index?currentLanguage=es-CO&Page=login&Country=CO&SkinName=CCE'
xpath = '//table[@class="VortalGrid"]/tbody/tr'

#Ejecucion de las funciones
limit = set_limit()
query = get_query()
data = Secop_scraper(url,xpath,query,limit)
write2csv(data)


input('Presione cualquier tecla para terminar.\nGracias por usar el programa.\n')


