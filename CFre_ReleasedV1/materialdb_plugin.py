#!/usr/bin/python
#-*-coding: UTF-8-*-
from abaqusGui import *
from abaqusConstants import ALL
import osutils, os

###########################################################################
# Class definition
###########################################################################

class materialdb_plugin(AFXForm):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, owner):
        
        # Construct the base class.
        #
        AFXForm.__init__(self, owner)
        self.radioButtonGroups = {}

        self.cmd = AFXGuiCommand(mode=self, method='',
            objectName='', registerQuery=False)
        pickedDefault = ''
        self.mattableKw = AFXTableKeyword(self.cmd, 'mattable', True)
        self.mattableKw.setColumnType(0, AFXTABLE_TYPE_STRING)
        self.mattableKw.setColumnType(1, AFXTABLE_TYPE_FLOAT)
        self.mattableKw.setColumnType(2, AFXTABLE_TYPE_FLOAT)
        self.mattableKw.setColumnType(3, AFXTABLE_TYPE_FLOAT)
        self.mattableKw.setColumnType(4, AFXTABLE_TYPE_FLOAT)
        self.mattableKw.setColumnType(5, AFXTABLE_TYPE_FLOAT)
        self.mattableKw.setColumnType(6, AFXTABLE_TYPE_FLOAT)
        self.searchnameKw = AFXStringKeyword(self.cmd, 'searchname', True, '')

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getFirstDialog(self):

        import materialdbDB
        return materialdbDB.materialdbDB(self)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def doCustomChecks(self):

        # Try to set the appropriate radio button on. If the user did
        # not specify any buttons to be on, do nothing.
        #
        for kw1,kw2,d in self.radioButtonGroups.values():
            try:
                value = d[ kw1.getValue() ]
                kw2.setValue(value)
            except:
                pass
        return True

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def okToCancel(self):

        # No need to close the dialog when a file operation (such
        # as New or Open) or model change is executed.
        #
        return False
