from abaqusConstants import *
from abaqusGui import *
from kernelAccess import mdb, session
import os

thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)


###########################################################################
# Class definition
###########################################################################

class SurrogateTipsDB(AFXDataDialog):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, form):

        # Construct the base class.
        #

        AFXDataDialog.__init__(self, form, 'SurrogateTips',
            self.CANCEL, DIALOG_ACTIONS_SEPARATOR)

        cancelBtn = self.getActionButton(self.ID_CLICKED_CANCEL)
        cancelBtn.setText('Cancel')


        fileName = os.path.join(thisDir, 'SurrogateTips.png')
        icon = afxCreatePNGIcon(fileName)
        FXLabel(p=self, text='', ic=icon)