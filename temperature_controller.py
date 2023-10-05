from communication.devices.lakeshore import Client as Lakeshore
import numpy as np
import time


# def drop(ls: Lakeshore, high: float, low: float, ramp_speed: float):
#     while ls.read_temperature() <= high:
#         time.sleep(600)
#     ls.set_ramp_speed(ramp_speed)
#     ls.set_setpoint(low)


class Controller:
    def __init__(self):
        self.ls = Lakeshore(331)

    def check_setpoint(self):
        """Returns the current set-point of the controller; this changes over time if ramping."""
        return self.ls.read_setpoint()

    def set_setpoint(self, setpoint):
        """Change the set-point that the controller will ramp to."""
        self.ls.set_setpoint(setpoint)

    # def check_flatness(self, length: int, wait_time: float):
    #     """
    #     Checks if the temperature is stabilized.
    #     :param length: number of temperature points to look at.
    #     :param wait_time: delta-t between each measured temperature.
    #     :return: True if flat; false if not.
    #     """
    #     times = np.empty(length)
    #     temperatures = np.empty(length)
    #     for ii in range(length):
    #         temperatures[ii] = self.ls.read_temperature()
    #         times[ii] = time.time()
    #         print(f"{temperatures[ii]} K")
    #         print(f"Waiting {wait_time} seconds")
    #         time.sleep(wait_time)
    #     times = np.vstack([times, np.ones(length)]).T
    #     slope = np.linalg.lstsq(times, temperatures, rcond=None)[0][0] * 60      # in K / min
    #     return abs(slope) < 0.01

    # def turnaround(self):
    #     if self.check_flatness(3, 30):
    #         sp = self.check_setpoint()
    #         if sp < 50:
    #             self.set_setpoint(300)
    #         else:
    #             self.set_setpoint(20)
    #         return True
    #     else:
    #         return False

    # def start(self):
    #     while True:
    #         accepted = self.turnaround()
    #         if accepted:
    #             time.sleep(3600)
    #         else:
    #             time.sleep(300)


if __name__ == "__main__":
    # c = Controller()
    input("LS>")
