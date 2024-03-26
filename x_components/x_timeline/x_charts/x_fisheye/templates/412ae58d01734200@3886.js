// https://observablehq.com/@springbrook/nectis-factory@3886
function _1(md){return(
md`
# Nectis Factory`
)}

function _2(html){return(
html`
<p style="background-color: rgba(255, 229, 100, 0.3); border-left: 0.5rem #e7c000 solid; padding: 8px 24px">
    WARNING<br>Alpha version.
</p>`
)}

function _3(md){return(
md`The Nectis factory provides... AMCharts4, AntVG2, AntVG2Plot, ChartJS, Data, ECharts, Highcharts, Narrative, PlotlyJS, Style, Table, Tile, VisNetwork... Presentations and Visuals... Components and Visuals... Vendors...`
)}

function _4(md){return(
md`
---
## Experiments`
)}

function _5(md){return(
md`
### *Embed SVG Image in Style Sheet*

https://stackoverflow.com/questions/19255296/is-there-a-way-to-use-svg-as-content-in-a-pseudo-element-before-or-after

https://yoksel.github.io/url-encoder/`
)}

function _6(md){return(
md`### *DOM*`
)}

function _7(DOM)
{
  const x = DOM.element("div");
  x.appendChild(DOM.text("Text node using DOM..."));
  return x;
}


function _8(DOM){return(
DOM.text("Text node using DOM...")
)}

function _9(md){return(
md`### *Formulas*`
)}

function _10(tex){return(
tex.options({
  trust: true
})`Termination\,Rate = \dfrac{\href{https://katex.org/}{Terminations}}{Average\,Headcount}*100`
)}

function _11(md){return(
md`### *SQLite*`
)}

function _12(SQLite){return(
SQLite
)}

function _chinook(FileAttachment){return(
FileAttachment("chinook.db").sqlite()
)}

function _14(chinook){return(
chinook.query(`SELECT * FROM albums`)
)}

async function _15(Inputs,chinook){return(
Inputs.table(await chinook.query(`SELECT * FROM albums`))
)}

function _16(md){return(
md`
---
## Settings`
)}

function _defaultVisualHeight(){return(
500
)}

function _18(md){return(
md`
---
## AGGrid Interface`
)}

function _AGGrid(AGGridVisualiser){return(
{ Visualiser: AGGridVisualiser }
)}

function _agGridVersion(){return(
"23.0.2"
)}

function _stylesheet1(html,agGridVersion){return(
html`<link rel='stylesheet'
  href='https://unpkg.com/ag-grid-community@${agGridVersion}/dist/styles/ag-theme-balham.css' />`
)}

function _stylesheet2(html,agGridVersion){return(
html`<link rel='stylesheet'
  href='https://unpkg.com/ag-grid-community@${agGridVersion}/dist/styles/ag-grid.css' />`
)}

function _AGGridVisualiser(require,agGridVersion,defaultVisualHeight,width){return(
class AGGridVisualiser {
  constructor(container, options) {
    this.container = container;
    this.options = options;
    this.element = undefined;
    this.visual = undefined;
  }

  async build() {
    // Load agGrid library. Subsequent loads retrieved from browser cache.
    const AGGrid = await require(`ag-grid-community@${agGridVersion}/dist/ag-grid-community.js`);

    this.element = document.createElement("div");
    if (this.container) {
      this.element.style.height = `${this.container.clientHeight ||
        defaultVisualHeight}px`;
      this.element.style.width = `${this.container.clientWidth || width}px`;
    } else {
      this.element.style.height = `${defaultVisualHeight}px`;
      this.element.style.width = `${width}px`;
    }

    this.visual = new AGGrid.Grid(this.element, this.options);

    return this;
  }

  resize(items) {
    return this;
  }
}
)}

function _container1(html){return(
html`<div class="ag-theme-balham" style="height: 200px; width: 50%"></div>`
)}

async function _25(AGGridVisualiser,container1)
{
  const visualiser = await new AGGridVisualiser(container1, {
    columnDefs: [
      { headerName: "Make", field: "make" },
      { headerName: "Model", field: "model" },
      { headerName: "Price", field: "price" }
    ],
    rowData: [
      { make: "Toyota", model: "Celica", price: 35000 },
      { make: "Ford", model: "Mondeo", price: 32000 },
      { make: "Porsche", model: "Boxter", price: 72000 },
      { make: "Toyota", model: "Celica", price: 35000 },
      { make: "Ford", model: "Mondeo", price: 32000 },
      { make: "Porsche", model: "Boxter", price: 72000 },
      { make: "Toyota", model: "Celica", price: 35000 },
      { make: "Ford", model: "Mondeo", price: 32000 },
      { make: "Porsche", model: "Boxter", price: 72000 }
    ],
    rowSelection: 'single'
  }).build();
  container1.replaceChildren(visualiser.element);
  return visualiser;
}


function _26(md){return(
md`
---
## AMCharts4 Interface`
)}

function _AMCharts4(AMCharts4Visualiser){return(
{ Visualiser: AMCharts4Visualiser }
)}

function _AMCharts4Visualiser(defaultVisualHeight,width){return(
class AMCharts4Visualiser {
  constructor(container, options) {
    this.container = container;
    this.options = options;
    this.element = undefined;
    this.visual = undefined;
  }

  async build() {
    // Load AMCharts4 library. Subsequent loads retrieved from browser cache. Import paths must be hardcoded.
    const modules = await Promise.all([
      import("https://unpkg.com/@amcharts/amcharts4@4.10.20/core.js?module"),
      import("https://unpkg.com/@amcharts/amcharts4@4.10.20/charts?module")
    ]);

    this.element = document.createElement("div");
    if (this.container) {
      this.element.style.height = `${this.container.clientHeight ||
        defaultVisualHeight}px`;
      this.element.style.width = `${this.container.clientWidth || width}px`;
    } else {
      this.element.style.height = `${defaultVisualHeight}px`;
      this.element.style.width = `${width}px`;
    }

    this.options.setup(modules[0], modules[1], this.element);

    return this;
  }

  resize(items) {
    return this;
  }
}
)}

function _29(md){return(
md`
---
## AntVG2 Interface`
)}

function _AntVG2(AntVG2Visualiser){return(
{ Visualiser: AntVG2Visualiser }
)}

function _antVG2Version(){return(
"4.1.22"
)}

function _AntVG2Visualiser(require,antVG2Version){return(
class AntVG2Visualiser {
  constructor(container, options) {
    this.container = container;
    this.options = options;
    this.element = undefined;
    this.visual = undefined;
  }

  async build() {
    // Load AntV G2 library. Subsequent loads retrieved from browser cache. Import paths must be hardcoded.
    const AntVG2 = await require(`@antv/g2@${antVG2Version}`);

    this.element = document.createElement("div");

    // Step 1: Create a Chart instance.
    const chart = new AntVG2.Chart({
      container: this.element,
      width: this.container.clientWidth,
      height: this.container.clientHeight
    });

    // Step 2: Load the data.
    chart.data(this.options.data);

    // Step 3：Declare the grammar of graphics, draw column chart.
    this.options.setup(chart);

    // Step 4: Render chart.
    chart.render();

    return this;
  }

  resize(items) {
    return this;
  }
}
)}

function _33(md){return(
md`
---
## AntVG2Plot Interface`
)}

function _AntVG2Plot(AntVG2PlotVisualiser){return(
{ Visualiser: AntVG2PlotVisualiser }
)}

function _antVG2PlotVersion(){return(
"2.3.28"
)}

function _AntVG2PlotVisualiser(require,antVG2PlotVersion,defaultVisualHeight,width,getAntV2G2PlotChart){return(
class AntVG2PlotVisualiser {
  constructor(container, options) {
    this.container = container;
    this.options = options;
    this.element = undefined;
    this.visual = undefined;
  }

  async build() {
    // Load AntV G2Plot library. Subsequent loads retrieved from browser cache.
    const AntVG2Plot = await require(`@antv/g2plot@${antVG2PlotVersion}`);

    this.element = document.createElement("div");
    this.element.style.visibility = "hidden";
    if (this.container) {
      this.element.style.height = `${this.container.clientHeight ||
        defaultVisualHeight}px`;
      this.element.style.width = `${this.container.clientWidth || width}px`;
    } else {
      this.element.style.height = `${defaultVisualHeight}px`;
      this.element.style.width = `${width}px`;
    }
    document.body.appendChild(this.element);
    const AntVG2PlotChart = getAntV2G2PlotChart(AntVG2Plot, this.options.type);

    this.visual = new AntVG2PlotChart(this.element, this.options.options);
    this.visual.render();

    this.element.remove();
    this.element.style.visibility = "visible";

    return this;
  }

  resize(items) {
    return this;
  }
}
)}

function _getAntV2G2PlotChart(){return(
(AntVG2Plot, id) => {
  switch (id) {
    case "chord":
      return AntVG2Plot.Chord;
    case "rose":
      return AntVG2Plot.Rose;
    default:
      return undefined;
  }
}
)}

function _38(md){return(
md`
---
## ChartJS Interface`
)}

function _ChartJS(ChartJSVisualiser,drawConnectionLines,getLegendSymbol,headcountTooltipHandler){return(
{
  Visualiser: ChartJSVisualiser,
  drawConnectionLines,
  getLegendSymbol,
  headcountTooltipHandler
}
)}

function _chartJSURL(chartJSVersion){return(
`https://cdn.jsdelivr.net/npm/chart.js@${chartJSVersion}/dist/chart.esm.js`
)}

function _chartJSVersion(){return(
"3.4.1"
)}

function _ChartJSVisualiser(loadChartJSLibrary,width){return(
class ChartJSVisualiser {
  constructor(container, options) {
    this.container = container;
    this.options = options;
    this.element = undefined;
    this.visual = undefined;
  }

  async build() {
    // Load Chart.js library. Subsequent loads retrieved from browser cache.
    const ChartJS = await loadChartJSLibrary();

    this.container.style.position = "relative";
    this.container.style.height = `500px`;
    this.container.style.width = `${width - 300 - 32}px`;

    this.element = document.createElement("canvas");
    //if (this.container) {
    //  // TODO: Required when embedded in HelpScout widget.
    //  // Does not cause issue because it is deleted an re added by notebook visualise method.
    //  // Not sure why it is not required in other circumstances.
    //  // Need to review approach once things stabalise. Should create tempory placeholder so chart does not appear while building.
    this.container.appendChild(this.element);

    //this.element.style.height = `${
    //  this.container.clientHeight || defaultVisualHeight
    //}px`;
    //this.element.style.width = `${this.container.clientWidth || width}px`;
    ////} else {
    ////  this.element.style.height = `${defaultVisualHeight}px`;
    ////  this.element.style.width = `${width}px`;
    ////}
    //this.element.style.padding = "0 16px";

    this.visual = new ChartJS(this.element, this.options);

    //const resizeVisual = () => this.visual.resize();
    //window.addEventListener("resize", resizeVisual);

    //resizeVisual();

    return this;
  }

  resize(items) {
    return this;
  }
}
)}

function _loadChartJSLibrary(chartJSURL){return(
async () => {
  // Import Chart.js module.
  const chartJS = await import(chartJSURL);
  const chartJSChart = chartJS.Chart;
  // Register controllers, elements, scales and plugins.
  chartJSChart.register(chartJS.BarController);
  chartJSChart.register(chartJS.BarElement);
  chartJSChart.register(chartJS.CategoryScale);
  chartJSChart.register(chartJS.Legend);
  chartJSChart.register(chartJS.LineController);
  chartJSChart.register(chartJS.LineElement);
  chartJSChart.register(chartJS.LinearScale);
  chartJSChart.register(chartJS.PointElement);
  chartJSChart.register(chartJS.Title);
  chartJSChart.register(chartJS.Tooltip);
  // Modify default options.
  chartJSChart.defaults.animation = false;
  chartJSChart.defaults.font.size = 16;
  chartJSChart.defaults.layout.padding = 2;
  chartJSChart.defaults.plugins.legend.position = "bottom";
  chartJSChart.defaults.plugins.legend.labels.boxHeight = 15;
  chartJSChart.defaults.plugins.legend.labels.boxWidth = 30;
  chartJSChart.defaults.plugins.title.display = true;
  chartJSChart.defaults.plugins.title.font.size = 20;
  chartJSChart.defaults.plugins.title.font.weight = "normal";
  chartJSChart.defaults.maintainAspectRatio = false;
  chartJSChart.defaults.responsive = true;
  // Return library.
  return chartJSChart;
}
)}

function _44(md){return(
md`### Connection Lines`
)}

function _drawConnectionLines(drawConnectionLine){return(
(chart, args, options) => {
  const config = chart.config;
  const configData = config.data;
  const configOptions = config.options;

  if (!configOptions.displayConnectionLines) return;

  const scales = chart.scales;
  const xAxis = scales.x;
  const yAxis = scales.y;

  const canvasRenderingContext2D = chart.ctx;

  const dataset = configData.datasets[2];
  const count = dataset.data.length - 1;
  for (let index = 0; index < count; index++) {
    const row = dataset.data[index];
    drawConnectionLine(canvasRenderingContext2D, xAxis, yAxis, row[1], index);
  }
}
)}

function _drawConnectionLine(scaleLinear){return(
(context, xAxis, yAxis, line, index) => {
  const y1 = scaleLinear(
    line,
    yAxis.min,
    yAxis.max,
    yAxis.height,
    0,
    yAxis.top
  );

  context.save();

  context.strokeStyle = '#aaa';
  context.globalCompositeOperation = 'destination-over';
  context.lineWidth = 1;

  const bandWidth = xAxis.width / xAxis.ticks.length;
  const left = xAxis.left + bandWidth * index + bandWidth * 0.14;
  const right = left + bandWidth * 2 - bandWidth * 0.28;

  context.beginPath();
  context.moveTo(left + 1, y1);
  context.lineTo(right - 1, y1);
  context.stroke();

  context.restore();
}
)}

function _scaleLinear(){return(
(
  value,
  domainStart,
  domainEnd,
  rangeStart,
  rangeEnd,
  rangeOffset
) => {
  const factor = (rangeEnd - rangeStart) / (domainEnd - domainStart);
  return rangeStart + factor * (value - domainStart) + rangeOffset;
}
)}

function _48(md){return(
md`### Legend Symbol`
)}

function _getLegendSymbol(getColour){return(
(legendHitBoxes, legendIndex) => {
  const green =
    legendIndex === 0 ? getColour('paired', 2) : getColour('paired', 3);
  const orange =
    legendIndex === 0 ? getColour('paired', 6) : getColour('paired', 7);

  if (legendHitBoxes.length < legendIndex + 1) return undefined;
  const left = legendHitBoxes[legendIndex].left;
  const top = legendHitBoxes[legendIndex].top;

  const canvas = document.createElement('canvas');
  const context = canvas.getContext('2d');
  const gradient = context.createLinearGradient(left, top, left + 30, top + 15);

  gradient.addColorStop(0, green);
  gradient.addColorStop(0.47, green);
  gradient.addColorStop(0.47, 'white');
  gradient.addColorStop(0.53, 'white');
  gradient.addColorStop(0.53, orange);
  gradient.addColorStop(1, orange);

  canvas.remove();
  return gradient;
}
)}

function _50(md){return(
md`### Tooltip`
)}

function _headcountTooltipHandler(establishTooltip,buildRow){return(
(context, workforceData) => {
  // Tooltip Element
  const { chart, tooltip } = context;
  const { caretElement, tooltipElement } = establishTooltip(chart, tooltip);

  // Hide if no tooltip
  if (tooltip.opacity === 0) {
    caretElement.style.opacity = 0;
    tooltipElement.style.opacity = 0;
    return;
  }

  // Set Text
  if (tooltip.body) {
    const thead = document.createElement('thead');
    for (const title of tooltip.title || []) {
      const tr = document.createElement('tr');
      const th = document.createElement('th');
      th.style.cssText =
        'color: white; font-weight: bold; padding: 0 0 5px 5px; text-align: left';
      const text = document.createTextNode(title);
      th.appendChild(text);
      tr.appendChild(th);
      thead.appendChild(tr);
    }
    const tbody = document.createElement('tbody');

    const month = workforceData[tooltip.dataPoints[0].dataIndex];
    tbody.appendChild(buildRow('Opening Headcount', month.openingHeadcount));
    tbody.appendChild(buildRow('+ Starting Hires', month.startingHires));
    tbody.appendChild(
      buildRow(
        '= Starting Headcount',
        month.openingHeadcount + month.startingHires
      )
    );
    tbody.appendChild(
      buildRow('+ In Period Hires', month.hires - month.startingHires)
    );
    tbody.appendChild(
      buildRow(
        '- In Period Terminations',
        month.terminations - month.endingTerminations
      )
    );
    tbody.appendChild(
      buildRow(
        '= Ending Headcount',
        month.closingHeadcount + month.endingTerminations
      )
    );
    tbody.appendChild(
      buildRow('- Ending Terminations', month.endingTerminations)
    );
    tbody.appendChild(buildRow('= Closing Headcount', month.closingHeadcount));

    const tableRoot = tooltipElement.querySelector('table');

    // Remove old children
    while (tableRoot.firstChild) {
      tableRoot.firstChild.remove();
    }

    // Add new children
    tableRoot.appendChild(thead);
    tableRoot.appendChild(tbody);
  }

  const { offsetLeft: positionX, offsetTop: positionY } = chart.canvas;

  const canvasBounds = chart.canvas.getBoundingClientRect();
  const canvasBottom = positionY + canvasBounds.height;

  const tooltipBounds = tooltipElement.getBoundingClientRect();
  const tooltipHeight = tooltipBounds.height;
  const tooltipWidth = tooltipBounds.width;

  let top = positionY + tooltip.caretY - 12;

  if (top + tooltipHeight > canvasBottom)
    top -= top + tooltipHeight - canvasBottom;

  caretElement.className = `caret ${tooltip.xAlign}`;
  caretElement.style.cssText = `left: ${positionX +
    tooltip.caretX -
    6}px; top: ${positionY + tooltip.caretY}px`;

  // Display, position, and set styles for font
  tooltipElement.style.opacity = 1;
  if (tooltip.xAlign === 'left') {
    tooltipElement.style.left = `${positionX + tooltip.caretX + 6}px`;
  } else {
    tooltipElement.style.left = `${positionX +
      tooltip.caretX -
      tooltipWidth -
      6}px`;
  }
  tooltipElement.style.top = `${top}px`;
}
)}

function _establishTooltip(){return(
(chart, tooltip) => {
  const parentNode = chart.canvas.parentNode;

  let caretElement = parentNode.querySelector('#nectisCaret');
  if (!caretElement) {
    caretElement = document.createElement('div');
    caretElement.id = 'nectisCaret';
    parentNode.appendChild(caretElement);
  }

  let tooltipElement = parentNode.querySelector('#nectisTooltip');
  if (!tooltipElement) {
    tooltipElement = document.createElement('div');
    tooltipElement.id = 'nectisTooltip';
    tooltipElement.style.background = 'rgba(0, 0, 0, 0.75)';
    tooltipElement.style.borderRadius = '5px';
    tooltipElement.style.color = 'white';
    tooltipElement.style.opacity = 1;
    tooltipElement.style.padding = `${tooltip.options.padding}px `;
    tooltipElement.style.pointerEvents = 'none';
    tooltipElement.style.position = 'absolute';
    const table = document.createElement('table');
    table.style['border-collapse'] = 'collapse';
    tooltipElement.appendChild(table);
    parentNode.appendChild(tooltipElement);
  }

  return { caretElement, tooltipElement };
}
)}

function _buildRow(headcountFormatter){return(
(label, value) => {
  const tr = document.createElement('tr');
  tr.style.borderWidth = 0;

  const tdLabel = document.createElement('td');
  tdLabel.style.cssText =
    'border-width: 0; border-style: solid; border-color: white; color: white; padding: 5px 5px';
  tdLabel.appendChild(
    document.createTextNode((label || '').replaceAll(' ', '\xa0'))
  );
  tr.appendChild(tdLabel);

  const tdValue = document.createElement('td');
  const border = label.startsWith('=') ? 'border-top: 1px solid white; ' : '';
  tdValue.style.cssText = `${border}color: white; padding: 5px 5px; text-align: right`;
  tdValue.appendChild(
    document.createTextNode(headcountFormatter().format(value))
  );
  tr.appendChild(tdValue);

  return tr;
}
)}

function _headcountFormatter(){return(
() => new Intl.NumberFormat()
)}

function _55(md){return(
md`
---
## D3 Chord Interface`
)}

function _D3Chord(D3ChordVisualiser){return(
{ Visualiser: D3ChordVisualiser }
)}

function _D3ChordVisualiser(defaultVisualHeight,width,chart){return(
class D3ChordVisualiser {
  constructor(container, options) {
    this.container = container;
    this.options = options;
    this.element = undefined;
    this.visual = undefined;
  }

  async build() {
    const chartHeight = this.container.clientHeight || defaultVisualHeight;
    const chartWidth = this.container.clientWidth || width;
    this.element = chart(this.options.data, chartHeight, chartWidth);
    return this;
  }

  resize(items) {
    return this;
  }
}
)}

function _chart(d3,width,DOM){return(
(data, chartHeight, chartWidth) => {
  const names = Array.from(new Set(data.flatMap(d => [d.source, d.target])));
  const color = d3.scaleOrdinal(names, d3.schemeCategory10);

  const innerRadius = Math.min(width, chartHeight) * 0.5 - 20;
  const outerRadius = innerRadius + 6;

  const arc = () =>
    d3
      .arc()
      .innerRadius(innerRadius)
      .outerRadius(outerRadius);

  const chord = () =>
    d3
      .chordDirected()
      .padAngle(12 / innerRadius)
      .sortSubgroups(d3.descending)
      .sortChords(d3.descending);

  const formatValue = x => `${x.toFixed(0)}B`;

  const matrix = () => {
    const index = new Map(names.map((name, i) => [name, i]));
    const matrix = Array.from(index, () => new Array(names.length).fill(0));
    for (const { source, target, value } of data)
      matrix[index.get(source)][index.get(target)] += value;
    return matrix;
  };

  const ribbon = () =>
    d3
      .ribbonArrow()
      .radius(innerRadius - 0.5)
      .padAngle(1 / innerRadius);

  const svg = d3
    .create("svg")
    .attr("viewBox", [
      -chartWidth / 2,
      -chartHeight / 2,
      chartWidth,
      chartHeight
    ]);

  const chords = chord()(matrix());

  const textId = DOM.uid("text");

  svg
    .append("path")
    .attr("id", textId.id)
    .attr("fill", "none")
    .attr("d", d3.arc()({ outerRadius, startAngle: 0, endAngle: 2 * Math.PI }));

  svg
    .append("g")
    .attr("fill-opacity", 0.75)
    .selectAll("g")
    .data(chords)
    .join("path")
    .attr("d", ribbon())
    .attr("fill", d => color(names[d.target.index]))
    .style("mix-blend-mode", "multiply")
    .append("title")
    .text(
      d =>
        `${names[d.source.index]} owes ${names[d.target.index]} ${formatValue(
          d.source.value
        )}`
    );

  svg
    .append("g")
    .attr("font-family", "sans-serif")
    .attr("font-size", 10)
    .selectAll("g")
    .data(chords.groups)
    .join("g")
    .call(g =>
      g
        .append("path")
        .attr("d", arc())
        .attr("fill", d => color(names[d.index]))
        .attr("stroke", "#fff")
    )
    .call(g =>
      g
        .append("text")
        .attr("dy", -3)
        .append("textPath")
        .attr("xlink:href", textId.href)
        .attr("startOffset", d => d.startAngle * outerRadius)
        .text(d => names[d.index])
    )
    .call(g =>
      g.append("title").text(
        d => `${names[d.index]}
owes ${formatValue(d3.sum(matrix()[d.index]))}
is owed ${formatValue(d3.sum(matrix(), row => row[d.index]))}`
      )
    );

  return svg.node();
}
)}

function _59(md){return(
md`
---
## Data Interface`
)}

function _Data(buildMeasureMap,monthAbbreviations,monthNames){return(
{
  buildMeasureMap,
  monthAbbreviations,
  monthNames
}
)}

function _monthAbbreviations(){return(
[
  'Jan',
  'Feb',
  'Mar',
  'Apr',
  'May',
  'Jun',
  'Jul',
  'Aug',
  'Sep',
  'Oct',
  'Nov',
  'Dec'
]
)}

function _monthNames(){return(
[
  'January',
  'February',
  'March',
  'April',
  'May',
  'June',
  'July',
  'August',
  'September',
  'October',
  'November',
  'December'
]
)}

function _buildMeasureMap(buildMapOfArrays){return(
(data, measures) => {
  return data.reduce((result, row) => {
    measures.forEach(measure => {
      if (measure.source) {
        if (typeof measure.source === "function") {
          result[measure.id].push(measure.source(row));
        } else {
          result[measure.id].push(row[String(measure.source)]);
        }
      } else {
        result[measure.id].push(row[measure.id]);
      }
    });
    return result;
  }, buildMapOfArrays(measures));
}
)}

function _buildMapOfArrays(){return(
(keys, arrayLength, itemValue) =>
  keys.reduce((result, key) => {
    const arr = arrayLength ? new Array(arrayLength) : [];
    return {
      ...result,
      [key.id]: arr.fill(itemValue === null ? null : itemValue)
    };
  }, {})
)}

function _65(md){return(
md`
---
## ECharts Interface`
)}

function _ECharts(EChartsVisualiser){return(
{ Visualiser: EChartsVisualiser }
)}

function _eChartsVersion(){return(
"5.1.2"
)}

function _eChartsURL(eChartsVersion){return(
`https://cdnjs.cloudflare.com/ajax/libs/echarts/${eChartsVersion}/echarts.esm.min.js`
)}

function _EChartsVisualiser(eChartsURL,defaultVisualHeight,width){return(
class EChartsVisualiser {
  constructor(container, options) {
    this.container = container;
    this.options = options;
    this.element = undefined;
    this.visual = undefined;
  }

  async build() {
    // Load ECharts library. Subsequent loads retrieved from browser cache.
    const ECharts = await import(eChartsURL);

    this.element = document.createElement("div");
    if (this.container) {
      this.element.style.height = `${this.container.clientHeight || defaultVisualHeight}px`;
      this.element.style.width = `${this.container.clientWidth || width}px`;
    } else {
      this.element.style.height = `${defaultVisualHeight}px`;
      this.element.style.width = `${width}px`;
    }

    this.visual = ECharts.init(this.element);
    this.visual.setOption(this.options);

    return this;
  }

  resize(items) {
    return this;
  }
}
)}

function _70(md){return(
md`
---
## Footer Interface`
)}

function _Footer(footer){return(
footer
)}

function _footer1(md,htl,narrativeStyle){return(
(markdown, options) => {
  const content = md`${markdown}`;
  return htl.html`
<div class="nectis" style="position: relative">
  <style scoped>${narrativeStyle}</style>
  <div style="background-color: yellow; position: absolute; right: 0px">Options...</div>
  © 2021 Nectis
</div>`;
}
)}

function _footer(html){return(
() =>
  Object.assign(
    html`
<div style="background: lightgrey; display: flex; padding: 5px">
  <div>© 2021 Nectis</div>
  <div style="margin-left: auto; visibility: hidden">Options...</div>
</div>`,
    {
      onmouseenter: event =>
        (event.target.lastElementChild.style.visibility = "visible"),
      onmouseleave: event =>
        (event.target.lastElementChild.style.visibility = "hidden")
    }
  )
)}

function _74(md){return(
md`
---
## Highcharts Interface`
)}

function _Highcharts(HighchartsVisualiser){return(
{ Visualiser: HighchartsVisualiser }
)}

function _highchartsURLPrefix(highchartsVersion){return(
`https://cdn.jsdelivr.net/npm/highcharts@${highchartsVersion}/es-modules/masters/`
)}

function _highchartsVersion(){return(
"9.1.2"
)}

function _HighchartsVisualiser(loadHighchartsLibrary,defaultVisualHeight,width,addBorderToLegendSymbols){return(
class HighchartsVisualiser {
  constructor(container, options) {
    this.container = container;
    this.options = options;
    this.element = undefined;
    this.visual = undefined;
  }

  async build() {
    // Load Highcharts library. Subsequent loads retrieved from browser cache.
    const Highcharts = await loadHighchartsLibrary();

    this.element = document.createElement("div");
    if (this.container) {
      this.element.style.height = `${this.container.clientHeight ||
        defaultVisualHeight}px`;
      this.element.style.width = `${this.container.clientWidth || width}px`;
    } else {
      this.element.style.height = `${defaultVisualHeight}px`;
      this.element.style.width = `${width}px`;
    }

    this.visual = Highcharts.chart(this.element, this.options, chart => {
      addBorderToLegendSymbols(chart);
    });

    return this;
  }

  resize(items) {
    return this;
  }
}
)}

function _addBorderToLegendSymbols(){return(
chart => {
  for (const series of chart.series || []) {
    const legendSymbol = series.legendSymbol;
    if (!legendSymbol) continue;
    const element = legendSymbol.element;
    if (!element) continue;
    element.setAttribute('stroke-width', '1');
    element.setAttribute('stroke', series.options.borderColor);
  }
}
)}

function _loadHighchartsLibrary(highchartsVersion){return(
async () => {
  // Import Highcharts modules.
  const imports = await Promise.all([
    import(`https://code.highcharts.com/${highchartsVersion}/es-modules/masters/highcharts.src.js`),
    //import(`${highchartsURLPrefix}highcharts.src.js`),
    import(`https://code.highcharts.com/${highchartsVersion}/es-modules/masters/highcharts-more.src.js`)
    //import(`${highchartsURLPrefix}highcharts-more.src.js`)
  ]);
  const Highcharts = imports[0].default;
  //const highchartsMore = imports[1].default;
  //highchartsMore(Highcharts);
  // Modify default options.
  Highcharts.setOptions({ lang: { thousandsSep: ',' } });
  // Return library.
  return Highcharts;
}
)}

function _81(md){return(
md`
---
## LokiJS Interface`
)}

function _LokiJS(Database){return(
{ Database }
)}

function _lokiVersion(){return(
"1.5.12"
)}

function _Database(require,lokiVersion){return(
class Database {
  constructor(name) {
    this.name = name;
    this.database = undefined;
  }

  async establish() {
    // Load Loki.js library. Subsequent loads retrieved from browser cache.
    const modules = await Promise.all([
      require(`lokijs@${lokiVersion}/build/lokijs.min.js`),
      require(`lokijs@${lokiVersion}/build/loki-indexed-adapter.min.js`)
    ]);
    const loki = modules[0];
    const LokiIndexedAdapter = modules[1];

    return new Promise((resolve, reject) => {
      try {
        this.database = new loki(this.name, {
          adapter: new LokiIndexedAdapter(),
          autoload: true,
          autoloadCallback: () => resolve(this)
        });
      } catch (error) {
        reject(error);
      }
    });
  }

  establishCollection(name, indices) {
    const collection = this.database.getCollection(name);
    if (collection) return collection;
    return this.database.addCollection(name, { disableMeta: true, indices });
  }

  save() {
    this.database.save();
  }
}
)}

function _85(md){return(
md`
---
## Narrative Interface`
)}

function _Narrative(narrative1){return(
narrative1
)}

function _narrative1(defaultTruncateHeight1,md,buildButton1,htl,narrativeStyle){return(
(markdown, options) => {
  let truncate;
  let truncateHeight;
  if (options) {
    truncate = options.truncate === false ? false : true;
    truncateHeight = options.truncateHeight || defaultTruncateHeight1;
  } else {
    truncate = true;
    truncateHeight = defaultTruncateHeight1;
  }

  const content = md`${markdown}`;
  document.body.appendChild(content);
  const height = content.clientHeight;
  content.remove();

  let button;
  if (truncate && height > truncateHeight) {
    content.style["-webkit-mask-image"] =
      "linear-gradient(180deg, #000 40%, transparent)";
    content.style.maxHeight = `${truncateHeight}px`;
    button = buildButton1(truncateHeight);
  } else {
    button = "";
  }

  return htl.html`
<div class="nectis" style="position: relative">
  <style scoped>${narrativeStyle}</style>
  ${content}${button}
</div>`;
}
)}

function _88(md){return(
md`### *Remove Following*`
)}

function _defaultTruncateHeight1(){return(
150
)}

function _buildButton1(htl){return(
height => {
  return htl.html`
<div style="left: 0; position: absolute; margin: 0 auto; max-width: 640px; right: 0; text-align: right; top: 0">
  <button id="toggleLength" onclick=${event => {
    const element =
      event.target.parentElement.parentElement.parentElement.children[1];
    if (element.style.maxHeight) {
      event.target.innerHTML = "Less";
      element.style["-webkit-mask-image"] = null;
      element.style.maxHeight = null;
    } else {
      event.target.innerHTML = "More";
      element.style["-webkit-mask-image"] =
        "linear-gradient(180deg, #000 40%, transparent)";
      element.style.maxHeight = `${height}px`;
    }
  }}>More</button>
</div>`;
}
)}

function _narrative2(htl,narrativeStyle,md){return(
(markdown, options) => {
  return htl.html`
<div class="nectis" style="position: relative">
  <style scoped>${narrativeStyle}</style>
  ${md(markdown)}
</div>`;
}
)}

function _92(md){return(
md`
---
## PlotlyJS Interface`
)}

function _PlotlyJS(PlotlyJSVisualiser){return(
{ Visualiser: PlotlyJSVisualiser }
)}

function _PlotlyJSVisualiser(require,defaultVisualHeight,width){return(
class PlotlyJSVisualiser {
  constructor(container, options) {
    this.container = container;
    this.options = options;
    this.element = undefined;
    this.visual = undefined;
  }

  async build() {
    // Load Plotly.js library. Subsequent loads retrieved from browser cache.
    const PlotlyJS = await require("https://cdn.plot.ly/plotly-latest.min.js");

    this.element = document.createElement("div");
    let plotHeight;
    let plotWidth;
    if (this.container) {
      plotHeight = this.container.clientHeight || defaultVisualHeight;
      plotWidth = this.container.clientWidth || width;
    } else {
      plotHeight = defaultVisualHeight;
      plotWidth = width;
    }

    this.visual = PlotlyJS.newPlot(this.element, this.options, {
      height: plotHeight,
      width: plotWidth
    });

    return this;
  }

  resize(items) {
    return this;
  }
}
)}

function _95(md){return(
md`
---
## Style Interface`
)}

function _Style(colours,narrativeStyle,palettes){return(
{ colours, narrative: narrativeStyle, palettes }
)}

function _colours(getColour){return(
{
  opening: getColour('tableau10', 5),
  starting: getColour('tableau10', 3),
  hires: getColour('paired', 2),
  terminations: getColour('paired', 6),
  ending: getColour('tableau10', 0),
  closing: getColour('tableau10', 2),
  openCloseDecrease: getColour('paired', 6),
  openCloseIncrease: getColour('paired', 2),
  startStopDecrease: getColour('paired', 7),
  startStopIncrease: getColour('paired', 3)
}
)}

function _palettes(){return(
{
  category10: [
    '#1f77b4',
    '#ff7f0e',
    '#2ca02c',
    '#d62728',
    '#9467bd',
    '#8c564b',
    '#e377c2',
    '#7f7f7f',
    '#bcbd22',
    '#17becf'
  ],
  dark2: [
    '#1b9e77',
    '#d95f02',
    '#7570b3',
    '#e7298a',
    '#66a61e',
    '#e6ab02',
    '#a6761d',
    '#666666'
  ],
  paired: [
    '#a6cee3',
    '#1f78b4',
    '#b2df8a',
    '#33a02c',
    '#fb9a99',
    '#e31a1c',
    '#fdbf6f',
    '#ff7f00',
    '#cab2d6',
    '#6a3d9a',
    '#ffff99',
    '#b15928'
  ],
  tableau10: [
    '#4e79a7',
    '#f28e2c',
    '#e15759',
    '#76b7b2',
    '#59a14f',
    '#edc949',
    '#af7aa1',
    '#ff9da7',
    '#9c755f',
    '#bab0ab'
  ]
}
)}

function _getColour(palettes){return(
(paletteId, index) => {
  return palettes[paletteId][index % palettes[paletteId].length];
}
)}

function _narrativeStyle(){return(
`
:root {
  --border_colour: #eee;
  --max_width: 640px;
}

.nectis * {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
}

.nectis h1 {
    font-weight: 400;
    font-size: 26px;
    /*margin-left: auto;*/
    /*margin-right: auto;*/
    max-width: var(--max_width);*/
}

.nectis h2 {
    border-bottom: 1px solid var(--border_colour);
    font-weight: 400;
    font-size: 22px;
    /*margin-left: auto;*/
    /*margin-right: auto;*/
    margin-top: 64px;
    /*max-width: var(--max_width);*/
    padding-bottom: 5px;
}
.nectis h2::before {
    background-image: url('https://nectis-content.web.app/analytics-light.svg');
    background-size: 27px 24px;
    content: '';
    display: inline-block;
    height: 24px;
    margin-right: 10px;
    width: 27px;
}

.nectis p {
    font-size: 16px;
    /*margin-left: auto;*/
    /*margin-right: auto;*/
    /*max-width: var(--max_width);*/
}

.nectis ul {
    font-size: 16px;
    /*margin-left: auto;*/
    /*margin-right: auto;*/
    /*max-width: var(--max_width);*/
}

.nectis div.warning {
    background-color: rgba(255, 229, 100, 0.3);
    border-left: 0.5rem #e7c000 solid;
    color: #6b5900;
    font-size: 16px;
    /*margin: 16px auto;*/
    /*max-width: var(--max_width);*/
}
.nectis div.warning > div {
    font-weight: 600;
    padding: 8px 24px;
}
.nectis div.warning > div > div {
    font-weight: 400;
}`
)}

function _panelStyle(){return(
`
:root {
  --border_colour: #eee;
}

.nectis .tabBar {
    height: 48px;
}

.nectis .tabButton {
    border-bottom: 2px solid transparent;
    cursor: pointer;
    display: flex;
    font-size: 16px;
    flex-direction: column;
    justify-content: center;
    padding-left: 15px;
    padding-right: 15px;
}
.nectis .tabButton:hover {
    background: #f7f7f7;
}
.nectis .tabButton.selected {
    border-bottom-color: #9e9e9e;
}
.nectis .tabButton.selected:hover {
    background: #f7f7f7;
}

.nectis .optionsButton {
    border-top: 2px solid transparent;
    cursor: pointer;
    font-size: 16px;
    padding: 5px 10px 7px 10px;
}
.nectis .optionsButton:hover {
    background: #f7f7f7;
}

.nectis .vendorButton {
    border-top: 2px solid transparent;
    align-items: center;
    cursor: pointer;
    display: flex;
    font-size: 16px;
    flex-direction: row;
    padding: 5px 10px 7px 10px;
}
.nectis .vendorButton:hover {
    background: #f7f7f7;
}
.nectis .vendorButton.selected {
    border-top-color: #9e9e9e;
}
.nectis .vendorButton.selected:hover {
    background: #f7f7f7;
}

.nectis .visualPanel {
    background: #fcfcfc;
    border: 1px solid var(--border_colour);
}`
)}

function _tableStyle(){return(
`
.nectis table {
    border-collapse: collapse;
    margin: 0;
    max-width: none;
}
.nectis tr:not(:last-child) {
    border-bottom: solid 1px #eee;
    line-height: normal;
}
.nectis th {
    font-size: 16px;
    font-weight: 400;
    padding: 5px 16px;
    vertical-align: bottom;
}
.nectis td {
    font-size: 16px;
    padding: 5px 16px;
}`
)}

function _103(md){return(
md`
---
## Table Interface`
)}

function _TableVisualiser(tableStyle,buildCellStyle,formatCellValue){return(
class TableVisualiser {
  constructor(element, options) {
    this.element = element;
    this.options = options;
  }

  show() {
    const data = this.options.data;
    const columns = this.options.columns;

    const wrapper = document.createElement('div');
    wrapper.style.cssText = 'overflow-x: scroll; padding: 10px 0 10px 10px';

    const style = document.createElement('style');
    style.appendChild(document.createTextNode(tableStyle));
    wrapper.appendChild(style);

    const tableWrapper = document.createElement('div');
    tableWrapper.style.cssText = 'display: flex';
    const table = document.createElement('table');
    table.style.cssText = 'flex: 1 1 auto';
    const tableRightPadding = document.createElement('div'); // Implements padding on right.
    tableRightPadding.style.cssText = 'flex: 0 0 10px';

    const header = document.createElement('tr');
    for (const column of columns) {
      const th = document.createElement('th');
      th.style.cssText = buildCellStyle(column);
      const text = document.createTextNode(column.label);
      th.append(text);
      header.appendChild(th);
    }
    table.appendChild(header);

    for (const record of data) {
      const row = document.createElement('tr');
      for (const column of columns) {
        const td = document.createElement('td');
        td.style.cssText = buildCellStyle(column);
        let text;
        if (typeof column.source === 'function') {
          text = document.createTextNode(
            formatCellValue(column, column.source(record, column))
          );
        } else {
          text = document.createTextNode(
            formatCellValue(column, record[column.source])
          );
        }
        td.appendChild(text);
        row.appendChild(td);
      }
      table.appendChild(row);
    }

    tableWrapper.appendChild(table);
    tableWrapper.appendChild(tableRightPadding);
    wrapper.appendChild(tableWrapper);
    this.element.replaceChildren(wrapper);

    return this;
  }

  resize(items) {
    return this;
  }
}
)}

function _buildCellStyle(){return(
column => {
  switch (column.typeId) {
    case 'decimalNumber':
    case 'wholeNumber':
      return ` text-align: ${column.align || 'right'}`;
    default:
      return ` text-align: ${column.align || 'left'}`;
  }
}
)}

function _formatCellValue(){return(
(column, value) => {
  if (!value) return '';
  switch (column.typeId) {
    case 'decimalNumber':
      return value.toLocaleString(undefined, {
        maximumFractionDigits: 2,
        minimumFractionDigits: 2
      });
    default:
      return value.toLocaleString();
  }
}
)}

function _107(md){return(
md`
---
## Tile Interface`
)}

function _Tile(define,show){return(
{ define, show }
)}

function _define(panelStyle){return(
(options) => {
  // Build tile element.
  const tileElement = document.createElement("div");
  tileElement.className = "nectis";
  if (options) tileElement.dataset.options = JSON.stringify(options);
  // Build style element and append to tile element.
  const styleElement = document.createElement("style");
  styleElement.appendChild(document.createTextNode(panelStyle));
  tileElement.appendChild(styleElement);
  // Build tile content element and append to tile element.
  const tileContentElement = document.createElement("div");
  tileContentElement.id = "tileContent";
  tileElement.appendChild(tileContentElement);
  // Return tile element.
  return tileElement;
}
)}

function _show(TabComponent){return(
tileElement => {
  // Establish options object.
  const options = JSON.parse(tileElement.dataset.options) || {};
  // Establish tab array.
  const fixedHeight = options.fixedHeight === false ? false : true;
  const tabs = options.tabs || [];
  // Render tab component.
  const tileContent = tileElement.querySelector('#tileContent');
  new TabComponent(tileContent, tabs, fixedHeight);
}
)}

function _111(md){return(
md`### Tab Component`
)}

function _TabComponent(renderTabPanel,buildTabBar,selectTab){return(
class TabComponent {
  constructor(tileContent, tabs, fixedHeight) {
    // Exit if there are no tabs.
    if (tabs.length === 0) return;
    // Build tab panel element.
    const tabPanel = document.createElement("div");
    tabPanel.id = "tabPanel";
    //
    if (tabs.length === 1 && !tabs[0].label) {
      tileContent.replaceChildren(tabPanel);
      renderTabPanel(tabs, fixedHeight, tabPanel, 0);
      return;
    }
    // Build tab bar element. Replace existing tile element content with tab bar element.
    const tabBar = buildTabBar(tabPanel, tabs, fixedHeight);
    tileContent.replaceChildren(tabBar);
    // Append tab panel element to tile content element.
    tileContent.appendChild(tabPanel);
    // Select first tab.
    selectTab(tabs, fixedHeight, tabBar, tabPanel, 0);
  }
}
)}

function _buildTabBar(buildTabButton){return(
(tabPanel, tabs, fixedHeight) => {
  const tabBar = document.createElement("div");
  tabBar.className = "tabBar";
  tabBar.style.cssText = "display: flex";
  for (const [index, tab] of tabs.entries()) {
    tabBar.appendChild(
      buildTabButton(tabs, fixedHeight, tabBar, tabPanel, index, tab)
    );
  }
  return tabBar;
}
)}

function _buildTabButton(selectTab){return(
(tabs, fixedHeight, tabBar, tabPanel, index, tab) => {
  const tabButton = document.createElement("div");
  tabButton.className = "tabButton";
  tabButton.id = `tabButton_${index}`;
  tabButton.onclick = () =>
    selectTab(tabs, fixedHeight, tabBar, tabPanel, index);
  tabButton.appendChild(document.createTextNode(tab.label));
  return tabButton;
}
)}

function _selectTab(renderTabPanel){return(
(tabs, fixedHeight, tabBar, tabPanel, index) => {
  // Clear tab button selection.
  const tabButtons = tabBar.getElementsByClassName("tabButton");
  for (let index = 0; index < tabButtons.length; index++) {
    tabButtons[index].className = "tabButton";
  }
  // Highlight selected tab button.
  const tabButton = tabBar.querySelector(`#tabButton_${index}`);
  tabButton.className = "tabButton selected";
  // Render tab panel.
  renderTabPanel(tabs, fixedHeight, tabPanel, index);
}
)}

function _renderTabPanel(VendorComponent){return(
(tabs, fixedHeight, tabPanel, index) => {
  // Remove any existing tab panel content.
  while (tabPanel.firstChild) tabPanel.firstChild.remove();
  // Render vendor component.
  new VendorComponent(tabPanel, tabs[index].vendors || [], fixedHeight);
}
)}

function _117(md){return(
md`### Vendor Component`
)}

function _vendorTypes(){return(
new Map([
  [
    "amCharts4",
    {
      imageWidth: 40,
      imageSource: "amCharts4-logo.png",
      label: "amCharts4",
      labelPadding: 5
    }
  ],
  [
    "antVG2",
    {
      imageHeight: 18,
      imageSource: "antVG2-logo.png",
      label: "AntV G2",
      labelPadding: 5
    }
  ],
  [
    "antVG2Plot",
    {
      imageHeight: 18,
      imageSource: "antVG2-logo.png",
      label: "AntV G2Plot",
      labelPadding: 5
    }
  ],
  [
    "chartJS",
    {
      imageHeight: 24,
      imageSource: "chartJS-logo.svg",
      label: "Chart.js",
      labelPadding: 3
    }
  ],
  [
    "d3",
    {
      imageHeight: 18,
      imageSource: "d3-logo.png",
      label: "D3",
      labelPadding: 5
    }
  ],
  [
    "eCharts",
    {
      imageHeight: 18,
      imageSource: "eCharts-logo.png",
      label: "ECharts",
      labelPadding: 5
    }
  ],
  [
    "plotlyJS",
    {
      imageHeight: 18,
      imageSource: "plotlyJS-logo.png",
      label: "Plotly.js",
      labelPadding: 5
    }
  ],
  [
    "highcharts",
    {
      imageHeight: 18,
      imageSource: "highcharts-logo.png",
      label: "Highcharts",
      labelPadding: 5
    }
  ],
  [
    "visNetwork",
    {
      imageHeight: 18,
      imageSource: "visNetwork-logo.png",
      label: "Vis Network",
      labelPadding: 5
    }
  ]
])
)}

function _VendorComponent(defaultVisualHeight,renderVisual,buildVendorBar,selectVendor){return(
class VendorComponent {
  constructor(tabPanelElement, vendors, fixedHeight) {
    // Exit if there are no vendors.
    if (vendors.length === 0) return;
    // Build visual element.
    const visualElement = document.createElement("div");
    visualElement.className = "visualPanel";
    //visualElement.id = "visual";
    if (fixedHeight)
      visualElement.style.cssText = `height: ${defaultVisualHeight}px`;
    // If single vendor and no vendor id, then don't show vendor bar.
    if (vendors.length === 1 && !vendors[0].id) {
      tabPanelElement.replaceChildren(visualElement);
      renderVisual(visualElement, 0, vendors[0]);
      return;
    }
    // Replace tab panel element content with visual element.
    tabPanelElement.replaceChildren(visualElement);
    // Build vendor bar element and append to tab panel element.
    const vendorBar = buildVendorBar(visualElement, vendors);
    tabPanelElement.appendChild(vendorBar);
    // Select first vendor.
    selectVendor(visualElement, vendorBar, 0, vendors[0]);
  }
}
)}

function _buildVendorBar(buildVendorButton){return(
(visual, vendors) => {
  //
  const vendorBar = document.createElement("div");
  vendorBar.style.cssText = "color: #777; display: flex; font-size: 14px";
  //
  for (const [index, vendor] of vendors.entries()) {
    vendorBar.appendChild(buildVendorButton(visual, vendorBar, index, vendor));
  }
  //
  const optionsButton = document.createElement("div");
  optionsButton.className = "optionsButton";
  optionsButton.onclick = () => console.log("Options button clicked...");
  optionsButton.style.cssText = "margin-left: auto";
  optionsButton.appendChild(document.createTextNode("Options"));
  vendorBar.appendChild(optionsButton);
  //
  return vendorBar;
}
)}

function _buildVendorButton(selectVendor,vendorTypes){return(
(visual, vendorBar, index, vendor) => {
  //
  const vendorButton = document.createElement("div");
  vendorButton.className = "vendorButton";
  vendorButton.id = `vendorButton_${index}`;
  vendorButton.onclick = () => selectVendor(visual, vendorBar, index, vendor);
  //
  const vendorType = vendorTypes.get(vendor.id) || {
    label: vendor.id || "Unknown",
    labelPadding: 0
  };
  //
  if (vendorType.imageSource) {
    const image = document.createElement("img");
    if (vendorType.imageHeight) image.height = vendorType.imageHeight;
    image.style.cssText = "margin: 0";
    image.src = `https://nectis-res-v00-dev-alpha.web.app/assets/logos/${vendorType.imageSource}`;
    if (vendorType.imageWidth) image.width = vendorType.imageWidth;
    vendorButton.appendChild(image);
  }
  //
  const label = document.createElement("div");
  label.style.cssText = `padding-left: ${vendorType.labelPadding}px`;
  label.appendChild(document.createTextNode(vendorType.label));
  vendorButton.appendChild(label);
  //
  return vendorButton;
}
)}

function _selectVendor(renderVisual){return(
(visual, vendorBar, index, vendor) => {
  // Associate current vendor with visual. Don't want slow async renders to overwrite latest selection.
  visual.dataset.vendorIndex = index;
  // Clear vendor button selection.
  const vendorButtons = vendorBar.getElementsByClassName("vendorButton");
  for (let index = 0; index < vendorButtons.length; index++) {
    vendorButtons[index].className = "vendorButton";
  }
  // Highlight selected vendor button.
  vendorBar.querySelector(`#vendorButton_${index}`).className =
    "vendorButton selected";
  // Render visual.
  renderVisual(visual, index, vendor);
}
)}

function _renderVisual(renderNotebook){return(
async (visual, index, vendor) => {
  while (visual.firstChild) visual.firstChild.remove();
  // await loadVisualNotebook(index, vendor.notebookId, visual);
  await renderNotebook(
    "@jonathan-terrell",
    "headcount-progression-chartjs",
    visual
  );
}
)}

function _124(md){return(
md`### Notebook Interface`
)}

function _observableVersion(){return(
"4"
)}

function _observableURL(observableVersion){return(
`https://cdn.jsdelivr.net/npm/@observablehq/runtime@${observableVersion}/dist/runtime.js`
)}

function _observable(observableURL){return(
import(observableURL)
)}

function _loadVisualNotebook1(observable){return(
async (index, notebookId, container) => {
  console.log(1111);
  //
  if (!notebookId) return;
  // Retrieve notebook module for specified notebook identifier.
  const urlPrefix = "https://api.observablehq.com/@jonathan-terrell/";
  const module = await import(`${urlPrefix}${notebookId}.js?v=3`);

  const runtime = new observable.Runtime();
  runtime.module(module.default, (name) => {
    switch (name) {
      case "visualise":
        return {
          fulfilled: async (value) => {
            const visualiser = await value(container);
            if (container.dataset.vendorIndex === String(index))
              container.replaceChildren(visualiser.element);
            runtime.dispose();
          },
          rejected: (error) => {
            console.error(error);
            runtime.dispose();
          }
        };
      default:
        return false;
    }
  });
}
)}

function _renderNotebook(DOM,observable){return(
async (account, name, visual) => {
  const container = DOM.element("div");

  const library = new observable.Library();
  const contentWidth = () => {
    return library.Generators.observe((change) => {
      let currentWidth = change(container.clientWidth - 32);
      const onResize = () => {
        let resizedWidth = container.clientWidth - 32;
        if (resizedWidth !== currentWidth)
          change((currentWidth = resizedWidth));
      };
      window.addEventListener("resize", onResize);
      return () => window.removeEventListener("resize", onResize);
    });
  };
  Object.assign(library, { width: contentWidth });

  const cellTypes = { h1: 1, h2: 1, n: 1, t: 1, v: 1 };
  const urlPrefix = "https://api.observablehq.com/";
  const notebook = await import(`${urlPrefix}${account}/${name}.js?v=3`);
  const module = new observable.Runtime(library).module(
    notebook.default,
    (cellName) => {
      if (!cellName) return true; // Run side-effects but do not render.
      const cellType = cellName.split("_")[0];
      if (!cellTypes[cellType]) return true; // Run side-effects but do not render.
      return {
        fulfilled: async (value) => {
          // if (typeof value === "function") return;
          // const visualiser = await value();
          // container.replaceChildren(visualiser.container);
          value.id = cellName;
          const element = container.querySelector(`#${cellName}`);
          if (element) element.replaceWith(value);
          else container.appendChild(value);
          //module.dispose();
        },
        rejected: (error) => {
          console.error(error);
          //module.dispose();
        }
      };
    }
  );
  visual.replaceChildren(container);
  return container;
}
)}

function _130(md){return(
md`
---
## Toolbar Interface`
)}

function _Toolbar(buildToolbar){return(
{ build: buildToolbar }
)}

function _toolbarStyle(html){return(
html`
<style>
:root {
  --dark-gray: #454545;
  --light-gray: #e2e2e2;
  --near-white: #f5f5f5;
  --spacing-small: .5rem;
}
.nectis .options-panel {
  position: absolute;
  right: 0
}
.nectis .options-panel .toolbar {
  display: flex;
  float: right
}
.nectis .options-panel .toolbar button {
  background: transparent;
  border: 1px solid var(--light-gray);
  border-radius: 4px;
  color: var(--dark-gray);
  cursor: pointer;
  margin-left: 5px;
  outline: none;
  padding: 6px 8px;
}
.nectis .options-panel .toolbar button.home-button::before {
content: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 512 512'%3E%3Ctitle%3Eionicons-v5-i%3C/title%3E%3Cpath d='M80,212V448a16,16,0,0,0,16,16h96V328a24,24,0,0,1,24-24h80a24,24,0,0,1,24,24V464h96a16,16,0,0,0,16-16V212' style='fill:none;stroke:%23000;stroke-linecap:round;stroke-linejoin:round;stroke-width:32px'/%3E%3Cpath d='M480,256,266.89,52c-5-5.28-16.69-5.34-21.78,0L32,256' style='fill:none;stroke:%23000;stroke-linecap:round;stroke-linejoin:round;stroke-width:32px'/%3E%3Cpolyline points='400 179 400 64 352 64 352 133' style='fill:none;stroke:%23000;stroke-linecap:round;stroke-linejoin:round;stroke-width:32px'/%3E%3C/svg%3E");
}
.nectis .options-panel .toolbar button.index-button::before {
content: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 512 512'%3E%3Ctitle%3Eionicons-v5-o%3C/title%3E%3Cline x1='160' y1='144' x2='448' y2='144' style='fill:none;stroke:%23000;stroke-linecap:round;stroke-linejoin:round;stroke-width:32px'/%3E%3Cline x1='160' y1='256' x2='448' y2='256' style='fill:none;stroke:%23000;stroke-linecap:round;stroke-linejoin:round;stroke-width:32px'/%3E%3Cline x1='160' y1='368' x2='448' y2='368' style='fill:none;stroke:%23000;stroke-linecap:round;stroke-linejoin:round;stroke-width:32px'/%3E%3Ccircle cx='80' cy='144' r='16' style='fill:none;stroke:%23000;stroke-linecap:round;stroke-linejoin:round;stroke-width:32px'/%3E%3Ccircle cx='80' cy='256' r='16' style='fill:none;stroke:%23000;stroke-linecap:round;stroke-linejoin:round;stroke-width:32px'/%3E%3Ccircle cx='80' cy='368' r='16' style='fill:none;stroke:%23000;stroke-linecap:round;stroke-linejoin:round;stroke-width:32px'/%3E%3C/svg%3E");
}
.nectis .options-panel .toolbar button:hover {
  background: var(--near-white);
  border-color: transparent;
}
.nectis.dropdown {
  background: white;
  border: 1px solid #eee;
  border-radius: 4px;
  box-shadow: 0 4px 12px 0 rgb(0 0 0 / 12%);
  margin-right: 6px;
  padding: var(--spacing-small);
  position: absolute;
  top: 58px;
  right: 0;
}
</style>`
)}

function _buildToolbar(toolbarStyle,htl,navigate,toggleIndex){return(
() => {
  let indexPanel;
  document.getElementsByTagName("head")[0].appendChild(toolbarStyle);
  return htl.html`
    <button class="home-button" onclick=${() => navigate("home")} />
    <button class="index-button" onclick=${() =>
      (indexPanel = toggleIndex(indexPanel))} />
    <button class="home-button" onclick=${() => navigate("home")} />`;
}
)}

function _navigate(htl){return(
(notebookId) => {
  document.body.appendChild(htl.html`
    <div class="nectis dropdown">
      <div>Loading notebook...</div>
    </div>`);
  window.top.location = `https://observablehq.com/@jonathan-terrell/${notebookId}`;
}
)}

function _toggleIndex(htl,navigate){return(
(indexPanel) => {
  console.log("indexPanel", indexPanel);
  if (indexPanel) {
    indexPanel.remove();
    return undefined;
  }
  return document.body.appendChild(htl.html`
    <div class="nectis dropdown" style="width: 500px">
      <div>
        <div onclick=${() =>
          navigate("visualise-movements-chord")}>Movements - Single Moves</div>
      </div>
    </div>`);
}
)}

function _136(md){return(
md`
---
## VisNetwork Interface`
)}

function _VisNetwork(VisNetworkVisualiser){return(
{ Visualiser: VisNetworkVisualiser }
)}

function _visNetworkURL(visNetworkVersion){return(
`https://cdn.jsdelivr.net/npm/vis-network@${visNetworkVersion}/dist/vis-network.esm.min.js`
)}

function _visNetworkVersion(){return(
"9.0.4"
)}

function _VisNetworkVisualiser(visNetworkURL,defaultVisualHeight,width){return(
class VisNetworkVisualiser {
  constructor(container, options) {
    this.container = container;
    this.options = options;
    this.element = undefined;
    this.visual = undefined;
  }

  async build() {
    const VisNetwork = await import(visNetworkURL);

    this.element = document.createElement("div");
    if (this.container) {
      this.element.style.height = `${this.container.clientHeight ||
        defaultVisualHeight}px`;
      this.element.style.width = `${this.container.clientWidth || width}px`;
    } else {
      this.element.style.height = `${defaultVisualHeight}px`;
      this.element.style.width = `${width}px`;
    }

    const nodes = new VisNetwork.DataSet(this.options.data.nodes);
    const edges = new VisNetwork.DataSet(this.options.data.edges);
    this.visual = new VisNetwork.Network(
      this.element,
      { edges, nodes },
      this.options.options
    );

    return this;
  }

  resize(items) {
    return this;
  }
}
)}

export default function define(runtime, observer) {
  const main = runtime.module();
  function toString() { return this.url; }
  const fileAttachments = new Map([
    ["chinook.db", {url: new URL("./files/b3711cfd9bdf50cbe4e74751164d28e907ce366cd4bf56a39a980a48fdc5f998c42a019716a8033e2b54defdd97e4a55ebe4f6464b4f0678ea0311532605a115", import.meta.url), mimeType: "application/x-sqlite3", toString}]
  ]);
  main.builtin("FileAttachment", runtime.fileAttachments(name => fileAttachments.get(name)));
  main.variable(observer()).define(["md"], _1);
  main.variable(observer()).define(["html"], _2);
  main.variable(observer()).define(["md"], _3);
  main.variable(observer()).define(["md"], _4);
  main.variable(observer()).define(["md"], _5);
  main.variable(observer()).define(["md"], _6);
  main.variable(observer()).define(["DOM"], _7);
  main.variable(observer()).define(["DOM"], _8);
  main.variable(observer()).define(["md"], _9);
  main.variable(observer()).define(["tex"], _10);
  main.variable(observer()).define(["md"], _11);
  main.variable(observer()).define(["SQLite"], _12);
  main.variable(observer("chinook")).define("chinook", ["FileAttachment"], _chinook);
  main.variable(observer()).define(["chinook"], _14);
  main.variable(observer()).define(["Inputs","chinook"], _15);
  main.variable(observer()).define(["md"], _16);
  main.variable(observer("defaultVisualHeight")).define("defaultVisualHeight", _defaultVisualHeight);
  main.variable(observer()).define(["md"], _18);
  main.variable(observer("AGGrid")).define("AGGrid", ["AGGridVisualiser"], _AGGrid);
  main.variable(observer("agGridVersion")).define("agGridVersion", _agGridVersion);
  main.variable(observer("stylesheet1")).define("stylesheet1", ["html","agGridVersion"], _stylesheet1);
  main.variable(observer("stylesheet2")).define("stylesheet2", ["html","agGridVersion"], _stylesheet2);
  main.variable(observer("AGGridVisualiser")).define("AGGridVisualiser", ["require","agGridVersion","defaultVisualHeight","width"], _AGGridVisualiser);
  main.variable(observer("container1")).define("container1", ["html"], _container1);
  main.variable(observer()).define(["AGGridVisualiser","container1"], _25);
  main.variable(observer()).define(["md"], _26);
  main.variable(observer("AMCharts4")).define("AMCharts4", ["AMCharts4Visualiser"], _AMCharts4);
  main.variable(observer("AMCharts4Visualiser")).define("AMCharts4Visualiser", ["defaultVisualHeight","width"], _AMCharts4Visualiser);
  main.variable(observer()).define(["md"], _29);
  main.variable(observer("AntVG2")).define("AntVG2", ["AntVG2Visualiser"], _AntVG2);
  main.variable(observer("antVG2Version")).define("antVG2Version", _antVG2Version);
  main.variable(observer("AntVG2Visualiser")).define("AntVG2Visualiser", ["require","antVG2Version"], _AntVG2Visualiser);
  main.variable(observer()).define(["md"], _33);
  main.variable(observer("AntVG2Plot")).define("AntVG2Plot", ["AntVG2PlotVisualiser"], _AntVG2Plot);
  main.variable(observer("antVG2PlotVersion")).define("antVG2PlotVersion", _antVG2PlotVersion);
  main.variable(observer("AntVG2PlotVisualiser")).define("AntVG2PlotVisualiser", ["require","antVG2PlotVersion","defaultVisualHeight","width","getAntV2G2PlotChart"], _AntVG2PlotVisualiser);
  main.variable(observer("getAntV2G2PlotChart")).define("getAntV2G2PlotChart", _getAntV2G2PlotChart);
  main.variable(observer()).define(["md"], _38);
  main.variable(observer("ChartJS")).define("ChartJS", ["ChartJSVisualiser","drawConnectionLines","getLegendSymbol","headcountTooltipHandler"], _ChartJS);
  main.variable(observer("chartJSURL")).define("chartJSURL", ["chartJSVersion"], _chartJSURL);
  main.variable(observer("chartJSVersion")).define("chartJSVersion", _chartJSVersion);
  main.variable(observer("ChartJSVisualiser")).define("ChartJSVisualiser", ["loadChartJSLibrary","width"], _ChartJSVisualiser);
  main.variable(observer("loadChartJSLibrary")).define("loadChartJSLibrary", ["chartJSURL"], _loadChartJSLibrary);
  main.variable(observer()).define(["md"], _44);
  main.variable(observer("drawConnectionLines")).define("drawConnectionLines", ["drawConnectionLine"], _drawConnectionLines);
  main.variable(observer("drawConnectionLine")).define("drawConnectionLine", ["scaleLinear"], _drawConnectionLine);
  main.variable(observer("scaleLinear")).define("scaleLinear", _scaleLinear);
  main.variable(observer()).define(["md"], _48);
  main.variable(observer("getLegendSymbol")).define("getLegendSymbol", ["getColour"], _getLegendSymbol);
  main.variable(observer()).define(["md"], _50);
  main.variable(observer("headcountTooltipHandler")).define("headcountTooltipHandler", ["establishTooltip","buildRow"], _headcountTooltipHandler);
  main.variable(observer("establishTooltip")).define("establishTooltip", _establishTooltip);
  main.variable(observer("buildRow")).define("buildRow", ["headcountFormatter"], _buildRow);
  main.variable(observer("headcountFormatter")).define("headcountFormatter", _headcountFormatter);
  main.variable(observer()).define(["md"], _55);
  main.variable(observer("D3Chord")).define("D3Chord", ["D3ChordVisualiser"], _D3Chord);
  main.variable(observer("D3ChordVisualiser")).define("D3ChordVisualiser", ["defaultVisualHeight","width","chart"], _D3ChordVisualiser);
  main.variable(observer("chart")).define("chart", ["d3","width","DOM"], _chart);
  main.variable(observer()).define(["md"], _59);
  main.variable(observer("Data")).define("Data", ["buildMeasureMap","monthAbbreviations","monthNames"], _Data);
  main.variable(observer("monthAbbreviations")).define("monthAbbreviations", _monthAbbreviations);
  main.variable(observer("monthNames")).define("monthNames", _monthNames);
  main.variable(observer("buildMeasureMap")).define("buildMeasureMap", ["buildMapOfArrays"], _buildMeasureMap);
  main.variable(observer("buildMapOfArrays")).define("buildMapOfArrays", _buildMapOfArrays);
  main.variable(observer()).define(["md"], _65);
  main.variable(observer("ECharts")).define("ECharts", ["EChartsVisualiser"], _ECharts);
  main.variable(observer("eChartsVersion")).define("eChartsVersion", _eChartsVersion);
  main.variable(observer("eChartsURL")).define("eChartsURL", ["eChartsVersion"], _eChartsURL);
  main.variable(observer("EChartsVisualiser")).define("EChartsVisualiser", ["eChartsURL","defaultVisualHeight","width"], _EChartsVisualiser);
  main.variable(observer()).define(["md"], _70);
  main.variable(observer("Footer")).define("Footer", ["footer"], _Footer);
  main.variable(observer("footer1")).define("footer1", ["md","htl","narrativeStyle"], _footer1);
  main.variable(observer("footer")).define("footer", ["html"], _footer);
  main.variable(observer()).define(["md"], _74);
  main.variable(observer("Highcharts")).define("Highcharts", ["HighchartsVisualiser"], _Highcharts);
  main.variable(observer("highchartsURLPrefix")).define("highchartsURLPrefix", ["highchartsVersion"], _highchartsURLPrefix);
  main.variable(observer("highchartsVersion")).define("highchartsVersion", _highchartsVersion);
  main.variable(observer("HighchartsVisualiser")).define("HighchartsVisualiser", ["loadHighchartsLibrary","defaultVisualHeight","width","addBorderToLegendSymbols"], _HighchartsVisualiser);
  main.variable(observer("addBorderToLegendSymbols")).define("addBorderToLegendSymbols", _addBorderToLegendSymbols);
  main.variable(observer("loadHighchartsLibrary")).define("loadHighchartsLibrary", ["highchartsVersion"], _loadHighchartsLibrary);
  main.variable(observer()).define(["md"], _81);
  main.variable(observer("LokiJS")).define("LokiJS", ["Database"], _LokiJS);
  main.variable(observer("lokiVersion")).define("lokiVersion", _lokiVersion);
  main.variable(observer("Database")).define("Database", ["require","lokiVersion"], _Database);
  main.variable(observer()).define(["md"], _85);
  main.variable(observer("Narrative")).define("Narrative", ["narrative1"], _Narrative);
  main.variable(observer("narrative1")).define("narrative1", ["defaultTruncateHeight1","md","buildButton1","htl","narrativeStyle"], _narrative1);
  main.variable(observer()).define(["md"], _88);
  main.variable(observer("defaultTruncateHeight1")).define("defaultTruncateHeight1", _defaultTruncateHeight1);
  main.variable(observer("buildButton1")).define("buildButton1", ["htl"], _buildButton1);
  main.variable(observer("narrative2")).define("narrative2", ["htl","narrativeStyle","md"], _narrative2);
  main.variable(observer()).define(["md"], _92);
  main.variable(observer("PlotlyJS")).define("PlotlyJS", ["PlotlyJSVisualiser"], _PlotlyJS);
  main.variable(observer("PlotlyJSVisualiser")).define("PlotlyJSVisualiser", ["require","defaultVisualHeight","width"], _PlotlyJSVisualiser);
  main.variable(observer()).define(["md"], _95);
  main.variable(observer("Style")).define("Style", ["colours","narrativeStyle","palettes"], _Style);
  main.variable(observer("colours")).define("colours", ["getColour"], _colours);
  main.variable(observer("palettes")).define("palettes", _palettes);
  main.variable(observer("getColour")).define("getColour", ["palettes"], _getColour);
  main.variable(observer("narrativeStyle")).define("narrativeStyle", _narrativeStyle);
  main.variable(observer("panelStyle")).define("panelStyle", _panelStyle);
  main.variable(observer("tableStyle")).define("tableStyle", _tableStyle);
  main.variable(observer()).define(["md"], _103);
  main.variable(observer("TableVisualiser")).define("TableVisualiser", ["tableStyle","buildCellStyle","formatCellValue"], _TableVisualiser);
  main.variable(observer("buildCellStyle")).define("buildCellStyle", _buildCellStyle);
  main.variable(observer("formatCellValue")).define("formatCellValue", _formatCellValue);
  main.variable(observer()).define(["md"], _107);
  main.variable(observer("Tile")).define("Tile", ["define","show"], _Tile);
  main.variable(observer("define")).define("define", ["panelStyle"], _define);
  main.variable(observer("show")).define("show", ["TabComponent"], _show);
  main.variable(observer()).define(["md"], _111);
  main.variable(observer("TabComponent")).define("TabComponent", ["renderTabPanel","buildTabBar","selectTab"], _TabComponent);
  main.variable(observer("buildTabBar")).define("buildTabBar", ["buildTabButton"], _buildTabBar);
  main.variable(observer("buildTabButton")).define("buildTabButton", ["selectTab"], _buildTabButton);
  main.variable(observer("selectTab")).define("selectTab", ["renderTabPanel"], _selectTab);
  main.variable(observer("renderTabPanel")).define("renderTabPanel", ["VendorComponent"], _renderTabPanel);
  main.variable(observer()).define(["md"], _117);
  main.variable(observer("vendorTypes")).define("vendorTypes", _vendorTypes);
  main.variable(observer("VendorComponent")).define("VendorComponent", ["defaultVisualHeight","renderVisual","buildVendorBar","selectVendor"], _VendorComponent);
  main.variable(observer("buildVendorBar")).define("buildVendorBar", ["buildVendorButton"], _buildVendorBar);
  main.variable(observer("buildVendorButton")).define("buildVendorButton", ["selectVendor","vendorTypes"], _buildVendorButton);
  main.variable(observer("selectVendor")).define("selectVendor", ["renderVisual"], _selectVendor);
  main.variable(observer("renderVisual")).define("renderVisual", ["renderNotebook"], _renderVisual);
  main.variable(observer()).define(["md"], _124);
  main.variable(observer("observableVersion")).define("observableVersion", _observableVersion);
  main.variable(observer("observableURL")).define("observableURL", ["observableVersion"], _observableURL);
  main.variable(observer("observable")).define("observable", ["observableURL"], _observable);
  main.variable(observer("loadVisualNotebook1")).define("loadVisualNotebook1", ["observable"], _loadVisualNotebook1);
  main.variable(observer("renderNotebook")).define("renderNotebook", ["DOM","observable"], _renderNotebook);
  main.variable(observer()).define(["md"], _130);
  main.variable(observer("Toolbar")).define("Toolbar", ["buildToolbar"], _Toolbar);
  main.variable(observer("toolbarStyle")).define("toolbarStyle", ["html"], _toolbarStyle);
  main.variable(observer("buildToolbar")).define("buildToolbar", ["toolbarStyle","htl","navigate","toggleIndex"], _buildToolbar);
  main.variable(observer("navigate")).define("navigate", ["htl"], _navigate);
  main.variable(observer("toggleIndex")).define("toggleIndex", ["htl","navigate"], _toggleIndex);
  main.variable(observer()).define(["md"], _136);
  main.variable(observer("VisNetwork")).define("VisNetwork", ["VisNetworkVisualiser"], _VisNetwork);
  main.variable(observer("visNetworkURL")).define("visNetworkURL", ["visNetworkVersion"], _visNetworkURL);
  main.variable(observer("visNetworkVersion")).define("visNetworkVersion", _visNetworkVersion);
  main.variable(observer("VisNetworkVisualiser")).define("VisNetworkVisualiser", ["visNetworkURL","defaultVisualHeight","width"], _VisNetworkVisualiser);
  return main;
}
