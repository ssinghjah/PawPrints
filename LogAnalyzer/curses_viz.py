import os, argparse, json, time, curses
import time, datetime

PAWPRINTS_LOG = ""
VEHICLE_LOG = "../Results/2024-04-09_18_57_04_vehicleOut.txt"

def main(stdscr):
    # Clear the screen
    stdscr.clear()

    # Get the dimensions of the screen
    height, width = stdscr.getmaxyx()

    line_dashes = "-" * (width - 2)  # Subtract 2 to leave space for the border
    line_dashes = ""

    # Calculate the center of the screen
    x = 0
    y = 0

    curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)


    # Initialize the value
    value = 0

    while True:

        y = 0

        with open(VEHICLE_LOG, "rb") as file:
            try:
                file.seek(-2, os.SEEK_END)
                while file.read(1) != b'\n':
                    file.seek(-2, os.SEEK_CUR)
            except OSError:
                file.seek(0)

            
            measurement = file.readline().decode()
            #print(last_measurement)
            y += 1

            stdscr.addstr(y, x, "Position ", curses.A_BOLD)
            y += 1

            stdscr.addstr(y, x, "---------")            
            y += 1
            stdscr.move(y, 0)
            stdscr.clrtoeol()


            measurementList = measurement.split(",")
            stdscr.addstr(y, 0, "Lat: ", curses.A_BOLD)
            stdscr.addstr(f"{measurementList[1]}")

            stdscr.addstr(" | Lon: ", curses.A_BOLD)
            stdscr.addstr(f"{measurementList[2]}")

            stdscr.addstr(" | Alt: ", curses.A_BOLD)
            stdscr.addstr(f"{measurementList[3]} m")

            # Refresh the screen to show the updated value
            stdscr.refresh()


        with open(PAWPRINTS_LOG, "rb") as file:
            try:
                file.seek(-2, os.SEEK_END)
                while file.read(1) != b'\n':
                    file.seek(-2, os.SEEK_CUR)
            except OSError:
                file.seek(0)
        
            last_measurement = file.readline().decode()
            #print(last_measurement)
            measurement = json.loads(last_measurement)
            y += 3
            stdscr.move(y, 0)
            stdscr.clrtoeol()

            connectedPCI = measurement["connected_pci"]
            relativeTime = measurement["rel_time"]
            numSeenCells = len(measurement["cells"])

            current_time = datetime.datetime.now()

            systemTime = current_time.strftime("%H:%M:%S")  # Format as hours:minutes:seconds

            stdscr.addstr(y, x, "Time ",  curses.A_BOLD)
            y += 1
            stdscr.addstr(y, x, "----")
            y += 1

            stdscr.move(y, 0)
            stdscr.clrtoeol()

            stdscr.addstr(y, x, f"System time: ", curses.A_BOLD)
            stdscr.addstr(f"{systemTime}")
            stdscr.addstr(" | Log elapsed time: ", curses.A_BOLD)
            stdscr.addstr(f"{relativeTime}")
            
            y += 3
            stdscr.addstr(y, x, "Cells", curses.color_pair(3) | curses.A_BOLD)
            y += 1
            stdscr.addstr(y, x, "-----")

            y+=1
            stdscr.move(y, 0)
            stdscr.clrtoeol()

            stdscr.attron(curses.color_pair(3))


            stdscr.addstr(y, x, "Detected cells: ", curses.A_BOLD)
            stdscr.addstr(f"{numSeenCells}")
            stdscr.addstr(" | Connected PCI: ", curses.A_BOLD)
            stdscr.addstr(f"{connectedPCI}")
            stdscr.attroff(curses.color_pair(3))

            y +=1
            stdscr.addstr(y, x, line_dashes)
            

            if numSeenCells > 0:
                connectedCell = measurement["cells"][0]
                rsrp = connectedCell["rsrp"]
                band_description = connectedCell["bands_description"]
                rsrq = connectedCell["rsrq"]
                rssi = connectedCell["rssi"]
                ta = connectedCell["ta"]
                
                stdscr.attron(curses.color_pair(1))
                
                y += 1
                #stdscr.addstr(y, x, line_dashes)
                y += 1
                stdscr.addstr(y, x, "4G KPIs ", curses.color_pair(1) | curses.A_BOLD)
                y += 1
                stdscr.addstr(y, x, "-------")
                y += 1
                stdscr.move(y, 0)
                stdscr.clrtoeol()

                stdscr.addstr(y, x, "RSRP: ",  curses.A_BOLD)
                stdscr.addstr(f"{rsrp} dBm")

                stdscr.addstr(" | RSRQ: ",  curses.A_BOLD)
                stdscr.addstr(f"{rsrq} dB")
                
                stdscr.addstr(" | RSSI: ",  curses.A_BOLD)
                stdscr.addstr(f"{rssi} dBm")

                y += 1
                stdscr.move(y, 0)
                stdscr.clrtoeol()

                stdscr.addstr(y, x, "Bands: ",  curses.A_BOLD)
                stdscr.addstr(band_description)

                #y += 1
                #stdscr.addstr(y, x, line_dashes)
                
                stdscr.attroff(curses.color_pair(1))

            if "nr_signal_strength" in measurement and len(measurement["nr_signal_strength"].keys()) > 1:
                nr_ss_rsrp = measurement["nr_signal_strength"]["ss_rsrp"]
                nr_ss_rsrq = measurement["nr_signal_strength"]["ss_rsrq"]
                nr_ss_sinr = measurement["nr_signal_strength"]["ss_sinr"]

                stdscr.attron(curses.color_pair(2))

                y += 1
                #stdscr.addstr(y, x, line_dashes)

                y += 2
                stdscr.addstr(y, x, "5G KPIs ",  curses.color_pair(2) | curses.A_BOLD)
                y += 1

                stdscr.addstr(y, x, "-------")
                y += 1
                stdscr.move(y, 0)
                stdscr.clrtoeol()

                                
                stdscr.addstr(y, x, "RSRP: ", curses.A_BOLD)
                stdscr.addstr(f"{nr_ss_rsrp} dBm")

                stdscr.addstr(" | RSRQ: ", curses.A_BOLD)
                stdscr.addstr(f"{nr_ss_rsrq} dB")
                
                stdscr.addstr(" | SINR: ", curses.A_BOLD)
                stdscr.addstr(f"{nr_ss_sinr} dB")

                y += 1
                stdscr.addstr(y, x, line_dashes)

                stdscr.attroff(curses.color_pair(2))

            # Refresh the screen to show the updated value
            stdscr.refresh()




            # Update the value (you can replace this with any logic to change the value)
            value += 1

            time.sleep(1)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Print latest received PawPrints measurement.')
    parser.add_argument('-p', '--pawprints-log', type=str, help="PawPrints log file")
    parser.add_argument('-v', '--vehicle-log', type=str, help="Vehicle log file")

    options = parser.parse_args()
    PAWPRINTS_LOG = options.pawprints_log
    VEHICLE_LOG = options.vehicle_log
    curses.wrapper(main)
