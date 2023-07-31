
import sys
import codecs
import random
import datetime

sys.path.append( '/usr/local/lib/python3.6/dist-packages' )

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as exp_c
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException, InvalidArgumentException, ElementClickInterceptedException, ElementNotInteractableException, NoSuchWindowException, WebDriverException
from time import sleep

import mysql.connector as myc
from mysql.connector import Error

from unidecode import unidecode

from target_info import item_info, get_products_href
from sql import save_item_into_db
from _node_source import targets_container, node_source


ITEMS_UPDATE_THRESHOLD = 30 # in days
PARENT_NAME = 'Automoviles'
family_names = [ PARENT_NAME ]
PARENT_ID = 1784
TIME = 1
FAMILY_ID=5

DB_PASSW = 'Logsid83'


def right_name( source_name ):

    name_split = source_name.split('(')
    right_name = name_split[0]
    right_name = right_name.replace('\n', '')

    return right_name.strip()


def from_str_arr_to_str( arr, init, end ):
    s = ''

    for i in range( init, end ):

        s += arr[ i ] + ' '

    return s.strip()


def validate_child( arr_of_t_ids, parent_id, new_target_id, my_cursor ):

    possible_t_ids = ( from_str_arr_to_str( arr_of_t_ids, 1, len( arr_of_t_ids )  ),
                       from_str_arr_to_str( arr_of_t_ids, 0, len( arr_of_t_ids )  ),
                       new_target_id )

    print('')
    print(">>> validating target id ...")
    print('')

    for poss_target_id in possible_t_ids:
       
        try:
            my_cursor.execute( "SELECT id FROM targets_map WHERE parent_id={} AND name='{}'".format( parent_id, poss_target_id ) ) 
            child = my_cursor.fetchone() 
        except Error as e:
            print(">>> [ERROR] while selecting time data:", e)
            return ''
        else:
            if child is not None:
                print( codecs.encode( ">>> [validated] {} ".format( poss_target_id ), encoding='utf-8' ) )
                print('')
                
                return poss_target_id
            else:
                print( codecs.encode( ">>>             {}".format( poss_target_id ), encoding='utf-8' ) )

    print('')

    return ''

            


def id_target( driver, prev_title, pid, myc ):

    target_title_location = ['//*[@id="root-app"]/div/div/aside/div[1]/h1',       # target title cellphones, cars
                             '//*[@id="root-app"]/div/div[2]/aside/div[1]/h1',    # target title supermarket, cloths
                             '//*[@id="root-app"]/div/div[1]/aside/div[1]/h1']    # heladera, computacion

    for xpath in target_title_location:

        try:
            target_title_node = WebDriverWait( driver, 20 ).until( exp_c.presence_of_element_located( (By.XPATH, xpath) ) )
        except TimeoutException:
            print(">>> no target id found")
        else:

            if target_title_node.text is None:
                continue

            ttitle_clean = target_title_node.text.replace('\n', ' ')  # delete break line
            rtitle = ttitle_clean.replace(' en Supermercado', '')     # delete en Supermercado

            # check if current targe title in target_title_location has changed

            if prev_title[0] == ttitle_clean:
                
                new_xpath = xpath.replace('div[1]/h1', 'section[1]/a')

                try:
                    target_title_nodes = WebDriverWait( driver, 20 ).until( exp_c.presence_of_all_elements_located( (By.XPATH, new_xpath) ) )
                except TimeoutException:
                    print(">>> no new target id found")
                else:

                    for node in target_title_nodes:
                        try:
                            text_node = node.find_element( By.XPATH, './div/div' )
                        except StaleElementReferenceException:
                            return None, None
                        except NoSuchElementException:
                            return None, None
                        else:

                            if text_node.text is None:
                                continue

                            name_not_found = True

                            for name in prev_title:
                                if name == text_node.text:
                                    name_not_found = False
                                    break
                                
                            if name_not_found:
                                prev_title.append( text_node.text )
                                break # there's just one target id that's not in prev_title, if found no need to keep searching, so break


                    rtitle = validate_child( arr_of_t_ids=prev_title,
                                             parent_id=pid,
                                             new_target_id=text_node.text,
                                             my_cursor=myc )

                    if rtitle == '':
                        rtitle = None
                        

            return rtitle, ttitle_clean
            

    return None, None




def nresults( driver ):

    xpaths = [ '//*[@id="root-app"]/div/div[2]/aside/div[2]/span', '//*[@id="root-app"]/div/div[1]/aside/div[2]/span' ]
    nr = -1

    for xpath in xpaths:
    
        try:
            nr_node = WebDriverWait( driver, 20 ).until( exp_c.presence_of_element_located( (By.XPATH, xpath) ) )
        except TimeoutException:
            pass
        else:
            nr = nr_node.text

            if nr is not None:
                nr = nr.replace('resultados', '')
                nr = nr.replace('.', '')

                try:
                    nr = int( nr )
                except ValueError:
                    nr = -1
                    pass

            else:
                nr = -1

    return nr
            




def suitable_target_node_index(target_node_index, a_target_nodes):

    target_node_text     = None
    aux_t_node_index     = target_node_index
    empty_a_text_counter = 0
    
    print("")
    print("[suitable_target_node_index]: receiving index: {}".format( target_node_index ) )

    
    while True:
        """
        if empty_a_text_counter == len( a_target_nodes )-1:
            print("all a nodes text are empty")
            return -1, None
        """
                
        try:
                    
            target_node_text = a_target_nodes[ target_node_index ].text
                    
        except StaleElementReferenceException:
                    
            target_node_index += 1
            print("[suitable_target_node_index]: stale element found")
            if target_node_index == len( a_target_nodes )-1:
                print("[suitable_target_node_index]: no target to go to")
                return -1, None
                    
            continue
        """
        if target_node_text == '':
            target_node_index += 1
            empty_a_text_counter += 1
            continue
        """
                    
        break

    print("[suitable_target_node_index]: throwing index: {}".format( target_node_index ) )
    print("")

    return target_node_index, target_node_text





def save_items( items_parent_id, nitems, phref_list, current_brand, connection, my_cursor, driver, time ):
    
    href_processed_counter = 0
    titles_list = []
    no_err = False
    item_saved_counter = 0
    
    for href in phref_list:

        try:
            driver.get( href )
        except WebDriverException:
            continue            

        wait = WebDriverWait(driver, 3)
    
        item, vspec = item_info( titles_list, my_cursor, driver )

        if item is None:
            continue

        titles_list.append( item.title )
                
        item.brand = current_brand
        """
        no_err = _save_items_into_db( items_parent_id,
                                      nitems,
                                      connection,
                                      my_cursor,
                                      item )

        if no_err:
            item_saved_counter += 1

        if item_saved_counter == 10:
            break
            
        """
        
        save_item_into_db(parent_id=items_parent_id,
                          conn=connection,
                          my_cursor=my_cursor,
                          itinfo=item,
                          vspecs=None,
                          time=time)
        

        href_processed_counter += 1
                    
    print("----------------------------------------------")


    print( codecs.encode( ">>> [{}]: {} items saved".format( current_brand, href_processed_counter ), encoding='utf-8' ) )
    

    if href_processed_counter > 0:
        no_err = True
        
    
    return no_err




def _save_items_into_db( parent_id, nitems, conn, my_cursor, i ):

    query = "INSERT INTO items ( id, parent_id, title, price, nsales, nitems, state, seller, currency ) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s )"

    vals = ( i.id,
             parent_id,
             i.title,
             i.price,
             i.nsales,
             nitems,
             i.state,
             i.seller,
             i.currency )

    try:
        my_cursor.execute(query, vals)
        conn.commit()
    except Error as e:
        print("error in query while inserting a product", e)
        return False
    else:
        print("\n>>> [item saved]\n")
        return True




def insert_record_into_targets_map( target_id, ttitle, parent_id, nr, i_owner, target_title_processed, my_cursor, connection ):

    type_of_t = 'branch'
    
    # ASIGN target_id AND parent_id

    try:
        my_cursor.execute( "INSERT INTO targets_map( id, name, parent_id, nitems, items_owner, family_id ) VALUES( %s, %s, %s, %s, %s, %s  );",
                           ( target_id, ttitle, parent_id, nr, i_owner, FAMILY_ID ) )
        connection.commit()
    except Error as e:
        print(">>> [ERROR] while inserting target data:", e)
        return -4, target_id

    if i_owner:
        type_of_t = 'leaf'
        
    print( codecs.encode( "\n>>> new target-{} SAVED: [{}] ID: {} PID: {}\n".format( type_of_t, ttitle, target_id, parent_id ), encoding='utf-8' ) )

    target_id += 1

    target_title_processed[ ttitle ] = 1

    return 1, target_id



def print_targets_list( a_target_nodes, target_a_node_index ):

    print('')
    for n in range( len( a_target_nodes ) ):

        r_t_name = right_name( a_target_nodes[ n ].text )
                        
        if n == target_a_node_index:
            print( codecs.encode( "-> {}".format( r_t_name ), encoding='utf-8' ) )
        else:
            print( codecs.encode( "   {}".format( r_t_name ), encoding='utf-8' ) )



def check_target_name_src( target_title, url_text, parent_name ):

    if target_title == parent_name:

        if url_text != '' and url_text != ' ' and url_text is not None:
            return url_text
        else:
            return None
        
    else:
        return target_title



def check_last_time( target_data, my_cursor ):

    try:
        my_cursor.execute( "SELECT saved_at, time FROM items WHERE parent={} ORDER BY saved_at DESC LIMIT 1".format( target_data[0] ) ) 
        time_data = my_cursor.fetchone() 
    except Error as e:
        print(">>> [ERROR] while selecting time data:", e)
        return -1
    else:

        if time_data is not None:

            a = datetime.date.today()
            b = time_data[0].date()
            delta = a - b
            #print( delta.days )
            
            if delta.days >= ITEMS_UPDATE_THRESHOLD:

                if time_data[1] is None:
                    return 0

                if time_data[1] >= 0:
                    print('')
                    print(">>> [{}]'s items pass the UPDATE THRESHOLD: [time to set: {}]".format( target_data[0], time_data[1] + 1 ) )
                    print('')
                    return time_data[1]
                else:
                    print(">>> [{}][last time CRITICAL ERROR]".format( target_data[0] ) )
                    return -1
            else:
                # take care with BEBIDAS
                print('')
                print(">>> [{}]'s items didn't pass the UPDATE THRESHOLD. [{} days]".format( target_data[0], delta.days ) )
                print('')
                return -1  
            
        else:
            return 0 # target exist but its very first items are stored in an old table


def duplicate_arr( origin ):

    arr = []

    for e in origin:
        arr.append( e )

    return arr



def browse( prev_page, family_names, url_text, id_offset, parent_id, parent_name, from_target_container, target_title_processed, my_cursor, connection, driver ):

    _family_names = duplicate_arr( family_names ) # each func in memory as its own family_names 
    t_title_processed = {}

    target_id = id_offset
    pid = 0
    init_target_id_decrement = 0
    ntarget_a_nodes_found = 0

    bad_status_counter = 0
      
    a_processed = {}
    target_container_page = ''
    
    target_a_node_index = 0

    web_a_node_index = 0
    
    a_processed_keys = []
      
    new_target_title = False

    select_r = ()

    
    tprocessed = [ 'Cronos', 'Toro' ]




    target_title, current_title = id_target( driver,
                                             _family_names,
                                             parent_id,
                                             my_cursor )
    

    if target_title is not None:   # when processing brand, target_title is the same as its parent, so use other source if any
        


        target_name = check_target_name_src( target_title,  #src1
                                             url_text,      #src2
                                             parent_name )

        

        if target_name is None:
            target_title_processed[ str( random.random() ) ] = 1
            return -2, target_id


        if target_name in target_title_processed:
            
            print( codecs.encode( "\n>>> [{}] already processed\n".format( target_name ), encoding='utf-8' ) )
            return -7, target_id
        


        target_title_processed[ target_name ] = 1
        
        
            
        if target_name in tprocessed or 'Mostrar' in target_name:
            
            print( codecs.encode( "\n>>> [{}] rejected by program\n".format( target_name ), encoding='utf-8' ) )
            return -6, target_id

       
        

        try:
            my_cursor.execute( "SELECT id, name FROM targets_map WHERE ( name='{}' AND parent_id={} ) OR ( name='{}' AND parent_id={} ) ".format( target_name.replace("'", "''"), parent_id, target_name.replace(' ', '').replace("'", "''"), parent_id  ) ) 
            select_r = my_cursor.fetchone() 
        except Error as e:
            print(">>> [ERROR] while selecting target id:", e)
            return -5, target_id
        
        

        if select_r is not None:


            target_name = select_r[1]
                        

            print( codecs.encode("\n>>> [{}][{}] already in database\n".format( select_r[0], target_name ), encoding='utf-8' ) )


            targets_cont, target_type = targets_container( driver )
            

            if targets_cont is not None:

                pid = select_r[0]

                # save target container page

                target_container_page = driver.current_url

            else:

                last_time = check_last_time( select_r, my_cursor )  # check the last time we saved this item

                if last_time == -1:
                    return -9, target_id

                nr = nresults( driver )

                # save current nitems

                try:
                    my_cursor.execute( "INSERT INTO nitems (id, nitems, time) VALUES ( %s, %s, %s )", ( select_r[0], nr, last_time + 1 ) ) 
                    connection.commit()
                except Error as e:
                    print(">>> [ERROR] while inserting nitems:", e)
                    return -8, target_id
                    
                # ---------------------------------------------------- SAVE ITEMS ----------------------------------------------------------
                
                phref_list = get_products_href( driver, target_name )
                
                no_error = save_items(  select_r[0],
                                        nr,
                                        phref_list,
                                        target_name,
                                        connection,      
                                        my_cursor,
                                        driver,
                                        last_time + 1 )
                
                return 0, target_id

                
                

        else:
          
            print( codecs.encode("\n>>> [{}][{}] new target\n".format( target_id, target_name ), encoding='utf-8' ) )

            
            nr = nresults( driver )

            if nr == -1:
                print("[ERROR] no number of items found")

            targets_cont, target_type = targets_container( driver )
            
            i_owner = 1

            if targets_cont is not None:
                i_owner = 0

            current_t_id = target_id
            
            status, target_id = insert_record_into_targets_map( target_id,  # the unique function that modify target_id variable
                                                                target_name,
                                                                parent_id,
                                                                nr,
                                                                i_owner,
                                                                target_title_processed,
                                                                my_cursor,
                                                                connection )

            if status != -4 and not i_owner:

                pid = current_t_id

                # save target container page

                target_container_page = driver.current_url

            elif status != -4 and i_owner:

                # ---------------------------------------------------- SAVE ITEMS ----------------------------------------------------------
                
                phref_list = get_products_href( driver, target_name )
                
                no_error = save_items( current_t_id,
                                       nr,
                                       phref_list,
                                       target_name,
                                       connection,      
                                       my_cursor,
                                       driver,
                                       0 )

                return 1, target_id
                
            else:
                return status, current_t_id
   


    else:
        target_title_processed[ str( random.random() ) ] = 1
        return -2, target_id
                

            
    while True:

        targets_cont, target_type = targets_container( driver )

        if targets_cont is None:
            return 0, target_id

        try:
            
            a_target_nodes = targets_cont.find_elements(By.TAG_NAME, 'a')
                
        except NoSuchElementException:
                    
            try:
                targets_cont, target_type = targets_container(driver)
                a_target_nodes = targets_cont.find_elements(By.TAG_NAME, 'a')
            except StaleElementReferenceException:
                print("[{}]: CRITICAL ERROR: reference don't point to current a_nodes".format( target_node_index ) ) 
                return -3, target_id
            except NoSuchElementException:
                print("[{}]: CRITICAL ERROR: no [a nodes] found".format( target_node_index )  )
                return -3, target_id
                
        except StaleElementReferenceException:
            print("[{}]: CRITICAL ERROR: reference don't point to current a_nodes".format( target_node_index ) )
            return -3, target_id


        

        # check links NODE SOURCE
        
        a_target_nodes = node_source( a_target_nodes, driver )

        if a_target_nodes is None:

            return -3, target_id


        
            
        ntarget_a_nodes_found = len( a_target_nodes )

        if sum( list( t_title_processed.values() ) ) >= ntarget_a_nodes_found:  # >= cause when its go back to targets container a new target could show up
            
            print( codecs.encode( "\n>>> all targets processed for container: {}\n".format( target_title ), encoding='utf-8' ) )
            return 1, target_id
        


        # check NODES INDEX

        if target_a_node_index == ntarget_a_nodes_found:
            target_a_node_index = 0


                    

        # print TARGETS LIST 

        print_targets_list( a_target_nodes, target_a_node_index )

        try:

            r_t_name = right_name( a_target_nodes[ target_a_node_index ].text )

        except IndexError:

            return -7, target_id
            

        if r_t_name == 'Ver todos' or r_t_name == 'Otros' or r_t_name == codecs.encode( "{}".format( 'Mostrar más' ), encoding='utf-8' ):

            # pos. error scenario: t_title_processed's 1s < ntarget_a_nodes_found && target_a_node_index = ntarget_a_nodes_found - 1
            
            t_title_processed[ 'vto' ] = 1
            target_a_node_index += 1                       # solution
            print( t_title_processed.values() )
            continue
        


        this_func_url = driver.current_url

        

        # ---------------------------------------------------------------- GO to URL ----------------------------------------------------------------------

        click_attempt_counter = 0
        bad_clicks = True

        while click_attempt_counter < 10:

            if target_a_node_index == ntarget_a_nodes_found:
                break

            try:           
                            
                driver.execute_script("arguments[0].click();", a_target_nodes[ target_a_node_index ])  # attamp to click a target
                wait = WebDriverWait(driver, 20)
            
            except StaleElementReferenceException:
                
                print(">>> click element stale")
                target_a_node_index += 1
                
                continue

            except ElementClickInterceptedException:
                target_a_node_index += 1
                continue

            if this_func_url != driver.current_url:
                bad_clicks = False
                break
            
            else:

                try:
                    
                    a_target_nodes[ target_a_node_index ].click()
                    
                    wait = WebDriverWait(driver, 20)

                    if this_func_url != driver.current_url:
                        bad_clicks = False
                        break

                except StaleElementReferenceException:
                
                    print(">>> click element stale")
                    target_a_node_index += 1
                
                    continue
                    
                except ElementClickInterceptedException:
                    target_a_node_index += 1
                    pass

                except ElementNotInteractableException:
                    target_a_node_index += 1
                    t_title_processed[ str( random.random() ) ] = 1
                    continue
                   
            

        if bad_clicks:  # click 10 times and can't go to the target page
            
            print(">>> bad clicks")
            return -1, target_id
        

        # call function only if new document has loaded 

        status, target_id = browse( prev_page=this_func_url,
                                    family_names=_family_names, # do not modify _family_names
                                    url_text=r_t_name,
                                    id_offset=target_id,
                                    parent_id=pid,
                                    parent_name=target_title,
                                    from_target_container=True,
                                    target_title_processed=t_title_processed,
                                    my_cursor=my_cursor,
                                    connection=connection,
                                    driver=driver )

        
        print('')
        print( codecs.encode( "[STATUS]: {}".format( status ), encoding='utf-8' ) )
        print('')
        

        if status < 0:

            bad_status_counter += 1

            if bad_status_counter == 10:
                return -1, target_id
            
            

        driver.get( target_container_page ) 

        wait = WebDriverWait(driver, 20)

        target_a_node_index += 1


        
def get_target_nodes( driver, xpath ):

    try:
        target_node = WebDriverWait( driver, 20 ).until( exp_c.presence_of_element_located( (By.XPATH, xpath) ) )
    except TimeoutException:
        print(">>> no a_node found")
        return None

    if target_node is None:
        print(">>> no target to go")
        return None

    return target_node
        



            
chrome_options = Options()

chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-setuid-sandbox")
chrome_options.add_argument("--remote-debugging-port=9222")


driver = webdriver.Chrome( executable_path='/usr/bin/chromedriver', options=chrome_options )
driver.implicitly_wait(1)
URL = 'https://autos.mercadolibre.com.ar/fiat_NoIndex_True#unapplied_filter_id%3DBRAND%26unapplied_filter_name%3DMarca%26unapplied_value_id%3D67781%26unapplied_value_name%3DFiat%26unapplied_autoselect%3Dtrue'




try:
    connection = myc.connect( host="localhost",
                              database="internet_data",
                              user="root",
                              password=DB_PASSW )
    
    if connection.is_connected():
        server_info = connection.get_server_info()
        print(">>> connected to mysql server ", server_info)
        
        mycursor = connection.cursor(buffered=True)

        
except Error as e:
    
    print("error while connecting to mysql ", e)
    
else:
    target_title_processed = {}
    updated_target_id = 1
    status = 0
    last_id = 0

    driver.get( URL )

    wait = WebDriverWait(driver, 20)
          

    targets_cont, target_type = targets_container( driver )

    if targets_cont is not None:

        try:
            mycursor.execute( "SELECT id FROM targets_map ORDER BY id DESC LIMIT 1" ) 
            last_id = mycursor.fetchone() 
        except Error as e:
            print(">>> [ERROR] while selecting target id:", e)
        else:

            if last_id is not None:
                    
                status, updated_target_id = browse( prev_page=URL,
                                                    family_names=family_names,
                                                    url_text='',
                                                    id_offset=last_id[0] + 1,
                                                    parent_id=PARENT_ID,
                                                    parent_name=PARENT_NAME,
                                                    from_target_container=False,
                                                    target_title_processed=target_title_processed,
                                                    my_cursor=mycursor,
                                                    connection=connection,
                                                    driver=driver )

    try:
        driver.stop_client()
        driver.close()
        driver.quit()
    except NoSuchWindowException:
        pass
        

    """
    
    target_title_processed = {}
                    
    init_xpaths = [ '/html/body/main/div/div[3]/div/section/div/div/div[3]/a',
                    '/html/body/main/div/div[3]/div/section/div/div/div[4]/a',
                    '/html/body/main/div/div[2]/section/div/div/div[1]/a',
                    '/html/body/main/div/div[3]/div/section/div/div/div[2]/a',
                    '/html/body/main/div/div[3]/div/section/div/div/div[5]/a' ] 
                      
                        

    updated_target_id = 1
    status = 0
    last_id = 0

    for xpath in init_xpaths:

        driver.get( URL )

        wait = WebDriverWait(driver, 20)

        a_target_node = get_target_nodes( driver, xpath )

        if a_target_node is None:
            continue


        try:
            
            driver.execute_script("arguments[0].click();", a_target_node)
            
        except StaleElementReferenceException:
            
            print(">>> [2] stale element found while trying to click it")
            
            a_target_node = get_target_nodes( driver, xpath )

            if a_target_node is None:
                continue

            wait = WebDriverWait(driver, 20)

            if driver.current_url == URL:
                continue

        else:
            wait = WebDriverWait(driver, 20)
          

        targets_cont, target_type = targets_container( driver )

        if targets_cont is None:
            break


        try:
            mycursor.execute( "SELECT id FROM targets_map ORDER BY id DESC LIMIT 1" ) 
            last_id = mycursor.fetchone() 
        except Error as e:
            print(">>> [ERROR] while selecting target id:", e)
        else:

            if last_id is None:
                continue
                
        

        status, updated_target_id = browse( prev_page=URL,
                                            prev_title=PARENT_NAME,
                                            url_text='',
                                            id_offset=last_id[0] + 1,
                                            parent_id=PARENT_ID,
                                            parent_name=PARENT_NAME,
                                            from_target_container=False,
                                            target_title_processed=target_title_processed,
                                            my_cursor=mycursor,
                                            connection=connection,
                                            driver=driver )
    """


    print( codecs.encode( "\n[STATUS]: {}".format(status), encoding='utf-8' ) )
    
    try:
        connection.close()
    except Error as e:
        pass
            

            
