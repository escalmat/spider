import sys
import codecs

sys.path.append( '/usr/local/lib/python3.6/dist-packages' )

import mysql.connector as myc
from mysql.connector import Error


def save_item_into_db(parent_id, conn, my_cursor, itinfo, vspecs, time):

    if itinfo is None:
        return

    query = """INSERT INTO items (  state,
                                    nsales,
                                    title,
                                    brand,
                                    ml_category_rank,
                                    price,
                                    model,
                                    id,
                                    seller,
                                    location,
                                    mpx_frontal_cam,
                                    mpx_rear_cam,
                                    screen_size,
                                    internal_memo,
                                    battery_span,
                                    resolution_type,
                                    with_touch_screen,
                                    extra_specs,
                                    parent,
                                    currency,
                                    ad_date,
                                    time )
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    
    vals = ( itinfo.state,            
             itinfo.nsales,         
             itinfo.title,           
             itinfo.brand,          
             itinfo.ml_category_rank, 
             itinfo.price,        
             itinfo.model,           
             itinfo.id,           
             itinfo.seller,          
             itinfo.location,                  

             itinfo.mpx_frontal_cam,  
             itinfo.mpx_rear_cam,     
        
             itinfo.screen_size,      
             itinfo.internal_memo,   
        
             itinfo.batery_span,       
             itinfo.resolution_type,   
             itinfo.with_touch_screen,
             itinfo.get_extra_specs(),
             parent_id,
             itinfo.currency,
             itinfo.ad_date,
             time ) 
    
    

    try:
        my_cursor.execute(query, vals)
        conn.commit()
    except Error as e:
        print("error in query while inserting a product", e)
        return
    else:
        print( codecs.encode( "\n>>> [item saved]", encoding='utf-8' ) )
 
    """
    query = "INSERT INTO dialogs VALUES (%s, %s, %s, %s, %s)"

 
    try:
        my_cursor.executemany(query, itinfo.get_dialogs())
        conn.commit()
    except Error as e:
        print("error in query while inserting dialogs ", e)
        return
    else:
        print(my_cursor.rowcount, "dialog were inserted")
        print("")
    """



def save_into_db(conn, my_cursor, pinfo, category):

    if pinfo is None:
        return

    query = """INSERT INTO products (category, product_description, price, n_sales, more_price_info, brand, line, name, prod_format, container_format, sale_unit, ml_category_rank, model, version, id, extra_specs, seller, location)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    
    vals = (category.strip(),
            pinfo.get_title(),
            pinfo.get_price(),
            pinfo.get_nsales(),
            pinfo.get_price_info(),
            pinfo.get_brand(),
            pinfo.get_line(),
            pinfo.get_name(),
            pinfo.get_format(),
            pinfo.get_container_type(),
            pinfo.get_unit_volume(),
            pinfo.get_ml_category_rank(),
            pinfo.get_model(),
            pinfo.get_version(),
            pinfo.get_id(),
            pinfo.get_extra_specs(),
            pinfo.get_seller(),
            pinfo.get_location() )
    
    print(">>> saving product: ", vals[1])

    try:
        my_cursor.execute(query, vals)
        conn.commit()
    except Error as e:
        print("error in query while inserting a product", e)
        return 
 

    query = "INSERT INTO dialogs VALUES (%s, %s, %s, %s)"

 
    try:
        my_cursor.executemany(query, pinfo.get_dialogs())
        conn.commit()
        print(my_cursor.rowcount, "dialog were inserted")
    except Error as e:
        print("error in query while inserting dialogs ", e)
        return

def save_cellphone_into_db(conn, my_cursor, pinfo, brand):

    if pinfo is None:
        return

    query = """INSERT INTO cellphones (brand, description, price, n_sales, ml_category_rank, seller, location, screen_size, internal_memo, mpx_frontal_cam, mpx_rear_cam, model, id, state)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    
    vals = (brand.strip(),
            pinfo.get_title(),
            pinfo.get_price(),
            pinfo.get_nsales(),
            pinfo.get_ml_category_rank(),
            pinfo.get_seller(),
            pinfo.get_location(),
            pinfo.screen_size,
            pinfo.internal_memo,
            pinfo.mpx_frontal_cam,
            pinfo.mpx_rear_cam,
            pinfo.get_model(),
            pinfo.get_id(),
            pinfo.get_state())

    try:
        my_cursor.execute(query, vals)
        conn.commit()
        print(">>> [saved] product: {} price: {} ".format( vals[1], vals[2]) )
    except Error as e:
        print("error in query while inserting a product", e)
        return 
 

    query = "INSERT INTO dialogs VALUES (%s, %s, %s, %s)"

 
    try:
        my_cursor.executemany(query, pinfo.get_dialogs())
        conn.commit()
        print(my_cursor.rowcount, "dialog were inserted")
    except Error as e:
        print("error in query while inserting dialogs ", e)
        return

def save_fridge_into_db(conn, my_cursor, pinfo, category_name):

    if pinfo is None:
        return

    query = """INSERT INTO fridge (brand, description, price, n_sales, ml_category_rank, seller, location, id, state, spec, parent)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    
    vals = (pinfo.brand,
            pinfo.title,
            pinfo.price,
            pinfo.nsales,
            pinfo.ml_category_rank,
            pinfo.seller,
            pinfo.location,
            pinfo.id,
            pinfo.state,
            pinfo.description,
            category_name.strip())

    try:
        my_cursor.execute(query, vals)
        conn.commit()
        print(">>> [saved] product: {} price: {} ".format( vals[1], vals[2]) )
    except Error as e:
        print("error in query while inserting a product", e)
        return 
 

    query = "INSERT INTO dialogs VALUES (%s, %s, %s, %s, %s)"

 
    try:
        my_cursor.executemany(query, pinfo.dialogs)
        conn.commit()
        print(my_cursor.rowcount, "dialog were inserted")
    except Error as e:
        print("error in query while inserting dialogs ", e)
        return
   
        
            
