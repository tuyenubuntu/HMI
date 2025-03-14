# PLC HMI Visualization Application - README

## Overview
This repository contains a Python-based Human-Machine Interface (HMI) application designed to monitor and control a Siemens S7 PLC (or its simulator, PLCSIM) using the `snap7` library. The application provides a graphical interface built with PyQt5 to visualize the status of Inputs and Outputs, configure device connections, assign tag names, and manually toggle Output states. It includes features such as real-time status updates, a log display, and a "Clear" button to reset the log.

The application is tailored for educational purposes or small-scale industrial monitoring, allowing users to connect to a PLC, monitor its I/O states, and interact with it through a user-friendly interface.

## Features
- **Real-Time Monitoring**: Displays the status (ON/OFF) of Inputs and Outputs with color-coded indicators (green for ON, red for OFF).
- **Device Configuration**: Allows users to add a PLC device by specifying its name, IP address, rack, slot, and the number of Inputs and Outputs.
- **Tag Name Configuration**: Enables users to assign custom tag names to Inputs and Outputs for better readability.
- **Manual Control**: Provides toggle buttons to manually switch Output states (ON/OFF).
- **Connection Management**: Supports automatic connection retries and manual refresh of the connection.
- **Log Display**: Shows connection status, errors, and action logs with a "Clear" button to reset the log.
- **Responsive Design**: Uses scrollable areas to handle varying numbers of Inputs and Outputs.

## Prerequisites
Before running the application, ensure the following dependencies and configurations are in place:

### Software Requirements
- **Python 3.6 or higher**
- **Libraries**:
  - `snap7`: For communication with Siemens PLCs.
  - `PyQt5`: For the graphical user interface.
- **Installation Commands**:
  ```bash
  pip install snap7
  pip install PyQt5
  ```
- **snap7 Library Setup**:
  - Download the `snap7` library from the official [Snap7 GitHub page](https://github.com/gijzelaerr/snap7).
  - Install the library by following the instructions for your operating system (e.g., copy `snap7.dll` to the Python environment or system PATH on Windows).

### Hardware/Software Configuration
- **PLC or PLCSIM**: The application is tested with Siemens S7-1200 PLC or PLCSIM (PLC Simulator).
- **Network Setup**:
  - Configure a Microsoft Loopback Adapter on your computer with IP `192.168.0.10`.
  - Set PLCSIM to use IP `192.168.0.1` and run in "RUN" mode.
  - Ensure the firewall allows TCP port 102 (default Snap7 port).
- **TIA Portal Configuration** (if using a real PLC):
  - Enable "Permit PUT/GET communication from remote partners" under Protection & Security > Connection Mechanisms.

## Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/tuyenubuntu/HMI.git
   cd HMI
   ```

2. **Install Dependencies**:
   Run the installation commands listed under Prerequisites.

3. **Verify Snap7 Installation**:
   - Test the Snap7 library by running a simple Python script (e.g., `print(snap7.__version__)`).

## Usage
### Running the Application
1. **Launch the Script**:
   Navigate to the directory containing the script and run:
   ```bash
   python app.py
   ```
   (Ensure the file is named `app.py` or adjust the command accordingly.)

2. **Initial Interface**:
   - The application starts with a default configuration (PLC name: "S7-1214C", IP: "192.168.0.1", 10 Inputs, 10 Outputs).
   - If no connection is established, a message will appear in the log.

3. **Configure a Device**:
   - Click the "Add Device" button to open a dialog.
   - Enter the PLC name, IP address, rack, slot, and the number of Inputs and Outputs.
   - Click "OK" to save and attempt a connection.

4. **Configure Tag Names**:
   - Click the "Tag Name" button to open a dialog.
   - Assign custom names to Inputs (e.g., "Start Button") and Outputs (e.g., "Motor").
   - Click "Save" to apply the changes.

5. **Monitor and Control**:
   - The interface displays Inputs and Outputs with their current states.
   - Use the "T" (Toggle) buttons next to Outputs to switch their states.
   - The log at the top updates with connection status and actions.

6. **Refresh Connection**:
   - Click "Refresh" to retry the connection if it fails.

7. **Clear Log**:
   - Click "Clear" to reset the log display.

8. **Exit**:
   - Close the window to disconnect from the PLC and exit the application.

### Example Workflow
- Connect to PLCSIM with IP `192.168.0.1`.
- Configure 5 Inputs and 5 Outputs.
- Assign tags like "Sensor1" to I0.0 and "Pump" to Q0.0.
- Monitor the states and toggle Q0.0 to ON using the "T" button.
- Clear the log if it becomes cluttered.

## Code Structure
### Classes
- **`ConnectionDialog`**: A dialog for configuring PLC connection details.
- **`TagNameDialog`**: A dialog for assigning tag names to Inputs and Outputs.
- **`PLC_HMI`**: The main window class handling the GUI, PLC communication, and logic.

### Key Methods
- **`connect_plc`**: Establishes a connection to the PLC with retry logic.
- **`init_ui`**: Initializes the graphical interface, including the "Clear" button.
- **`update_status`**: Updates the status of Inputs and Outputs every 500ms.
- **`toggle_output`**: Toggles the state of a specified Output.
- **`clear_log`**: Clears the log display.

### Configuration
- Default connection info: `{"name": "S7-1214C", "ip": "192.168.0.1", "rack": 0, "slot": 1, "inputs": 10, "outputs": 10}`.
- Timer interval: 500ms for status updates.

## Troubleshooting
### Common Issues
- **Connection Failure**:
  - Ensure PLCSIM or the PLC is running and configured with the correct IP.
  - Check the firewall settings for port 102.
  - Verify the Microsoft Loopback Adapter is active.
- **Snap7 Errors**:
  - If `snap7` is not found, reinstall it or add the library path to your system.
- **GUI Not Responding**:
  - Increase the timer interval (e.g., 1000ms) if the PLC response is slow.
- **Invalid Data**:
  - Ensure the number of Inputs/Outputs matches the PLC configuration.

### Debug Steps
1. **Check Log**: Review messages in the status display for errors.
2. **Ping Test**: Run `ping 192.168.0.1` to verify network connectivity.
3. **PLCSIM Status**: Ensure PLCSIM is in "RUN" mode.
4. **Update Code**: Share the log output or error messages with the developer for further assistance.

## Customization
- **Add Features**:
  - Save/load configuration to a file.
  - Add support for reading/writing to Data Blocks (DB).
  - Implement alarm notifications.
- **Modify Appearance**:
  - Change colors or fonts in the stylesheet (e.g., `setStyleSheet`).
  - Adjust the layout for different screen sizes.
- **Performance**:
  - Optimize `update_status` by reducing the timer interval or using `read_multi_vars` for bulk reads.

## Contributing
Contributions are welcome! Please fork the repository, create a feature branch, and submit a pull request with your changes. Include detailed descriptions of the modifications and any testing performed.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgments
- **Snap7**: Developed by Davide Nardella for Siemens PLC communication.
- **PyQt5**: Provided by Riverbank Computing for the GUI framework.
- Inspiration from various open-source HMI projects and PLC tutorials.

## Contact
For questions or support, please open an issue on the repository or contact the maintainer via email (if applicable).

---

This README provides a comprehensive guide to set up, use, and extend the PLC HMI application. Let me know if you need further details or adjustments!