import ark
import variables
import time
import utils
import windows
import template
import settings
import pyautogui
import discordbot

def berry_collection():
    time.sleep(0.5)
    ark.open_structure()
    if template.template_sleep("inventory",0.7,2):
        ark.transfer_all_from()
        ark.close_inventory()
    time.sleep(0.5)

def berry_station():
    berry_collection()
    utils.turn_down(50)
    berry_collection()
    utils.turn_up(50)
    
def iguanadon(metadata):
    #put berries in
    time.sleep(0.2)
    utils.set_yaw(metadata.yaw)
    time.sleep(0.2)
    ark.open_structure()
    if template.check_template("inventory",0.7) == False:
        discordbot.gachalogs.warning("iguanadon failed to open retrying now")
        utils.zero()
        utils.set_yaw(metadata.yaw)
        time.sleep(0.2)
        ark.open_structure()
        time.sleep(0.2)
    time.sleep(0.3)
    if template.check_template("inventory",0.7):    
        ark.transfer_all_from() # transfering all berries currently inside
        time.sleep(0.3)
        ark.search_in_inventory(settings.berry_type)#iguanadon has 1450 weight for the 145 stacks of berries
        ark.transfer_all_inventory()
        time.sleep(0.3)
        ark.drop_all_inv()
        time.sleep(0.4)
        ark.close_inventory()
    time.sleep(0.2)
    if template.template_sleep("seed_inv",0.7,2) == False :
        discordbot.gachalogs.warning("iguanadon seeding hasnt been spotted re adding berries")
        ark.open_structure()
        ark.search_in_object(settings.berry_type)
        ark.transfer_all_from()
        ark.search_in_inventory(settings.berry_type)
        ark.transfer_all_inventory()
        ark.close_inventory()
        time.sleep(0.5)
    utils.press_key("Use")
    time.sleep(1) # wait time where iguanadon doesnt do anything
    ark.open_structure()
    if template.template_sleep("inventory",0.7,2):
        ark.search_in_object("seed")
        ark.transfer_all_from()
        time.sleep(0.5)
        ark.close_inventory()
    time.sleep(0.2)

def gacha_dropoff(metadata):
    direction = metadata.side
    time.sleep(0.2)
    if direction == "right":
        utils.turn_right(40) 
    else:
        utils.turn_left(40)
    time.sleep(0.3)    
    ark.open_structure()
    
    if template.check_template("inventory",0.7) == False: # assuming that the bot didnt turn properly
        discordbot.gachalogs.warning("gacha failed to open retrying now")
        utils.zero()
        utils.set_yaw(metadata.yaw)
        if direction == "right":
            utils.turn_right(40) 
        else:
            utils.turn_left(40)
        time.sleep(0.2)
        ark.open_structure()

    ark.transfer_all_from()
    time.sleep(0.5)
    temp = False
    if template.template_sleep_no_bounds("slot_capped",0.7,0.4):
        ark.drop_all_obj()
        ark.search_in_inventory("pell")
        time.sleep(0.2)
        if not template.template_sleep_no_bounds("snow_owl_pellet",0.5,1):
            ark.close_inventory()
            time.sleep(0.2)
            utils.turn_right(180)
            time.sleep(0.2)
            ark.open_inventory()
            time.sleep(0.2)
            ark.search_in_inventory("seed")
            temp = True
        windows.click(variables.get_pixel_loc("inv_slot_start_x")+50,variables.get_pixel_loc("inv_slot_start_y")+70)
        for x in range(8):
            windows.move_mouse(variables.get_pixel_loc("inv_slot_start_x")+50,variables.get_pixel_loc("inv_slot_start_y")+70)
            utils.press_key("DropItem")
            time.sleep(0.2)
        time.sleep(0.2)
    ark.close_inventory()
    time.sleep(0.5)    
    if temp:
        utils.turn_left(180)
        time.sleep(0.5)
    if direction == "right":
        utils.turn_right(90)
    else:
        utils.turn_left(90)

    time.sleep(0.3)
    ark.open_structure()
    if not template.template_sleep("crop_plot",0.7,2):
        discordbot.gachalogs.warning("could not open up the crop plot retrying now")
        utils.zero()
        utils.set_yaw(metadata.yaw)
        if direction == "right":
            utils.turn_right(130) 
        else:
            utils.turn_left(130)
        time.sleep(0.2)
        ark.open_structure()
    if template.check_template("crop_plot",0.7):
        ark.transfer_all_from()
        time.sleep(0.2)
        ark.transfer_all_inventory() #take out all input all # refreshing owl pelletes
        time.sleep(0.2)
        ark.close_inventory()
    time.sleep(0.4)

    if direction == "right":
        utils.turn_left(90)
    else:
        utils.turn_right(90)
    time.sleep(0.4)
    ark.open_structure()
    if template.template_sleep("inventory",0.7,2):
        ark.search_in_inventory("seed")
        time.sleep(0.2)
        ark.transfer_all_inventory()
        time.sleep(0.2)
        ark.search_in_inventory("pell")
        time.sleep(0.2)
        ark.transfer_all_inventory()
        time.sleep(0.4)
    ark.close_inventory()
    time.sleep(0.4)
    if direction == "right":
        utils.turn_left(40)
    else:
        utils.turn_right(40)
   
def gacha_collection(metadata): # this is used for gachas that have snails or phenixs 
    direction = metadata.side
    time.sleep(0.2)
    if direction == "right":
        utils.turn_right(40) 
    else:
        utils.turn_left(40)
    time.sleep(0.3)    
    ark.open_structure()

    if template.check_template("inventory",0.7) == False: # assuming that the bot didnt turn properly
        discordbot.gachalogs.warning("gacha failed to open retrying now")
        utils.zero()
        utils.set_yaw(metadata.yaw)
        if direction == "right":
            utils.turn_right(40) 
        else:
            utils.turn_left(40)
        time.sleep(0.2)
        ark.open_structure()

    ark.transfer_all_from()
    time.sleep(0.5)
    ark.close_inventory() 

    if direction == "right":
        utils.turn_left(40)
    else:
        utils.turn_right(40)
        
if __name__ == "__main__":
    time.sleep(2)
    iguanadon()
