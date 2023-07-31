import sys
sys.path.append( "C:\\mysql-connector-python-8.0.26" )
import mysql.connector as myc
from mysql.connector import Error

class item:

    def __init__(self):

        self.state            = None
        self.nsales           = None
        self.title            = None
        self.brand            = None
        self.ml_category_rank = None
        self.price            = None
        self.currency         = None
        self.model            = None
        self.id               = None
        self.seller           = None
        self.location         = None
        self.ad_date          = None
        self.dialogs          = []

        self.mpx_frontal_cam  = None
        self.mpx_rear_cam     = None
        
        self.screen_size      = None
        self.internal_memo    = None
        
        self.batery_span       = None
        self.resolution_type   = None
        self.with_touch_screen = None

        self.extra_specs      = None


    def set_internal_memo(self, x):
        self.internal_memo = x
        
    def set_screen_size(self, x):
        self.screen_size = x
        
    def set_batery_span(self, x):
        self.batery_span = x
        
    def set_resolution_type(self, x):
        self.resolution_type = x
        
    def set_with_touch_screen(self, x):
        self.with_touch_screen = x

    def set_id(self, mycursor):

        query = "SELECT id FROM items ORDER BY id DESC LIMIT 1"
        last_id = 9999
        
        try:
            mycursor.execute(query)
            row = mycursor.fetchone()
    
        except Error as e:
            print("error in query while selection product id ", e)
            return
        else:
            if row is not None:
                last_id = row[0]

            self.id = 1 + last_id
            

    def set_extra_specs(self, espec):
        
        if self.extra_specs is None:
            self.extra_specs = espec + " - "
        else:
            self.extra_specs = self.extra_specs + espec + " - "

    def get_extra_specs(self):

        return self.extra_specs
    

    def set_dialog(self, dialog_elements):

        self.dialogs.append( dialog_elements )

    def get_dialogs(self):

        return self.dialogs

    def set_brand(self, brand):

        self.brand = brand

    def set_line(self, line):

        self.line = line

    def set_name(self, name):

        self.name = name

    def set_format(self, _format):

        self.format = _format

    def set_container_type(self, ctype):

        self.container_type = ctype

    def set_unit_volume(self, uvol):

        self.unit_volume = uvol

    def set_model(self, model):

        self.model = model

    def set_version(self, version):

        self.version = version

