class ImpulseResponse(Waveform):
...
    def DelayBy(self,d):
        return ImpulseResponse(self.TimeDescriptor().DelayBy(d),self.Values())
...