import template
import logs.gachalogs as logs
import utils
import windows
import variables
import time 
import settings
import bot.config 
import ASA.player.player_inventory
import ASA.player.player_state
import pyautogui
import local_player
import ASA.player.buffs
global render_flag
render_flag = False #starts as false as obviously we are not rendering anything


def is_open():
    return template.check_template_no_bounds("bed_radical",0.6)

def enter_tekpod():
    global render_flag
    buffs = ASA.player.buffs.check_buffs()
    attempts = 0 
    while not render_flag:
        attempts += 1
        if attempts == bot.config.render_attempts:
            logs.logger.warning(f"{attempts} attempts however bot could not get into the render bed we are dieing and respawning to try and fix this")
            ASA.player.player_inventory.implant_eat()
            logs.logger.warning(f"Returning from implant eat function")
            ASA.player.player_state.check_state() # this should respawn our char in the bed
        time.sleep(0.5*settings.sleep_constant)    
        utils.press_key(local_player.get_input_settings("Run")) #uncrouching char just in case
        utils.zero()
        utils.set_yaw(settings.station_yaw)
        utils.turn_down(15)
        time.sleep(0.3*settings.sleep_constant)
        pyautogui.keyDown(chr(utils.keymap_return(local_player.get_input_settings("Use"))))
        
        if not template.template_await_true(template.check_template_no_bounds,1,"bed_radical",0.6):
            logs.logger.warning(f"We don't see the bed radical, Render_Flag: {render_flag}, Attempts: {attempts}")
            pyautogui.keyUp(local_player.get_input_settings("Use"))
            time.sleep(0.5*settings.sleep_constant)    
            utils.press_key(local_player.get_input_settings("Run")) 
            utils.zero()
            utils.set_yaw(settings.station_yaw)
            utils.turn_down(60)
            time.sleep(0.3*settings.sleep_constant)
            pyautogui.keyDown(chr(utils.keymap_return(local_player.get_input_settings("Use"))))
            time.sleep(0.5*settings.sleep_constant)

        if not template.template_await_true(template.check_template_no_bounds,1,"bed_radical",0.6):
            logs.logger.warning(f"We don't see the bed radical, Render_Flag: {render_flag}, Attempts: {attempts}")
            pyautogui.keyUp(local_player.get_input_settings("Use"))
            time.sleep(0.5*settings.sleep_constant)    
            utils.press_key(local_player.get_input_settings("Run")) 
            utils.zero()
            utils.set_yaw(settings.station_yaw)
            utils.turn_right(30)
            time.sleep(0.3*settings.sleep_constant)
            pyautogui.keyDown(chr(utils.keymap_return(local_player.get_input_settings("Use"))))
            time.sleep(0.5*settings.sleep_constant)  

        if not template.template_await_true(template.check_template_no_bounds,1,"bed_radical",0.6):
            logs.logger.warning(f"We don't see the bed radical, Render_Flag: {render_flag}, Attempts: {attempts}")
            pyautogui.keyUp(local_player.get_input_settings("Use"))
            time.sleep(0.5*settings.sleep_constant)    
            utils.press_key(local_player.get_input_settings("Run")) 
            utils.zero()
            utils.set_yaw(settings.station_yaw)
            utils.turn_left(30)
            time.sleep(0.3*settings.sleep_constant)
            pyautogui.keyDown(chr(utils.keymap_return(local_player.get_input_settings("Use"))))
            time.sleep(0.5*settings.sleep_constant)     

        if template.template_await_true(template.check_template_no_bounds,1,"bed_radical",0.6):
            logs.logger.warning(f"We see the bed radical and will select laydown, Render_Flag: {render_flag}, Attempts: {attempts}")
            time.sleep(0.2*settings.sleep_constant)
            windows.move_mouse(variables.get_pixel_loc("radical_laydown_x"), variables.get_pixel_loc("radical_laydown_y"))
            time.sleep(0.5*settings.sleep_constant)
            pyautogui.keyUp(chr(utils.keymap_return(local_player.get_input_settings("Use"))))
            time.sleep(1)
        else:
            utils.zero()
            utils.set_yaw(settings.station_yaw)
            utils.press_key("=") # moving forwards
            utils.press_key("=") # moving forwards
            utils.press_key("=") # moving forwards

        if buffs.check_buffs() == 1:
            logs.logger.critical(f"bot is now in the render pod rendering the station after {attempts} attempts")
            ASA.player.player_state.errorCount = 0
            render_flag = True
            utils.current_pitch = 0 # resetting the pitch for when char leaves the tekpod
        else:
            #ASA.player.player_state.check_state() #Bitbucket 5/13 May have found error. Checkstate will leave tek pod if in it.
            logs.logger.error(f"we were unable to get into the tekpod on the {attempts} attempt retrying now")

        if attempts >= bot.config.render_attempts and render_flag == False:    #Bitbucket Added Render_flag check in case we made it into Tek_pod:
            logs.logger.error(f"we were unable to get into the tekpod after {attempts} attempts pausing execution to avoid unbreakable loops")
            break

def leave_tekpod():
    logs.logger.debug(f"leave_tekpod")
    global render_flag
    buffs = ASA.player.buffs.check_buffs()
    ASA.player.player_state.reset_state() 
    time.sleep(0.2*settings.sleep_constant)
    utils.press_key(local_player.get_input_settings("Use"))
    time.sleep(1*settings.sleep_constant)
    if buffs.check_buffs == 1:
        time.sleep(3)
        logs.logger.warning("bot didnt leave the tekpod first try we are retrying now")
        utils.press_key(local_player.get_input_settings("Use"))
        time.sleep(1*settings.sleep_constant)
    utils.current_yaw = settings.render_pushout
    utils.set_yaw(settings.station_yaw)
    time.sleep(0.5*settings.sleep_constant)
    render_flag = False