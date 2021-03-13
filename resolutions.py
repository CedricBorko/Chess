import ctypes

def monitor_size():
    try:
        system = ctypes.windll.user32
        w, h = system.GetSystemMetrics(0), system.GetSystemMetrics(1)
        w_partial = w / 2560
        h_partial = h / 1440
        return w_partial, h_partial
    except EnvironmentError:
        print("Only possible for Windows")
        return 1, 1
