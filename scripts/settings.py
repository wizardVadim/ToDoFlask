import json
from pathlib import Path

def parseSettingsJSON(rootPath):
    return json.load(open(str(rootPath / 'settings.json')))

def getSettings():
    return settings

def getSetting(settingsName):
    return settings[settingsName]

rootPath = Path(__file__).resolve().parents[1]
settings = parseSettingsJSON(rootPath)