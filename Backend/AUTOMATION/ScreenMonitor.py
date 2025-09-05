from .screen_monitor.monitor import ScreenMonitorService

_monitor = None

def start_screen_monitor(region=None):
    """
    Launches the background screen-capture thread.
    Returns True if started, False if already running.
    """
    global _monitor
    if _monitor and _monitor.running:
        return False

    _monitor = ScreenMonitorService(region=region)
    _monitor.start()
    # Wait briefly until the first frame is captured to avoid early None frames
    try:
        _monitor.wait_until_ready(timeout=2.0)
    except Exception:
        pass
    return True

def stop_screen_monitor():
    """
    Stops the background thread. Returns True if stopped, False if not running.
    """
    global _monitor
    if _monitor:
        _monitor.stop()
        _monitor = None
        return True
    return False

def get_screen_monitor():
    """
    Returns the live ScreenMonitorService or None.
    """
    return _monitor