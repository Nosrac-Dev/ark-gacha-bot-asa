import json
import pyautogui
import numpy as np
import time
import screen
import discordbot
import variables
import settings
import utils
import win32clipboard
import windows
import template
import stations.render as render
import reconnect.start
import reconnect.recon_utils
import reconnect.crash

global bed_number
global first_run

first_run = True

def ini():
    time.sleep(0.2)
    if template.check_template_no_bounds("console",0.55) == False:
        utils.press_key("ConsoleKeys")

    with open("txt_files/iniFile.txt","r") as file:
        ini = file.read()

    count = 0
    while template.check_template_no_bounds("console",0.55) == False:
        if count > 20:
            break
        count += 1
        time.sleep(0.1)
    time.sleep(0.2)
    pyautogui.write(ini, interval=0.005) # issues when insta writing 
    utils.press_key("Enter")
    time.sleep(0.3)
    pyautogui.scroll(10) # puts char in first person

class station_metadata():
    def __init__(self):
        super().__init__()
        self.name = None
        self.xpos = None
        self.ypos = None
        self.zpos = None
        self.yaw = None
        self.pitch = 0
        self.side = None
        self.resource = None

def open_tribelog():
    count = 0
    discordbot.gachalogs.debug("trying to open up the tribe logs")
    while template.check_template_no_bounds("tribelog_check",0.8) == False and count < 100: # stopping inf loops 
        utils.press_key("ShowTribeManager") # tribelog doesnt close if you spam the key 
        time.sleep(0.1)
        count += 1

def close_tribelog():
    discordbot.gachalogs.debug("trying to close out of the tribe logs")
    if template.check_template_no_bounds("tribelog_check",0.8):
        time.sleep(0.2*settings.sleep_constant)
        windows.click(variables.get_pixel_loc("close_inv_x"),variables.get_pixel_loc("close_inv_y")) # now ready to do whatever we need to 
        
        if template.window_still_open_no_bounds("tribelog_check",0.8,2):
            discordbot.gachalogs.warning("tribe log failed to close retrying in 3 seconds(timer maybe?)")
            time.sleep(3) # guessing its timer
            windows.click(variables.get_pixel_loc("close_inv_x"),variables.get_pixel_loc("close_inv_y"))
            time.sleep(2)
    time.sleep(0.2*settings.sleep_constant)

def close_teleporter():
    discordbot.gachalogs.debug("trying to close out of the teleporter screen")
    if template.check_template_no_bounds("teleporter_title",0.7):
        time.sleep(0.2*settings.sleep_constant)
        windows.click(variables.get_pixel_loc("back_button_tp_x"),variables.get_pixel_loc("back_button_tp_y")) # now ready to do whatever we need to 
        
        if template.window_still_open_no_bounds("teleporter_title",0.7,2):
            discordbot.gachalogs.warning("teleporter failed to close retrying in 3 seconds(timer maybe?)")
            time.sleep(3) # guessing its timer
            windows.click(variables.get_pixel_loc("back_button_tp_x"),variables.get_pixel_loc("back_button_tp_y"))
            time.sleep(2)

def open_inventory():
    discordbot.gachalogs.debug("trying to open up the charecters inventory")
    if not template.check_template("inventory",0.7):
        utils.press_key("ShowMyInventory")
    if template.template_sleep("inventory",0.7,2) == False:
        discordbot.gachalogs.warning("inventory failed to open retrying now")
        utils.press_key("AccessInventory")
        template.template_sleep("inventory",0.7,2)


def close_inventory():
    discordbot.gachalogs.debug("trying to close the charecters inventory")
    if template.check_template("inventory",0.7):
        windows.click(variables.get_pixel_loc("close_inv_x"), variables.get_pixel_loc("close_inv_y"))
    else:
        discordbot.gachalogs.debug("inventory is already closed")
        return
    if template.window_still_open("inventory", 0.7, 2):
        windows.click(variables.get_pixel_loc("close_inv_x"), variables.get_pixel_loc("close_inv_y"))
        if template.window_still_open("inventory", 0.7, 2):
            discordbot.gachalogs.warning("inventory failed to close retrying in 3 seconds(timer maybe?)")
            time.sleep(3)  # Guessing timer hit
            windows.click(variables.get_pixel_loc("close_inv_x"), variables.get_pixel_loc("close_inv_y"))

def open_structure():
    discordbot.gachalogs.debug("trying to open up the charecters inventory")
    utils.press_key("AccessInventory")
    if template.template_sleep("inventory",0.7,2) == False:
        discordbot.gachalogs.warning("object didnt open retrying")
        utils.press_key("AccessInventory")
        template.template_sleep("inventory",0.7,2)
    if settings.singleplayer == False: # in single player i havent had the issue of the waiting screen
        if template.template_sleep("waiting_inv",0.8,2): # if the waiting_inv is shown on the screen in the 2 seconds after inventory apears 
            template.window_still_open("waiting_inv",0.8,5) # if server is laggy might take a while to get the data from the object
    
def dedi_withdraw(amount:int):
    time.sleep(0.1*settings.sleep_constant)
    discordbot.gachalogs.debug(f"withdrawing {amount} from the dedi") 
    for x in range(amount):
        time.sleep(0.5*settings.sleep_constant)
        windows.click(variables.get_pixel_loc("dedi_withdraw_x"),variables.get_pixel_loc("dedi_withdraw_y"))
    time.sleep(0.1*settings.sleep_constant)
    
def search_in_object(item:str): 
    discordbot.gachalogs.debug(f"searching in structure/dino for {item}")
    time.sleep(0.2*settings.sleep_constant)
    windows.click(variables.get_pixel_loc("search_object_x"),variables.get_pixel_loc("transfer_all_y"))
    utils.ctrl_a() 
    time.sleep(0.2*settings.sleep_constant)
    utils.write(item)
    time.sleep(0.1*settings.sleep_constant)

def search_in_inventory(item:str):
    discordbot.gachalogs.debug(f"searching in inventory for {item}")
    time.sleep(0.2*settings.sleep_constant)
    windows.click(variables.get_pixel_loc("search_inventory_x"),variables.get_pixel_loc("transfer_all_y")) 
    utils.ctrl_a()  
    time.sleep(0.2*settings.sleep_constant)
    utils.write(item)
    time.sleep(0.1*settings.sleep_constant)

def drop_all_inv():  
    discordbot.gachalogs.debug(f"dropping all items from our inventory ")
    time.sleep(0.2*settings.sleep_constant)
    windows.click(variables.get_pixel_loc("drop_all_x"),variables.get_pixel_loc("transfer_all_y")) 
    time.sleep(0.1*settings.sleep_constant)

def drop_all_obj():
    discordbot.gachalogs.debug(f"dropping all items from object")
    time.sleep(0.2*settings.sleep_constant)
    windows.click(variables.get_pixel_loc("drop_all_obj_x"),variables.get_pixel_loc("transfer_all_y")) 
    time.sleep(0.1*settings.sleep_constant)

def transfer_all_from(): 
    discordbot.gachalogs.debug(f"transfering all from object")
    time.sleep(0.2*settings.sleep_constant)
    windows.click(variables.get_pixel_loc("transfer_all_from_x"), variables.get_pixel_loc("transfer_all_y"))
    time.sleep(0.1*settings.sleep_constant)

def transfer_all_inventory(): 
    discordbot.gachalogs.debug(f"transfering all in inventory")
    time.sleep(0.2*settings.sleep_constant)
    windows.click(variables.get_pixel_loc("transfer_all_inventory_x"),variables.get_pixel_loc("transfer_all_y"))
    time.sleep(0.1*settings.sleep_constant)

def buffs():
    open_inventory()
    count = 0
    time.sleep(0.5*settings.sleep_constant)
    while template.check_template("show_buff",0.7) and count < 10:
        windows.click(variables.get_pixel_loc("buff_button_x"),variables.get_pixel_loc("buff_button_y"))
        time.sleep(0.2)
        count += 1
    time.sleep(0.4*settings.sleep_constant)
    if template.check_buffs("tek_pod_buff",0.7):
        close_inventory()
        return 2 
    elif template.check_buffs("starving",0.7):
        discordbot.gachalogs.debug("char is starving")
        close_inventory()
        return 3
    elif template.check_buffs("dehydration",0.7):
        discordbot.gachalogs.debug("char is dehydrated")
        close_inventory()
        return 4
    else:
        close_inventory()
        return False
    
def check_disconected():
    rejoin = reconnect.start.reconnect(str(settings.server_number))
    
    if rejoin.check_disconected():
        discordbot.gachalogs.critical("we are disconnected from the server")
        rejoin.rejoin_server()
        close_tribelog()
        discordbot.gachalogs.critical("joined back into the server waiting 60 seconds to render everything ") # not critical but it is important info
        time.sleep(60)
        utils.set_yaw(settings.station_yaw)    
        
def check_state():
    discordbot.gachalogs.debug(f"currently checking the state of the bot")
    crash = reconnect.crash.crash(windows.hwnd)
    crash.crash_rejoin()  # wecheck the crash before disconected as we can rejoin back with disconect 
    check_disconected()

    clear = False
    loopcount = 0
    while not clear and loopcount < 4:   #loop in case multiple conditions exist (i.e. tribelog and tekpod)
        clear = True
        loopcount += 1
        if template.check_template("beds_title",0.7):
            discordbot.gachalogs.debug(f"check_state")
            bed_spawn_in(settings.bed_spawn)
            time.sleep(0.2*settings.sleep_constant)
            utils.set_yaw(settings.station_yaw)
            clear = False
    
        if template.check_template_no_bounds("tribelog_check",0.7):
            discordbot.gachalogs.debug(f"check_state")
            close_tribelog()
            clear = False
        if template.check_template("inventory",0.7):
            discordbot.gachalogs.debug(f"check_state")
            close_inventory()
            clear = False
        if template.check_template("teleporter_title",0.7):
            discordbot.gachalogs.debug(f"check_state")
            close_teleporter()
            
        type = buffs() 
        if type == 2 or render.render_flag:
            discordbot.gachalogs.debug(f"render flag : {render.render_flag} type {type} leaving tekpod now")
            render.leave_tekpod()
            clear = False

        # if starving.....
        if type == 3 or type == 4:
            discordbot.gachalogs.debug(f"tping back to render bed to replenish food and water | 3= food 4 = water | reason:{type}")
            time.sleep(0.2*settings.sleep_constant)
            teleport_not_default(settings.bed_spawn)
            render.enter_tekpod()
            time.sleep(30) #idk easy way to ensure that the food goes to the top
            render.leave_tekpod() 
            time.sleep(0.2*settings.sleep_constant)
            clear = False

    if loopcount >= 4:
        discordbot.gachalogs.warning("state could not be corrected")

    return

def get_custom_stations():
    file_path = "json_files/stations.json"
    try:
        with open(file_path, 'r') as file:
            data = file.read().strip()
            if not data:
                return []
            return json.loads(data)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        return []

def get_station_metadata(teleporter_name:str):
    global custom_stations
    custom_stations = False
    stationdata = station_metadata()
    foundstation = False

    all_stations = get_custom_stations()

    if len(all_stations) > 0:
        custom_stations = True
        for entry_station in all_stations:
            if entry_station["name"] == teleporter_name:
                stationdata.name = entry_station["name"]
                stationdata.xpos = entry_station["xpos"]
                stationdata.ypos = entry_station["ypos"]
                stationdata.zpos = entry_station["zpos"]
                stationdata.yaw  = entry_station["yaw"]
                #stationdata.pitch = entry_station["pitch"]
                foundstation = True
                break

    if not foundstation:   #setting up default station metadata
        stationdata.name = teleporter_name
        stationdata.xpos = 0
        stationdata.ypos = 0
        stationdata.zpos = 0
        stationdata.yaw = settings.station_yaw
        stationdata.pitch = 0

    return stationdata

def popcorn_inventory(item):
    if template.check_template("inventory",0.7) == False:
        utils.press_key("ShowMyInventory")
        template.template_sleep("inventory",0.7,2)
        time.sleep(0.5*settings.sleep_constant)
    search_in_inventory(item)
    time.sleep(0.5*settings.sleep_constant)

    while template.inventory_first_slot(item,0.35):
        pyautogui.click(variables.get_pixel_loc("inv_slot_start_x")+30,variables.get_pixel_loc("inv_slot_start_y")+30)
        utils.press_key("DropItem")
        time.sleep(0.2*settings.sleep_constant)

    close_inventory()

def implant_eat():
    open_inventory()
        
    if template.template_sleep("inventory",0.7,2) == False:
    
        if template.check_template("exit_resume",0.4) == True:
            utils.press_key("PauseMenu")
            time.sleep(1)
        else:
            utils.press_key("PauseMenu") # bed screen or tp screen

        time.sleep(1)
        utils.press_key("ShowMyInventory")
        
    time.sleep(1)
    close_inventory()
    time.sleep(1.5)
    pyautogui.keyDown("s")
    time.sleep(1)        # walking back to avoid suiciding on parts needing to be accessed
    pyautogui.keyUp("s")
    time.sleep(0.2)
    open_inventory()
    time.sleep(1.5)
    pyautogui.click(variables.get_pixel_loc("implant_eat_x"),variables.get_pixel_loc("implant_eat_y"))
    time.sleep(10) # acouting for lag on high ping 
    utils.press_key("Use")
    template.template_sleep("death_regions",0.7,10)
    time.sleep(1)


def white_flash():
    roi = screen.get_screen_roi(500,500,100,100)
    total_pixels = roi.size
    num_255_pixels = np.count_nonzero(roi == 255)
    percentage_255 = (num_255_pixels / total_pixels) * 100
    return percentage_255 >= 80


def console_ccc(attempt=0):
    if attempt >= 3:
        discordbot.gachalogs.warning("Max retries reached. Exiting.")
        return None
    if template.check_template("inventory",0.7):
        discordbot.gachalogs.debug("inventory found in CCC check")
        close_inventory()
    if template.check_template("teleporter_title",0.7):
        discordbot.gachalogs.debug("teleporter title found in CCC check")
        windows.click(variables.get_pixel_loc("search_bar_bed_alive_x")-200,variables.get_pixel_loc("search_bar_bed_y"))
        template.window_still_open("teleporter_title",0.7,2)
        time.sleep(0.4*settings.sleep_constant)
    if template.check_template("beds_title",0.7):
        discordbot.gachalogs.debug("bed_title found in CCC check")
        windows.click(variables.get_pixel_loc("search_bar_bed_alive_x")-200,variables.get_pixel_loc("search_bar_bed_y")) # this is the back button in the bed screen/tp screen
        template.window_still_open("beds_title",0.7,2)
        time.sleep(0.4*settings.sleep_constant)

    time.sleep(0.1)
    utils.press_key("ConsoleKeys")
    count = 0
    while template.check_template_no_bounds("console",0.55) == False:
        if count > 31:
            break
        time.sleep(0.2)
        if count % 10 == 0 and count != 0:
            discordbot.gachalogs.warning("console could not be found")
            utils.press_key("ConsoleKeys")
        count += 1
    if template.check_template_no_bounds("console",0.55):
        pyautogui.write("ccc") # for some reason utils.write doesnt register
        time.sleep(0.3*settings.sleep_constant)
        utils.press_key("Enter")
        time.sleep(0.6*settings.sleep_constant) # slow to try and prevent opening clipboard to empty data
        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
        if data == None:
            discordbot.gachalogs.warning(f"data returned is none retrying {attempt + 1} / 3")
            return console_ccc(attempt + 1)
        
        ccc_data = data.split()
        return ccc_data
    
def console_write(info:str):
    utils.press_key("ConsoleKeys")
    count = 0
    while template.check_template_no_bounds("console",0.55) == False:
        if count > 21:
            break
        time.sleep(0.2)
        if count % 10 == 0 and count != 0:
            utils.press_key("ConsoleKeys")
        count += 1
    if template.check_template_no_bounds("console",0.55):
        pyautogui.write(info)
        time.sleep(0.3)
        utils.press_key("Enter")
        time.sleep(0.2)
    
def bed_spawn_in(bed_name:str):

    if template.check_template("beds_title",0.7) == False:
        discordbot.gachalogs.debug("bed_title not found SUICIDING")
        implant_eat()
    
    if template.check_template("death_regions",0.7) == True:
        discordbot.gachalogs.debug("in the death screen")
        windows.click(variables.get_pixel_loc("search_bar_bed_dead_x"),variables.get_pixel_loc("search_bar_bed_y"))
        utils.ctrl_a()
        utils.write(bed_name)
    else:
        discordbot.gachalogs.debug("in the fast travel screen")
        windows.click(variables.get_pixel_loc("search_bar_bed_alive_x"),variables.get_pixel_loc("search_bar_bed_y"))
        utils.ctrl_a()
        utils.write(bed_name)

    time.sleep(0.2*settings.sleep_constant)
    windows.click(variables.get_pixel_loc("first_bed_slot_x"),variables.get_pixel_loc("first_bed_slot_y"))
    if template.template_sleep("ready_clicked_bed",0.7,1) == False:
        pass # maybe use ocr to see when bed is ready    

    windows.click(variables.get_pixel_loc("spawn_button_x"),variables.get_pixel_loc("spawn_button_y"))
   
    discordbot.gachalogs.debug("checking for white flash")
    while white_flash() == False: # waiting for white flash to be true
        time.sleep(0.1)
    while white_flash() == True: # now waiting till its false
        time.sleep(0.1)
    discordbot.gachalogs.debug("white flash over waiting for the spawn animation to finish")
    time.sleep(10) # animation spawn in is about 7 seconds 
    count = 0
    while template.check_template("tribelog_check",0.8) == False and count < 100: # stopping inf loops 
        utils.press_key("ShowTribeManager")
        time.sleep(0.1)
        count += 1
    
    time.sleep(0.5*settings.sleep_constant)
    close_tribelog()

    global first_run
    if first_run:
        ini()
        first_run = False
    time.sleep(0.5)

    

def teleport_not_default(arg):
    if isinstance(arg, station_metadata):
        stationdata = arg
    else:
        stationdata = get_station_metadata(arg)

    teleporter_name = stationdata.name

    time.sleep(0.5*settings.sleep_constant)
    utils.turn_down(80)    # include the looking down part into the teleport as it is common for everytime
    time.sleep(0.3*settings.sleep_constant)
    utils.press_key("Use")

    if template.template_sleep("teleporter_title",0.7,2) == False:
        discordbot.gachalogs.warning("teleporter screen not found retrying now")
        check_state()
        utils.pitch_zero()
        utils.set_yaw(stationdata.yaw)
        utils.turn_down(80)
        time.sleep(0.2)
        utils.press_key("Use")
        template.template_sleep("teleporter_title",0.7,2)

    time.sleep(0.5*settings.sleep_constant)
    if template.teleport_icon(0.55) == False: # checking to see if we have the bed bug causing crashes 
        discordbot.gachalogs.warning("we found beds when opening up tp waiting 10 seconds to prevent crashes")
        time.sleep(10)
    
    windows.click(variables.get_pixel_loc("search_bar_bed_alive_x"),variables.get_pixel_loc("search_bar_bed_y"))
    utils.ctrl_a()
    utils.write(teleporter_name)

    time.sleep(0.2*settings.sleep_constant)
    windows.click(variables.get_pixel_loc("first_bed_slot_x"),variables.get_pixel_loc("first_bed_slot_y"))
    time.sleep(0.2*settings.sleep_constant)
    windows.click(variables.get_pixel_loc("spawn_button_x"),variables.get_pixel_loc("spawn_button_y"))
    count = 0
    while white_flash() == False and count < 20:
        count += 1
        time.sleep(0.1)
    count = 0          
    while white_flash() == True and count < 100:    
        time.sleep(0.1)          # would cause a inf loop
    count = 0

    while template.check_template_no_bounds("tribelog_check",0.8) == False and count < 100: # stopping inf loops 
        utils.press_key("ShowTribeManager")
        time.sleep(0.1)
        count += 1

    close_tribelog()
    
    time.sleep(0.4*settings.sleep_constant)
    if settings.singleplayer: # correcting for singleplayers wierd tp mechanics
        utils.current_pitch = 0
        utils.turn_down(80)
    utils.turn_up(80)
    utils.set_yaw(stationdata.yaw)
    #utils.pitch_zero() # correcting pitch back to 0 from looking down at the tp
    time.sleep(0.4*settings.sleep_constant)
    utils.press_key("Run")

def teleport_default(teleporter_name): # param teleporter_name incase of unable to default
    
    ccc_data_before = console_ccc()
    utils.press_key("Reload")

    time.sleep(1)          
    while white_flash() == True: #dont need white flash== False as if we are in render white flash will not appear on the screen   
        time.sleep(0.1)

    count = 0
    while template.check_template("tribelog_check",0.8) == False and count < 100: # stopping inf loops 
        utils.press_key("ShowTribeManager")
        time.sleep(0.1)
        count += 1

    close_tribelog()
    time.sleep(0.2)

    ccc_data_after = console_ccc()
    result = [a == b for a, b in zip(ccc_data_after[:3], ccc_data_before[:3])]

    if not (False in result):

        time.sleep(0.4)
        utils.pitch_zero()
        time.sleep(0.4)
        utils.turn_down(80)
        time.sleep(0.5)
        teleport_not_default(teleporter_name)

        

if __name__ == "__main__":
    time.sleep(2)
    render.enter_tekpod()
    pass



   