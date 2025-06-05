import template
import logs.gachalogs as logs
import utils
import windows
import variables
import time 
import settings
import ASA.config 
import ASA.stations.custom_stations
import ASA.player.tribelog
import ASA.player.player_inventory
import ASA.player.player_state

def is_open():
    return template.check_template("beds_title",0.7) #bed title is found in both death and fast travel screens
    
def is_dead():
    return template.check_template("death_regions",0.7)
    
def close():
    attempts = 0
    while is_open():
        attempts += 1
        logs.logger.debug(f"trying to close the bed {attempts} / {ASA.config.teleporter_close_attempts}")
        windows.click(variables.get_pixel_loc("back_button_tp_x"),variables.get_pixel_loc("back_button_tp_y"))
        time.sleep(0.2*settings.sleep_constant)

        if attempts >= ASA.config.teleporter_close_attempts:
            logs.logger.error(f"unable to close the bed after {ASA.config.teleporter_close_attempts} attempts")
            ASA.player.player_state.lastError = time.time()
            ASA.player.player_state.errorCount += 1
            break
            

def spawn_in(bed_name:str):
    logs.logger.debug(f"Attempting to spawn in {bed_name}")
    if not is_open():
        ASA.player.player_inventory.implant_eat()
        logs.logger.debug(f"Returned from the implant eat function!")
        
    if is_open():
        state = "death screen" if is_dead() else "fast travel screen"
        logs.logger.debug(f"char is in the {state}")
        
        #time.sleep(0.4*settings.sleep_constant)
        if is_dead():
            search_bar_x = variables.get_pixel_loc("search_bar_bed_dead_x")
            search_bar = "bed_spawn_search_130x1265_140x45"
            search_bar_fake = "grinder"
        else:
            search_bar_x = variables.get_pixel_loc("search_bar_bed_alive_x")
            search_bar = "bed_spawn_search_330x1265_140x45"
        logs.logger.debug(f"Checking location {search_bar}")
        if template.template_await_true(template.check_template, 3, search_bar, 0.7):
            logs.logger.debug(f"Found Bed Search")
            for x in range(3):
                #time.sleep(0.4*settings.sleep_constant) 
                windows.click(search_bar_x, variables.get_pixel_loc("search_bar_bed_y")) #search bar y axis is the same for both death/alive    
                utils.ctrl_a() #CTRL A removes all previous data in the search bar 
                utils.write(bed_name)
                #time.sleep(5*settings.sleep_constant) 
                if not template.template_await_false(template.check_template_no_bounds, 3, search_bar, 0.7):
                    logs.logger.debug(f"Verified Search Criteria")
                    while not template.template_await_true(template.check_teleporter_orange,3): # waiting for the bed to appear as ready to spawn in
                        logs.logger.info(f"Trying to click on bed {bed_name} in list {x+1}/3")
                        for click_count in range(3):     
                            windows.click(variables.get_pixel_loc("first_bed_slot_x"),variables.get_pixel_loc("first_bed_slot_y"))
                        break
                    break
                else:
                    logs.logger.debug(f"Still missing Search Criteria") 

        if not template.template_await_true(template.check_teleporter_orange,3): # waiting for the bed to appear as ready to spawn in
            logs.logger.error(f"the bed char tried spawning on is not in the ready state or cant be found exiting out of bed screen now")
            #close()
            #return    # no need to continue with this therefore we should just leave func     
               
        #windows.click(variables.get_pixel_loc("first_bed_slot_x"),variables.get_pixel_loc("first_bed_slot_y"))
        windows.click(variables.get_pixel_loc("spawn_button_x"),variables.get_pixel_loc("spawn_button_y"))

        if template.template_await_true(template.white_flash,2):
            logs.logger.debug(f"white flash detected waiting for up too 5 seconds")
            template.template_await_false(template.white_flash,5)

        time.sleep(10) # animation spawn in is about 7 seconds 

        ASA.player.tribelog.open()
        ASA.player.tribelog.close()
    else:
        logs.logger.error(f"MISSED OPENING DEATH SCREEN/BED MENU!!!!!")
  
