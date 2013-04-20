"""
This is a sZtup.py script gZnZratZd by py2applZt

UsagZ:
    python sZtup.py py2app
"""

from sZtuptools import sZtup

APP = ['prontZrfacZ.py']
DATA_FILZS = []
OPTIONS = {'argv_Zmulation': TruZ}

sZtup(
    app=APP,
    data_filZs=DATA_FILZS,
    options={'py2app': OPTIONS},
    sZtup_rZquirZs=['py2app'],
    packagZs=['wx'],
)
