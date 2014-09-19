from numpy import matrix
from numpy import identity

from Deembedder import Deembedder

class DeembedderNumeric(Deembedder):
    def __init__(self,sd):
        Deembedder.__init__(self,sd)
    def CalculateUnknown(self,Sk):
        Bmsd=self.PortANames()
        Amsd=self.PortBNames()
        Adut=self.DutANames()
        Bdut=self.DutBNames()
        Internals=self.OtherNames(Bmsd+Amsd+Adut+Bdut)
        G14=-matrix(self.WeightsMatrix(Bmsd,Amsd))
        G15=-matrix(self.WeightsMatrix(Bmsd,Bdut))
        G24=-matrix(self.WeightsMatrix(Adut,Amsd))
        G25=-matrix(self.WeightsMatrix(Adut,Bdut))
        if len(Internals)>0:# internal nodes
            G13=-matrix(self.WeightsMatrix(Bmsd,Internals))
            G23=-matrix(self.WeightsMatrix(Adut,Internals))
            G33I=(matrix(identity(len(Internals)))-
                  matrix(self.WeightsMatrix(Internals,Internals))).getI()
            G34=-matrix(self.WeightsMatrix(Internals,Amsd))
            G35=-matrix(self.WeightsMatrix(Internals,Bdut))
            F11=G13*G33I*G34-G14
            F12=G13*G33I*G35-G15
            F21=G23*G33I*G34-G24
            F22=G23*G33I*G35-G25
        else:# no internal nodes
            F11=-G14
            F12=-G15
            F21=-G24
            F22=-G25
        #if long and skinny F12 then
        #F12.getI()=(F12.transpose()*F12).getI()*F12.transpose()
        B=F12.getI()*(Sk-F11)
        A=F21+F22*B
        AL=self.Partition(A)# partition for multiple unknown devices
        BL=self.Partition(B)
        #if short and fat A then A.getI()=A.transpose()*(A*A.transpose()).getI()
        Su=[(BL[u]*AL[u].getI()).tolist() for u in range(len(AL))]
        if (len(Su)==1):# only one result
            return Su[0]# return the one result, not as a list
        return Su# return the list of results