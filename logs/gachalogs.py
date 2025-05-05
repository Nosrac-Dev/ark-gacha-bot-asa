import logging

""" FOR TEMPLATE DEBUGGING AS DEBUG WILL CAUSE DISCORDBOT TO STOP WORKING"""
TEMPLATE_LEVEL = 5
logging.addLevelName(TEMPLATE_LEVEL,"TEMPLATE")
def template(self,message,*args,**kwargs):
    if self.isEnabledFor(TEMPLATE_LEVEL):
        self._log(TEMPLATE_LEVEL,message,args,**kwargs)

logging.Logger.template = template
logging_level = logging.INFO  

logger = logging.getLogger("Gacha")
if logging_level >= logging.CRITICAL:
    logging.basicConfig(filename="logs/logs.txt",level=logging_level,format="%(asctime)s - %(levelname)s - %(funcName)s - <@576182444592463892> - %(message)s",datefmt="%H:%M:%S")
else:
    logging.basicConfig(filename="logs/logs.txt",level=logging_level,format="%(asctime)s - %(levelname)s - %(funcName)s - %(message)s",datefmt="%H:%M:%S")
logger.setLevel(logging_level) 





