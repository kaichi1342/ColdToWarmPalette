from krita import DockWidgetFactory, DockWidgetFactoryBase
from .ColdToWarmPalette import ColdToWarmPalette


DOCKER_NAME = 'ColdToWarmPalette'
DOCKER_ID = 'pykrita_ColdWarmPalette' 


Application.addDockWidgetFactory(
    DockWidgetFactory(DOCKER_ID, DockWidgetFactoryBase.DockPosition.DockRight,
        ColdToWarmPalette))

