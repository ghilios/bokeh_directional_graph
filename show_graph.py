import networkx as nx

import math
from bokeh.io import show, output_file
from bokeh.plotting import figure
from bokeh.models.graphs import from_networkx, NodesAndLinkedEdges, EdgesAndLinkedNodes, NodesOnly
from bokeh.models import CustomJS, Circle, HoverTool, MultiLine, Line, LabelSet, PanTool, WheelZoomTool, Segment

from directed_graph_renderer import directed_from_networkx, NodesAndEdgesAndLinked
from dynamic_hover_tool import DynamicHoverTool

G = nx.karate_club_graph()
bb = nx.edge_betweenness_centrality(G, normalized=False)
nx.set_edge_attributes(G, 'betweenness', bb)

# hack in edge and node types for the demo
for _, v in G.node.items():
    v['_type'] = 'KarateClubRole'
for _, e_s in G.edge.items():
    for _, e_e in e_s.items():
        e_e['_type'] = 'isFriendsWith'

plot = figure(title="Bokeh Graph Demo", x_range=(-1.1, 1.1), y_range=(-1.1, 1.1),
              tools="pan,wheel_zoom,box_zoom,save,reset,help", toolbar_location="right",
              plot_width=800, plot_height=800)
plot.toolbar.active_scroll = next(t for t in plot.tools if type(t) is WheelZoomTool)

graph = directed_from_networkx(G, nx.spring_layout, scale=10, center=(0, 0))
plot.renderers.append(graph)

graph_layout_map = graph.layout_provider.graph_layout
node_positions = [graph_layout_map[k] for k, v in G.node.items()]

graph.node_renderer.data_source.data['_id'] = [k for k, _ in G.node.items()]
graph.node_renderer.data_source.data['props'] = [v for _, v in G.node.items()]
graph.node_renderer.data_source.data['_xpos'] = [np[0] for np in node_positions]
graph.node_renderer.data_source.data['_ypos'] = [np[1] for np in node_positions]
graph.node_renderer.data_source.tags.append('nodes')

edge_data_source = graph.edge_renderer.data_source
edge_positions = [(graph_layout_map[s_i], graph_layout_map[e_i]) for s_i, e_i in
                  zip(edge_data_source.data['start'], edge_data_source.data['end'])]
edge_x_midpoints = [(x1 + x2) / 2.0 for ((x1, _), (x2, _)) in edge_positions]
edge_y_midpoints = [(y1 + y2) / 2.0 for ((_, y1), (_, y2)) in edge_positions]


def clamp_angle(angle):
    norm_angle = angle % (2 * math.pi)
    if 0.5 * math.pi < norm_angle < 1.5 * math.pi:
        norm_angle += math.pi
    return norm_angle


radian_angles = [math.atan2(y2 - y1, x2 - x1) for ((x1, y1), (x2, y2)) in edge_positions]

# Hack in edge props for demo
edge_props = [{'_type': 'isFriendsWith', 'betweenness': round(G.edge[s_i][e_i]['betweenness'], 2)} for s_i, e_i in
              zip(edge_data_source.data['start'], edge_data_source.data['end'])]

graph.edge_renderer.data_source.data['_id'] = ["--friends_with-->"] * len(edge_data_source.data['start'])
graph.edge_renderer.data_source.data['props'] = edge_props
graph.edge_renderer.data_source.data['_xpos'] = edge_x_midpoints
graph.edge_renderer.data_source.data['_ypos'] = edge_y_midpoints
graph.edge_renderer.data_source.data['_angle'] = radian_angles
graph.edge_renderer.data_source.tags.append('edges')

node_labels = LabelSet(x='_xpos', y='_ypos', text='_id', level='glyph',
                       x_offset=0, y_offset=0, source=graph.node_renderer.data_source, render_mode='canvas',
                       text_align="center", text_baseline="middle")
edge_labels = LabelSet(x='_xpos', y='_ypos', angle='_angle', text='_id', level='glyph',
                       x_offset=0, y_offset=0, source=graph.edge_renderer.data_source, render_mode='canvas',
                       text_align="center", text_baseline="middle")
plot.renderers.append(node_labels)
plot.renderers.append(edge_labels)

graph.node_renderer.glyph = Circle(radius=.1, fill_color='#2b83ba')
graph.edge_renderer.glyph = MultiLine(line_color="#cccccc", line_alpha=0.8, line_width=2)

# green hover for both nodes and edges
graph.node_renderer.hover_glyph = Circle(radius=.1, fill_color='#abdda4')
graph.edge_renderer.hover_glyph = MultiLine(line_color='#abdda4', line_width=4)

# When we hover over nodes, highlight adjecent edges too
graph.inspection_policy = NodesAndEdgesAndLinked()


def dynamic_hover_tooltips(ds, i, vars, Window=None):
    return [
        ("index2", "$index"),
        ("club2", "@_club")
    ]


jscode = """
i = cb_data.i
props = cb_data.ds.data.props[i]
console.log(props, cb_obj, cb_data);
tooltips = []
if (cb_data.ds.tags.indexOf('nodes') !== -1) {
    tooltips.push(["graph_obj_type", "Node"])
} else {
    tooltips.push(["graph_obj_type", "Edge"])
}
Object.keys(props).forEach(function(key) {
    value = props[key];
    console.log(key, value.toString())
    tooltips.push([key, value.toString()])
});
return tooltips
"""

plot.add_tools(DynamicHoverTool(tooltips=[
    ("index", "$index"),
    ("club", "@_club")
],
    #    dynamic_tooltips=CustomJS.from_py_func(dynamic_hover_tooltips)))
    dynamic_tooltips=CustomJS(code=jscode)))

show(plot)
