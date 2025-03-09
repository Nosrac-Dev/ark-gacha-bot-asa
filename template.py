import screen
import numpy as np
import cv2
import discordbot
import settings
import time

roi_regions = {
    "bed_radical": {"start_x":1120, "start_y":345 ,"width":250 ,"height":250},
    "beds_title": {"start_x":100, "start_y":100 ,"width":740 ,"height":180},
    "console": {"start_x":0, "start_y":1400 ,"width":50 ,"height":40},
    "crop_plot": {"start_x":1100, "start_y":250 ,"width":310 ,"height":150},
    "crystal_in_hotbar": {"start_x":750, "start_y":1250 ,"width":1060 ,"height":250},
    "death_regions": {"start_x":100, "start_y":100 ,"width":700 ,"height":200},
    "dedi": {"start_x":1100, "start_y":245 ,"width":355 ,"height":70},
    "vault": {"start_x":1100, "start_y":245 ,"width":355 ,"height":150},
    "grinder": {"start_x":1100, "start_y":245 ,"width":355 ,"height":70},
    "exit_resume": {"start_x":550, "start_y":450 ,"width":1670 ,"height":880},
    "inventory": {"start_x":200, "start_y":125 ,"width":360 ,"height":150},
    "ready_clicked_bed": {"start_x":580, "start_y":250 ,"width":150 ,"height":1000},
    "seed_inv": {"start_x":550, "start_y":450 ,"width":1670 ,"height":880},
    "slot_capped": {"start_x":2240, "start_y":1314 ,"width":150 ,"height":100},
    "teleporter_title": {"start_x":200, "start_y":135 ,"width":405 ,"height":185},
    "tribelog_check": {"start_x":1150, "start_y":35 ,"width":150 ,"height":150},
    "waiting_inv": {"start_x":2000, "start_y":100 ,"width":500,"height":250},
    "bed_icon": {"start_x":800, "start_y":200 ,"width":1690 ,"height":1100},
    "teleporter_icon": {"start_x":800, "start_y":200 ,"width":1690 ,"height":1100},
    "teleporter_icon_pressed": {"start_x":800, "start_y":200 ,"width":1690 ,"height":1100},
    "first_slot" :{"start_x": 220, "start_y": 305, "width": 130, "height": 130},
    "player_stats": {"start_x":1120, "start_y":240 ,"width":300 ,"height":900},
    "show_buff":{"start_x":1200, "start_y":1150 ,"width":200 ,"height":50},
    "snow_owl_pellet":{"start_x":200, "start_y":150 ,"width":600 ,"height":600}
}

def template_sleep(template:str,threshold:float,sleep_amount:float) -> bool:
    count = 0 
    while check_template(template,threshold) == False:
        if count >= sleep_amount * 10 : #  seconds of sleep
            break    
        time.sleep(0.1)
        count += 1
    return check_template(template,threshold)

def template_sleep_no_bounds(template:str,threshold:float,sleep_amount:float) -> bool:
    count = 0 
    while check_template_no_bounds(template,threshold) == False:
        if count >= sleep_amount * 10 : #  seconds of sleep
            break    
        time.sleep(0.1)
        count += 1
    return check_template_no_bounds(template,threshold)

def window_still_open(template:str,threshold:float,sleep_amount:float) -> bool: # oposite of the function above mainly to check if inventory is still open
    count = 0
    while check_template(template,threshold) == True:
        if count >= sleep_amount * 10 : #  seconds of sleep
            break    
        time.sleep(0.1)
        count += 1
    return check_template(template,threshold)

def window_still_open_no_bounds(template:str,threshold:float,sleep_amount:float) -> bool: # oposite of the function above mainly to check if inventory is still open
    count = 0
    while check_template_no_bounds(template,threshold) == True:
        if count >= sleep_amount * 10 : #  seconds of sleep
            break    
        time.sleep(0.1)
        count += 1
    return check_template_no_bounds(template,threshold)

def check_template(item:str, threshold:float) -> bool:
    
    region = roi_regions[item]
    if screen.screen_resolution == 1440:
        roi = screen.get_screen_roi(region["start_x"], region["start_y"], region["width"], region["height"])
    else:
        roi = screen.get_screen_roi(int(region["start_x"] * 0.75), int(region["start_y"] * 0.75), int(region["width"] * 0.75), int(region["height"] * 0.75))
        
    lower_boundary = np.array([0,30,200])
    upper_boundary = np.array([255,255,255])

    hsv = cv2.cvtColor(roi,cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv,lower_boundary,upper_boundary)
    masked_template = cv2.bitwise_and(roi, roi, mask= mask)
    gray_roi = cv2.cvtColor(masked_template, cv2.COLOR_BGR2GRAY)

    image = cv2.imread(f"icons{screen.screen_resolution}/{item}.png")
    hsv = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv,lower_boundary,upper_boundary)
    masked_template = cv2.bitwise_and(image, image, mask=mask)
    image = cv2.cvtColor(masked_template,cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_roi, image, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if max_val > threshold:
        #discordbot.gachalogs.debug(f"{item} found:{max_val}")
        return True
    #discordbot.gachalogs.debug(f"{item} not found:{max_val} threshold:{threshold}")
    return False

def check_template_no_bounds(item:str, threshold:float) -> bool:
    
    region = roi_regions[item]
    if screen.screen_resolution == 1440:
        roi = screen.get_screen_roi(region["start_x"], region["start_y"], region["width"], region["height"])
    else:
        roi = screen.get_screen_roi(int(region["start_x"] * 0.75), int(region["start_y"] * 0.75), int(region["width"] * 0.75), int(region["height"] * 0.75))
        
    lower_boundary = np.array([0,0,0])
    upper_boundary = np.array([255,255,255])

    hsv = cv2.cvtColor(roi,cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv,lower_boundary,upper_boundary)
    masked_template = cv2.bitwise_and(roi, roi, mask= mask)
    gray_roi = cv2.cvtColor(masked_template, cv2.COLOR_BGR2GRAY)

    image = cv2.imread(f"icons{screen.screen_resolution}/{item}.png")
    hsv = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv,lower_boundary,upper_boundary)
    masked_template = cv2.bitwise_and(image, image, mask=mask)
    image = cv2.cvtColor(masked_template,cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_roi, image, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if max_val > threshold:
        #discordbot.gachalogs.debugf"{item} found:{max_val}")
        return True
    #discordbot.gachalogs.debugf"{item} not found:{max_val} threshold:{threshold}")
    return False

def teleport_icon(threshold:float) -> bool:
    region = roi_regions["teleporter_icon"]
    if screen.screen_resolution == 1440:
        roi = screen.get_screen_roi(region["start_x"], region["start_y"], region["width"], region["height"])
    else:
        roi = screen.get_screen_roi(int(region["start_x"] * 0.75), int(region["start_y"] * 0.75), int(region["width"] * 0.75), int(region["height"] * 0.75))
        
    lower_boundary = np.array([0,0,150])
    upper_boundary = np.array([255,255,255])

    hsv = cv2.cvtColor(roi,cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv,lower_boundary,upper_boundary)
    masked_template = cv2.bitwise_and(roi, roi, mask= mask)
    gray_roi = cv2.cvtColor(masked_template, cv2.COLOR_BGR2GRAY)

    image = cv2.imread(f"icons{screen.screen_resolution}/teleporter_icon.png")
    hsv = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv,lower_boundary,upper_boundary)
    masked_template = cv2.bitwise_and(image, image, mask=mask)
    image = cv2.cvtColor(masked_template,cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_roi, image, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if max_val > threshold:
        #discordbot.gachalogs.debug(f"teleporter_icon found:{max_val}")
        return True
    #discordbot.gachalogs.debug(f"teleporter_icon not found:{max_val} threshold:{threshold}")
    return False

def inventory_first_slot(item:str,threshold:float) -> bool:
    region = roi_regions["first_slot"]
    if screen.screen_resolution == 1440:
        roi = screen.get_screen_roi(region["start_x"], region["start_y"], region["width"], region["height"])
    else:
        roi = screen.get_screen_roi(int(region["start_x"] * 0.75), int(region["start_y"] * 0.75), int(region["width"] * 0.75), int(region["height"] * 0.75))
    
    lower_boundary = np.array([0,0,0])
    upper_boundary = np.array([255,255,255])

    hsv = cv2.cvtColor(roi,cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv,lower_boundary,upper_boundary)
    masked_template = cv2.bitwise_and(roi, roi, mask= mask)
    gray_roi = cv2.cvtColor(masked_template, cv2.COLOR_BGR2GRAY)

    image = cv2.imread(f"icons{screen.screen_resolution}/{item}.png")
    hsv = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv,lower_boundary,upper_boundary)
    masked_template = cv2.bitwise_and(image, image, mask=mask)
    image = cv2.cvtColor(masked_template,cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_roi, image, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)


    if max_val > threshold:
        #discordbot.gachalogs.debug(f"{item} found:{max_val}")
        return True
    #discordbot.gachalogs.debug(f"{item} not found:{max_val} threshold:{threshold}")
    return False

def check_buffs(buff,threshold):
    region = roi_regions["player_stats"]
    if screen.screen_resolution == 1440:
        roi = screen.get_screen_roi(region["start_x"], region["start_y"], region["width"], region["height"])
    else:
        roi = screen.get_screen_roi(int(region["start_x"] * 0.75), int(region["start_y"] * 0.75), int(region["width"] * 0.75), int(region["height"] * 0.75))
    
    lower_boundary = np.array([0, 0, 180])
    upper_boundary = np.array([255,255,255])

    hsv = cv2.cvtColor(roi,cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv,lower_boundary,upper_boundary)
    masked_template = cv2.bitwise_and(roi, roi, mask= mask)
    gray_roi = cv2.cvtColor(masked_template, cv2.COLOR_BGR2GRAY)

    image = cv2.imread(f"icons{screen.screen_resolution}/{buff}.png")
    hsv = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv,lower_boundary,upper_boundary)
    masked_template = cv2.bitwise_and(image, image, mask=mask)
    image = cv2.cvtColor(masked_template,cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_roi, image, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if max_val > threshold:
        #discordbot.gachalogs.debug(f"{buff} found:{max_val}")
        return True
    #discordbot.gachalogs.debug(f"{buff} not found:{max_val} threshold:{threshold}")
    return False

if __name__ == "__main__":
    pass
    
    
