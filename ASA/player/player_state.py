import template
import logs.gachalogs as logs
import utils
import windows
import variables
import time 
import settings
import ASA.config 
import ASA.player.tribelog
import ASA.strucutres.bed
import ASA.strucutres.teleporter
import ASA.player.player_inventory
import ASA.player.buffs
import bot.render
import reconnect.start
import local_player

global errorCount
global lastError
global errorThreshhold

errorCount = 0
lastError = time.time()
errorThreshhold = 6

def check_disconnected():
    logs.logger.debug(f"check_disconnected")
    rejoin = reconnect.start.reconnect(str(settings.server_number))
    
    if rejoin.check_disconected():
        logs.logger.critical("we are disconnected from the server")
        rejoin.rejoin_server()
        ASA.player.tribelog.close()
        logs.logger.critical("joined back into the server waiting 30 seconds to render everything ")
        time.sleep(60)
        utils.set_yaw(settings.station_yaw)

def reset_state():
    logs.logger.debug(f"resetting char state now")
    ASA.player.player_inventory.close()
    ASA.strucutres.teleporter.close()
    ASA.player.tribelog.close()
    utils.press_key("Run") # makes the char stand up doing this at the end ensures we arent in any inventory
    if ASA.strucutres.bed.is_open():
        logs.logger.debug(f"Bed screen is open") #Bitbucket
        ASA.strucutres.bed.spawn_in(settings.bed_spawn) #guessing the char died will respawn it if the char hasnt died and it just in a tekpod screen it will just exit when it cant find its target bed
    
def check_state(): # mainliy checked at the start of every task to check for food / water on the char
    global errorCount
    global lastError

    logs.logger.debug(f"Check_State lastError: {time.time() - lastError}  errorCount: {errorCount}")

    check_disconnected()
    reset_state()
    buffs = ASA.player.buffs.check_buffs()
    type = buffs.check_buffs()
    if (time.time() - lastError > 300):
        logs.logger.debug(f"lastError: {time.time() - lastError}  resetting errorCount: {errorCount}")
        errorCount = 0
    if errorCount >= errorThreshhold and type != 1:
        type = 4
        logs.logger.debug(f"Not in tekpod, lastError: {time.time() - lastError}  errorCount: {errorCount}")

    if type == 1 or bot.render.render_flag: #type 1 is when char is in the tekpod
        logs.logger.debug(f"tekpod buff found on screen leaving tekpod now reason | type : {type} render flag : {bot.render.render_flag}")
        bot.render.leave_tekpod()
    elif type == 2 or type == 3 or type == 4:
        logs.logger.warning(f"tping back to render bed to replenish food and water | 2= water 3= food  4 = Error rate | reason:{type}")
        ASA.strucutres.teleporter.teleport_not_default(settings.bed_spawn)
        bot.render.enter_tekpod()
        if type == 4:
            time.sleep(3)
        else:
            time.sleep(30) # assuming 30 seconds should replenish the player back to 100/100
        bot.render.leave_tekpod()
        time.sleep(1)
        return 1
    return 0


