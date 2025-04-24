from core.live_plotter import LivePlot
import matplotlib.pyplot as plt

if __name__ == "__main__":
    plotter = LivePlot()
    plotter.run()
    plt.show(block=True)  # <--- manchmal nötig, um das Verhalten in PyCharm zu stabilisieren
