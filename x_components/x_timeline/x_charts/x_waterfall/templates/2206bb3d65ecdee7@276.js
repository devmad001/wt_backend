// https://observablehq.com/@springbrook/workforce-data@276
function _1(md){return(
md`
# Workforce Data`
)}

function _2(html){return(
html`
<p style="background-color: rgba(255, 229, 100, 0.3); border-left: 0.5rem #e7c000 solid; padding: 8px 24px">
    WARNING<br>Alpha version.
</p>`
)}

function _3(md){return(
md`
Sample workforce data. It serves as the default data when external data is not available to populate workforce visuals and presentations.

The following sections provide data for workforce size, hires and terminations.`
)}

function _4(md){return(
md`
---
## Interface`
)}

function _WorkforceData(colours,sizeByMonthForCalendarYear){return(
{ colours, sizeByMonthForCalendarYear }
)}

function _6(md){return(
md`
---
## Colours`
)}

function _colours(){return(
{}
)}

function _8(md){return(
md`
---
## Data - Size`
)}

function _sizeByMonthForCalendarYear(){return(
{
  year: 2020,
  months: [
    {
      month: 1,
      openingHeadcount: 1105,
      openingFTE: 0,
      startingHires: 0,
      startingFTE: 0,
      hires: 23,
      newHires: 22,
      rehires: 1,
      inPeriodHeadcount: 0,
      distinctPeriodHeadcount: 0,
      terminations: 18,
      averageHeadcount: 1108.1935483870966,
      fte: 1090.2701774193545,
      endingFTE: 0,
      endingTerminations: 2,
      closingFTE: 0,
      closingHeadcount: 1110
    },
    {
      month: 2,
      openingHeadcount: 1110,
      openingFTE: 0,
      startingHires: 1,
      startingFTE: 0,
      hires: 18,
      newHires: 14,
      rehires: 4,
      inPeriodHeadcount: 0,
      distinctPeriodHeadcount: 0,
      terminations: 19,
      averageHeadcount: 1113.4482758620695,
      fte: 1095.128286206897,
      endingFTE: 0,
      endingTerminations: 1,
      closingFTE: 0,
      closingHeadcount: 1109
    },
    {
      month: 3,
      openingHeadcount: 1109,
      openingFTE: 0,
      startingHires: 0,
      startingFTE: 0,
      hires: 38,
      newHires: 34,
      rehires: 4,
      inPeriodHeadcount: 0,
      distinctPeriodHeadcount: 0,
      terminations: 18,
      averageHeadcount: 1121.967741935484,
      fte: 1103.577693548387,
      endingFTE: 0,
      endingTerminations: 5,
      closingFTE: 0,
      closingHeadcount: 1129
    },
    {
      month: 4,
      openingHeadcount: 1129,
      openingFTE: 0,
      startingHires: 3,
      startingFTE: 0,
      hires: 22,
      newHires: 22,
      rehires: 0,
      inPeriodHeadcount: 0,
      distinctPeriodHeadcount: 0,
      terminations: 22,
      averageHeadcount: 1132.3999999999996,
      fte: 1114.0404999999998,
      endingFTE: 0,
      endingTerminations: 5,
      closingFTE: 0,
      closingHeadcount: 1129
    },
    {
      month: 5,
      openingHeadcount: 1129,
      openingFTE: 0,
      startingHires: 1,
      startingFTE: 0,
      hires: 26,
      newHires: 24,
      rehires: 2,
      inPeriodHeadcount: 0,
      distinctPeriodHeadcount: 0,
      terminations: 21,
      averageHeadcount: 1134.7419354838717,
      fte: 1114.941145161291,
      endingFTE: 0,
      endingTerminations: 2,
      closingFTE: 0,
      closingHeadcount: 1134
    },
    {
      month: 6,
      openingHeadcount: 1134,
      openingFTE: 0,
      startingHires: 17,
      startingFTE: 0,
      hires: 63,
      newHires: 58,
      rehires: 5,
      inPeriodHeadcount: 0,
      distinctPeriodHeadcount: 0,
      terminations: 25,
      averageHeadcount: 1160.333333333332,
      fte: 1139.8760233333317,
      endingFTE: 0,
      endingTerminations: 4,
      closingFTE: 0,
      closingHeadcount: 1172
    },
    {
      month: 7,
      openingHeadcount: 1172,
      openingFTE: 0,
      startingHires: 2,
      startingFTE: 0,
      hires: 42,
      newHires: 38,
      rehires: 4,
      inPeriodHeadcount: 0,
      distinctPeriodHeadcount: 0,
      terminations: 41,
      averageHeadcount: 1175.5483870967737,
      fte: 1155.5572387096768,
      endingFTE: 0,
      endingTerminations: 4,
      closingFTE: 0,
      closingHeadcount: 1173
    },
    {
      month: 8,
      openingHeadcount: 1173,
      openingFTE: 0,
      startingHires: 1,
      startingFTE: 0,
      hires: 37,
      newHires: 32,
      rehires: 5,
      inPeriodHeadcount: 0,
      distinctPeriodHeadcount: 0,
      terminations: 34,
      averageHeadcount: 1180.0967741935488,
      fte: 1160.2840935483875,
      endingFTE: 0,
      endingTerminations: 0,
      closingFTE: 0,
      closingHeadcount: 1176
    },
    {
      month: 9,
      openingHeadcount: 1176,
      openingFTE: 0,
      startingHires: 16,
      startingFTE: 0,
      hires: 41,
      newHires: 38,
      rehires: 3,
      inPeriodHeadcount: 0,
      distinctPeriodHeadcount: 0,
      terminations: 31,
      averageHeadcount: 1189.5999999999995,
      fte: 1170.280466666666,
      endingFTE: 0,
      endingTerminations: 6,
      closingFTE: 0,
      closingHeadcount: 1186
    },
    {
      month: 10,
      openingHeadcount: 1186,
      openingFTE: 0,
      startingHires: 4,
      startingFTE: 0,
      hires: 23,
      newHires: 21,
      rehires: 2,
      inPeriodHeadcount: 0,
      distinctPeriodHeadcount: 0,
      terminations: 20,
      averageHeadcount: 1190.0000000000002,
      fte: 1170.4818612903225,
      endingFTE: 0,
      endingTerminations: 0,
      closingFTE: 0,
      closingHeadcount: 1189
    },
    {
      month: 11,
      openingHeadcount: 1189,
      openingFTE: 0,
      startingHires: 0,
      startingFTE: 0,
      hires: 45,
      newHires: 44,
      rehires: 1,
      inPeriodHeadcount: 0,
      distinctPeriodHeadcount: 0,
      terminations: 21,
      averageHeadcount: 1199.866666666667,
      fte: 1180.5033666666668,
      endingFTE: 0,
      endingTerminations: 4,
      closingFTE: 0,
      closingHeadcount: 1213
    },
    {
      month: 12,
      openingHeadcount: 1213,
      openingFTE: 0,
      startingHires: 1,
      startingFTE: 0,
      hires: 13,
      newHires: 13,
      rehires: 0,
      inPeriodHeadcount: 0,
      distinctPeriodHeadcount: 0,
      terminations: 15,
      averageHeadcount: 1216.0645161290317,
      fte: 1196.9270225806447,
      endingFTE: 0,
      endingTerminations: 6,
      closingFTE: 0,
      closingHeadcount: 1211
    }
  ]
}
)}

function _10(md){return(
md`
---
## Data - Hire`
)}

function _11(md){return(
md`
---
## Data - Termination`
)}

export default function define(runtime, observer) {
  const main = runtime.module();
  main.variable(observer()).define(["md"], _1);
  main.variable(observer()).define(["html"], _2);
  main.variable(observer()).define(["md"], _3);
  main.variable(observer()).define(["md"], _4);
  main.variable(observer("WorkforceData")).define("WorkforceData", ["colours","sizeByMonthForCalendarYear"], _WorkforceData);
  main.variable(observer()).define(["md"], _6);
  main.variable(observer("colours")).define("colours", _colours);
  main.variable(observer()).define(["md"], _8);
  main.variable(observer("sizeByMonthForCalendarYear")).define("sizeByMonthForCalendarYear", _sizeByMonthForCalendarYear);
  main.variable(observer()).define(["md"], _10);
  main.variable(observer()).define(["md"], _11);
  return main;
}
