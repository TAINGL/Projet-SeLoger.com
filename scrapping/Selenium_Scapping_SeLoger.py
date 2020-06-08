# -*- coding: utf-8 -*-

import time
import pandas as pd
import numpy as np
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
import selenium.webdriver.support.ui as ui
import requests # to sent GET requests
import urllib.request
import urllib.parse


def generate_number_delay(mean = 4, sigma = 0.8):
    """
    Retourne un chiffre aléatoire suivant une distribution normal de moyenne 4 secondes et d'écart type de 0.8
    Ce chiffre aléatoire est le délai après chaque clic. Le but est de simuler le comportement d'un humain:
    un délai fixe peut attirer l'attention des contrôleurs, tout comme un délai aléatoire d'une distribution uniforme
    """
    delay = np.random.normal(mean,sigma,1)[0]
    if delay < 0.2: # relancer si inférieur à 0.2
        delay = np.random.normal(mean,sigma,1)[0]
        return delay
    else:
        return delay
    

# dictionnaire: en clé, le nom de la colonne de la dataframe, en valeurn leur xpath, class ou selecteur css sur le site internet

d_xpath = {'sl_style': '//*[@id="root"]/div/main/div[3]/div[2]/div[1]/div[1]/div[3]/div[2]/div[1]/div[1]',
'sl_nb_piece':'//*[@id="root"]/div/main/div[3]/div[2]/div[1]/div[1]/div[3]/div[2]/div[3]/div[1]/div[2]',
'sl_nb_chambre':'//*[@id="root"]/div/main/div[3]/div[2]/div[1]/div[1]/div[3]/div[2]/div[3]/div[2]/div[2]',
'sl_taille':'//*[@id="root"]/div/main/div[3]/div[2]/div[1]/div[1]/div[3]/div[2]/div[3]/div[3]/div[2]',
'sl_prix':'//*[@id="root"]/div/main/div[3]/div[2]/div[1]/div[1]/div[3]/div[2]/div[2]/div/span/span',
'sl_paragraphe':'//*[@id="showcase-description"]/div[1]/div/div/div[1]/p',
'sl_salle_d_eau': "//li[text()[contains(.,'eau')]]",
'sl_salle_de_bain': "//li[text()[contains(.,'bain')]]",
'sl_toilette': "//li[text()[contains(.,'Toilette')]]",
'sl_annee': "//li[text()[contains(.,'construction')]]",
'sl_etage': "//li[text()[contains(.,'Au')]]",
'sl_hauteur' : "//li[text()[contains(.,'Bâtiment de')]]",
'sl_ascenseur' : "//figcaption[text()[contains(.,'Ascenseur')]]",
'sl_vue' : "//figcaption[text()[contains(.,'Vue')]]",
'sl_cave' : "//figcaption[text()[contains(.,'Cave')]]",
'sl_parking' : "//figcaption[text()[contains(.,'Parking')]]",
'sl_chemine' : "//li[text()[contains(.,'Cheminée')]]",
'sl_exposition' : "//figcaption[text()[contains(.,'Orientation')]]",
'sl_balcon' : "//figcaption[text()[contains(.,'Balcon')]]",
'sl_terrasse' : "//figcaption[text()[contains(.,'Terrasse')]]",
'sl_gardien' : "//figcaption[text()[contains(.,'Gardien')]]",
'sl_travaux' : "//li[text()[contains(.,'travaux')]]",
'sl_neuf' : "//li[text()[contains(.,'neuf')]]",
'sl_parquet' : "//li[text()[contains(.,'Parquet')]]",
'sl_cuisine' : "//li[text()[contains(.,'uisine')]]",
'sl_vis_a_vis' : "//li[text()[contains(.,'vis à vis')]]",
'sl_jardin' : "//li[text()[contains(.,'Jardin')]]",
'sl_piscine' : "//li[text()[contains(.,'Piscine')]]",

'bd_nb_piece': "//li[text()[contains(.,'Pièces')]]",
'bd_nb_chambre':"//li[text()[contains(.,'Chambre')]]",
'bd_taille':'/html/body/nav/ol/li[6]/span',
'bd_prix': "//p[text()[contains(.,'€')]]",
'bd_paragraphe':'//*[@id="wrapper"]/div[1]/div/div[2]/div[3]/p[1]',
'bd_salle_d_eau': "//li[text()[contains(.,'eau')]]",
'bd_salle_de_bain': "//li[text()[contains(.,'bain')]]",
'bd_toilette': "//li[text()[contains(.,'Toilette')]]",
'bd_annee': "//li[text()[contains(.,'construction')]]",
'bd_etage': "//li[text()[contains(.,'Au')]]",
'bd_hauteur' : "//li[text()[contains(.,'Bâtiment de')]]",
'bd_ascenseur' : "//span[text()[contains(.,'Ascenseur')]]",
'bd_vue' : "//span[text()[contains(.,'vue')]]",
'bd_cave' : "//span[text()[contains(.,'Cave')]]",
'bd_parking' : "//span[text()[contains(.,'Parking')]]",
'bd_chemine' : "//span[text()[contains(.,'Cheminée')]]",
'bd_exposition' : "//span[text()[contains(.,'Orientation')]]",
'bd_balcon' : "//span[text()[contains(.,'Balcon')]]",
'bd_terrasse' :"//span[text()[contains(.,'Terrasse')]]",
'bd_gardien' :  "//span[text()[contains(.,'Gardien')]]",
'bd_travaux' : "//li[text()[contains(.,'travaux')]]",
'bd_neuf' : "//li[text()[contains(.,'neuf')]]",
'bd_parquet' : "//li[text()[contains(.,'Parquet')]]",
'bd_cuisine' : "//li[text()[contains(.,'uisine')]]",
'bd_vis_a_vis' : "//span[text()[contains(.,'vis à vis')]]",
'bd_jardin' : "//span[text()[contains(.,'Jardin')]]",
'bd_piscine' : "//span[text()[contains(.,'Piscine')]]"
}

d_class = {'bd_style': 'detailBannerInfosTypeBien',
'bd_localisation': 'js_locality'}

d_id = {'sl_localisation': 'summary-address'}


def update_dic(dic, column, d):
    """
    Met à jour le dictionnaire d à chaque fiche (cf boucle while plus bas)
    dic: dictionnaire, soit d_xpath, d_class_name
    column: nom de la colonne de la dataframe et de la clé du dictionnaire
    """
    if dic == d_xpath:
        try:
            d[column] = browser.find_element_by_xpath(dic[column]).text
        except NoSuchElementException:
            d[column] = 'Non reference'
    elif dic == d_class:
        try:
            d[column] = browser.find_element_by_class_name(dic[column]).text
        except NoSuchElementException:
            d[column] = 'Non reference'
    else :
        try:
            d[column] = browser.find_element_by_id(dic[column]).text
        except NoSuchElementException:
            d[column] = 'Non reference'
    return d


def aera_bd(dic, column, d):
    """
    Pour récupérer la surface en mètre carré (des annonces Belle Demeure)
    """
    if dic == d_xpath:
        try:
            d[column] = re.findall('\d+ M²',browser.find_element_by_xpath(dic[column]).text) 
            print('solution a')
        except NoSuchElementException:
            aera_xpath = "/html/body/nav/ol/li[5]/span"
            d[column] = re.findall('\d+ M²',browser.find_element_by_xpath(aera_xpath).text) 
            print('solution b')
        else:
            print('Non reference')
    return d


def localisation_bd(dic, column, d):
    """
    Pour récupérer la localisation (des annonces Belle Demeure)
    """
    if dic == d_class:
        try:
            d[column] = browser.find_element_by_class_name(dic[column]).text
            print('solution class')
        except:
            try: 
                localisation_xpath = "/html/body/div[2]/div/main/div[3]/div[2]/div[1]/div[1]/div[3]/div[2]/div[1]/div[2]"
                d[column] = browser.find_element_by_xpath(localisation_xpath).text 
                print('solution xpath1')
            except NoSuchElementException:
                localisation_xpath = "/html/body/div[2]/div/main/div[3]/div[2]/div[1]/div[1]/div[3]/div[2]/div[1]/div[3]"
                d[column] = browser.find_element_by_xpath(localisation_xpath).text 
                print('solution xpath2')
        else:
            print('Non reference')
    return d


def find_info_sl(dic, column, d):
    """
    Pour récupérer les informations supplémentaires des annonces Belle Demeure
    (là où il y a plusieurs solutions et points de récupération)
    """ 
    if dic == d_xpath:
        try:
            d[column] = browser.find_element_by_xpath(dic[column]).text 
            print('solution figcaption')
        except NoSuchElementException:
            try: 
                if column == 'sl_exposition':
                    exposition_xpath = "//li[text()[contains(.,'Orientation')]]"
                    d[column] = browser.find_element_by_xpath(exposition_xpath).text 
                    print('solution li')
                else:
                    column == 'sl_parking'
                    parking_xpath = "//li[text()[contains(.,'Parking')]]"
                    d[column] = browser.find_element_by_xpath(parking_xpath).text 
                    print('solution li')
        
            except NoSuchElementException:
                d[column] = 'Non reference'
                print('Non reference')
    return d


def find_info_bd(dic, column, d):
    """
    Pour récupérer les informations supplémentaires des annonces SeLoger
    (là où il y a plusieurs solutions et points de récupération)
    """ 
    if dic == d_xpath:
        try:
            d[column] = browser.find_element_by_xpath(dic[column]).text 
            print('solution span')
        except NoSuchElementException:
            try:
                if column == 'bd_exposition':
                    exposition_xpath = "//li[text()[contains(.,'Orientation')]]"
                    d[column] = browser.find_element_by_xpath(exposition_xpath).text 
                    print('solution li')
                else:
                    column == 'bd_vis_a_vis'
                    vis_xpath = "//li[text()[contains(.,'vis à vis')]]"
                    d[column] = browser.find_element_by_xpath(vis_xpath).text 
                    print('solution li')

            except NoSuchElementException:
                d[column] = 'Non reference'
                print('Non reference')
    return d


def returninfologement_sl(d):
    """
    Retourne un dictionnaire contenant toute les informations nécessaires pour les annonces
    SE LOGER
    """
    d = update_dic(d_xpath,'sl_style', d)
    d = update_dic(d_id,'sl_localisation', d)
    d = update_dic(d_xpath,'sl_nb_chambre', d)
    d = update_dic(d_xpath,'sl_taille', d)
    d = update_dic(d_xpath,'sl_nb_piece', d)
    d = update_dic(d_xpath,'sl_prix', d)
    d = update_dic(d_xpath,'sl_paragraphe',d)
    d = update_dic(d_xpath,'sl_salle_d_eau', d)
    d = update_dic(d_xpath,'sl_salle_de_bain', d)
    d = update_dic(d_xpath,'sl_toilette', d)
    d = update_dic(d_xpath,'sl_annee', d)
    d = update_dic(d_xpath,'sl_etage', d)
    d = update_dic(d_xpath,'sl_hauteur', d)
    d = update_dic(d_xpath,'sl_ascenseur', d)
    d = update_dic(d_xpath,'sl_vue', d)
    d = update_dic(d_xpath,'sl_cave', d)
    d = find_info_sl(d_xpath,'sl_parking', d)
    d = update_dic(d_xpath,'sl_chemine', d)
    d = find_info_sl(d_xpath,'sl_exposition', d)
    d = update_dic(d_xpath,'sl_balcon', d)
    d = update_dic(d_xpath,'sl_terrasse', d)
    d = update_dic(d_xpath,'sl_gardien', d)
    d = update_dic(d_xpath,'sl_travaux', d)
    d = update_dic(d_xpath,'sl_neuf', d)
    d = update_dic(d_xpath,'sl_parquet', d)
    d = update_dic(d_xpath,'sl_cuisine', d)
    d = update_dic(d_xpath,'sl_vis_a_vis', d)
    d = update_dic(d_xpath,'sl_jardin', d)
    d = update_dic(d_xpath,'sl_piscine', d)
    return d

def returninfologement_bd(d):
    """
    Retourne un dictionnaire contenant toute les informations nécessaires pour les annonces
    BELLE DEMEURE
    """
    d = update_dic(d_class,'bd_style', d)
    d = localisation_bd(d_class,'bd_localisation', d)
    d = update_dic(d_xpath,'bd_nb_chambre', d)
    d = aera_bd(d_xpath,'bd_taille', d)
    d = update_dic(d_xpath,'bd_nb_piece', d)
    d = update_dic(d_xpath,'bd_prix', d)
    d = update_dic(d_xpath,'bd_paragraphe', d)
    d = update_dic(d_xpath,'bd_salle_d_eau', d)
    d = update_dic(d_xpath,'bd_salle_de_bain', d)
    d = update_dic(d_xpath,'bd_toilette', d)
    d = update_dic(d_xpath,'bd_annee', d)
    d = update_dic(d_xpath,'bd_etage', d)
    d = update_dic(d_xpath,'bd_hauteur', d)
    d = update_dic(d_xpath,'bd_ascenseur', d)
    d = update_dic(d_xpath,'bd_vue', d)
    d = update_dic(d_xpath,'bd_cave', d)
    d = update_dic(d_xpath,'bd_parking', d)
    d = update_dic(d_xpath,'bd_chemine', d)
    d = find_info_bd(d_xpath,'bd_exposition', d)
    d = update_dic(d_xpath,'bd_balcon', d)
    d = update_dic(d_xpath,'bd_terrasse', d)
    d = update_dic(d_xpath,'bd_gardien', d)
    d = update_dic(d_xpath,'bd_travaux', d)
    d = update_dic(d_xpath,'bd_neuf', d)
    d = update_dic(d_xpath,'bd_parquet', d)
    d = update_dic(d_xpath,'bd_cuisine', d)
    d = find_info_bd(d_xpath,'bd_vis_a_vis', d) 
    d = update_dic(d_xpath,'bd_jardin', d)
    d = update_dic(d_xpath,'bd_piscine', d)
    return d


def get_liste_link():
    """
    Retourne la liste de tout les objets selenium correspondant aux liens pour accéder aux annonces
    """
    elems = browser.find_elements_by_name('classified-link')
    tab_url = [elem.get_attribute("href") for elem in elems]
    return tab_url


def find_the_website(links):
    """
    Pour faire la redirection, collecter les informations selon si c'est une page
    SeLoger ou Belle Demeure
    """ 
    z = re.search('seloger.com', links)
    if z != None:
        return True
    else:
        return False 

def afficher_plus():
    """
    Pour cliquer sur le "Afficher Plus" afin de récupérer l'information sur les pages
    SeLoger
    """ 
    try:
        element = browser.find_element_by_xpath("//div[@class='Showcase__StyledShowMoreText-sc-1y4y37c-1 dGFayi']/div[2][contains(@class,'ShowMoreText__UIShowMoreContainer-sc-5ggbbc-1 gDEVQY')]")
        return element
        
    except NoSuchElementException:  
        #Certaines annonces ont un url "seloger" -> et en cliquant ce sont des annonces de Belles Demeures
        good_to_see_you()
        time.sleep(generate_number_delay())
        print('ok')

    finally:    
        print('Mauvais Xpath')


def good_to_see_you():
    """
    Pour scroller la page vers le bas (dans un paramètre défini) afin de voir l'information à récupérer sur 
    les annonces Belle Demeure
    """ 
    pixel_start = 3300
    pixel_end = 4500
    pas = 100
    for i in range(pixel_start, pixel_end, pas): 
        browser.execute_script("window.scrollTo(0, {});".format(i))



option = webdriver.ChromeOptions()
option.add_argument("--incognito")

####################### Lien à changer!!!!!!!!#########################
#Exemple = Paris 16
#url = 'https://www.seloger.com/list.htm?projects=2&types=1,2&natures=1&places=[{ci:750116}]&enterprise=0&qsVersion=1.0'

'''
Afin d’éviter d’être bloqué, on peut demander à notre robot de se présenter correctement,
comme un humain, en précisant un bon User_agent. 
Pour ne pas endommager le site et se comporter de façon plus “humaine”, 
on peut également demander à notre robot de patienter quelques secondes sur une page avant de passer à une autre. 
Enfin, à chaque passage, nous pouvons changer l’adresse IP du robot.
'''

# using Selenium and wants to use proxy IPs with Selenium 
def get_random_ua():
    random_ua = ''
    ua_file = 'ua_file.txt'
    try:
        with open(ua_file) as f:
            lines = f.readlines()
        if len(lines) > 0:
            prng = np.random.RandomState()
            index = prng.permutation(len(lines) - 1)
            idx = np.asarray(index, dtype=np.integer)[0]
            random_proxy = lines[int(idx)]
    except Exception as ex:
        print('Exception in random_ua')
        print(str(ex))
    finally:
        return random_ua

def get_proxy_from_file():
    f = open("proxy.txt","r") #opens file with name of "test.txt"
    for i in range(48):
        return f.read(i)
    f.close()   


user_agent = get_random_ua()
proxy = get_proxy_from_file()

headers = {
        'user-agent': user_agent,
        'referrer': 'https://google.com',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Pragma': 'no-cache',
    }

r = requests.get(url,headers=headers,proxies={'https': proxy})

delays = [7, 4, 6, 2, 10, 19]
delay = np.random.choice(delays)
time.sleep(delay)

service_args = [
    '--proxy={0}'.format(proxy),
    '--proxy-type=http',
    '--proxy-auth=user:password'
]
print('Processing..' + url)

browser = webdriver.Chrome(service_args=service_args)
browser.get(url)
browser.maximize_window()
time.sleep(3)


name_csv_1 = 'page_SeLoger_Paris16.csv'
name_csv_2 = 'page_BelleDemeure_Paris16.csv'

try:
    df_seloger = pd.read_csv(name_csv_1)
    df_bd = pd.read_csv(name_csv_2)
except:
    df_seloger = pd.DataFrame(columns=['sl_style', 'sl_localisation','sl_nb_chambre', 'sl_taille', 'sl_prix', 'sl_paragraphe',
    'sl_salle_d_eau', 'sl_salle_de_bain', 'sl_toilette', 'sl_annee','sl_etage', 'sl_hauteur', 'sl_ascenseur','sl_vue',
    'sl_cave','sl_parking', 'sl_chemine', 'sl_exposition','sl_balcon', 'sl_terrasse', 'sl_gardien', 'sl_travaux',
     'sl_neuf', 'sl_parquet', 'sl_cuisine','sl_vis_a_vis','sl_jardin', 'sl_piscine'])
    
    df_bd = pd.DataFrame(columns=['bd_style','bd_localisation','bd_nb_chambre','bd_nb_piece','bd_prix','bd_paragraphe',
    'bd_salle_d_eau','bd_salle_de_bain','bd_toilette', 'bd_annee', 'bd_etage', 'bd_hauteur', 'bd_ascenseur', 'bd_vue',
    'bd_cave','bd_parking', 'bd_chemine', 'bd_exposition','bd_balcon', 'bd_terrasse', 'bd_gardien', 'bd_travaux',
    'bd_neuf', 'bd_parquet', 'bd_cuisine','bd_vis_a_vis','bd_jardin', 'bd_piscine'])
page = True

while page:
    i = 0 # i est le compteur de lien des annonces par page
    while i<len(get_liste_link()): # parcours tout les liens de la page, tant que i est plus petit que le nombre de liens
        liste_element = get_liste_link() # nécessaire de mettre à jour cette liste dans la boucle car ses éléments sont périmés à chaque rafraichissement ou back
        print(liste_element[i]) # affiche l'élement qui va être cliqué
        print(i) # affiche l'élement qui va être cliqué

        # Au cas où y a un pop up
        try:
            time.sleep(0.5)
            WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_hj-f5b2a1eb-9b07_survey_invite_container"]/a'))).click()
            print('kill add')
        except:
            pass

        try:
            time.sleep(0.5)
            WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_hj-f5b2a1eb-9b07_survey_invite_container"]/div/div[3]/a'))).click()
            print('Non Merci')
        except:
            pass


        browser.execute_script("window.open('');") # Switch to the new window and open URL B
        browser.switch_to.window(browser.window_handles[1])
        browser.get(liste_element[i]) # Each url of list
        time.sleep(generate_number_delay())

        if find_the_website(liste_element[i]) == True:

            browser.execute_script("window.scrollTo(0, 1000);")
            element = afficher_plus()
            try:
                browser.execute_script("arguments[0].click();", element)
                d = {}
                d = returninfologement_sl(d)
                df_seloger = df_seloger.append(d, ignore_index=True)
                time.sleep(generate_number_delay())
                i+=1
                df_seloger.to_csv('name_csv_Paris_ls', index=False, encoding='utf-8') # sauvegarde, en cas de pépin, il sera inutile de tout scrapper depuis le début
                browser.back()
                time.sleep(generate_number_delay())

            except:
                good_to_see_you()
                time.sleep(generate_number_delay())
                d = {}
                d = returninfologement_bd(d)
                df_bd = pd.DataFrame(columns=['bd_style','bd_nb_chambre','bd_nb_piece','bd_prix','bd_paragraphe','bd_salle_d_eau','bd_salle_de_bain','bd_toilette', 'bd_annee', 'bd_etage'])
                df_bd = df_bd.append(d, ignore_index=True)
                time.sleep(generate_number_delay())
                i+=1
                df_bd.to_csv('name_csv_Paris_bd', index=False, encoding='utf-8') # sauvegarde, en cas de pépin, il sera inutile de tout scrapper depuis le début
                browser.back()
                time.sleep(generate_number_delay())
                print("Annonce Belle Demeure avec mauvais url")
        
        else:
            good_to_see_you()
            time.sleep(generate_number_delay())
            d = {}
            d = returninfologement_bd(d)
            df_bd = df_bd.append(d, ignore_index=True)
            time.sleep(generate_number_delay())
            i+=1
            df_bd.to_csv('name_csv_Paris_bd', index=False, encoding='utf-8') # sauvegarde, en cas de pépin, il sera inutile de tout scrapper depuis le début
            browser.back()
            time.sleep(generate_number_delay())
        
        browser.close() # Switch back to the first tab with URL A
        browser.switch_to.window(browser.window_handles[0])
        
        # break # to remove after, just for the demo

    # sort de la boucle une fois que tous les éléments de la page ne sont pas 
    # s'il reste des pages
    try:
        time.sleep(generate_number_delay())
        next_page = browser.find_element_by_link_text('Suivant')
        actions = ActionChains(browser)
        actions.move_to_element(next_page)
        actions.perform()
        next_page.click()
        time.sleep(generate_number_delay())
    
    except ElementClickInterceptedException:
        # Au cas où y a un pop up
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_hj-f5b2a1eb-9b07_survey_invite_container"]/div/div[3]/a'))).click()
        print('Non Merci_1')
        next = WebDriverWait(browser, 30).until(
                EC.presence_of_element_located((By.PARTIAL_LINK_TEXT,'Suivant')))
        next.click()

    except TimeoutException:
        page = False
        print("Toutes les pages ont été visité")
        #break