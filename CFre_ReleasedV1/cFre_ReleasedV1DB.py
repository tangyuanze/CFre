from abaqusConstants import *
from abaqusGui import *
from kernelAccess import mdb, session
import os
from surrogateTips_plugin import SurrogateTips_plugin  # tips
from materialdb_plugin import materialdb_plugin  # db

thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)


###########################################################################
# Class definition
###########################################################################

class CFre_ReleasedV1DB(AFXDataDialog):

    [ID_TIPS,ID_test]=range(AFXDataDialog.ID_LAST,AFXDataDialog.ID_LAST+2) # tips/db
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, form):

        self.SurrogateTips_plugin = SurrogateTips_plugin(form.getOwner())  # tips
        self.materialdb_plugin = materialdb_plugin(form.getOwner())  # db
        
        # Construct the base class.
        #

        AFXDataDialog.__init__(self, form, 'CFre',
            self.OK|self.CANCEL, DIALOG_ACTIONS_SEPARATOR)
            

        okBtn = self.getActionButton(self.ID_CLICKED_OK)
        okBtn.setText('OK')
            
        HFrame_20 = FXHorizontalFrame(p=self, opts=0, x=0, y=0, w=0, h=0,
            pl=3, pr=0, pt=0, pb=0)
        fileName = os.path.join(thisDir, 'LOGO.bmp')
        icon = afxCreateBMPIcon(fileName)
        FXLabel(p=HFrame_20, text='', ic=icon)
        TabBook_1 = FXTabBook(p=self, tgt=None, sel=0,
            opts=TABBOOK_NORMAL|LAYOUT_FILL_X|LAYOUT_FILL_Y,
            x=0, y=0, w=0, h=0, pl=DEFAULT_SPACING, pr=DEFAULT_SPACING,
            pt=DEFAULT_SPACING, pb=DEFAULT_SPACING)
        tabItem = FXTabItem(p=TabBook_1, text='FEM', ic=None, opts=TAB_TOP_NORMAL,
            x=0, y=0, w=0, h=0, pl=6, pr=6, pt=DEFAULT_PAD, pb=DEFAULT_PAD)
        TabItem_1 = FXVerticalFrame(p=TabBook_1,
            opts=FRAME_RAISED|FRAME_THICK|LAYOUT_FILL_X,
            x=0, y=0, w=0, h=0, pl=DEFAULT_SPACING, pr=DEFAULT_SPACING,
            pt=DEFAULT_SPACING, pb=DEFAULT_SPACING, hs=DEFAULT_SPACING, vs=DEFAULT_SPACING)
        GroupBox_10 = FXGroupBox(p=TabItem_1, text='FEM', opts=FRAME_GROOVE|LAYOUT_FILL_X|LAYOUT_FILL_Y)
        VFrame_7 = FXVerticalFrame(p=GroupBox_10, opts=LAYOUT_FILL_X, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0)
        HFrame_14 = FXHorizontalFrame(p=VFrame_7, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0)
        frame = FXHorizontalFrame(HFrame_14, 0, 0,0,0,0, 0,0,0,0)

        # Model combo
        # Since all forms will be canceled if the  model changes,
        # we do not need to register a query on the model.
        #
        self.RootComboBox_5 = AFXComboBox(p=frame, ncols=0, nvis=1, text='Model:', tgt=form.MnKw, sel=0)
        self.RootComboBox_5.setMaxVisible(10)

        names = mdb.models.keys()
        names.sort()
        for name in names:
            self.RootComboBox_5.appendItem(name)
        if not form.MnKw.getValue() in names:
            form.MnKw.setValue( names[0] )
        msgCount = 30
        form.MnKw.setTarget(self)
        form.MnKw.setSelector(AFXDataDialog.ID_LAST+msgCount)
        msgHandler = str(self.__class__).split('.')[-1] + '.onComboBox_5PartsChanged'
        exec('FXMAPFUNC(self, SEL_COMMAND, AFXDataDialog.ID_LAST+%d, %s)' % (msgCount, msgHandler) )

        # Parts combo
        #
        self.ComboBox_5 = AFXComboBox(p=frame, ncols=0, nvis=1, text='Part:', tgt=form.PnKw, sel=0)
        self.ComboBox_5.setMaxVisible(10)

        self.form = form
        VAligner_17 = AFXVerticalAligner(p=HFrame_14, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0)
        ComboBox_6 = AFXComboBox(p=HFrame_14, ncols=0, nvis=1, text='Material:', tgt=form.MaKw, sel=0)
        ComboBox_6.setMaxVisible(50)
        
        filename= os.path.join(thisDir, 'material_database.dat')
        f=file(filename,'r')
        k=1
        while True:
            line=f.readline()
            if len(line)==0:
                break
            data=line.strip().split(',')
            ComboBox_6.appendItem(text=data[0])
            k+=1
        ComboBox_6.appendItem(text='User Define')
        
        HFrame_15 = FXHorizontalFrame(p=VFrame_7, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=10, pb=0)
        AFXTextField(p=HFrame_15, ncols=7, labelText='Job Name:', tgt=form.JnKw, sel=0)
        spinner = AFXSpinner(HFrame_15, 2, ' CPUs:', form.nCpusKw, 0)
        spinner.setRange(1, 40)
        spinner.setIncrement(1)
        VAligner_18 = AFXVerticalAligner(p=HFrame_15, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0)
        AFXTextField(p=HFrame_15, ncols=4, labelText=' Sim. Times:', tgt=form.STKw, sel=0)
        FXCheckButton(p=HFrame_15, text=' Temp. ', tgt=form.tempKw, sel=0)
        FXMAPFUNC(self,SEL_COMMAND,self.ID_test,CFre_ReleasedV1DB.button)  # db
        FXButton(p=HFrame_15,text='Database',ic=None,tgt=self,sel=self.ID_test)  # db
        
        GroupBox_11 = FXGroupBox(p=TabItem_1, text='Reliability Criterion Selection', opts=FRAME_GROOVE|LAYOUT_FILL_X|LAYOUT_FILL_Y)
        FXCheckButton(p=GroupBox_11, text='Load-Life Interference (LLI)', tgt=form.LLIKw, sel=0)
        FXCheckButton(p=GroupBox_11, text='Strength-Damage Interference (SDI)', tgt=form.SDIKw, sel=0)
        FXCheckButton(p=GroupBox_11, text='Probabilistic Damage Interaction Diagram (PDID)', tgt=form.PDIDKw, sel=0)
        GroupBox_12 = FXGroupBox(p=TabItem_1, text='Independent Random Variables Selection', opts=FRAME_GROOVE|LAYOUT_FILL_X|LAYOUT_FILL_Y)
        VFrame_6 = FXVerticalFrame(p=GroupBox_12, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=5, pb=0)
        HFrame_11 = FXHorizontalFrame(p=VFrame_6, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0)
        l = FXLabel(p=HFrame_11, text='General:', opts=JUSTIFY_LEFT)
        l.setFont( getAFXFont(FONT_BOLD) )
        FXCheckButton(p=HFrame_11, text='load', tgt=form.loadKw, sel=0)
        FXCheckButton(p=HFrame_11, text='geom.', tgt=form.geomKw, sel=0)
        FXCheckButton(p=HFrame_11, text='dens.', tgt=form.densityKw, sel=0)
        FXCheckButton(p=HFrame_11, text='T. cond.', tgt=form.conductivityKw, sel=0)
        FXCheckButton(p=HFrame_11, text='T. expan.', tgt=form.expansionKw, sel=0)
        FXCheckButton(p=HFrame_11, text='E', tgt=form.EKw, sel=0)
        FXCheckButton(p=HFrame_11, text='u', tgt=form.uKw, sel=0)
        HFrame_12 = FXHorizontalFrame(p=VFrame_6, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0)
        l = FXLabel(p=HFrame_12, text='Creep:', opts=JUSTIFY_LEFT)
        l.setFont( getAFXFont(FONT_BOLD) )
        VAligner_11 = AFXVerticalAligner(p=HFrame_12, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=7, pt=0, pb=0)
        l = FXLabel(p=HFrame_12, text='SEDE:', opts=JUSTIFY_LEFT)
        VAligner_13 = AFXVerticalAligner(p=HFrame_12, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0)
        FXCheckButton(p=HFrame_12, text='wfcrit', tgt=form.wfcritKw, sel=0)
        VAligner_19 = AFXVerticalAligner(p=HFrame_12, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=4, pt=0, pb=0)
        FXCheckButton(p=HFrame_12, text='n1', tgt=form.n1Kw, sel=0)
        FXCheckButton(p=HFrame_12, text='fai', tgt=form.faiKw, sel=0)
        VAligner_15 = AFXVerticalAligner(p=HFrame_12, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=1, pt=0, pb=0)
        l = FXLabel(p=HFrame_12, text='N-B:', opts=JUSTIFY_LEFT)
        FXCheckButton(p=HFrame_12, text='A', tgt=form.nbAKw, sel=0)
        VAligner_16 = AFXVerticalAligner(p=HFrame_12, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0)
        FXCheckButton(p=HFrame_12, text='n', tgt=form.nbnKw, sel=0)
        FXCheckButton(p=HFrame_12, text='m', tgt=form.nbmKw, sel=0)
        HFrame_13 = FXHorizontalFrame(p=VFrame_6, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0)
        l = FXLabel(p=HFrame_13, text='Fatigue:', opts=JUSTIFY_LEFT)
        l.setFont( getAFXFont(FONT_BOLD) )
        l = FXLabel(p=HFrame_13, text='CPM:', opts=JUSTIFY_LEFT)
        VAligner_12 = AFXVerticalAligner(p=HFrame_13, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=3, pt=0, pb=0)
        FXCheckButton(p=HFrame_13, text='sigmaf', tgt=form.XsigmaKw, sel=0)
        FXCheckButton(p=HFrame_13, text='epsilonf', tgt=form.XepsilonKw, sel=0)
        VAligner_14 = AFXVerticalAligner(p=HFrame_13, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=8, pt=0, pb=0)
        l = FXLabel(p=HFrame_13, text='R-O:', opts=JUSTIFY_LEFT)
        FXCheckButton(p=HFrame_13, text='Kf', tgt=form.roKKw, sel=0)
        FXCheckButton(p=HFrame_13, text='nf', tgt=form.ronKw, sel=0)
        tabItem = FXTabItem(p=TabBook_1, text='Uncertainty', ic=None, opts=TAB_TOP_NORMAL,
            x=0, y=0, w=0, h=0, pl=6, pr=6, pt=DEFAULT_PAD, pb=DEFAULT_PAD)
        TabItem_3 = FXVerticalFrame(p=TabBook_1,
            opts=FRAME_RAISED|FRAME_THICK|LAYOUT_FILL_X,
            x=0, y=0, w=0, h=0, pl=DEFAULT_SPACING, pr=DEFAULT_SPACING,
            pt=DEFAULT_SPACING, pb=DEFAULT_SPACING, hs=DEFAULT_SPACING, vs=DEFAULT_SPACING)
        GroupBox_1 = FXGroupBox(p=TabItem_3, text='Material/Model Parameters', opts=FRAME_GROOVE|LAYOUT_FILL_X|LAYOUT_FILL_Y)
        HFrame_1 = FXHorizontalFrame(p=GroupBox_1, opts=LAYOUT_FILL_X, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0)
        GroupBox_5 = FXGroupBox(p=HFrame_1, text='Material', opts=FRAME_GROOVE|LAYOUT_FILL_X)
        ComboBox_1 = AFXComboBox(p=GroupBox_5, ncols=0, nvis=1, text='Dist. : ', tgt=form.D1Kw, sel=0)
        ComboBox_1.setMaxVisible(10)
        ComboBox_1.appendItem(text='ND')
        ComboBox_1.appendItem(text='LND')
        ComboBox_1.appendItem(text='2WD')
        ComboBox_1.appendItem(text='CONST')
        AFXTextField(p=GroupBox_5, ncols=7, labelText='CV:    ', tgt=form.C1Kw, sel=0)
        VAligner_1 = AFXVerticalAligner(p=HFrame_1, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=3, pt=0, pb=0)
        GroupBox_6 = FXGroupBox(p=HFrame_1, text=' Creep', opts=FRAME_GROOVE|LAYOUT_FILL_X)
        ComboBox_2 = AFXComboBox(p=GroupBox_6, ncols=0, nvis=1, text='Dist. : ', tgt=form.D2Kw, sel=0)
        ComboBox_2.setMaxVisible(10)
        ComboBox_2.appendItem(text='ND')
        ComboBox_2.appendItem(text='LND')
        ComboBox_2.appendItem(text='2WD')
        ComboBox_2.appendItem(text='CONST')
        AFXTextField(p=GroupBox_6, ncols=7, labelText='CV:    ', tgt=form.C2Kw, sel=0)
        VAligner_2 = AFXVerticalAligner(p=HFrame_1, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=3, pt=0, pb=0)
        GroupBox_7 = FXGroupBox(p=HFrame_1, text='Fatigue', opts=FRAME_GROOVE|LAYOUT_FILL_X)
        ComboBox_3 = AFXComboBox(p=GroupBox_7, ncols=0, nvis=1, text='Dist. : ', tgt=form.D5Kw, sel=0)
        ComboBox_3.setMaxVisible(10)
        ComboBox_3.appendItem(text='ND')
        ComboBox_3.appendItem(text='LND')
        ComboBox_3.appendItem(text='2WD')
        ComboBox_3.appendItem(text='CONST')
        AFXTextField(p=GroupBox_7, ncols=7, labelText='CV:    ', tgt=form.C5Kw, sel=0)
        GroupBox_2 = FXGroupBox(p=TabItem_3, text='Geometry', opts=FRAME_GROOVE|LAYOUT_FILL_X|LAYOUT_FILL_Y)
        HFrame_2 = FXHorizontalFrame(p=GroupBox_2, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0)
        AFXTextField(p=HFrame_2, ncols=14, labelText='Sketch Name:', tgt=form.FnKw, sel=0)
        VAligner_4 = AFXVerticalAligner(p=HFrame_2, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=20, pt=0, pb=0)
        pickHf = FXHorizontalFrame(p=HFrame_2, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0, hs=DEFAULT_SPACING, vs=DEFAULT_SPACING)
        # Note: Set the selector to indicate that this widget should not be
        #       colored differently from its parent when the 'Color layout managers'
        #       button is checked in the RSG Dialog Builder dialog.
        pickHf.setSelector(99)
        label = FXLabel(p=pickHf, text='Key Dimensions' + ' (None)', ic=None, opts=LAYOUT_CENTER_Y|JUSTIFY_LEFT)
        pickHandler = CFre_ReleasedV1DBPickHandler(form, form.keysKw, 'Pick the Key Dimensions', SKETCH_DIMENSIONS, MANY, label)
        icon = afxGetIcon('select', AFX_ICON_SMALL )
        FXButton(p=pickHf, text='\tPick Items in Viewport', ic=icon, tgt=pickHandler, sel=AFXMode.ID_ACTIVATE,
            opts=BUTTON_NORMAL|LAYOUT_CENTER_Y, x=0, y=0, w=0, h=0, pl=2, pr=2, pt=1, pb=1)
        HFrame_3 = FXHorizontalFrame(p=GroupBox_2, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0)
        AFXTextField(p=HFrame_3, ncols=10, labelText='Means:', tgt=form.valuesKw, sel=0)
        VAligner_3 = AFXVerticalAligner(p=HFrame_3, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=1, pt=0, pb=0)
        AFXTextField(p=HFrame_3, ncols=7, labelText='CV:', tgt=form.C3Kw, sel=0)
        VAligner_5 = AFXVerticalAligner(p=HFrame_3, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=19, pt=0, pb=0)
        AFXTextField(p=HFrame_3, ncols=8, labelText='(IF NEED)  Depth:', tgt=form.dpthKw, sel=0)
        GroupBox_3 = FXGroupBox(p=TabItem_3, text='Load', opts=FRAME_GROOVE|LAYOUT_FILL_X|LAYOUT_FILL_Y)
        HFrame_4 = FXHorizontalFrame(p=GroupBox_3, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0)
            
        AFXTextField(p=HFrame_4, ncols=16, labelText='Load Name:', tgt=form.loadnameKw, sel=0)
        
        
        HFrame_5 = FXHorizontalFrame(p=GroupBox_3, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0)
        ComboBox_4 = AFXComboBox(p=HFrame_5, ncols=0, nvis=1, text='Dir. :', tgt=form.direcKw, sel=0)
        ComboBox_4.setMaxVisible(10)
        ComboBox_4.appendItem(text='Magnitude')
        ComboBox_4.appendItem(text='CF1')
        ComboBox_4.appendItem(text='CF2')
        ComboBox_4.appendItem(text='CF3')
        ComboBox_4.appendItem(text='U1')
        ComboBox_4.appendItem(text='U2')
        ComboBox_4.appendItem(text='U3')
        ComboBox_4.appendItem(text='UR1')
        ComboBox_4.appendItem(text='UR2')
        ComboBox_4.appendItem(text='UR3')
        VAligner_8 = AFXVerticalAligner(p=HFrame_5, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=2, pt=0, pb=0)
        AFXTextField(p=HFrame_5, ncols=8, labelText='Means:', tgt=form.val_loadKw, sel=0)
        VAligner_9 = AFXVerticalAligner(p=HFrame_5, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=5, pt=0, pb=0)
        AFXTextField(p=HFrame_5, ncols=8, labelText='CV:', tgt=form.C4Kw, sel=0)
        HFrame_6 = FXHorizontalFrame(p=GroupBox_3, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0)
        AFXTextField(p=HFrame_6, ncols=8, labelText='(IF NEED)  Hold time:', tgt=form.dwellKw, sel=0)
        VAligner_10 = AFXVerticalAligner(p=HFrame_6, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=1, pt=0, pb=0)
        AFXTextField(p=HFrame_6, ncols=8, labelText='Amp. Name:', tgt=form.ampKw, sel=0)
        VAligner_7 = AFXVerticalAligner(p=HFrame_6, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=2, pt=0, pb=0)
        AFXTextField(p=HFrame_6, ncols=6, labelText='CV:', tgt=form.C42Kw, sel=0)
        tabItem = FXTabItem(p=TabBook_1, text='Surrogate Model', ic=None, opts=TAB_TOP_NORMAL,
            x=0, y=0, w=0, h=0, pl=6, pr=6, pt=DEFAULT_PAD, pb=DEFAULT_PAD)
        TabItem_4 = FXVerticalFrame(p=TabBook_1,
            opts=FRAME_RAISED|FRAME_THICK|LAYOUT_FILL_X,
            x=0, y=0, w=0, h=0, pl=DEFAULT_SPACING, pr=DEFAULT_SPACING,
            pt=DEFAULT_SPACING, pb=DEFAULT_SPACING, hs=DEFAULT_SPACING, vs=DEFAULT_SPACING)
        GroupBox_8 = FXGroupBox(p=TabItem_4, text='Data Source', opts=FRAME_GROOVE|LAYOUT_FILL_X|LAYOUT_FILL_Y)
        FXRadioButton(p=GroupBox_8, text='No Training', tgt=form.trainKw1, sel=155)
        FXRadioButton(p=GroupBox_8, text='Train with the Data from FEM', tgt=form.trainKw1, sel=156)
        HFrame_7 = FXHorizontalFrame(p=GroupBox_8, opts=LAYOUT_FILL_Y, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0)
        FXRadioButton(p=HFrame_7, text='Train with the Data from .xls File', tgt=form.trainKw1, sel=157)
        fileHandler = CFre_ReleasedV1DBFileHandler(form, 'xlsname', '(*.xls)')
        fileTextHf = FXHorizontalFrame(p=HFrame_7, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0, hs=DEFAULT_SPACING, vs=DEFAULT_SPACING)
        # Note: Set the selector to indicate that this widget should not be
        #       colored differently from its parent when the 'Color layout managers'
        #       button is checked in the RSG Dialog Builder dialog.
        fileTextHf.setSelector(99)
        AFXTextField(p=fileTextHf, ncols=10, labelText=':', tgt=form.xlsnameKw, sel=0,
            opts=AFXTEXTFIELD_STRING|LAYOUT_CENTER_Y)
        icon = afxGetIcon('fileOpen', AFX_ICON_SMALL )
        FXButton(p=fileTextHf, text='	Select File\nFrom Dialog', ic=icon, tgt=fileHandler, sel=AFXMode.ID_ACTIVATE,
            opts=BUTTON_NORMAL|LAYOUT_CENTER_Y, x=0, y=0, w=0, h=0, pl=1, pr=1, pt=1, pb=1)
        GroupBox_9 = FXGroupBox(p=TabItem_4, text='Surrogate Model Selection', opts=FRAME_GROOVE|LAYOUT_FILL_X|LAYOUT_FILL_Y)
        HFrame_99 = FXHorizontalFrame(p=GroupBox_9, opts=0, x=0, y=0, w=0, h=0, pl=0, pr=0, pt=0, pb=0)
        FXRadioButton(p=HFrame_99, text='Support Vector Regression (SVR)                                           ', tgt=form.mlKw1, sel=158)
        FXMAPFUNC(self,SEL_COMMAND,self.ID_TIPS,CFre_ReleasedV1DB.button) # tips
        FXButton(p=HFrame_99,text=' tips ',ic=None,tgt=self,sel=self.ID_TIPS) # tips
        FXRadioButton(p=GroupBox_9, text='Extreme Learning Machine (ELM)', tgt=form.mlKw1, sel=159)
        FXRadioButton(p=GroupBox_9, text='Artificial Neural Network (ANN)', tgt=form.mlKw1, sel=160)
        FXRadioButton(p=GroupBox_9, text='General Regression Neural Network (GRNN)', tgt=form.mlKw1, sel=161)
        if isinstance(GroupBox_9, FXHorizontalFrame):
            FXVerticalSeparator(p=GroupBox_9, x=0, y=0, w=0, h=0, pl=2, pr=2, pt=2, pb=2)
        else:
            FXHorizontalSeparator(p=GroupBox_9, x=0, y=0, w=0, h=0, pl=2, pr=2, pt=2, pb=2)
        HFrame_8 = FXHorizontalFrame(p=GroupBox_9, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0)
        l = FXLabel(p=HFrame_8, text='Tips :', opts=JUSTIFY_LEFT)
        l.setFont( getAFXFont(FONT_BOLD) )
        l = FXLabel(p=HFrame_8, text='ELM or ANN is recommended to perform with sample expansion.', opts=JUSTIFY_LEFT)
        FXCheckButton(p=GroupBox_9, text='Sample Expansion with SVR', tgt=form.EXKw, sel=0)
        AFXTextField(p=GroupBox_9, ncols=6, labelText='Size of Virtual Sample Generation:', tgt=form.sampleKw, sel=0)
        tabItem = FXTabItem(p=TabBook_1, text='Result Analysis', ic=None, opts=TAB_TOP_NORMAL,
            x=0, y=0, w=0, h=0, pl=6, pr=6, pt=DEFAULT_PAD, pb=DEFAULT_PAD)
        TabItem_2 = FXVerticalFrame(p=TabBook_1,
            opts=FRAME_RAISED|FRAME_THICK|LAYOUT_FILL_X,
            x=0, y=0, w=0, h=0, pl=DEFAULT_SPACING, pr=DEFAULT_SPACING,
            pt=DEFAULT_SPACING, pb=DEFAULT_SPACING, hs=DEFAULT_SPACING, vs=DEFAULT_SPACING)
        GroupBox_13 = FXGroupBox(p=TabItem_2, text='Damage and Life Evaluation', opts=FRAME_GROOVE|LAYOUT_FILL_X|LAYOUT_FILL_Y)
        VFrame_11 = FXVerticalFrame(p=GroupBox_13, opts=0, x=0, y=0, w=0, h=0,
            pl=5, pr=0, pt=0, pb=0)
        HFrame_22 = FXHorizontalFrame(p=VFrame_11, opts=LAYOUT_FILL_X, x=0, y=0, w=0, h=0, pl=0, pr=0, pt=0, pb=0)
        HFrame_222 = FXHorizontalFrame(p=VFrame_11, opts=LAYOUT_FILL_X, x=0, y=0, w=0, h=0, pl=0, pr=0, pt=0, pb=0)
        FXCheckButton(p=HFrame_22, text='Deterministic Life Evaluation              ', tgt=form.lifeKw, sel=0)
        AFXTextField(p=HFrame_22, ncols=14, labelText='    Target Points ', tgt=form.pointKw, sel=0)
        FXCheckButton(p=HFrame_222, text='MCS on Surrogate Model    ', tgt=form.mcsKw, sel=0)
        FXCheckButton(p=HFrame_222, text='Correlation Analysis of variables and life', tgt=form.correKw, sel=0)
        GroupBox_20 = FXGroupBox(p=TabItem_2, text='Relaibility Assessment', opts=FRAME_GROOVE|LAYOUT_FILL_X|LAYOUT_FILL_Y)
        HFrame_23 = FXHorizontalFrame(p=GroupBox_20, opts=0, x=0, y=0, w=0, h=0,
            pl=5, pr=0, pt=0, pb=0)
        FXCheckButton(p=HFrame_23, text='Design Life-Failure Probability Curve   ', tgt=form.PfKw, sel=0)
        FXCheckButton(p=HFrame_23, text='Joint Failure Assessment', tgt=form.jointKw, sel=0)
        GroupBox_19 = FXGroupBox(p=TabItem_2, text='Sensitivity Analysis', opts=FRAME_GROOVE|LAYOUT_FILL_X|LAYOUT_FILL_Y)
        HFrame_24 = FXHorizontalFrame(p=GroupBox_19, opts=0, x=0, y=0, w=0, h=0,
            pl=5, pr=0, pt=0, pb=0)
        FXCheckButton(p=HFrame_24, text='Curve with Different Reliability', tgt=form.sensicurveKw, sel=0)
        AFXTextField(p=HFrame_24, ncols=5, labelText='        Pie Chart at Reliability of ', tgt=form.sensiKw, sel=0)
        GroupBox_21 = FXGroupBox(p=TabItem_2, text='Influence of Uncertainties', opts=FRAME_GROOVE|LAYOUT_FILL_X|LAYOUT_FILL_Y)
        VFrame_15 = FXVerticalFrame(p=GroupBox_21, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0)
        HFrame_35 = FXHorizontalFrame(p=VFrame_15, opts=0, x=0, y=0, w=0, h=0,
            pl=5, pr=0, pt=0, pb=0)
        l = FXLabel(p=HFrame_35, text='                    Material', opts=JUSTIFY_LEFT)
        l = FXLabel(p=HFrame_35, text='      Creep', opts=JUSTIFY_LEFT)
        l = FXLabel(p=HFrame_35, text='       Fatigue', opts=JUSTIFY_LEFT)
        l = FXLabel(p=HFrame_35, text='     Geometry', opts=JUSTIFY_LEFT)
        l = FXLabel(p=HFrame_35, text='      Load', opts=JUSTIFY_LEFT)
        HFrame_33 = FXHorizontalFrame(p=VFrame_15, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0)
        l = FXLabel(p=HFrame_33, text='Case1/Case2 ', opts=JUSTIFY_LEFT)
        FXCheckButton(p=HFrame_33, text=' /', tgt=form.para1Kw, sel=0)
        FXCheckButton(p=HFrame_33, text='.   ', tgt=form.para6Kw, sel=0)
        FXCheckButton(p=HFrame_33, text=' /', tgt=form.para2Kw, sel=0)
        FXCheckButton(p=HFrame_33, text='.   ', tgt=form.para7Kw, sel=0)
        FXCheckButton(p=HFrame_33, text=' /', tgt=form.para3Kw, sel=0)
        FXCheckButton(p=HFrame_33, text='.   ', tgt=form.para8Kw, sel=0)
        FXCheckButton(p=HFrame_33, text=' /', tgt=form.para4Kw, sel=0)
        FXCheckButton(p=HFrame_33, text='.   ', tgt=form.para9Kw, sel=0)
        FXCheckButton(p=HFrame_33, text=' /', tgt=form.para5Kw, sel=0)
        FXCheckButton(p=HFrame_33, text='.', tgt=form.para10Kw, sel=0)
        HFrame_25 = FXHorizontalFrame(p=TabItem_2, opts=0, x=0, y=0, w=0, h=0,
            pl=5, pr=0, pt=5, pb=0)
        ComboBox_10 = AFXComboBox(p=HFrame_25, ncols=0, nvis=1, text='Multi-Conditions:  Variables', tgt=form.multi1Kw, sel=0)
        ComboBox_10.setMaxVisible(10)
        ComboBox_10.appendItem(text='Magnitude')
        ComboBox_10.appendItem(text='Hold_Time')
        ComboBox_10.appendItem(text='CV_Material')
        ComboBox_10.appendItem(text='CV_Creep')
        ComboBox_10.appendItem(text='CV_Fatigue')
        ComboBox_10.appendItem(text='CV_Geometry')
        ComboBox_10.appendItem(text='CV_Load')
        AFXTextField(p=HFrame_25, ncols=7, labelText='   Start,Stop,Num:', tgt=form.range1Kw, sel=0)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def show(self):

        AFXDataDialog.show(self)

        # Register a query on parts
        #
        self.currentModelName = getCurrentContext()['modelName']
        self.form.MnKw.setValue(self.currentModelName)
        mdb.models[self.currentModelName].parts.registerQuery(self.updateComboBox_5Parts)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def hide(self):

        AFXDataDialog.hide(self)

        mdb.models[self.currentModelName].parts.unregisterQuery(self.updateComboBox_5Parts)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onComboBox_5PartsChanged(self, sender, sel, ptr):

        self.updateComboBox_5Parts()
        return 1

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def updateComboBox_5Parts(self):

        modelName = self.form.MnKw.getValue()

        # Update the names in the Parts combo
        #
        self.ComboBox_5.clearItems()
        names = mdb.models[modelName].parts.keys()
        names.sort()
        for name in names:
            self.ComboBox_5.appendItem(name)
        if names:
            if not self.form.PnKw.getValue() in names:
                self.form.PnKw.setValue( names[0] )
        else:
            self.form.PnKw.setValue('')

        self.resize( self.getDefaultWidth(), self.getDefaultHeight() )

    def button(self,sender,sel,ptr): # tips/db
        if SELID(sel) == self.ID_TIPS:
            self.SurrogateTips_plugin.activate()
        elif SELID(sel) == self.ID_test:
            self.materialdb_plugin.activate()
        return 1

###########################################################################
# Class definition
###########################################################################

class CFre_ReleasedV1DBPickHandler(AFXProcedure):

        count = 0

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        def __init__(self, form, keyword, prompt, entitiesToPick, numberToPick, label):

                self.form = form
                self.keyword = keyword
                self.prompt = prompt
                self.entitiesToPick = entitiesToPick # Enum value
                self.numberToPick = numberToPick # Enum value
                self.label = label
                self.labelText = label.getText()

                AFXProcedure.__init__(self, form.getOwner(),type = AFXProcedure.SUBPROCEDURE)

                CFre_ReleasedV1DBPickHandler.count += 1
                self.setModeName('CFre_ReleasedV1DBPickHandler%d' % (CFre_ReleasedV1DBPickHandler.count) )

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        def getFirstStep(self):

                return  AFXPickStep(self, self.keyword, self.prompt, 
                    self.entitiesToPick, self.numberToPick, sequenceStyle=TUPLE)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        def getNextStep(self, previousStep):

                self.label.setText( self.labelText.replace('None', 'Picked') )
                return None


###########################################################################
# Class definition
###########################################################################

class CFre_ReleasedV1DBFileHandler(FXObject):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, form, keyword, patterns='*'):

        self.form = form
        self.patterns = patterns
        self.patternTgt = AFXIntTarget(0)
        exec('self.fileNameKw = form.%sKw' % keyword)
        self.readOnlyKw = AFXBoolKeyword(None, 'readOnly', AFXBoolKeyword.TRUE_FALSE)
        FXObject.__init__(self)
        FXMAPFUNC(self, SEL_COMMAND, AFXMode.ID_ACTIVATE, CFre_ReleasedV1DBFileHandler.activate)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def activate(self, sender, sel, ptr):

       fileDb = AFXFileSelectorDialog(getAFXApp().getAFXMainWindow(), 'Select a File',
           self.fileNameKw, self.readOnlyKw,
           AFXSELECTFILE_ANY, self.patterns, self.patternTgt)
       fileDb.setReadOnlyPatterns('*.odb')
       fileDb.create()
       fileDb.showModal()
