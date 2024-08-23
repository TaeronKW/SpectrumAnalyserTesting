import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

# Constant for the default file name
DEFAULT_FILE_NAME = "sweep_2024-08-22-15-14-38.csv"

# Function to read the CSV file and plot the data
def plot_sweep_data(file_name):
    # Check if the file exists
    if not os.path.exists(file_name):
        print(f"File '{file_name}' not found.")
        return

    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_name, header=None)

    # Verify the file format
    if df.shape[1] < 3:
        print(f"File '{file_name}' does not have the expected format.")
        return

    # Extract columns for plotting
    frequency = df[1]  # Column 2 (index 1)
    amplitude = df[2]  # Column 3 (index 2)

    # Plot the data
    plt.plot(frequency, amplitude)
    plt.xlabel("Frequency [MHz]")
    plt.ylabel("Amplitude [dBm]")
    plt.title("Frequency vs. Amplitude from " + file_name)
    plt.grid(True)
    plt.show()

def main():
    # Check if a file name is provided as a command-line argument
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    else:
        file_name = DEFAULT_FILE_NAME

    # Call the function to plot the data
    plot_sweep_data(file_name)

if __name__ == "__main__":
    main()
