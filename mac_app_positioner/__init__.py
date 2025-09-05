"""Mac App Positioner - A utility for positioning macOS applications across monitors"""

from .display import DisplayManager
from .application import ApplicationManager
from .profiles import ProfileManager
from .config import load_config

class MacAppPositioner:
    def __init__(self, config_path="config.yaml", verbose=False):
        self.config = load_config(config_path)
        self.display_manager = DisplayManager(verbose=verbose)
        self.app_manager = ApplicationManager(verbose=verbose)
        self.profile_manager = ProfileManager(self.config, self.display_manager, self.app_manager, verbose=verbose)
