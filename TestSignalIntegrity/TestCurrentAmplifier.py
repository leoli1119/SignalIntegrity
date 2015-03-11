import unittest

import SignalIntegrity as si
from numpy import linalg
from numpy import matrix
from TestHelpers import *

class TestCurrentAmplifier(unittest.TestCase,SourcesTesterHelper,RoutineWriterTesterHelper):
    def __init__(self, methodName='runTest'):
        RoutineWriterTesterHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
    def testCurrentAmplifierFourPort(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DC 4','device ZI 2','device ZO 2',
            'port 1 ZI 1 2 DC 2 3 DC 4 4 DC 3',
            'connect ZI 2 DC 1','connect ZO 1 DC 4','connect ZO 2 DC 3'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        ssps.AssignSParameters('DC',si.sy.CurrentControlledCurrentSource('\\beta'))
        ssps.AssignSParameters('ZI',si.sy.SeriesZ('Z_i'))
        ssps.AssignSParameters('ZO',si.sy.SeriesZ('Z_o'))
        ssps.LaTeXBlockSolutionBig().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Current Amplifier Four Port')
    def testCurrentAmplifierFourPortSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DC 4','port 1 DC 1 2 DC 2 3 DC 3 4 DC 4'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,False)
        ssps.m_eqPrefix='\\begin{equation} '
        ssps.m_eqSuffix=' \\end{equation}'
        ssps.AssignSParameters('DC',si.sy.CurrentAmplifierFourPort('\\beta','Z_i','Z_o'))
        ssps.LaTeXBlockSolution().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Current Amplifier Four Port Symbolic')
    def testCurrentAmplifierFourPortNumeric(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1.4 # Zin
        ZO=2000 # Zout
        sdp.AddLines(['device DC 4 currentcontrolledcurrentsource '+str(G),
            'device ZI 2 R '+str(ZI),
            'device ZO 2 R '+str(ZO),
            'port 1 ZI 1 2 DC 2 3 DC 4 4 DC 3',
            'connect ZI 2 DC 1','connect ZO 1 DC 4','connect ZO 2 DC 3'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        rescalc=sspn.SParameters()
        rescorrect=si.dev.CurrentAmplifier(4,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Current Amplifier Four Port incorrect')
    def testCurrentAmplifierFourPortNumeric2(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1.4 # Zin
        ZO=2000 # Zout
        sdp.AddLines(['device DC 4','device ZI 2','device ZO 2',
            'port 1 ZI 1 2 DC 2 3 DC 4 4 DC 3',
            'connect ZI 2 DC 1','connect ZO 1 DC 4','connect ZO 2 DC 3'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        sspn.AssignSParameters('DC',si.dev.CurrentControlledCurrentSource(G))
        sspn.AssignSParameters('ZI',si.dev.SeriesZ(ZI))
        sspn.AssignSParameters('ZO',si.dev.SeriesZ(ZO))
        rescalc=sspn.SParameters()
        rescorrect=si.dev.CurrentAmplifier(4,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Current Amplifier Four Port incorrect')
    def testCurrentAmplifierFourPortNumeric3(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1.4 # Zin
        ZO=2000 # Zout
        sdp.AddLines(['device D 4 currentamplifier gain '+str(G)+' zi '+str(ZI)+' zo '+str(ZO),
            'port 1 D 1 2 D 2 3 D 3 4 D 4'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        rescalc=sspn.SParameters()
        rescorrect=si.dev.CurrentAmplifier(4,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Current Amplifier Four Port incorrect')
    def testCurrentAmplifierThreePort(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 4',
            'port 1 D 1 2 D 3 3 D 2',
            'connect D 2 D 4'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        ssps.AssignSParameters('D',si.sy.CurrentAmplifier(4,'\\beta','Z_i','Z_o'))
        ssps.LaTeXBlockSolutionBiggest().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Current Amplifier Three Port')
    def testCurrentAmplifierThreePortSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 3','port 1 D 1 2 D 2 3 D 3'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        ssps.m_eqPrefix='\\begin{equation} '
        ssps.m_eqSuffix=' \\end{equation}'
        ssps.AssignSParameters('D',si.sy.CurrentAmplifier(3,'\\beta','Z_i','Z_o'))
        ssps.LaTeXBlockSolution().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Current Amplifier Three Port Symbolic')
    def testCurrentAmplifierThreePortNumeric(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1.4 # Zin
        ZO=2000 # Zout
        sdp.AddLines(['device D 4 currentamplifier gain '+str(G)+' zi '+str(ZI)+' zo '+str(ZO),
            'port 1 D 1 2 D 3 3 D 2',
            'connect D 2 D 4'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        rescalc=sspn.SParameters()
        rescorrect=si.dev.CurrentAmplifierThreePort(G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Current Amplifier Three Port incorrect')
    def testCurrentAmplifierThreePortNumeric2(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1.4 # Zin
        ZO=2000 # Zout
        sdp.AddLines(['device D 4',
            'port 1 D 1 2 D 3 3 D 2',
            'connect D 2 D 4'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        sspn.AssignSParameters('D',si.dev.CurrentAmplifierFourPort(G,ZI,ZO))
        rescalc=sspn.SParameters()
        rescorrect=si.dev.CurrentAmplifierThreePort(G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Current Amplifier Three Port incorrect')
    def testCurrentAmplifierThreePortNumeric3(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1.4 # Zin
        ZO=2000 # Zout
        sdp.AddLines(['device D 3 currentamplifier gain '+str(G)+' zi '+str(ZI)+' zo '+str(ZO),
            'port 1 D 1 2 D 2 3 D 3'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        rescalc=sspn.SParameters()
        rescorrect=si.dev.CurrentAmplifier(3,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Current Amplifier Three Port incorrect')
    def testCurrentAmplifierTwoPort(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 4','device G1 1 ground','device G2 1 ground',
            'port 1 D 1 2 D 3',
            'connect D 2 G1 1','connect D 4 G2 1'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        D=si.sy.CurrentAmplifier(4,'\\beta','Z_i','Z_o')
        ssps.AssignSParameters('D',D)
        ssps.LaTeXBlockSolutionBiggest().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Current Amplifier Two Port Full')
    def testCurrentAmplifierTwoPortAlternate(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 3','device G 1 ground',
            'port 1 D 1 2 D 2',
            'connect D 3 G 1'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        D=si.sy.CurrentAmplifier(3,'\\beta','Z_i','Z_o')
        ssps.AssignSParameters('D',D)
        ssps.LaTeXBlockSolutionBiggest().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Current Amplifier Two Port Alternate')
    def testCurrentAmplifierTwoPortSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 2',
            'port 1 D 1 2 D 2'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,False)
        ssps.m_eqPrefix='\\begin{equation} '
        ssps.m_eqSuffix=' \\end{equation}'
        D=si.sy.CurrentAmplifierTwoPort('\\beta','Z_i','Z_o')
        ssps.AssignSParameters('D',D)
        ssps.LaTeXBlockSolution().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Current Amplifier Two Port Symbolic')
    def testCurrentAmplifierTwoPortNumeric(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1000. # Zin
        ZO=1.4 # Zout
        sdp.AddLines(['device D 4 currentamplifier gain '+str(G)+' zi '+str(ZI)+' zo '+str(ZO),
            'device G 1 ground',
            'port 1 D 1 2 D 3',
            'connect D 2 D 4 G 1'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        rescalc=sspn.SParameters()
        rescorrect=si.dev.CurrentAmplifier(2,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Current Amplifier Two Port incorrect')
    def testCurrentAmplifierTwoPortNumeric2(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1000. # Zin
        ZO=1.4 # Zout
        sdp.AddLines(['device D 4',
            'device G 1 ground',
            'port 1 D 1 2 D 3',
            'connect D 2 D 4 G 1'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        sspn.AssignSParameters('D',si.dev.CurrentAmplifier(4,G,ZI,ZO))
        rescalc=sspn.SParameters()
        rescorrect=si.dev.CurrentAmplifier(2,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Current Amplifier Two Port incorrect')
    def testCurrentAmplifierTwoPortNumeric3(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1000. # Zin
        ZO=1.4 # Zout
        sdp.AddLines(['device D 2 currentamplifier gain '+str(G)+' zi '+str(ZI)+' zo '+str(ZO),
            'port 1 D 1 2 D 2'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        rescalc=sspn.SParameters()
        rescorrect=si.dev.CurrentAmplifier(2,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Current Amplifier Two Port incorrect')
    def testCurrentAmplifierTwoPortAlternateNumeric(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1000. # Zin
        ZO=1.4 # Zout
        sdp.AddLines(['device D 3 currentamplifier gain '+str(G)+' zi '+str(ZI)+' zo '+str(ZO),
            'device G 1 ground',
            'port 1 D 1 2 D 2',
            'connect D 3 G 1'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        rescalc=sspn.SParameters()
        rescorrect=si.dev.CurrentAmplifier(2,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Current Amplifier Two Port Alternate incorrect')
    def testCurrentAmplifierFourPortCode(self):
        self.WriteCode('TestCurrentAmplifier.py','testCurrentAmplifierFourPort(self)',self.standardHeader)
    def testCurrentAmplifierThreePortCode(self):
        self.WriteCode('TestCurrentAmplifier.py','testCurrentAmplifierThreePort(self)',self.standardHeader)
    def testCurrentAmplifierThreePortAlternateCode(self):
        self.WriteCode('TestCurrentAmplifier.py','testCurrentAmplifierThreePortAlternate(self)',self.standardHeader)
    def testCurrentAmplifierTwoPortCode(self):
        self.WriteCode('TestCurrentAmplifier.py','testCurrentAmplifierTwoPort(self)',self.standardHeader)
    def testCurrentAmplifierTwoPortAlternateCode(self):
        self.WriteCode('TestCurrentAmplifier.py','testCurrentAmplifierTwoPortAlternate(self)',self.standardHeader)


if __name__ == '__main__':
    unittest.main()
