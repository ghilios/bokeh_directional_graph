import {GraphHitTestPolicy} from "models/graphs/graph_hit_test_policy"
import {contains, uniq} from "core/util/array"
import {create_hit_test_result} from "core/hittest"

export class NodesAndEdgesAndLinked extends GraphHitTestPolicy
  type: 'NodesAndEdgesAndLinked'

  _do: (geometry, graph_view, final, append) ->
    [node_view, edge_view] = [graph_view.node_view, graph_view.edge_view]
    node_hit_test_result = node_view.glyph.hit_test(geometry)
    edge_hit_test_result = edge_view.glyph.hit_test(geometry)

    if node_hit_test_result == null and edge_hit_test_result == null
      return false

    hit = 0
    all_edge_indices = []
    all_node_indices = []
    if node_hit_test_result != null
      node_indices = (node_view.model.data_source.data.index[i] for i in node_hit_test_result["1d"].indices)
      if node_indices.length
        hit = 1
      edge_source = edge_view.model.data_source
      for i in [0...edge_source.data.start.length]
        if contains(node_indices, edge_source.data.start[i]) or contains(node_indices, edge_source.data.end[i])
          all_edge_indices.push(i)
      Array.prototype.push.apply(all_node_indices, node_indices)

    if edge_hit_test_result != null
      edge_indices = (parseInt(i) for i in Object.keys(edge_hit_test_result['2d'].indices))
      # Since edges enter into nodes, it is possible to have edges "hit" when you're selecting a node. Make sure we're not
      # doing that
      if edge_indices.length and hit == 0
        hit = 2

      nodes = []
      for i in edge_indices
        nodes.push(edge_view.model.data_source.data.start[i])
        nodes.push(edge_view.model.data_source.data.end[i])
        Array.prototype.push.apply(all_node_indices, (node_view.model.data_source.data.index.indexOf(i) for i in uniq(nodes)))
      Array.prototype.push.apply(all_edge_indices, edge_indices)

    node_hit_test_result = create_hit_test_result()
    node_hit_test_result["1d"].indices = uniq(all_node_indices)

    @_node_selector.update(node_hit_test_result, final, append)

    edge_hit_test_result = create_hit_test_result()
    # There is a bug in hover_tool.coffee. If multiple edges are selected...
    edge_hit_test_result["1d"].indices = uniq(all_edge_indices)
    for i in uniq(all_edge_indices)
      edge_hit_test_result["2d"].indices[i] = [0] #currently only supports 2-element multilines, so this is all of it

    @_edge_selector.update(edge_hit_test_result, final, append)

    return hit

  do_selection: (geometry, graph_view, final, append) ->
    @_node_selector = graph_view.node_view.model.data_source.selection_manager.selector
    @_edge_selector = graph_view.edge_view.model.data_source.selection_manager.selector

    did_hit = @_do(geometry, graph_view, final, append)

    graph_view.node_view.model.data_source.selected = @_node_selector.indices
    graph_view.edge_view.model.data_source.selected = @_edge_selector.indices
    graph_view.node_view.model.data_source.select.emit()

    return did_hit != 0

  do_inspection: (geometry, graph_view, final, append) ->
    @_node_selector = graph_view.node_view.model.data_source.selection_manager.get_or_create_inspector(graph_view.node_view.model)
    @_edge_selector = graph_view.edge_view.model.data_source.selection_manager.get_or_create_inspector(graph_view.edge_view.model)

    did_hit = @_do(geometry, graph_view, final, append)

    # silently set inspected attr to avoid triggering data_source.change event and rerender
    graph_view.node_view.model.data_source.setv({inspected: @_node_selector.indices}, {silent: true})
    graph_view.edge_view.model.data_source.setv({inspected: @_edge_selector.indices}, {silent: true})
    if did_hit == 1
      graph_view.node_view.model.data_source.inspect.emit([graph_view.node_view, {geometry: geometry}])
    # HoverTool seems only able to show 1 tooltip at a time. To make this work, we'll have to be selective about which one to emit
    if did_hit == 2
      graph_view.edge_view.model.data_source.inspect.emit([graph_view.edge_view, {geometry: geometry}])

    return did_hit != 0