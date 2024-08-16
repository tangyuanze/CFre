from abaqusGui import *
from abaqusConstants import ALL
import osutils, os


###########################################################################
# Class definition
###########################################################################

class CFre_ReleasedV1_plugin(AFXForm):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, owner):
        
        # Construct the base class.
        #
        AFXForm.__init__(self, owner)
        self.radioButtonGroups = {}

        self.cmd = AFXGuiCommand(mode=self, method='ReliabilityFunction',
            objectName='CFre_ReleasedV1', registerQuery=False)
        pickedDefault = ''
        self.MnKw = AFXStringKeyword(self.cmd, 'Mn', True)
        self.PnKw = AFXStringKeyword(self.cmd, 'Pn', True)
        self.MaKw = AFXStringKeyword(self.cmd, 'Ma', True, 'GH4169')
        self.JnKw = AFXStringKeyword(self.cmd, 'Jn', True, 'Job-1')
        self.nCpusKw = AFXIntKeyword(self.cmd, 'nCpus', True, 8)
        self.STKw = AFXIntKeyword(self.cmd, 'ST', True, 1)
        self.tempKw = AFXBoolKeyword(self.cmd, 'temp', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.LLIKw = AFXBoolKeyword(self.cmd, 'LLI', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.SDIKw = AFXBoolKeyword(self.cmd, 'SDI', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.PDIDKw = AFXBoolKeyword(self.cmd, 'PDID', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.loadKw = AFXBoolKeyword(self.cmd, 'load', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.geomKw = AFXBoolKeyword(self.cmd, 'geom', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.densityKw = AFXBoolKeyword(self.cmd, 'density', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.conductivityKw = AFXBoolKeyword(self.cmd, 'conductivity', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.expansionKw = AFXBoolKeyword(self.cmd, 'expansion', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.EKw = AFXBoolKeyword(self.cmd, 'E', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.uKw = AFXBoolKeyword(self.cmd, 'u', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.wfcritKw = AFXBoolKeyword(self.cmd, 'wfcrit', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.n1Kw = AFXBoolKeyword(self.cmd, 'n1', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.faiKw = AFXBoolKeyword(self.cmd, 'fai', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.nbAKw = AFXBoolKeyword(self.cmd, 'nbA', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.nbnKw = AFXBoolKeyword(self.cmd, 'nbn', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.nbmKw = AFXBoolKeyword(self.cmd, 'nbm', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.XsigmaKw = AFXBoolKeyword(self.cmd, 'Xsigma', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.XepsilonKw = AFXBoolKeyword(self.cmd, 'Xepsilon', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.roKKw = AFXBoolKeyword(self.cmd, 'roK', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.ronKw = AFXBoolKeyword(self.cmd, 'ron', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.D1Kw = AFXStringKeyword(self.cmd, 'D1', True, 'ND')
        self.C1Kw = AFXFloatKeyword(self.cmd, 'C1', True, 0.05)
        self.D2Kw = AFXStringKeyword(self.cmd, 'D2', True, 'ND')
        self.C2Kw = AFXFloatKeyword(self.cmd, 'C2', True, 0.05)
        self.D5Kw = AFXStringKeyword(self.cmd, 'D5', True, 'ND')
        self.C5Kw = AFXFloatKeyword(self.cmd, 'C5', True, 0.05)
        self.FnKw = AFXStringKeyword(self.cmd, 'Fn', True, 'Solid extrude-1')
        self.keysKw = AFXObjectKeyword(self.cmd, 'keys', TRUE, pickedDefault)
        self.valuesKw = AFXStringKeyword(self.cmd, 'values', True, '0')
        self.C3Kw = AFXFloatKeyword(self.cmd, 'C3', True, 0.00033)
        self.dpthKw = AFXStringKeyword(self.cmd, 'dpth', True, '')
        self.loadnameKw = AFXStringKeyword(self.cmd, 'loadname', True, 'Load-1')
        self.direcKw = AFXStringKeyword(self.cmd, 'direc', True, 'Magnitude')
        self.val_loadKw = AFXFloatKeyword(self.cmd, 'val_load', True, 0)
        self.C4Kw = AFXFloatKeyword(self.cmd, 'C4', True, 0.1)
        self.dwellKw = AFXStringKeyword(self.cmd, 'dwell', True, '')
        self.ampKw = AFXStringKeyword(self.cmd, 'amp', True, '')
        self.C42Kw = AFXStringKeyword(self.cmd, 'C42', True, '')
        if not self.radioButtonGroups.has_key('train'):
            self.trainKw1 = AFXIntKeyword(None, 'trainDummy', True)
            self.trainKw2 = AFXStringKeyword(self.cmd, 'train', True)
            self.radioButtonGroups['train'] = (self.trainKw1, self.trainKw2, {})
        self.radioButtonGroups['train'][2][155] = 'No Training'
        self.trainKw1.setValue(155)
        if not self.radioButtonGroups.has_key('train'):
            self.trainKw1 = AFXIntKeyword(None, 'trainDummy', True)
            self.trainKw2 = AFXStringKeyword(self.cmd, 'train', True)
            self.radioButtonGroups['train'] = (self.trainKw1, self.trainKw2, {})
        self.radioButtonGroups['train'][2][156] = 'Train with the Data from FEM'
        if not self.radioButtonGroups.has_key('train'):
            self.trainKw1 = AFXIntKeyword(None, 'trainDummy', True)
            self.trainKw2 = AFXStringKeyword(self.cmd, 'train', True)
            self.radioButtonGroups['train'] = (self.trainKw1, self.trainKw2, {})
        self.radioButtonGroups['train'][2][157] = 'Train with the Data from .xls File'
        self.xlsnameKw = AFXStringKeyword(self.cmd, 'xlsname', True, '')
        if not self.radioButtonGroups.has_key('ml'):
            self.mlKw1 = AFXIntKeyword(None, 'mlDummy', True)
            self.mlKw2 = AFXStringKeyword(self.cmd, 'ml', True)
            self.radioButtonGroups['ml'] = (self.mlKw1, self.mlKw2, {})
        self.radioButtonGroups['ml'][2][158] = 'Support Vector Regression (SVR)'
        if not self.radioButtonGroups.has_key('ml'):
            self.mlKw1 = AFXIntKeyword(None, 'mlDummy', True)
            self.mlKw2 = AFXStringKeyword(self.cmd, 'ml', True)
            self.radioButtonGroups['ml'] = (self.mlKw1, self.mlKw2, {})
        self.radioButtonGroups['ml'][2][159] = 'Extreme Learning Machine (ELM)'
        if not self.radioButtonGroups.has_key('ml'):
            self.mlKw1 = AFXIntKeyword(None, 'mlDummy', True)
            self.mlKw2 = AFXStringKeyword(self.cmd, 'ml', True)
            self.radioButtonGroups['ml'] = (self.mlKw1, self.mlKw2, {})
        self.radioButtonGroups['ml'][2][160] = 'Artificial Neural Network (ANN)'
        if not self.radioButtonGroups.has_key('ml'):
            self.mlKw1 = AFXIntKeyword(None, 'mlDummy', True)
            self.mlKw2 = AFXStringKeyword(self.cmd, 'ml', True)
            self.radioButtonGroups['ml'] = (self.mlKw1, self.mlKw2, {})
        self.radioButtonGroups['ml'][2][161] = 'General Regression Neural Network (GRNN)'
        self.EXKw = AFXBoolKeyword(self.cmd, 'EX', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.sampleKw = AFXIntKeyword(self.cmd, 'sample', True, 0)
        self.lifeKw = AFXBoolKeyword(self.cmd, 'life', AFXBoolKeyword.TRUE_FALSE, True, True)
        self.mcsKw = AFXBoolKeyword(self.cmd, 'mcs', AFXBoolKeyword.TRUE_FALSE, True, True)
        self.correKw = AFXBoolKeyword(self.cmd, 'corre', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.pointKw = AFXStringKeyword(self.cmd, 'point', True, '')
        self.PfKw = AFXBoolKeyword(self.cmd, 'Pf', AFXBoolKeyword.TRUE_FALSE, True, True)
        self.jointKw = AFXBoolKeyword(self.cmd, 'joint', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.sensicurveKw = AFXBoolKeyword(self.cmd, 'sensicurve', AFXBoolKeyword.TRUE_FALSE, True, True)
        self.sensiKw = AFXStringKeyword(self.cmd, 'sensi', True, '')
        self.para1Kw = AFXBoolKeyword(self.cmd, 'para1', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.para6Kw = AFXBoolKeyword(self.cmd, 'para6', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.para2Kw = AFXBoolKeyword(self.cmd, 'para2', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.para7Kw = AFXBoolKeyword(self.cmd, 'para7', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.para3Kw = AFXBoolKeyword(self.cmd, 'para3', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.para8Kw = AFXBoolKeyword(self.cmd, 'para8', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.para4Kw = AFXBoolKeyword(self.cmd, 'para4', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.para9Kw = AFXBoolKeyword(self.cmd, 'para9', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.para5Kw = AFXBoolKeyword(self.cmd, 'para5', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.para10Kw = AFXBoolKeyword(self.cmd, 'para10', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.multi1Kw = AFXStringKeyword(self.cmd, 'multi1', True)
        self.range1Kw = AFXStringKeyword(self.cmd, 'range1', True, '')

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getFirstDialog(self):

        import cFre_ReleasedV1DB
        return cFre_ReleasedV1DB.CFre_ReleasedV1DB(self)

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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Register the plug-in
#
thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)

toolset = getAFXApp().getAFXMainWindow().getPluginToolset()
toolset.registerGuiMenuButton(
    buttonText='Creep-Fatigue Analysis|Reliability', 
    object=CFre_ReleasedV1_plugin(toolset),
    messageId=AFXMode.ID_ACTIVATE,
    icon=None,
    kernelInitString='import CFre_ReleasedV1',
    applicableModules=ALL,
    version='N/A',
    author='N/A',
    description='N/A',
    helpUrl='N/A'
)
