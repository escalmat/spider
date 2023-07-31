
import sys
import codecs

sys.path.append( '/usr/local/lib/python3.6/dist-packages' )

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException, WebDriverException, InvalidSessionIdException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as exp_c
from selenium.webdriver.common.keys import Keys

from time import sleep

import mysql.connector as myc
from mysql.connector import Error

from unidecode import unidecode
from _item import item
from vehicle_specs import vehicle_specs

def seller(seller_xpath, driver):

    seller = None

    for xpath in seller_xpath:
    
        try:
            seller = driver.find_element( By.XPATH, xpath ).text 
        except NoSuchElementException:
            pass
        except StaleElementReferenceException:
            continue
        else:
            seller = seller.replace('\n', ' ')
            break

    return seller


def save_specifics(feature_name, feature_value, item_info, vspec):

    if feature_name == 'vMarca':
        vspec = vehicle_specs()
    
    specifics = {
        'Marca': lambda x: item_info.set_brand(x),
        'Línea': lambda x: item_info.set_line(x),
        'Nombre': lambda x: item_info.set_name(x),
        'Formatodelproducto': lambda x: item_info.set_format(x),
        'Tipodeenvase': lambda x: item_info.set_container_type(x),
        'Volumendelaunidad': lambda x: item_info.set_unit_volume(x),
        'Modelo': lambda x: item_info.set_model(x),
        'Versión': lambda x: item_info.set_version(x),

        'MemoriaRAM': lambda x: item_info.set_internal_memo(x),
        'RAM': lambda x: item_info.set_internal_memo(x),
        'Tamañodelapantalla': lambda x: item_info.set_screen_size(x),
        'Duracióndelabatería': lambda x: item_info.set_batery_span(x),
        'Tipoderesolución': lambda x: item_info.set_resolution_type(x),
        'Conpantallatáctil': lambda x: item_info.set_with_touch_screen(x),

        'vMarca': lambda x: vspec.set_brand(x),
        'vModelo': lambda x: vspec.set_model(x),
        'vAño': lambda x: vspec.set_year(x),
        'vColor': lambda x: vspec.set_color(x),
        'vTipodecombustible': lambda x: vspec.set_fuel(x),
        'vPuertas': lambda x: vspec.set_ndoors(x),
        'vTransmisión': lambda x: vspec.set_transmision(x),
        'vMotor': lambda x: vspec.set_engine(x),
        'vTipodecarroceria': lambda x: vspec.set_body_type(x),
        'vKilómetros': lambda x: vspec.set_kms(x)
    }


    feature_name_key = feature_name.replace(" ", "")

    specifics_keys = list( specifics.keys() )
    
    if not feature_name_key in specifics_keys:
        specifics[ feature_name_key ] = lambda x: item_info.set_extra_specs(x)        
        specifics[ feature_name_key ]( feature_name + " " + feature_value )
    else:
        specifics[ feature_name_key ]( feature_value )

    return item_info, vspec




def look_at_com_info_divs_to_find_title(comm_info_divs, title_xpaths):
    
    title = ''
    for comm_info_div in comm_info_divs:

        for xpath in title_xpaths:
        
            try:
                item_info.title = comm_info_div.find_element( By.XPATH, xpath ).text 
            except NoSuchElementException:
                pass
            except StaleElementReferenceException:
                pass
            except WebDriverException:
                pass
            else:
                if item_info.title == '' or item_info.title == None or item_info.title == ' ':
                    continue
                else:
                    title = item_info.title # FOR LATER: title should be VALIDATED against some keyword
                    return title

    return title




def item_info( titles_list, my_cursor, driver ):

    item_info = None
    prod_spec_cont_found = True

    commercial_info_divs_xpath = [ '//*[@id="root-app"]/div/div[4]/div/div[1]/div/div[1]/div/div',  # like cellphones
                                   '//*[@id="root-app"]/div[2]/div[3]/div[1]/div[1]/div/div[1]/div[2]/div', # like cellphones new
                                   '//*[@id="root-app"]/div/div[5]/div/div[1]/div/div[1]/div/div',
                                   '//*[@id="root-app"]/div/div[4]/div/div[1]/div[1]/div/div',                                 
                                   '//*[@id="root-app"]/div/div[3]/div/div[1]/div[1]/div/div',
                                   '//*[@id="root-app"]/div[2]/div[2]/div[1]/div[1]/div/div[1]/div[2]/div',
                                   '//*[@id="root-app"]/div/div[3]/div/div[1]/div/div[1]/div/div' ]
    
    state_and_nsales_xpath     = [ './div[1]/div[1]/span',
                                   './div/div[1]/span',
                                   './div/div[1]/p',
                                   './div/div[2]/span' ]
    
    title_xpath                = [ './div[1]/div[2]/h1',
                                   './div/div[3]/h1',
                                   './div/div[2]/h1' ]
    
    ml_category_rank_xpath     = [ './div[2]/a' ]
    
    price_xpath                = [ './div[2]/div/div[1]/span/meta',
                                   './div[1]/span[1]/meta',
                                   './div[1]/span/meta',
                                   './div/div[1]/span[1]/meta',
                                   './div/div[1]/span/meta',
                                   './div/div/span/meta' ]

    currency_type_xpath        = [ './div[2]/div/div[1]/span/span[2]',
                                   './div[1]/span[1]/span',
                                   './div[1]/span/span',
                                   './div/div[1]/span[1]/span',
                                   './div/div[1]/span/span',
                                   './div/div/span/span' ]
    
    seller_xpath               = [ '//*[@id="buybox-form"]/div[2]/div/div/div/div/a/span',
                                   '//*[@id="buybox-form"]/div[2]/div/div',
                                   '//*[@id="root-app"]/div[2]/div[2]/div[1]/div[2]/div/div[2]/div[1]/div/div[1]/div[2]/p',
                                   '//*[@id="root-app"]/div[2]/div[2]/div[1]/div[2]/div/div[2]/div[1]/div/div[1]/div[2]' ]

    # --------------------------------------------------------------------------------------------------------------------------------------

    specifics_container_xpath = [ '//*[@id="highlighted-specs"]',
                                  '//*[@id="highlighted-specs"]/div[2]/div',
                                  '//*[@id="root-app"]/div/div[3]/div/div[2]/div[2]/div[1]/div/div[1]/table/tbody',
                                  '//*[@id="root-app"]/div/div[4]/div/div[2]/div[2]/div[2]/div/div[1]/table/tbody',
                                  '//*[@id="root-app"]/div/div[3]/div/div[2]/div[2]/div[2]/div/div[1]/table/tbody' ]
    
    spec1 = [ './div[2]/div/div[2]/p/span[2]',                    # screen_size_xpath
             './div[1]/div[1]/div/div[2]/p/span' ]
    
    spec2 = [ './div[3]/div/div[1]/div[1]/div/div[2]/p/span[2]'   # internal_memo_xpath
             './div[1]/div[2]/div/div[2]/p/span' ]
    
    spec3 = [ './div[3]/div/div[2]/div[1]/div/div[2]/p/span[2]',  # mpx_frontal_cam_xpath
             './div[1]/div[3]/div/div[2]/p/span' ]
    
    spec4 = [ './div[3]/div/div[1]/div[2]/div/div[2]/p/span[2]',  # mpx_rear_cam_xpath
             './div[2]/div[1]/div/div[2]/p/span' ]
    
    spec5 = ['./div[2]/div[2]/div/div[2]/p/span' ]

    specifics_xpath = [ spec1,
                        spec2,
                        spec3,
                        spec4,
                        spec5 ]

    # --------------------------------------------------------------------------------------------------------------------------------------
 
    dialog_divs_xpath = [ '//*[@id="root-app"]/div[2]/div[2]/div[3]/div[1]/div[1]/div/div/div[3]/div/div',
                          '//*[@id="root-app"]/div/div[3]/div/div[2]/div[2]/div[4]/div[3]/div/div' ]

    # --------------------------------------------------------------------------------------------------------------
    
    item_info = item()
    node_no_found = True

    # comm_info_divs is found when ( commercial_info_divs_xpath: found AND title_xpath: found )
    
    for xpath in commercial_info_divs_xpath:
        
        try:
        
            commercial_info_divs = WebDriverWait( driver, 20 ).until( exp_c.presence_of_all_elements_located( ( By.XPATH, xpath ) ) )
                                                                                                              
        except TimeoutException:
            continue
        except StaleElementReferenceException:
            continue
        except InvalidSessionIdException:
            continue
        else:
            item_info.title = look_at_com_info_divs_to_find_title( commercial_info_divs, title_xpath )
            if item_info.title != '':
                node_no_found = False
                break

    if node_no_found:
        print(">>> CRITITAL ERROR: commercial info not found\n")
        return None, None   

    # ------------------------------ check if this TITLE was already processed -------------------------------------

    if item_info.title in titles_list:
        return None, None

    print( codecs.encode( ">>> title: {}".format( item_info.title ), encoding='utf-8' ) )

    # ------------------------------------ try to find STATE AND NSALES --------------------------------------------

    for comm_info_div in commercial_info_divs:
    
        for xpath in state_and_nsales_xpath:
        
            try:
                elm_text = comm_info_div.find_element( By.XPATH, xpath ).text
            except NoSuchElementException:
                continue
            except StaleElementReferenceException:
                continue
            else:

                if not 'Nuevo' in elm_text and not 'Usado' in elm_text and not 'Reacondicionado' in elm_text and not 'vendidos' in elm_text:
                    continue
                
                l = elm_text.split()
                
                if len( l ) == 0:
                    continue
                else:
      
                    if len(l) == 1:
                        item_info.state = l[0] 
                    elif len(l) == 2:
                        item_info.state = l[0]
   
                        try:
                            item_info.nsales = int(l[1])
                        except ValueError:

                            try:
                                item_info.nsales = int(l[0])
                            except ValueError:
                                pass
                            else:
                                item_info.state = None
                                break
                        
                    elif len(l) == 3:
                        continue
                    elif len(l) == 4:
                        item_info.state = l[0]
                        try:
                            item_info.nsales = int(l[2])
                        except ValueError:
                            break
                    else:
                        item_info.ad_date = l[-2] + ' ' + l[-1]
                
                    break

        if item_info.state is not None or item_info.nsales is not None:
            break
        
    print( codecs.encode( ">>> state: {}".format( item_info.state ), encoding='utf-8' ) )
    print( codecs.encode( ">>> nsales: {}".format( item_info.nsales ), encoding='utf-8' ) )
    print( codecs.encode( ">>> ad_date: {}".format( item_info.ad_date ), encoding='utf-8' ) )
    
   
    # ------------------------------------ try to find ML CATEGORY RANK --------------------------------------------
    """
    for xpath in ml_category_rank_xpath:
        
        try:
            item_info.ml_category_rank = commercial_info_divs[1].find_element( By.XPATH, xpath ).text.split()[0] 
        except NoSuchElementException:
            pass
        except StaleElementReferenceException:
            continue
        else:
            break
        
    print(">>> ml rank: ", item_info.ml_category_rank)
    """
    # ------------------------------------ try to find PRICE --------------------------------------------

    for index, xpath in enumerate( price_xpath ):

        for commercial_info in commercial_info_divs:

            try:    
                item_info.price = float( commercial_info.find_element( By.XPATH, xpath ).get_attribute('content'))
                curr_type = commercial_info.find_element( By.XPATH, currency_type_xpath[ index ] ).text
            except NoSuchElementException:
                pass
            except StaleElementReferenceException:
                pass
            except ValueError:
                pass
            else:
                if 'pesos' in curr_type or '$' in curr_type:
                    item_info.currency = 'ARS'
                elif 'dólares' in curr_type or 'u$s' in curr_type:
                    item_info.currency = 'USD'
                else:
                    print(">>> another currency type was found: ", curr_type)
                    
                break

        
    print( codecs.encode( ">>> price: {}".format(  item_info.price ), encoding='utf-8' ) )
    print( codecs.encode( ">>> currency: {}".format( item_info.currency ), encoding='utf-8' ) )
    # ------------------------------------ try to find SELLER --------------------------------------------

    item_info.seller = seller( seller_xpath, driver )
    """
    try:

        seller_profile = driver.find_element( By.XPATH, '//*[@id="seller_profile"]' )
        
    except NoSuchElementException:
        pass
    except StaleElementReferenceException:
        pass
    else:

        try:
            item_info.seller = seller_profile.find_element( By.XPATH, './div/div/a/h3' ).text
            item_info.seller = item_info.seller.replace('\n', ' ')
        except NoSuchElementException:
            pass
        except StaleElementReferenceException:
            pass

        try:
            seller_profile_divs = seller_profile.find_elements( By.XPATH, './ul/div' )
        except NoSuchElementException:
            pass
        except StaleElementReferenceException:
            pass
        else:
            for div in seller_profile_divs:
                
                if "Ubicación del vehículo" in div.text:
                    try:
                        item_info.location = div.find_element( By.XPATH, './div/p' ).text
                    except NoSuchElementException:
                        continue
                    except StaleElementReferenceException:
                        continue
                    else:
                        break
    """
    print( codecs.encode( ">>> seller: {}".format( item_info.seller ), encoding='utf-8' ) )
    print( codecs.encode( ">>> location: {}".format( item_info.location ), encoding='utf-8' ) )
    
    # -------------------------------------------- ID --------------------------------------------------

    item_info.set_id(my_cursor)

    # ------------------------------------ try to find SPECS ---------------------------------------------
    """
    xpath_index = 0
    vspec = None
    for xpath in specifics_container_xpath:
    
        try:
            specs_element = driver.find_element( By.XPATH, xpath )
        except NoSuchElementException:
            xpath_index += 1
        except StaleElementReferenceException:
            xpath_index += 1
            continue
        else:
            if xpath_index == 2 or xpath_index == 3:

                try:
                    tr_nodes = specs_element.find_elements( By.TAG_NAME, 'tr' )
                except NoSuchElementException:
                    continue
                except StaleElementReferenceException:
                    continue
                else:

                    for tr in tr_nodes:

                        try:
                            feature = tr.find_element( By.TAG_NAME, 'th' ).text.replace('"', '')
                            value   = tr.find_element( By.TAG_NAME, 'td' ).text
                        except NoSuchElementException:
                            continue
                        except StaleElementReferenceException:
                            continue
                        else:
                            if feature == 'Kilómetros':
                                
                                vnumber = value.split()[0]

                                try:
                                    value = int(vnumber)
                                except ValueError:
                                    print(">>> ERROR: couldn't cast kms")
                                    continue
                            
                                
                            item_info, vspec = save_specifics('extraspecs', value, item_info, vspec)
                            print(">>> feature: value ---> {}: {} ".format( feature, value ) )

                    try:
                        ram = driver.find_element( By.XPATH, '//*[@id="root-app"]/div/div[3]/div/div[2]/div[2]/div[2]/div/div[2]/ul[1]/li[1]/p/span' ).text
                        ram_value = driver.find_element( By.XPATH, '//*[@id="root-app"]/div/div[3]/div/div[2]/div[2]/div[2]/div/div[2]/ul[1]/li[1]/p' ).text
                    except NoSuchElementException:
                        continue
                    except StaleElementReferenceException:
                        continue
                    else:
                        ram_value = ram_value.replace(ram, 'extraspecs')
                        item_info, vspec = save_specifics('', value, item_info, vspec)
                        print(">>> feature: value ---> {}: {} ".format( ram, ram_value ) )
            else:
                                   
                for spec_xpaths in specifics_xpath:

                    for xpath in spec_xpaths:
                    
                        try:
                            spec_spans = specs_element.find_elements( By.XPATH, xpath )
                            if len(spec_spans) < 2:
                                continue
                        except NoSuchElementException:
                            pass
                        except StaleElementReferenceException:
                            continue
                        else:
                            print(">>> feature: value ---> {} {} ".format( spec_spans[0].text, spec_spans[1].text ) )
                            item_info, vspec = save_specifics(spec_spans[0].text, spec_spans[1].text, item_info, vspec)
            
    
        
    # ------------------------------------ try to find DIALOGS --------------------------------------------
    
    for xpath in dialog_divs_xpath:

        try:
    
            dialog_divs = driver.find_elements( By.XPATH, xpath )

        except NoSuchElementException:
            print("couldn't find an element of a dialog")
        except StaleElementReferenceException:
            continue
        else:

            for ddiv in dialog_divs:
        
                question = None
                answer = None
                date = None

                try:
                    question = ddiv.find_element( By.XPATH, './div[1]/span' ).text
                except NoSuchElementException:
                    print("couldn't find question of dialog")
                except StaleElementReferenceException:
                    continue
        
                try:
                    answer = ddiv.find_element( By.XPATH, './div[2]/div/div/span' ).text
                except NoSuchElementException:
                    print("couldn't find answer 1 of dialog")
                    
                    try:
                        answer = ddiv.find_element( By.XPATH, './div[2]/div/div/span[1]' ).text
                    except NoSuchElementException:
                        print("couldn't find answer of dialog")
                    except StaleElementReferenceException:
                        continue
                    
                except StaleElementReferenceException:
                    continue
                else:
                    if answer == '' or answer is None:
                        try:
                            answer = ddiv.find_element( By.XPATH, './div[2]/div/div/span[1]' ).text
                        except NoSuchElementException:
                            print("couldn't find answer of dialog")
                        except StaleElementReferenceException:
                            continue

                try:
                    date = ddiv.find_element( By.XPATH, './div[2]/div/span' ).text
                except NoSuchElementException:
                    print("couldn't find date of dialog")
                except StaleElementReferenceException:
                    continue

                dialog_elements = ( item_info.id, question, answer, date, None )

                item_info.set_dialog( dialog_elements )

    """
    # ------------------------------------------- MODEL --------------------------------------------------
    
    
    return item_info, None

            


def get_title_and_href_mr(title, href, a_text):

    title = unidecode(title)
    title_parts = title.split()
    title_parts_len = len(title_parts)
    part_match_counter_href = 0
    part_match_counter_a_text = 0

    for tp in title_parts:
        try:
           if tp.lower() in href or tp.lower().replace("s", "") in href:
               part_match_counter_href += 1

           if tp in a_text or tp.replace("s", "") in a_text:
               part_match_counter_a_text += 1
        except TypeError:
            return -1

    avg = ( ( part_match_counter_href / title_parts_len ) + ( part_match_counter_a_text / title_parts_len ) )  / 2

    return avg * 100
        
    

def get_products_href(driver, target):

    prods_href = []
    sections = []
    sections = driver.find_elements( By.TAG_NAME, 'section' )
    sec_counter = 0
    a_nodes = []
    li_nodes_counter = 0
    saved_mr = 0
    a_nodes_match_counter = 0
    
    print( codecs.encode( "\n>>> [{}] trying to collect href".format( target ), encoding='utf-8' ) )
    
    for s in sections:
        
        sec_counter += 1 
        nfails = 0
        ols = []
        
        try:
            ols = s.find_elements( By.TAG_NAME, 'ol' )
        except NoSuchElementException:
            print("no ol nodes found inside the current section")
            continue
        except StaleElementReferenceException:
            continue
        
        for ol in ols:
            
            lis = []
            try:              
                a_nodes = ol.find_elements( By.TAG_NAME, 'a' ) 
                            
            except NoSuchElementException:
                
                print("no 'a node' found inside the current section")
                continue
            except StaleElementReferenceException:
                continue
            
            else:
                a_nodes_match_counter = 0
                for a in a_nodes:
                    link = a.get_attribute('href')
                    text = a.text

                    match_rate = get_title_and_href_mr(target, link, text)
                    
                    if match_rate >= 0:
                        prods_href.append( link )
                        a_nodes_match_counter += 1
                        saved_mr = match_rate

                try:
                    li_nodes = ol.find_elements( By.TAG_NAME, 'li' )
                except NoSuchElementException:
                    pass
                except StaleElementReferenceException:
                    continue
                else:
                    li_nodes_counter += len( li_nodes )

    


    print( codecs.encode( ">>> [{}] number of a_nodes that matched {}% with {}: {} ".format( target, saved_mr, target, a_nodes_match_counter ), encoding='utf-8' ) )
    print( codecs.encode( ">>> [{}] number of li nodes: {} ".format( target, li_nodes_counter ), encoding='utf-8' ) )

    if ( a_nodes_match_counter >= 90 and a_nodes_match_counter <= 150 ) or li_nodes_counter >= 2:
        return prods_href
    else:
        return []
        
