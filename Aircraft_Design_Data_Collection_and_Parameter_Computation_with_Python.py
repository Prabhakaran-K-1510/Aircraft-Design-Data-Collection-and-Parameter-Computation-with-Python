import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Ellipse

# Function to get user input for aircraft design parameters based on type
def get_aircraft_parameters():
    print("Welcome to the Aircraft Design Setup!")

    # Prompt user to select aircraft type
    print("Select the type of aircraft you want to design:")
    print("1. Cargo")
    print("2. Passenger")
    print("3. Private Jet")
    aircraft_type = int(input("Enter your choice (1/2/3): "))

    # Validate user input
    while aircraft_type not in [1, 2, 3]:
        print("Invalid choice! Please enter 1, 2, or 3.")
        aircraft_type = int(input("Enter your choice (1/2/3): "))

    # Initialize parameters dictionary
    parameters = {}

    # Get parameters based on aircraft type
    if aircraft_type == 1:  # Cargo Aircraft
        parameters['type'] = 'Cargo'
        parameters['payload_capacity'] = float(input("Payload Capacity (in kg or tons): "))
        parameters['crew_count'] = int(input("Total Number of Crew Members: "))
        parameters['range_distance'] = float(input("Desired Range (in kilometers or miles): "))
    elif aircraft_type == 2:  # Passenger Aircraft
        parameters['type'] = 'Passenger'
        parameters['total_passengers'] = int(input("Total Number of Passengers including Crew: "))
        parameters['range_distance'] = float(input("Desired Range (in kilometers or miles): "))
    elif aircraft_type == 3:  # Private Jet
        parameters['type'] = 'Private Jet'
        parameters['total_passengers'] = int(input("Total Number of Passengers including Crew: "))
        parameters['range_distance'] = float(input("Desired Range (in kilometers or miles): "))

    return parameters

# Function to read aircraft parameters from an Excel file
def read_aircraft_parameters_from_excel(file_path):
    try:
        df = pd.read_excel(file_path)
        print("Excel file successfully read!")
        return df
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None

# Function to plot Range vs Cruise Speed and draw vertical line
def plot_range_vs_cruise_speed(data):
    plt.figure(figsize=(10, 6))
    plt.scatter(data['Range (km)'], data['Cruise Speed (km/hr)'], color='b', marker='o')
    plt.xlabel('Range (km)')
    plt.ylabel('Cruise Speed (km/hr)')
    plt.title('Range vs Cruise Speed')

    # Add vertical line at x = 10000 km
    plt.axvline(x=10000, color='r', linestyle='--', label='Range = 10000 km')

    # Ellipse parameters
    circle_center_x = 10000
    circle_radius = data['Range (km)'].std()  # Adjust based on your data

    # Add ellipse
    ellipse = Ellipse((circle_center_x, data['Cruise Speed (km/hr)'].mean()), 
                      width=2 * circle_radius, height=2 * data['Cruise Speed (km/hr)'].std(), 
                      edgecolor='g', facecolor='none', linestyle='--', label='Coverage Ellipse')
    plt.gca().add_patch(ellipse)

    plt.legend()
    plt.grid(True)
    plt.show()

    # Find horizontal lines within the ellipse
    def is_within_ellipse(x, y, cx, cy, a, b):
        return ((x - cx) ** 2 / a ** 2) + ((y - cy) ** 2 / b ** 2) <= 1

    within_ellipse = data[is_within_ellipse(data['Range (km)'], data['Cruise Speed (km/hr)'], circle_center_x, data['Cruise Speed (km/hr)'].mean(), circle_radius, data['Cruise Speed (km/hr)'].std())]
    
    horizontal_lines = within_ellipse['Cruise Speed (km/hr)'].value_counts()
    if len(horizontal_lines) > 1:
        # Identify the highest value of horizontal lines
        highest_y_value = horizontal_lines.idxmax()
    else:
        highest_y_value = None

    return highest_y_value

# Function to plot each parameter vs Cruise Speed and add ellipse
def plot_parameters_vs_cruise_speed(data, cruise_speed_value):
    parameters = ['Wing Span (m)', 'Wing Area (m^2)', 'Wing Loading (kg/m^2)', 'Aspect Ratio', 'Thrust-to-Weight Ratio', 
                   'Number of Engines', 'Single Engine Thrust(KN)', 'Empty Weight of Flight (kg)', 'Takeoff Weight (kg)', 
                   'Total Length (m)', 'Height (m)', 'Sweep Angle (deg)',
                   'Service Ceiling (km)', 'Fineness Ratio','Empty to Takeoff Weight Ratio']
    
    mean_values = {'Cruise Speed (km/hr)': cruise_speed_value}
    
    for param in parameters:
        if param in data.columns:
            plt.figure(figsize=(12, 6))
            plt.scatter(data['Cruise Speed (km/hr)'], data[param], color='b', marker='o')

            # Parameters for the ellipse
            ellipse_center_x = cruise_speed_value
            ellipse_center_y = data[param].mean()  # Center y-value based on mean
            semi_major_axis = data['Cruise Speed (km/hr)'].std()  # Adjust this based on your data
            semi_minor_axis = data[param].std()  # Adjust this based on your data
            
            if semi_major_axis > 0 and semi_minor_axis > 0:
                # Add an ellipse centered at the given cruise speed
                ellipse = Ellipse((ellipse_center_x, ellipse_center_y), width=2*semi_major_axis, height=2*semi_minor_axis, 
                                  edgecolor='r', facecolor='none', linestyle='--', label='Coverage Ellipse')
                plt.gca().add_patch(ellipse)

                # Compute mean of the points within the ellipse
                def is_within_ellipse(x, y, cx, cy, a, b):
                    return ((x - cx) ** 2 / a ** 2) + ((y - cy) ** 2 / b ** 2) <= 1

                within_ellipse = data[is_within_ellipse(data['Cruise Speed (km/hr)'], data[param], ellipse_center_x, ellipse_center_y, semi_major_axis, semi_minor_axis)]
                
                if not within_ellipse.empty:
                    mean_value = within_ellipse[param].mean()
                    mean_values[param] = mean_value
                else:
                    mean_values[param] = np.nan
            else:
                print(f"Ellipse dimensions for parameter '{param}' are not valid. Check data range.")

            plt.title(f'{param} vs Cruise Speed')
            plt.xlabel('Cruise Speed (km/hr)')
            plt.ylabel(param)
            plt.grid(True)
            plt.axvline(x=cruise_speed_value, color='r', linestyle='--', label=f'Cruise Speed = {cruise_speed_value}')
            plt.legend()
            plt.show()
        else:
            print(f"Parameter '{param}' not found in data.")

    return mean_values

# Main program execution
if __name__ == "__main__":
    # Call the function to get aircraft parameters
    aircraft_parameters = get_aircraft_parameters()

    # Print out the gathered parameters for confirmation
    print("\nAircraft Design Parameters:")
    print(f"Aircraft Type: {aircraft_parameters['type']}")
    if aircraft_parameters['type'] == 'Cargo':
        print(f"Payload Capacity: {aircraft_parameters['payload_capacity']} kg or tons")
        print(f"Total Number of Crew Members: {aircraft_parameters['crew_count']}")
    elif aircraft_parameters['type'] == 'Passenger' or aircraft_parameters['type'] == 'Private Jet':
        print(f"Total Number of Passengers including Crew: {aircraft_parameters['total_passengers']}")
    print(f"Desired Range: {aircraft_parameters['range_distance']} kilometers or miles")

    # Prompt user to provide Excel file path
    file_path = input("\nPlease provide the path to the Excel file containing additional aircraft parameters: ")

    # Read aircraft parameters from Excel
    aircraft_data = read_aircraft_parameters_from_excel(file_path)

    if aircraft_data is not None:
        # Get the cruise speed value from the range vs cruise speed plot
        cruise_speed_value = plot_range_vs_cruise_speed(aircraft_data)

        # Plot each parameter vs Cruise Speed and add ellipse
        mean_values = plot_parameters_vs_cruise_speed(aircraft_data, cruise_speed_value)

        # Save mean values to an Excel file
        mean_values_df = pd.DataFrame(list(mean_values.items()), columns=['Parameter', 'Mean Value'])
        mean_values_df.to_excel('C:\\PRABHAKARAN K\\IIT KANPUR\\python\\aircraft_analysis.xlsx', index=False)
        print("analysed values saved to 'aircraft_analysis.xlsx'")
