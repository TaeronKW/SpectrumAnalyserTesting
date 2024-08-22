import time
from datetime import datetime
import RFExplorer
from RFExplorer import RFE_Common
from RFExplorer.RFEConfiguration import RFEConfiguration
from RFExplorer.RFESweepDataCollection import RFESweepDataCollection


BAUDRATE = 500000

# Constants for the frequency
POINTS_PER_SCAN = 2000		# points per scan
FREQ_PER_POINT_MHZ = 0.1	# 100 kHz intervals
SCAN_SPAN_MHZ = POINTS_PER_SCAN * FREQ_PER_POINT_MHZ	#

def connectToAnalyser():
    rfe = RFExplorer.RFECommunicator()
    rfe.AutoConfigure = False
    rfe.GetConnectedPorts()
    rfe.ResetIOT_HW(True)
    if not rfe.ConnectPort(None, BAUDRATE):
        print("Error: Could not connect to RF Explorer.")
        return None
    rfe.ProcessReceivedString(True)
    return rfe

def main():
    try:
        print("open")
        rfe = connectToAnalyser()
        if (rfe == None):
            return


        rfe.SendCommand_RequestConfigData()
        while rfe.ActiveModel == RFE_Common.eModel.MODEL_NONE:
            bDraw,rString=rfe.ProcessReceivedString(True)


        start_freq_MHz = rfe.MinFreqMHZ
        stop_freq_MHz = start_freq_MHz + SCAN_SPAN_MHZ
        numPoints = POINTS_PER_SCAN



        while (stop_freq_MHz <= rfe.MaxFreqMHZ):
            rfe.CleanSweepData()
            if ((stop_freq_MHz + SCAN_SPAN_MHZ) > rfe.MaxFreqMHZ):
                stop_freq_MHz=rfe.MaxFreqMHZ
                numPoints = int((stop_freq_MHz-start_freq_MHz) / FREQ_PER_POINT_MHZ)
                rfe.SendCommand_SweepDataPointsEx(numPoints)
            else:
                rfe.SendCommand_SweepDataPoints(numPoints)
            
            rfe.UpdateDeviceConfig(start_freq_MHz, stop_freq_MHz)
            
            while True:
                bDraw,rString=rfe.ProcessReceivedString(True)
                if (start_freq_MHz == rfe.StartFrequencyMHZ):
                    break
            
            print(f"Start:{rfe.StartFrequencyMHZ:4.1f} MHz, End:{rfe.StopFrequencyMHZ:4.1f} MHZ, Points:{rfe.FreqSpectrumSteps+1}, Size:{rfe.StepFrequencyMHZ} MHz")
            
            filename = f"scan_{rfe.StartFrequencyMHZ:04.0f}MHz-{rfe.StopFrequencyMHZ:04.0f}MHz_{rfe.FreqSpectrumSteps+1:04.0f}pps.csv"
            filename
            
            rfe.CleanSweepData()
            while (rfe.SweepData.Count < 1):
                bDraw,rString=rfe.ProcessReceivedString(True)
            
            rfe.SweepData.GetData(0).SaveFileCSV(filename,",",None)
            
            start_freq_MHz = stop_freq_MHz
            stop_freq_MHz = start_freq_MHz + SCAN_SPAN_MHZ


    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        rfe.Close()
        rfe = None


if __name__ == "__main__":
    main()
