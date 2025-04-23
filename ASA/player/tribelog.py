import ASA.player
import ASA.player.player_state
import template
import logs.gachalogs as logs
import utils
import windows
import variables
import time 
import settings
import ASA.config 

def is_open():
    return template.check_template_no_bounds("tribelog_check",0.8)
    
def open():
    attempts = 0
    logs.logger.debug("trying to open up the tribelog screen")
    while not is_open():
        attempts += 1
        utils.press_key("ShowTribeManager")
        time.sleep(0.1)
        if attempts >= ASA.config.tribelog_open_attempts:
            logs.logger.warning(f"tribelogs didnt open in {attempts} attempts")
            break
    
def close():
    attempts = 0
    while is_open():
        attempts += 1
        logs.logger.debug(f"trying to close out of the tribelog screen {attempts} / {ASA.config.tribelog_close_attempts} ")
        windows.click(variables.get_pixel_loc("close_inv_x"),variables.get_pixel_loc("close_inv_y"))
        template.template_await_false(template.check_template_no_bounds,2,"tribelog_check",0.8)
            
        if attempts >= ASA.config.inventory_close_attempts:
            logs.logger.error(f"unable to close the objects inventory after {attempts} attempts") 
            #check state of the char the reason we can do it now is that the latter should spam click close inv 
            ASA.player.player_state.check_state()
            break