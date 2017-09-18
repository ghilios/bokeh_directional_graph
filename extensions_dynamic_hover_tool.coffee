import {HoverTool, HoverToolView} from "models/tools/inspectors/hover_tool"
import * as p from "core/properties"
import {isString, isFunction} from "core/util/types"

export class DynamicHoverToolView extends HoverToolView
  _render_tooltips: (ds, i, vars) ->
    dynamic_tooltips = @model.dynamic_tooltips
    if not dynamic_tooltips?
      return super(ds, i, vars)
    tooltips = if isFunction(dynamic_tooltips) then dynamic_tooltips(ds, i, vars) else dynamic_tooltips.execute(ds, i, vars)
    if isString(tooltips)
      el = div()
      el.innerHTML = replace_placeholders(tooltips, ds, i, @model.formatters, vars)
      return el
    else if isFunction(tooltips)
      return tooltips(ds, vars)
    else
      rows = div({style: {display: "table", borderSpacing: "2px"}})

      for [label, value] in tooltips
        row = div({style: {display: "table-row"}})
        rows.appendChild(row)

        cell = div({style: {display: "table-cell"}, class: 'bk-tooltip-row-label'}, "#{label}: ")
        row.appendChild(cell)

        cell = div({style: {display: "table-cell"}, class: 'bk-tooltip-row-value'})
        row.appendChild(cell)

        if value.indexOf("$color") >= 0
          [match, opts, colname] = value.match(/\$color(\[.*\])?:(\w*)/)
          column = ds.get_column(colname)
          if not column?
            el = span({}, "#{colname} unknown")
            cell.appendChild(el)
            continue
          hex = opts?.indexOf("hex") >= 0
          swatch = opts?.indexOf("swatch") >= 0
          color = column[i]
          if not color?
            el = span({}, "(null)")
            cell.appendChild(el)
            continue
          if hex
            color = _color_to_hex(color)
          el = span({}, color)
          cell.appendChild(el)
          if swatch
            el = span({class: 'bk-tooltip-color-block', style: {backgroundColor: color}}, " ")
            cell.appendChild(el)
        else
          value = value.replace("$~", "$data_")
          el = span()
          el.innerHTML = replace_placeholders(value, ds, i, @model.formatters, vars)
          cell.appendChild(el)

      return rows

export class DynamicHoverTool extends HoverTool
  default_view: DynamicHoverToolView
  type: "DynamicHoverTool"
  tool_name: "DynamicHover"
  icon: "bk-tool-icon-hover"

  @define {
    dynamic_tooltips: [p.Any, {}]
  }