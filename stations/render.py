import pyautogui
import template 
import variables
import time
import windows
import utils
import settings
import local_player
import discordbot
import ark
global render_flag
render_flag = False #starts as false as obviously we are not rendering anything

def open_inv_dropall():
    utils.press_key("ShowMyInventory")
    if template.template_sleep("inventory", 0.7, 2):
        ark.drop_all_inv()
        time.sleep(0.4)
        ark.close_inventory()

def enter_tekpod():
    global render_flag
    retry = 0  
    while retry < 3: 
        if retry == 2:
            discordbot.gachalogs.warning("2 attempts unsucsessful trying to kill survivor now")
            ark.implant_eat()
            ark.check_state()
        utils.press_key("Run") # incase player is crouched somehow
        time.sleep(1)
        utils.zero()
        utils.set_yaw(settings.station_yaw)
        utils.turn_down(10)
        time.sleep(1)
        pyautogui.keyDown(local_player.get_input_settings("Use"))
        
        if not template.template_sleep_no_bounds("bed_radical", 0.6,2):
            discordbot.gachalogs.warning("cannot find the bed radical")
            pyautogui.keyUp(local_player.get_input_settings("Use"))
            time.sleep(1)
            utils.zero()
            utils.set_yaw(settings.station_yaw)
            utils.turn_down(10)
            time.sleep(1)
            pyautogui.keyDown(local_player.get_input_settings("Use"))
        time.sleep(1)
        if template.check_template_no_bounds("bed_radical", 0.6):
            windows.move_mouse(variables.get_pixel_loc("radical_laydown_x"), variables.get_pixel_loc("radical_laydown_y"))
            time.sleep(0.5*settings.sleep_constant)
            pyautogui.keyUp(local_player.get_input_settings("Use"))
        time.sleep(1)
        if ark.buffs() == 2:
            discordbot.gachalogs.critical("NOW RENDERING STATION")
            utils.current_pitch = 0
            render_flag = True
            time.sleep(0.5)
            return  
        else:
            discordbot.gachalogs.warning(f"failed to get into the tekpod. attempt {retry + 1}/3. retrying in 10 seconds")
            time.sleep(10)
            ark.check_state()
            retry += 1 

    discordbot.gachalogs.error("Failed to enter the tekpod after 3 attempts.")


def leave_tekpod():
    ark.close_tribelog()
    time.sleep(0.4)
    pyautogui.press(local_player.get_input_settings("Use"))
    time.sleep(1)
    if ark.buffs() == 2: # long time for big timers 
        pyautogui.press(local_player.get_input_settings("Use"))
    time.sleep(1)
    utils.current_yaw = settings.render_pushout
    utils.set_yaw(settings.station_yaw)
    time.sleep(0.5)
    global render_flag
    render_flag = False

if __name__ == "__main__":
    pass
    