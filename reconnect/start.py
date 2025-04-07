from reconnect import join_menu , main_menu , multiplayer_menu , recon_utils , crash 

import template
import windows
class reconnect():

    def __init__(self,server):
        self.server = server
        pass

    def check_disconected(self):
        return recon_utils.check_template_no_bounds("escape",0.7)
             
    def rejoin_server(self):
        joined = False

        c = crash.crash(windows.hwnd)
        c.re_open_game()

        while not joined:
            main_menu.enter_menu()
            join_menu.enter_menu()
            multiplayer_menu.join_server(self.server)
            if template.check_template_no_bounds("tribelog_check",0.8) or template.check_template("death_regions",0.7):
                joined = True
                return 
