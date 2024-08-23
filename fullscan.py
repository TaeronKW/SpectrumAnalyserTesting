import time
import traceback
from datetime import datetime
import RFExplorer
from RFExplorer import RFE_Common
from plotscan import plot_sweep_data

BAUDRATE = 500000

# Constants for the frequency spectrum definition
POINTS_PER_SCAN = 2000		# points per scan
FREQ_PER_POINT_MHZ = 0.1	# 100 kHz intervals
SCAN_SPAN_MHZ = POINTS_PER_SCAN * FREQ_PER_POINT_MHZ

def connectToAnalyser():
    """Open a connection to the device as per the IoT module examples"""
    rfe = RFExplorer.RFECommunicator()
    rfe.AutoConfigure = False
    rfe.GetConnectedPorts()
    rfe.ResetIOT_HW(True)
    if not rfe.ConnectPort(None, BAUDRATE):
        print("Error: Could not connect to RF Explorer.")
        return None
    rfe.ProcessReceivedString(True)
    return rfe

def append_results_to_file(sweepData, filename):
    """Append to a CSV file using one frequency point/dBm value per line

    Parameters:
        sweepData           -- RFExplorer.RFESweepData.RFESweepData object
        sFilename           -- Full path filename
    """
    try:
        with open(filename, "a") as file:
            for nStep in range(sweepData.TotalDataPoints):
                file.write(sweepData.CaptureTime.strftime('%H:%M:%S.%f'))
                file.write(",")
                file.write("{0:.3f}".format(sweepData.GetFrequencyMHZ(nStep)))
                file.write(",")
                file.write("{0:.1f}".format(sweepData.GetAmplitudeDBM(nStep, None, None)))
                file.write("\n")
    except Exception as obEx:
        print("Error: " + str(obEx))


def main():
    try:
        rfe = connectToAnalyser()
        if (rfe == None):
            return
        
        # Download device details from the IoT module
        rfe.SendCommand_RequestConfigData()
        while rfe.ActiveModel == RFE_Common.eModel.MODEL_NONE:
            bDraw,rString=rfe.ProcessReceivedString(True)

        # Set the initial frequency scan parameters
        start_freq_MHz = rfe.MinFreqMHZ
        stop_freq_MHz = start_freq_MHz + SCAN_SPAN_MHZ
        numPoints = POINTS_PER_SCAN
        sweepfile = f"sweep_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.csv"

        # Note that due to issues with the way the RFExplorer IoT module handles the 
        # setting of data points it is not possible to fully generallise the command 
        # structure for setting this value (SendCommand_SweepDataPointsEx vs 
        # SendCommand_SweepDataPoints). This has been submitted as an issue to the 
        # RFExplorer-for-Python repo.

        # The number of points per scan is constant until the final scan which has a different span
        rfe.SendCommand_SweepDataPoints(numPoints)

        while (stop_freq_MHz <= rfe.MaxFreqMHZ):
            # Remove existing sweep data
            rfe.CleanSweepData()

            # For the final pass expand the span and increase the number of points to maintain a 
            # constant number of points per MHz
            if ((stop_freq_MHz + SCAN_SPAN_MHZ) > rfe.MaxFreqMHZ):
                stop_freq_MHz=rfe.MaxFreqMHZ
                numPoints = int((stop_freq_MHz-start_freq_MHz) / FREQ_PER_POINT_MHZ)
                rfe.SendCommand_SweepDataPointsEx(numPoints)

            # There is a "quirk" in the device where setting the number of data points causes the Start 
            # and Stop frequencies to be reset. For this reason an UpdateDeviceConfig command MUST follow 
            # a change in the number of data points.
            rfe.UpdateDeviceConfig(start_freq_MHz, stop_freq_MHz)
            
            # Wait for the device to confirm it has received the new parameters. No error checking is being 
            # done here by this code.
            while True:
                bDraw,rString=rfe.ProcessReceivedString(True)
                if (start_freq_MHz == rfe.StartFrequencyMHZ):
                    break
            
            # Dsiplay the new settings to the screen. In this way the user is informed of the realised settings
            # so they can observe errors.
            print(f"Start:{rfe.StartFrequencyMHZ:6.1f} MHz, End:{rfe.StopFrequencyMHZ:6.1f} MHZ, Points:{rfe.FreqSpectrumSteps+1}, Size:{rfe.StepFrequencyMHZ} MHz")
            
            # Remove existing sweep data then collect new sweep data
            rfe.CleanSweepData()
            while (rfe.SweepData.Count < 1):
                bDraw,rString=rfe.ProcessReceivedString(True)
            
            # Choose a filename based on the parameters of the lastest sweep and save the data
            #filename = f"scan_{rfe.StartFrequencyMHZ:04.0f}MHz-{rfe.StopFrequencyMHZ:04.0f}MHz_{rfe.FreqSpectrumSteps+1:04.0f}pps.csv"
            #rfe.SweepData.GetData(0).SaveFileCSV(filename, ",", None)

            # Store all the results in one file
            append_results_to_file(rfe.SweepData.GetData(0), sweepfile)
            
            # Set the frequncy limits for the next loop
            start_freq_MHz = stop_freq_MHz
            stop_freq_MHz = start_freq_MHz + SCAN_SPAN_MHZ
        # This is the end of the loop "while (stop_freq_MHz <= rfe.MaxFreqMHZ)"

        # Display a plot of the results
        plot_sweep_data(sweepfile)

    except Exception as e:
        print(f"\nAn error occurred: {e}\n")
        traceback.print_exc()
    finally:
        rfe.Close()
        rfe = None

if __name__ == "__main__":
    main()
