from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException, InvalidArgumentException

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as exp_c


def targets_container(driver):

    targets_container = None
    target_type = None
    
    try:
        aside = WebDriverWait( driver, 20 ).until( exp_c.presence_of_element_located( (By.TAG_NAME, 'aside') ) )
    except TimeoutException:
        targets_container = None
        target_type = None
    else:

        try:
            aside_divs = aside.find_elements( By.TAG_NAME, 'div' )
        except NoSuchElementException:
            targets_container = None
            target_type = None
        except StaleElementReferenceException:
            targets_container = None
            target_type = None
        else:

            for div in aside_divs:
                if div.text == 'Modelo':
                    targets_container = div.find_element( By.XPATH, './..' )
                    target_type = 'Modelo'
                    return targets_container, target_type

            for div in aside_divs:
                if div.text == 'Año':
                    targets_container = div.find_element( By.XPATH, './..' )
                    target_type = 'Modelo'
                    return targets_container, target_type

            """
            for div in aside_divs:
                if div.text == 'Marca':
                    targets_container = div.find_element( By.XPATH, './..' )
                    target_type = 'Marca'
                    return targets_container, target_type

            for div in aside_divs:
                if div.text == 'Talle':
                    targets_container = div.find_element( By.XPATH, './..' )
                    target_type = 'Talle'
                    return targets_container, target_type
                
            
            for div in aside_divs:
                if div.text == 'Categorías':
                    targets_container = div.find_element( By.XPATH, './..' )
                    target_type = 'Categorías'
                    return targets_container, target_type           

            
            
            for div in aside_divs:
                if div.text == 'Marca':
                    targets_container = div.find_element( By.XPATH, './..' )
                    target_type = 'Marca'
                    return targets_container, target_type
                

            
            for div in aside_divs:
                if div.text == 'Serie':
                    targets_container = div.find_element( By.XPATH, './..' )
                    target_type = 'Serie'
                    return targets_container, target_type
                    
            

            for div in aside_divs:
                if div.text == 'Material del tapizado':
                    targets_container = div.find_element( By.XPATH, './..' )
                    target_type = 'Categorías'
                    return targets_container, target_type
                
            
            for div in aside_divs:
                if div.text == 'Cuerpos':
                    targets_container = div.find_element( By.XPATH, './..' )
                    target_type = 'Marca'
                    return targets_container, target_type
            """

            
                

    return targets_container, target_type




def invalid_node_counter( target_nodes ):

    counter = 0
    elm_error = False

    for target_node in target_nodes:

        try:
            
            if target_node.text == '' or target_node.text == ' ' or target_node.text == 'Ver todos' or target_node.text == 'Otros' or 'Mostrar' in target_node.text:
                counter += 1
                
        except StaleElementReferenceException:
            elm_error = True

        except NoSuchElementException:
            elm_error = True

    return counter


def node_source( target_nodes, driver ):

    counter = 0
    elm_error = False

    counter = invalid_node_counter( target_nodes )

    if counter == len( target_nodes ):

        targets_cont, target_type = targets_container( driver )

        target_nodes = targets_cont.find_elements(By.TAG_NAME, 'button')

        counter = invalid_node_counter( target_nodes )

        if counter == len( target_nodes ):

            target_nodes = None

    else:

        if elm_error:

            targets_cont, target_type = targets_container( driver )
            target_nodes = targets_cont.find_elements(By.TAG_NAME, 'a')

    return target_nodes

        

        
