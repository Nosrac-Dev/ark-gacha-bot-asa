import ASA.stations
import ASA.stations.custom_stations
import ASA.strucutres
import ASA.strucutres.teleporter
import template
import logs.gachalogs as logs
import utils
import windows
import variables
import time 
import settings
import ASA.config 
import ASA.strucutres.inventory
import ASA.player.player_inventory
import bot.config
import json

def load_resolution_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

#Steps
    # fill inventory #prototype complete
    # access transmiter
    # search Depo server prototype complete
    # attempt transfer prototype complete
    # check for 'items not ready'
    # if 'items not ready' maybe lay in tek pod if not retry every minut
    # transfer
    # wait for beds
    # spawn in #recycle from gacha code
    # deposit
    #     loop
    #     access transmiter
    #     Search origin server
    #     check for 'items not ready' 
    #     if 'items not ready' redeposit
    # transfer 
    # wait for beds 
    # sPAWn #recycle from gacha code
    # deposit #recycle from gacha code
    # repeat


def dedi_deposit(height): #added extra 5 degrees turning 6/10/25  N0s
    if height == 3:
        logs.logger.debug("Deposit top row") #Bitbucket
        time.sleep(1*settings.sleep_constant)
        utils.turn_up(15)
        utils.turn_left(15)
        time.sleep(1.3*settings.sleep_constant)
        utils.press_key("Use")
        time.sleep(1.3*settings.sleep_constant)
        utils.press_key("Use")
        utils.turn_right(50)
        time.sleep(1.3*settings.sleep_constant)
        utils.press_key("Use")
        time.sleep(1.3*settings.sleep_constant)
        utils.press_key("Use")
        utils.turn_left(35)
        utils.turn_down(15)
        time.sleep(1.3*settings.sleep_constant)

    logs.logger.debug("Deposit middle row") #Bitbucket
    utils.turn_left(15)
    #utils.press_key("Crouch")
    time.sleep(1.3*settings.sleep_constant)
    utils.press_key("Use")
    time.sleep(1.3*settings.sleep_constant)
    utils.press_key("Use")
    utils.turn_right(50)
    time.sleep(1.3*settings.sleep_constant)
    utils.press_key("Use")
    time.sleep(1.3*settings.sleep_constant)
    utils.press_key("Use")
    logs.logger.debug("Deposit bottom row") #Bitbucket
    utils.turn_down(25)
    time.sleep(1.3*settings.sleep_constant)
    utils.press_key("Use")
    time.sleep(1.3*settings.sleep_constant)
    utils.press_key("Use")
    utils.turn_left(50)
    time.sleep(1.3*settings.sleep_constant)
    utils.press_key("Use")
    time.sleep(1.4*settings.sleep_constant)
    utils.press_key("Use")
    utils.press_key("Run")
    #utils.turn_up(35)
    #utils.turn_right(15)
    utils.zero()
    time.sleep(1.1*settings.sleep_constant)


def dedi_withdraw(height): #Nosrac
    if height == 3:
        logs.logger.debug("withdraw top row") #Bitbucket
        utils.turn_up(15)
        utils.turn_left(15)
        time.sleep(0.3*settings.sleep_constant)
        withdraw()
        utils.turn_right(50)
        time.sleep(0.3*settings.sleep_constant)
        withdraw()
        utils.turn_left(35)
        utils.turn_down(15)
        time.sleep(0.3*settings.sleep_constant)

    logs.logger.debug("Deposit middle row") #Bitbucket
    utils.turn_left(15)
    #utils.press_key("Crouch")
    time.sleep(0.3*settings.sleep_constant)
    withdraw()
    utils.turn_right(50)
    time.sleep(0.3*settings.sleep_constant)
    withdraw()
    logs.logger.debug("Deposit bottom row") #Bitbucket
    utils.turn_down(27)
    time.sleep(0.3*settings.sleep_constant)
    withdraw()
    utils.turn_left(50)
    time.sleep(0.3*settings.sleep_constant)
    withdraw()
    utils.press_key("Run")
    utils.turn_up(35)
    utils.turn_right(15)
    time.sleep(0.1*settings.sleep_constant)

def withdraw():
    ASA.strucutres.inventory.open()
    time.sleep(1.3*settings.sleep_constant)
    if template.template_await_true(template.check_template,2,"dedicated_storage",0.7):
    #if template.check_template("dedi",0.7):   
        ASA.strucutres.inventory.transfer_all_from()
        time.sleep(1.2*settings.sleep_constant)
        ASA.strucutres.inventory.close()


# def vault_deposit(items, metadata):
#     logs.logger.info("Deposit in vaults") #Bitbucket

#     side = metadata.side
#     if side == "right":
#         turn_constant = 1
#     else:
#         turn_constant = -1
#     utils.turn_right(90*turn_constant)
#     time.sleep(0.2*settings.sleep_constant)
#     ASA.strucutres.inventory.open()
#     if not template.template_await_true(template.check_template,1,"vault",0.7):
#         logs.logger.error(f"{side} vault was not opened retrying now ")
#         ASA.strucutres.inventory.close()
#         utils.zero()
#         utils.set_yaw(metadata.yaw)
#         utils.turn_right(90*turn_constant)
#         time.sleep(0.2*settings.sleep_constant)
#         ASA.strucutres.inventory.open()
#     if template.template_await_true(template.check_template,1,"inventory",0.7):
#         time.sleep(0.1*settings.sleep_constant)
#         for x in range(len(items)):
#             ASA.player.player_inventory.search_in_inventory(items[x])
#             ASA.player.player_inventory.transfer_all_inventory()
#             time.sleep(0.3*settings.sleep_constant)
#         ASA.strucutres.inventory.close()
#         time.sleep(0.2*settings.sleep_constant)
#     utils.turn_left(90*turn_constant)
#     time.sleep(0.2*settings.sleep_constant)

# def drop_useless():
#     ASA.player.player_inventory.open()
#     if template.check_template("inventory",0.7):
#         ASA.player.player_inventory.drop_all_inv()
#         time.sleep(0.2*settings.sleep_constant)
#     ASA.player.player_inventory.close()

# def depo_grinder(metadata):
#     logs.logger.info("Deposit Grinder") #Bitbucket

#     utils.turn_right(180)
#     time.sleep(0.5*settings.sleep_constant)
#     ASA.strucutres.inventory.open()
#     attempt = 0
#     while not template.template_await_true(template.check_template,1,"grinder",0.7):
#         attempt += 1
#         logs.logger.error("couldnt open up the grinder while trying to deposit")
#         ASA.strucutres.inventory.close()
#         utils.zero()
#         utils.set_yaw(metadata.yaw)
#         utils.turn_right(180)
#         time.sleep(0.5*settings.sleep_constant)
#         ASA.strucutres.inventory.open()
#         if attempt >= bot.config.grinder_attempts:
#             logs.logger.error(f"while trying to deposit we couldnt access grinder")
#             break

#     if template.check_template("grinder",0.7):
#         ASA.player.player_inventory.transfer_all_inventory()
#         time.sleep(0.3*settings.sleep_constant)
#         windows.click(variables.get_pixel_loc("dedi_withdraw_x"),variables.get_pixel_loc("dedi_withdraw_y")) #this is pressing the grind all button 
#         time.sleep(0.1*settings.sleep_constant)
#         windows.click(variables.get_pixel_loc("dedi_withdraw_x"),variables.get_pixel_loc("dedi_withdraw_y")) #this is pressing the grind all button #Bitbucket Added second click
#         time.sleep(0.3*settings.sleep_constant)
#         ASA.strucutres.inventory.close()
#     template.template_await_false(template.check_template,1,"inventory",0.7)
#     time.sleep(0.2*settings.sleep_constant)
#     utils.turn_right(180)

# def collect_grindables(metadata):
#     utils.turn_right(90)
#     time.sleep(0.3*settings.sleep_constant) # sleep stops the grinder from opening the dedis on accident 
#     ASA.strucutres.inventory.open()
#     attempt = 0
#     while not template.template_await_true(template.check_template,1,"grinder",0.7):
#         attempt += 1
#         logs.logger.error("couldnt open up the grinder while trying to deposit")
#         ASA.strucutres.inventory.close()
#         utils.zero()
#         utils.set_yaw(metadata.yaw)
#         utils.turn_right(90)
#         time.sleep(0.5*settings.sleep_constant)
#         ASA.strucutres.inventory.open()
#         if attempt >= bot.config.grinder_attempts:
#             logs.logger.error(f"while trying to deposit we couldnt access grinder")
#             break

#     if template.check_template("grinder",0.7):
#         ASA.strucutres.inventory.transfer_all_from()
#         time.sleep(0.2*settings.sleep_constant)
#         ASA.strucutres.inventory.close()
#     template.template_await_false(template.check_template,1,"inventory",0.7)
#     time.sleep(0.2*settings.sleep_constant)
#     utils.turn_left(90)
#     time.sleep(0.5*settings.sleep_constant) # stopping hitting E on the fabricator and turing it off
#     dedi_deposit(settings.height_grind)
#     time.sleep(0.2*settings.sleep_constant)
#     drop_useless()

# def vaults(metadata):
#     vaults_data = load_resolution_data("json_files/vaults.json")
#     for entry_vaults in vaults_data:
#         name = entry_vaults["name"]
#         side = entry_vaults["side"]
#         items = entry_vaults["items"]
#         metadata.side = side
#         logs.logger.debug(f"openening up {name} on the {side} side to depo{items}")
#         vault_deposit(items,metadata)

# def deposit_all(metadata):
#     utils.pitch_zero()
#     utils.set_yaw(metadata.yaw)
#     logs.logger.debug("opening crystals")
#     open_crystals()
#     logs.logger.debug("depositing in ele dedi")
#     dedi_deposit(settings.height_ele)
#     vaults(metadata)
#     if settings.height_grind != 0:
#         logs.logger.debug("depositing in grinder")
#         depo_grinder(metadata)
#         grindables_metadata = ASA.stations.custom_stations.get_station_metadata(settings.grindables)
#         ASA.strucutres.teleporter.teleport_not_default(grindables_metadata)
#         logs.logger.debug("collecting grindables")
#         collect_grindables(grindables_metadata)
#     else:
#         drop_useless()


