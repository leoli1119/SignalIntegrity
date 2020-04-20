"""
NetworkAnalyzer.py
"""
# Copyright (c) 2018 Teledyne LeCroy, Inc.
# All rights reserved worldwide.
#
# This file is part of SignalIntegrity.
#
# SignalIntegrity is free software: You can redistribute it and/or modify it under the terms
# of the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>

import sys

if sys.version_info.major < 3:
    import Tkinter as tk
    import tkMessageBox as messagebox
else:
    import tkinter as tk
    from tkinter import messagebox

from SignalIntegrity.App.ProgressDialog import ProgressDialog
from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
from SignalIntegrity.App.Simulator import SimulatorDialog

from SignalIntegrity.Lib.Exception import SignalIntegrityException,SignalIntegrityExceptionNetworkAnalyzer

import copy,os

import SignalIntegrity.App.Project

class NetworkAnalyzerSimulator(object):
    def __init__(self,parent):
        self.parent=parent
    def SimulatorDialog(self):
        if not hasattr(self,'simulatorDialog'):
            self.simulatorDialog=SimulatorDialog(self)
        if self.simulatorDialog == None:
            self.simulatorDialog=SimulatorDialog(self)
        else:
            if not self.simulatorDialog.winfo_exists():
                self.simulatorDialog=SimulatorDialog(self)
        return self.simulatorDialog
    def UpdateWaveforms(self,outputWaveformList,outputWaveformLabels):
        self.SimulatorDialog().UpdateWaveforms(outputWaveformList,outputWaveformLabels).state('normal')
    def _ProcessWaveforms(self,callback=None):
        return self.transferMatriceProcessor.ProcessWaveforms(self.inputWaveformList,adaptToLargest=True)
    def Simulate(self,SParameters=False):
        self.parent.Drawing.stateMachine.Nothing()
        netList=self.parent.Drawing.schematic.NetList().Text()
        import SignalIntegrity.Lib as si
        fd=si.fd.EvenlySpacedFrequencyList(
                SignalIntegrity.App.Project['CalculationProperties.EndFrequency'],
                SignalIntegrity.App.Project['CalculationProperties.FrequencyPoints'])
        cacheFileName=None
        if SignalIntegrity.App.Preferences['Cache.CacheResults']:
            cacheFileName=self.parent.fileparts.FileNameTitle()+'_DUTSParameters'
        si.sd.Numeric.trySVD=SignalIntegrity.App.Preferences['Calculation.TrySVD']
        spnp=si.p.DUTSParametersNumericParser(fd,cacheFileName=cacheFileName)
        spnp.AddLines(netList)
        progressDialog = ProgressDialog(self.parent,"Calculating DUT S-parameters",spnp,spnp.SParameters,granularity=1.0)
        try:
            (DUTSp,NetworkAnalyzerProjectFile)=progressDialog.GetResult()
            showDutsp=False
            if showDutsp:
                from SignalIntegrity.App.SParameterViewerWindow import SParametersDialog
                self.spd=self.spd=SParametersDialog(self.parent,DUTSp,filename=self.parent.fileparts.FullFilePathExtension('s'+str(DUTSp.m_P)+'p'))
        except si.SignalIntegrityException as e:
            messagebox.showerror('DUT S-parameter Calculator',e.parameter+': '+e.message)                
            return None
        netListText=None
        if NetworkAnalyzerProjectFile != None:
            self.ProjectCopy=copy.deepcopy(SignalIntegrity.App.Project)
            self.cwdCopy=os.getcwd()
            try:
                app=SignalIntegrityAppHeadless()
                if app.OpenProjectFile(os.path.realpath(NetworkAnalyzerProjectFile)):
                    app.Drawing.DrawSchematic()
                    netList=app.Drawing.schematic.NetList()
                    netListText=netList.Text()
                else:
                    raise SignalIntegrityExceptionNetworkAnalyzer('file could not be opened: '+NetworkAnalyzerProjectFile)
            except SignalIntegrityException as e:
                messagebox.showerror('Network Analyzer Model: ',e.parameter+': '+e.message)                
            finally:
                SignalIntegrity.App.Project=copy.deepcopy(self.ProjectCopy)
                os.chdir(self.cwdCopy)
        else:
            netList=self.parent.Drawing.schematic.NetList()
            netListText=self.parent.NetListText()
            
        if netListText==None:
            return
        cacheFileName=None
        if SignalIntegrity.App.Preferences['Cache.CacheResults']:
            cacheFileName=self.parent.fileparts.FileNameTitle()+'_TransferMatrices'
        si.sd.Numeric.trySVD=SignalIntegrity.App.Preferences['Calculation.TrySVD']
        snp=si.p.NetworkAnalyzerSimulationNumericParser(fd,DUTSp,spnp.NetworkAnalyzerPortConnectionList,cacheFileName=cacheFileName)
        snp.AddLines(netListText)
        progressDialog = ProgressDialog(self.parent,"Calculating Transfer Matrices",snp,snp.TransferMatrices,granularity=1.0)
        try:
            self.transferMatrices=progressDialog.GetResult()
        except si.SignalIntegrityException as e:
            messagebox.showerror('Transfer Matrices Calculation: ',e.parameter+': '+e.message)                
            return None

        snp.m_sd.pOutputList
        self.sourceNames=snp.m_sd.SourceVector()
        
        if NetworkAnalyzerProjectFile != None:
            self.ProjectCopy=copy.deepcopy(SignalIntegrity.App.Project)
            self.cwdCopy=os.getcwd()
            try:
                app=SignalIntegrityAppHeadless()
                if app.OpenProjectFile(os.path.realpath(NetworkAnalyzerProjectFile)):
                    app.Drawing.DrawSchematic()
                    stateList=[app.Device(self.sourceNames[port])['state']['Value'] for port in range(snp.simulationNumPorts)]
                    self.wflist=[]
                    for driven in range(snp.simulationNumPorts):
                        thiswflist=[]
                        for port in range(snp.simulationNumPorts):
                            app.Device(self.sourceNames[port])['state']['Value']='on' if port==driven else 'off'
                        for wfIndex in range(len(self.sourceNames)):
                            thiswflist.append(app.Device(self.sourceNames[wfIndex]).Waveform())
                        self.wflist.append(thiswflist)
                    for port in range(snp.simulationNumPorts):
                        app.Device(self.sourceNames[port])['state']['Value']=stateList[port]
                else:
                    raise SignalIntegrityExceptionNetworkAnalyzer('file could not be opened: '+NetworkAnalyzerProjectFile)
            except SignalIntegrityException as e:
                messagebox.showerror('Network Analyzer Model: ',e.parameter+': '+e.message)                
            finally:
                SignalIntegrity.App.Project=copy.deepcopy(self.ProjectCopy)
                os.chdir(self.cwdCopy)
        else:
            stateList=[app.Device(self.sourceNames[port])['state']['Value'] for port in range(snp.simulationNumPorts)]
            self.wflist=[]
            for driven in range(snp.simulationNumPorts):
                thiswflist=[]
                for port in range(snp.simulationNumPorts):
                    app.Device(self.sourceNames[port])['state']['Value']='on' if port==driven else 'off'
                for wfIndex in range(len(self.sourceNames)):
                    thiswflist.append(app.Device(self.sourceNames[wfIndex]).Waveform())
                self.wflist.append(thiswflist)
            for port in range(snp.simulationNumPorts):
                app.Device(self.sourceNames[port])['state']['Value']=stateList[port]

        self.transferMatriceProcessor=si.td.f.TransferMatricesProcessor(self.transferMatrices)
        si.td.wf.Waveform.adaptionStrategy='SinX' if SignalIntegrity.App.Preferences['Calculation.UseSinX'] else 'Linear'

        progressDialog=ProgressDialog(self.parent,"Waveform Processing",self.transferMatriceProcessor,self._ProcessWaveforms)
        try:
            outputWaveformList = progressDialog.GetResult()
        except si.SignalIntegrityException as e:
            messagebox.showerror('Simulator',e.parameter+': '+e.message)
            return

        portConnections=[]
        for pci in range(len(snp.PortConnectionList)):
            if snp.PortConnectionList[pci]: portConnections.append(pci)

        outputWaveformList=[]
        self.outputWaveformLabels=[]
        for r in range(len(self.outputwflist)):
            wflist=self.outputwflist[r]
            for c in range(len(wflist)):
                wf=wflist[c]
                outputWaveformList.append(wf)
                self.outputWaveformLabels.append(snp.m_sd.pOutputList[c][2]+str(portConnections[r]+1))
#         
#             
#             
# 
#         for outputWaveformIndex in range(len(outputWaveformList)):
#             outputWaveform=outputWaveformList[outputWaveformIndex]
#             outputWaveformLabel = self.outputWaveformLabels[outputWaveformIndex]
#             for device in self.parent.Drawing.schematic.deviceList:
#                 if device['partname'].GetValue() in ['Output','DifferentialVoltageOutput','CurrentOutput']:
#                     if device['ref'].GetValue() == outputWaveformLabel:
#                         # probes may have different kinds of gain specified
#                         gainProperty = device['gain']
#                         gain=gainProperty.GetValue()
#                         offset=device['offset'].GetValue()
#                         delay=device['td'].GetValue()
#                         if gain != 1.0 or offset != 0.0 or delay != 0.0:
#                             outputWaveform = outputWaveform.DelayBy(delay)*gain+offset
#                         outputWaveformList[outputWaveformIndex]=outputWaveform
#                         break
        userSampleRate=SignalIntegrity.App.Project['CalculationProperties.UserSampleRate']
        outputWaveformList = [wf.Adapt(
            si.td.wf.TimeDescriptor(wf.td.H,int(wf.td.K*userSampleRate/wf.td.Fs),userSampleRate))
                for wf in outputWaveformList]

        td=si.td.wf.TimeDescriptor(-5e-9,
           SignalIntegrity.App.Project['CalculationProperties.TimePoints'],
           SignalIntegrity.App.Project['CalculationProperties.BaseSampleRate'])
        frequencyList=td.FrequencyList()

        if snp.simulationType != 'CW':
            # note this matrix is transposed from what is normally expected
            Vmat=[[outputWaveformList[self.outputWaveformLabels.index('V'+str(portConnections[r]+1)+str(portConnections[c]+1))]
                for r in range(len(portConnections))]
                    for c in range(len(portConnections))]

            for vli in range(len(Vmat)):
                tdr=si.m.tdr.TDRWaveformToSParameterConverter(
                    WindowForwardHalfWidthTime=500e-12,
                    WindowReverseHalfWidthTime=500e-12,
                    WindowRaisedCosineDuration=10e-12,
                    Step=(snp.simulationType=='TDRStep'),
                    Length=0,
                    Denoise=(snp.simulationType !='TDRStep'),
                    DenoisePercent=20.,
                    Inverted=False,
                    fd=frequencyList
                 )

                tdr.Convert(Vmat[vli],vli)
                for r in range(len(portConnections)):
                    outputWaveformList.append(tdr.IncidentWaveform if r==vli else si.td.wf.Waveform(td))
                    self.outputWaveformLabels.append('A'+str(portConnections[r]+1)+str(portConnections[vli]+1))
                for r in range(len(portConnections)):
                    outputWaveformList.append(tdr.ReflectWaveforms[r])
                    self.outputWaveformLabels.append('B'+str(portConnections[r]+1)+str(portConnections[vli]+1))


        if not SParameters:
            self.SimulatorDialog().title('Sim: '+self.parent.fileparts.FileNameTitle())
            self.SimulatorDialog().ExamineTransferMatricesDoer.Activate(True)
            self.SimulatorDialog().SimulateDoer.Activate(True)
            self.SimulatorDialog().ViewTimeDomainDoer.Set(snp.simulationType != 'CW')
            #self.SimulatorDialog().ViewTimeDomainDoer.Activate(snp.simulationType != 'CW')
            self.SimulatorDialog().ViewSpectralContentDoer.Set(snp.simulationType == 'CW')
            self.SimulatorDialog().ViewSpectralDensityDoer.Set(False)
            self.UpdateWaveforms(outputWaveformList, self.outputWaveformLabels)
        else:
            frequencyContentList=[wf.FrequencyContent(fd) for wf in outputWaveformList]

            Afc=[[frequencyContentList[self.outputWaveformLabels.index('A'+str(portConnections[r]+1)+str(portConnections[c]+1))]
                for c in range(len(portConnections))]
                    for r in range(len(portConnections))]
            Bfc=[[frequencyContentList[self.outputWaveformLabels.index('B'+str(portConnections[r]+1)+str(portConnections[c]+1))]
                for c in range(len(portConnections))]
                    for r in range(len(portConnections))]

            from numpy import matrix

            data=[None for _ in range(len(frequencyList))]
            for n in range(len(frequencyList)):
                B=[[Bfc[r][c][n] for c in range(snp.simulationNumPorts)] for r in range(snp.simulationNumPorts)]
                A=[[Afc[r][c][n] for c in range(snp.simulationNumPorts)] for r in range(snp.simulationNumPorts)]
                data[n]=(matrix(B)*matrix(A).getI()).tolist()
            sp=si.sp.SParameters(frequencyList,data)
            return sp

    def _ProcessWaveforms(self,callback=None):
        self.outputwflist=[]
        for port in range(len(self.wflist)):
            self.outputwflist.append(self.transferMatriceProcessor.ProcessWaveforms(self.wflist[port],adaptToLargest=True))

