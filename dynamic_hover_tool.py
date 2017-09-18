from bokeh.core.properties import Instance
from bokeh.models.callbacks import Callback
from bokeh.models.tools import HoverTool


class DynamicHoverTool(HoverTool):
    __implementation__ = 'extensions_dynamic_hover_tool.coffee'

    dynamic_tooltips = Instance(Callback)
