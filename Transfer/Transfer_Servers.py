from reconnect import recon_utils
import time 
import screen
import windows 
import utils
import pyautogui
import template
import settings
import ASA.stations
import ASA.stations.custom_stations
import ASA.strucutres
import ASA.strucutres.teleporter
import logs.gachalogs as logs
import variables
import ASA.config 
import ASA.strucutres.bed
import ASA.strucutres.inventory
import ASA.player.player_inventory
import bot.config
import json
import ASA.player.player_state
import local_player
import ASA.player.buffs
import Transfer.Dedi_Interaction
from bot import render   
global render_flag
render_flag = False #starts as false as obviously we are not rendering anything

buttons = {
    "search_x": 2230, "search_y": 260,
    "first_server_x": 2230, "first_server_y": 438,
    "join_x": 2230, "join_y": 1260,
    "refresh_x": 1240, "refresh_y": 1250,
    "back_x": 230, "back_y": 1180,
    "cancel_x":1426,"cancel_y":970,
    "red_okay_x":1270,"red_okay_y":880,
    "mod_join_x":700,"mod_join_y":1250,
    "travel_to_another_server_x":1250,"travel_to_another_server_y":1055,
    "transmiter_join_x":2190,"transmiter_join_y":1188 
}

def get_pixel_loc(location):
    if screen.screen_resolution == 1080:
        return round(buttons.get(location) * 0.75)
    return buttons.get(location)

def transfer_bundle(location):
    items = True
    
    while items == True:
        if location == "withdraw":
            enter_transferpod()
            time.sleep(.5*settings.sleep_constant)
            logs.logger.debug(f"leave tek pod")
            render.leave_tekpod(settings.withdraw_yaw)
            time.sleep(.5*settings.sleep_constant)
            logs.logger.debug(f"withdraw")
            Transfer.Dedi_Interaction.dedi_withdraw(settings.height_transfer)
            time.sleep(.5*settings.sleep_constant)
            utils.turn_right(180)
            time.sleep(.5*settings.sleep_constant)
            access_transmiter(location)
            time.sleep(.5*settings.sleep_constant)
            travel_button()
            time.sleep(.5*settings.sleep_constant)
            transfer_server(settings.deposit_server)
            time.sleep(.5*settings.sleep_constant)
            template.template_await_true(template.check_template,2,"beds_title",0.7)
            server_spawn("deposit")
            location = "deposit"
        if location == "deposit":
            enter_transferpod()
            time.sleep(.5*settings.sleep_constant)
            render.leave_tekpod(settings.depodsit_yaw)
            time.sleep(1.5*settings.sleep_constant)
            Transfer.Dedi_Interaction.dedi_deposit(settings.height_transfer)
            time.sleep(.5*settings.sleep_constant)
            utils.turn_right(180)
            time.sleep(.5*settings.sleep_constant)
            access_transmiter(location)
            time.sleep(.5*settings.sleep_constant)
            travel_button()
            time.sleep(.5*settings.sleep_constant)
            transfer_server(settings.withdraw_server)
            time.sleep(.5*settings.sleep_constant)
            template.template_await_true(template.check_template,2,"beds_title",0.7)
            server_spawn("withdraw")
            time.sleep(.5*settings.sleep_constant)
            location = "withdraw"
    time.sleep(.5*settings.sleep_constant)
            

def transfer_server(server_number):

    if not template.check_template_no_bounds("cluster", 0.7): #check that we are on sever list
        travel_button()
        return      

    windows.click(get_pixel_loc("search_x"), get_pixel_loc("search_y"))
    time.sleep(0.5*settings.sleep_constant)
    utils.ctrl_a()
    utils.write(str(server_number))
    time.sleep(0.5*settings.sleep_constant)    
    windows.click(get_pixel_loc("first_server_x"), get_pixel_loc("first_server_y"))
    
    if template.check_template_no_bounds("transmiter_join", 0.7):
        print("see button")
        time.sleep(0.5*settings.sleep_constant) 
        windows.click(get_pixel_loc("transmiter_join_x"), get_pixel_loc("transmiter_join_y"))
        time.sleep(0.5*settings.sleep_constant) # inital wait for the text to appear 
    recon_utils.window_still_open("join_text",0.7,20) # long wait as it can be on the screen for a long time 

    time.sleep(10)

    while template.check_template_no_bounds("transfer_timer", 0.7): #trying to wait for the transfer timer
        while template.check_template_no_bounds("transfer_timer", 0.7): #trying to wait for the transfer timer
            time.sleep(.5*settings.sleep_constant)
            windows.click(get_pixel_loc("cancel_x"), get_pixel_loc("cancel_y"))
            time.sleep(.5*settings.sleep_constant)
            windows.click(get_pixel_loc("first_server_x"), get_pixel_loc("first_server_y"))
            time.sleep(5)
            time.sleep(0.5*settings.sleep_constant) 
            print("server click")
            windows.click(get_pixel_loc("transmiter_join_x"), get_pixel_loc("transmiter_join_y"))
            print("join")
            time.sleep(0.5*settings.sleep_constant) # inital wait for the text to appear 
            recon_utils.window_still_open("join_text",0.7,20) # long wait as it can be on the screen for a long time 
    print("missed timer")

    if recon_utils.check_template_no_bounds("mod_join",0.7):
        if recon_utils.template_sleep_no_bounds("req_mods",0.7,10): # idk maybe mods take a while to load
            time.sleep(0.5*settings.sleep_constant)
            windows.click(get_pixel_loc("mod_join_x"), get_pixel_loc("mod_join_y")) 
            time.sleep(2)
            recon_utils.window_still_open("join_text",0.7,20)
            time.sleep(2)

    #if recon_utils.template_sleep_no_bounds("loading_screen",0.7,0.5):
    #    recon_utils.window_still_open_no_bounds("loading_screen",0.7,10)
        
   #     count = 0
   #     while template.check_template_no_bounds("tribelog_check",0.8) == False and count < 600: # stopping inf loops 
   #         utils.press_key("ShowTribeManager")
   #         time.sleep(0.1*settings.sleep_constant)
   #         count += 1
        
   #     time.sleep(5)
   #     return 

    if recon_utils.check_template("server_full",0.7):
        windows.click(get_pixel_loc("cancel_x"), get_pixel_loc("cancel_y")) 
        recon_utils.window_still_open_no_bounds("server_full",0.7,2)
        time.sleep(0.5)
        windows.click(get_pixel_loc("back_x"), get_pixel_loc("back_y")) 
        return 
    
    if recon_utils.check_template("red_fail",0.7):
        windows.click(get_pixel_loc("red_okay_x"), get_pixel_loc("red_okay_y")) 
        recon_utils.window_still_open_no_bounds("red_fail",0.7,2)
        time.sleep(0.5)
        windows.click(get_pixel_loc("back_x"), get_pixel_loc("back_y")) 
        return 

    time.sleep(0.5)
    #windows.click(get_pixel_loc("refresh_x"), get_pixel_loc("refresh_y")) #if it cant see we refresh the page
    windows.click(get_pixel_loc("back_x"), get_pixel_loc("back_y"))

    if recon_utils.template_sleep_no_bounds("searching",0.7,0.5):
        recon_utils.window_still_open_no_bounds("searching",0.7,10)
        time.sleep(2)

    if recon_utils.check_template_no_bounds("no_session",0.7):
        time.sleep(2)
        windows.click(get_pixel_loc("back_x"), get_pixel_loc("back_y"))
        time.sleep(2)
    
    utils.press_key("ShowTribeManager") # if there is a special event going on the loading screen changes this might fix that

def travel_button():
    while not template.check_template_no_bounds("cluster", 0.7):
        if not template.check_template_no_bounds("travel_off_Server", 0.7):
            access_transmiter()
            return
        windows.click(get_pixel_loc("travel_to_another_server_x"), get_pixel_loc("travel_to_another_server_y"))
        time.sleep(0.5*settings.sleep_constant)
    
def server_spawn(server):
    
    if ASA.strucutres.bed.is_open():
        logs.logger.debug(f"Bed screen is open") 
        if server == "deposit":
            ASA.strucutres.bed.spawn_in(settings.deposit_bed)     
        elif server == "withdraw":
            ASA.strucutres.bed.spawn_in(settings.withdraw_bed)
        else:
            ASA.strucutres.bed.spawn_in(settings.station_yaw)

def access_transmiter(server):
    while not template.check_template_no_bounds("travel_off_Server", 0.7):
        time.sleep(.5*settings.sleep_constant)
        enter_transferpod()
        time.sleep(.5*settings.sleep_constant)
        if server == "deposit":
            render.leave_tekpod(settings.depodsit_yaw)
        else:
            render.leave_tekpod(settings.withdraw_yaw)
        time.sleep(.5)
        utils.turn_left(180)
        time.sleep(.5*settings.sleep_constant)
        #if not template.check_template_no_bounds("power_symbol", 0.7):
        #    utils.press_key("ShowTribeManager")
        #    return
        utils.press_key("accessinventory")
        time.sleep(.5*settings.sleep_constant)



def withdraw():
    ASA.strucutres.inventory.open()
    time.sleep(0.5*settings.sleep_constant)
    if template.check_template("dedi",0.7):   
        ASA.strucutres.inventory.transfer_all_from()
        time.sleep(0.5*settings.sleep_constant)
        ASA.strucutres.inventory.close()

def enter_transferpod():
    global render_flag
    buffs = ASA.player.buffs.check_buffs()
    attempts = 0 
    render_flag = False
    while not render_flag:
        attempts += 1
        if attempts == bot.config.render_attempts:
            logs.logger.warning(f"{attempts} attempts however bot could not get into the render bed we are dieing and respawning to try and fix this")
            ASA.player.player_inventory.implant_eat()
            ASA.player.player_state.check_state() # this should respawn our char in the bed
        time.sleep(0.5*settings.sleep_constant)    
        utils.press_key(local_player.get_input_settings("Run")) #uncrouching char just in case
        time.sleep(0.5*settings.sleep_constant)
        utils.zero()
        time.sleep(0.5*settings.sleep_constant)
        utils.turn_down(90)
        time.sleep(0.5*settings.sleep_constant)
        pyautogui.keyDown(local_player.get_input_settings("Use"))
        
        print("Get back in bed")
        if not template.template_await_true(template.check_template_no_bounds,1,"bed_radical",0.6):
            pyautogui.keyUp(local_player.get_input_settings("Use"))
            time.sleep(0.5*settings.sleep_constant)    
            utils.press_key(local_player.get_input_settings("Run")) 
            time.sleep(0.5*settings.sleep_constant)
            utils.zero()
            time.sleep(0.5*settings.sleep_constant)
            utils.turn_down(90)
            time.sleep(0.5*settings.sleep_constant)
            pyautogui.keyDown(local_player.get_input_settings("Use"))   
            time.sleep(0.5*settings.sleep_constant)

        if template.template_await_true(template.check_template_no_bounds,1,"bed_radical",0.6):
            time.sleep(0.5*settings.sleep_constant)
            windows.move_mouse(variables.get_pixel_loc("radical_laydown_x"), variables.get_pixel_loc("radical_laydown_y"))
            time.sleep(0.5*settings.sleep_constant)
            pyautogui.keyUp(local_player.get_input_settings("Use"))
            time.sleep(1)

        if buffs.check_buffs() == 1:
            logs.logger.critical(f"bot is now in the render pod rendering the station after {attempts} attempts")
            render_flag = True
            utils.current_pitch = 0 # resetting the pitch for when char leaves the tekpod
        else:
            ASA.player.player_state.check_state()
            logs.logger.error(f"we were unable to get into the tekpod on the {attempts} attempt retrying now")

        if attempts >= bot.config.render_attempts and render_flag != True:    #Bitbucket Added Render_flag check in case we made it into Tek_pod
            logs.logger.error(f"we were unable to get into the tekpod after {attempts} attempts pausing execution to avoid unbreakable loops")
            break



def main(location):
    time.sleep(3)
    transfer_bundle(location)

if __name__ =="__main__":
    pass
