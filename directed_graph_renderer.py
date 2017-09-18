from bokeh.models import GraphRenderer
from bokeh.models.sources import ColumnDataSource
from bokeh.models.graphs import GraphHitTestPolicy


class DirectedGraphRenderer(GraphRenderer):
    __implementation__ = 'extensions_directed_graph_renderer.coffee'

    pass


class NodesAndEdgesAndLinked(GraphHitTestPolicy):
    __implementation__ = 'extensions_nodes_and_edes_and_linked.coffee'

    pass


def directed_from_networkx(graph, layout_function, **kwargs):
    # inline import to prevent circular imports
    from bokeh.models.graphs import StaticLayoutProvider

    nodes = graph.nodes()
    edges = graph.edges()
    edges_start = [edge[0] for edge in edges]
    edges_end = [edge[1] for edge in edges]

    node_source = ColumnDataSource(data=dict(index=nodes))
    edge_source = ColumnDataSource(data=dict(
        start=edges_start,
        end=edges_end
    ))

    graph_renderer = DirectedGraphRenderer()
    graph_renderer.node_renderer.data_source.data = node_source.data
    graph_renderer.edge_renderer.data_source.data = edge_source.data

    graph_layout = layout_function(graph, **kwargs)
    graph_renderer.layout_provider = StaticLayoutProvider(graph_layout=graph_layout)

    return graph_renderer
