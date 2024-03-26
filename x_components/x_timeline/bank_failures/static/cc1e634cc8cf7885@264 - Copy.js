function _1(md){return(
md`# Bank failures

Note: Only shows FDIC-reported bank failures; does not include investment banks and non-U.S. banks. Data: [FDIC](https://www.fdic.gov/bank/historical/bank/bfb2023.html), [FRED](https://fred.stlouisfed.org/series/CPIAUCSL). For a walkthrough of how I made this chart, please see [my YouTube channel](https://www.youtube.com/watch?v=AhdfQhi0zNU).`
)}

function _Assets(Inputs){return(
Inputs.toggle({label: "Adjust for inflation", value: false, values: ["Assets (adj.)", "Assets"]})
)}

function _sort(Inputs){return(
Inputs.radio(new Map([["date", "Date"], ["size", Promise.resolve()]]), {label: "Sort by", key: "size"})
)}

function _4(Plot,sort,fails,Assets){return(
Plot.plot({
  width: 1152,
  height: sort === "Date" ? 760 : 680,
  insetLeft: 10,
  insetRight: 60,
  r: {range: [0, 80]},
  marks: [
    Plot.frame({anchor: "bottom"}),
    Plot.dot(
      fails,
      Plot.dodgeY({
        sort,
        anchor: "bottom",
        padding: 2,
        x: "Date",
        r: Assets, // N.B. sqrt scale
        title: (d) => `${d["Bank Name"]}\n${(d[Assets] / 1000).toFixed(1)}B`,
        tip: true,
        fill: "#ddd",
        stroke: "#000",
        strokeWidth: 1
      })
    ),
    Plot.text(
      fails,
      Plot.filter((d) => d.Assets > 2000, Plot.dodgeY({
        sort,
        anchor: "bottom",
        padding: 2,
        x: "Date",
        lineWidth: 5,
        r: Assets,
        text: (d) => d.Assets > 12900 
          ? `${d["Bank Name"]}\n${(d[Assets] / 1000).toFixed(0)}B` 
          : `${(d[Assets] / 1000).toFixed(1)}`,
        pointerEvents: "none",
        fill: "#000",
        stroke: "#ddd"
      }))
    )
  ]
})
)}

function _5(__query,fails,invalidation){return(
__query(fails,{from:{table:"fails"},sort:[],slice:{to:null,from:null},filter:[],select:{columns:null}},invalidation,"fails")
)}

async function _fails(FileAttachment,parseDate,parseAssets,adjustForInflation){return(
(await FileAttachment("bfb-data@2.csv").csv({array: true}))
  .slice(1, -2)
  .map((d) => {
    const date = parseDate(d[2]);
    const assets = parseAssets(d[3]);
    return {
      "Bank Name": d[0].split(", ")[0],
      "City, State": d[0].split(", ").slice(1).join(", "),
      "Date": date,
      "Assets": assets,
      "Assets (adj.)": adjustForInflation(date, assets),
      "Acquirer": d[5]
    };
  })
)}

function _parseDate(d3){return(
d3.utcParse("%d-%b-%y")
)}

function _parseAssets(){return(
(x) => parseFloat(x.replace(/[^\d.]/g, ""))
)}

function _cpiaucsl(__query,FileAttachment,invalidation){return(
__query(FileAttachment("CPIAUCSL.csv"),{from:{table:"CPIAUCSL"},sort:[],slice:{to:null,from:null},filter:[],select:{columns:null}},invalidation)
)}

function _findCpi(d3,cpiaucsl)
{
  const bisector = d3.bisector((d) => d.DATE);
  return (date) => cpiaucsl[bisector.center(cpiaucsl, date)].CPIAUCSL;
}


function _adjustForInflation(findCpi)
{
  const currentCpi = findCpi(new Date("2023-05-01"));
  return (date, value) => currentCpi / findCpi(date) * value;
}


export default function define(runtime, observer) {
  const main = runtime.module();
  function toString() { return this.url; }
  const fileAttachments = new Map([
    ["CPIAUCSL.csv", {url: new URL("./files/0dbd3049187fe89552eae2ef468da950c7a987de68b0239923deb95505863cfdc25efb08348b9a8108585769f286d242d74cb41df75416cf0d0ca8293e5017cd.csv", import.meta.url), mimeType: "text/csv", toString}],
    ["bfb-data@2.csv", {url: new URL("./files/4b4f979a3bd6da7b023fa75d22911e3404663566a8abe8e393d873c6254734a5237123278fec5f63684de1c99fa867b5e630ffab712a5dffdd139e780a250c18.csv", import.meta.url), mimeType: "text/csv", toString}]
  ]);
  main.builtin("FileAttachment", runtime.fileAttachments(name => fileAttachments.get(name)));
  main.variable(observer()).define(["md"], _1);
  main.variable(observer("viewof Assets")).define("viewof Assets", ["Inputs"], _Assets);
  main.variable(observer("Assets")).define("Assets", ["Generators", "viewof Assets"], (G, _) => G.input(_));
  main.variable(observer("viewof sort")).define("viewof sort", ["Inputs"], _sort);
  main.variable(observer("sort")).define("sort", ["Generators", "viewof sort"], (G, _) => G.input(_));
  main.variable(observer()).define(["Plot","sort","fails","Assets"], _4);
  main.variable(observer()).define(["__query","fails","invalidation"], _5);
  main.variable(observer("fails")).define("fails", ["FileAttachment","parseDate","parseAssets","adjustForInflation"], _fails);
  main.variable(observer("parseDate")).define("parseDate", ["d3"], _parseDate);
  main.variable(observer("parseAssets")).define("parseAssets", _parseAssets);
  main.variable(observer("cpiaucsl")).define("cpiaucsl", ["__query","FileAttachment","invalidation"], _cpiaucsl);
  main.variable(observer("findCpi")).define("findCpi", ["d3","cpiaucsl"], _findCpi);
  main.variable(observer("adjustForInflation")).define("adjustForInflation", ["findCpi"], _adjustForInflation);
  return main;
}
