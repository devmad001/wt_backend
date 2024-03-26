// https://observablehq.com/@springbrook/headcount-progression-2-highcharts@229
import define1 from "./412ae58d01734200@3886.js";
import define2 from "./2206bb3d65ecdee7@276.js";

function _narrative_1(visualise,visual_1,Narrative)
{
  visualise(visual_1);
  return Narrative`
# Headcount Progression 2 (Highcharts)

<div class="warning"><div>WARNING<div>Alpha version.</div></div></div>

...`;
}


function _visual_1(html){return(
html`<div class="nectis" style="height: 500px"></div>`
)}

function _3(md){return(
md`
--- 
## Visualise Method`
)}

function _visualise(Highcharts,options){return(
async container => {
  const visualiser = await new Highcharts.Visualiser(
    container,
    options
  ).build();
  container.replaceChildren(visualiser.element);
  return visualiser;
}
)}

function _5(md){return(
md`### Data`
)}

function _data(buildEmptyArray,WorkforceData)
{
  const data = {
    openingHeadcounts1: buildEmptyArray(14),
    // openingHeadcounts2: buildEmptyArray(14),
    hires: buildEmptyArray(14),
    startingHires: buildEmptyArray(14),
    averageHeadcounts: buildEmptyArray(14),
    // offsets: buildEmptyArray(14),
    endingTerminations: buildEmptyArray(14),
    terminations: buildEmptyArray(14),
    closingHeadcounts: buildEmptyArray(14)
  };
  for (const [
    month,
    record
  ] of WorkforceData.sizeByMonthForCalendarYear.months.entries()) {
    if (month === 0) {
      data.openingHeadcounts1[0] = record.openingHeadcount;
      // data.openingHeadcounts2[0] = record.openingHeadcount + record.hires;
    }
    // if (month > 0) {
    //   data.offsets[month] = record.hires;
    // }
    if (month === 11) {
      data.closingHeadcounts[month + 2] = record.closingHeadcount * -1;
    }
    data.hires[month + 1] = record.hires - record.startingHires;
    data.startingHires[month + 1] = record.startingHires;
    data.averageHeadcounts[month + 1] = record.averageHeadcount;
    data.endingTerminations[month + 1] = record.endingTerminations * -1;
    data.terminations[month + 1] =
      (record.terminations - record.endingTerminations) * -1;
  }
  return { ...data };
}


function _buildEmptyArray(){return(
size => {
  return new Array(size).fill(null);
}
)}

function _8(md){return(
md`### Options`
)}

function _options(data,WorkforceData,Data){return(
{
  chart: {
    animation: false,
    reflow: false,
    style: { fontSize: '1em' },
    type: 'waterfall'
  },
  legend: {
    itemStyle: { fontSize: '0.875em', fontWeight: 'normal' },
    symbolRadius: 0
  },
  plotOptions: {
    series: { animation: false },
    waterfall: { stacking: 'normal' }
  },
  series: [
    {
      borderColor: '#BDBDBD',
      color: '#EEEEEE',
      data: data.openingHeadcounts1,
      legendIndex: 0,
      lineWidth: 2,
      name: 'Headcount',
      stack: 0
    },
    {
      borderColor: '#FFA726',
      color: '#FFCC7F',
      data: data.endingTerminations,
      legendIndex: 4,
      lineWidth: 0,
      name: 'Terminations at End',
      stack: 0
    },
    {
      borderColor: '#66BB6A',
      color: '#C8E6C9',
      data: data.hires,
      legendIndex: 2,
      lineWidth: 0,
      name: 'Hires During',
      stack: 0
    },
    {
      borderColor: '#FFA726',
      color: '#FFFFFF',
      data: data.terminations,
      legendIndex: 3,
      lineWidth: 0,
      name: 'Terminations During',
      stack: 0
    },
    {
      borderColor: '#66BB6A',
      color: '#A5D6A7',
      data: data.startingHires,
      legendIndex: 1,
      lineWidth: 0,
      name: 'Hires at Start',
      stack: 0
    },
    {
      borderColor: '#BDBDBD',
      color: '#EEEEEE',
      data: data.closingHeadcounts,
      lineWidth: 0,
      name: 'Headcount',
      showInLegend: false,
      stack: 0
    },
    {
      color: '#2196F3',
      data: data.averageHeadcounts,
      legendIndex: 5,
      name: 'Average Headcount',
      type: 'line'
    }
  ],
  title: {
    style: { fontSize: '1.125em' },
    text: `Change in Headcount by Month for ${WorkforceData.sizeByMonthForCalendarYear.year}`
  },
  xAxis: [
    {
      categories: ["Open"].concat(Data.monthAbbreviations).concat(["Close"]),
      labels: { style: { fontSize: '0.875em' } }
    }
  ],
  yAxis: {
    labels: { format: '{value:,.0f}', style: { fontSize: '0.875em' } },
    min: 1075,
    title: { text: 'Headcount' }
  }
}
)}

function _10(md){return(
md`
--- 
## Appendix`
)}

export default function define(runtime, observer) {
  const main = runtime.module();
  main.variable(observer("narrative_1")).define("narrative_1", ["visualise","visual_1","Narrative"], _narrative_1);
  main.variable(observer("visual_1")).define("visual_1", ["html"], _visual_1);
  main.variable(observer()).define(["md"], _3);
  main.variable(observer("visualise")).define("visualise", ["Highcharts","options"], _visualise);
  main.variable(observer()).define(["md"], _5);
  main.variable(observer("data")).define("data", ["buildEmptyArray","WorkforceData"], _data);
  main.variable(observer("buildEmptyArray")).define("buildEmptyArray", _buildEmptyArray);
  main.variable(observer()).define(["md"], _8);
  main.variable(observer("options")).define("options", ["data","WorkforceData","Data"], _options);
  main.variable(observer()).define(["md"], _10);
  const child1 = runtime.module(define1);
  main.import("Data", child1);
  main.import("Highcharts", child1);
  main.import("Narrative", child1);
  const child2 = runtime.module(define2);
  main.import("WorkforceData", child2);
  return main;
}
