"""
HyperGradeFX Core Module
Core compositing and post-production functionality
"""

from . import compositing
from . import render_pass_automator
from . import node_blueprints
from . import color_harmony
from . import post_fog
from . import fx_layers
from . import edge_detection
from . import export


def register():
    """Register core classes and operators"""
    compositing.register()
    render_pass_automator.register()
    node_blueprints.register()
    color_harmony.register()
    post_fog.register()
    fx_layers.register()
    edge_detection.register()
    export.register()


def unregister():
    """Unregister core classes and operators"""
    export.unregister()
    edge_detection.unregister()
    fx_layers.unregister()
    post_fog.unregister()
    color_harmony.unregister()
    node_blueprints.unregister()
    render_pass_automator.unregister()
    compositing.unregister()
