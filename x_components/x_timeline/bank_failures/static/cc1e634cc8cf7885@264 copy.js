function _1(md) {
  return (
    //md`# Bank failures

    //md`
    //Note: This is a sample layout view only. Possible to add colors, DEBIT/CREDITS above below, links between "accounts", or view as stacked bar, etc.`
    md ``

  )
}

function _Assets(Inputs) {
  return (
    Inputs.toggle({
      label: "Adjust for inflation",
      value: false,
      values: ["Assets (adj.)", "Assets"]
    })
  )
}

function _sort(Inputs) {
  const radio = Inputs.radio(new Map([
    ["date", "Date"],
    ["size", Promise.resolve()]
  ]), {
    label: "Sort by",
    key: "size"
  });
  return radio;
}

function _sortNOP(Inputs) {
  const form = Inputs.radio(new Map([
    ["date", "Date"],
    ["size", Promise.resolve()]
  ]), {
    label: "Sort by",
    key: "size"
  });
  
  form.style.display = "none";
  return form;
}

// JC:  was 720 height for sort by date but causes problems in iframe
//            fill: (d) => d['color'] || "#BBB",
//            fill: "#ddd",
function _4(Plot, sort, fails, Assets) {

  return (
    Plot.plot({
      width: 1152,
      height: sort === "Date" ? 681 : 680,
      insetLeft: 10,
      insetRight: 60,
      r: {
        range: [0, 80]
      },
      marks: [
        Plot.frame({
          anchor: "bottom"
        }),
        Plot.dot(
          fails,
          Plot.dodgeY({
            sort,
            anchor: "bottom",
            padding: 2,
            x: "Date",
            r: Assets, // N.B. sqrt scale
            title: (d) => `${d["Bank Name"]}\n${(d[Assets] / 1).toFixed(0)}`,
            tip: true,
            fill: (d) => d['color'] || "#ddd", 
            stroke: "#000",
            strokeWidth: 1,
            fontSize: "16px"
          })
        ),
        Plot.text(
          fails,
          Plot.filter((d) => d.Assets > 500, Plot.dodgeY({
            sort,
            anchor: "bottom",
            padding: 2,
            x: "Date",
            lineWidth: 5,
            r: Assets,
            text: (d) => d.Assets > 12900 ?
              `${d["Bank Name"]}\n\$${(d[Assets] / 1).toFixed(0)}` :
              `${(d[Assets] / 1).toFixed(0)}`,
            pointerEvents: "none",
            fill: "#000",
            stroke: "#ddd",
            fontSize: "16px"
          }))
        )
      ]
    })
  )
}

function _5(__query, fails, invalidation) {
  return (
    __query(fails, {
      from: {
        table: "fails"
      },
      sort: [],
      slice: {
        to: null,
        from: null
      },
      filter: [],
      select: {
        columns: null
      }
    }, invalidation, "fails")
  )
}

const RANDOMIZE_ALL_Date = false; // demo remove

function randomizeDate(date) {
  // Define a random range, for example, +/- 30 days.
  var base=264*10;
  var halfbase=base/2;

  const daysToAdjust = Math.floor(Math.random() * base) - halfbase;
  const adjustedDate = new Date(date);
  adjustedDate.setDate(date.getDate() + daysToAdjust);
  return adjustedDate;
}

async function _fails(dataArray, parseDate, parseAssets, adjustForInflation) {
  return dataArray.map(d => {
    let date = parseDate(d["Closing Date"]);
    
    // Check if RANDOMIZE_ALL_Date is true and randomize the date.
    if (RANDOMIZE_ALL_Date) {
      date = randomizeDate(date);
    }
    
    const assets = parseAssets(d["Approx. Asset (Millions)"]);
    return {
      "Bank Name": d["Bank Name, City, State"].split(", ")[0],
      "City, State": d["Bank Name, City, State"].split(", ").slice(1).join(", "),
      "Date": date,
      "Assets": assets,
      "Assets (adj.)": adjustForInflation(date, assets),
      "Acquirer": d["Acquirer & Transaction"],
      "color": d["color"]
    };
  });
}

async function _failsVARFILENAME(FileAttachment, parseDate, parseAssets, adjustForInflation, csvName) {
  return (
    (await FileAttachment(csvName).csv({
      array: true
    }))
    .slice(1, -2)
    .map((d) => {
      let date = parseDate(d[2]);
      
      // Check if RANDOMIZE_ALL_Date is true and randomize the date.
      if (RANDOMIZE_ALL_Date) {
        date = randomizeDate(date);
      }
      
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
  )
}


async function _failsORG(FileAttachment, parseDate, parseAssets, adjustForInflation, csvName) {
  return (
    (await FileAttachment("bfb-data@2.csv").csv({
      array: true
    }))
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
  )
}

function _parseDate(d3) {
  return (
    d3.utcParse("%d-%b-%y")
  )
}

function _parseAssets() {
  return (
    (x) => parseFloat(x.replace(/[^\d.]/g, ""))
  )
}

function _cpiaucsl(__query, FileAttachment, invalidation) {
  return (
    __query(FileAttachment("CPIAUCSL.csv"), {
      from: {
        table: "CPIAUCSL"
      },
      sort: [],
      slice: {
        to: null,
        from: null
      },
      filter: [],
      select: {
        columns: null
      }
    }, invalidation)
  )
}

function _findCpi(d3, cpiaucsl) {
  const bisector = d3.bisector((d) => d.DATE);
  return (date) => cpiaucsl[bisector.center(cpiaucsl, date)].CPIAUCSL;
}


function _adjustForInflation(findCpi) {
  const currentCpi = findCpi(new Date("2023-05-01"));
  return (date, value) => currentCpi / findCpi(date) * value;
}

export default function define(runtime, observer,csvName = "bfb-data@2.csv", dataArrayGiven) {
  const main = runtime.module();
  // [ ] jc: ok csvName is passed from start but not fully used here

  function toString() {
    return this.url;
  }
  const fileAttachments = new Map([
    ["CPIAUCSL.csv", {
      url: "/static/CPIAUCSL.csv",
      mimeType: "text/csv",
      toString
    }],
    ["bfb-data@2.csv", {
      url: "/static/bfb-data@2.csv",
      mimeType: "text/csv",
      toString
    }]
  ]);

  main.builtin("FileAttachment", runtime.fileAttachments(name => fileAttachments.get(name)));

  main.variable().define("csvName", function() {
    // return "bfb-data@2.csv";
    return csvName;  // Scoped as passed
  });
  
  main.variable().define("dataArray", function() {
    // Define your sample data here
    return dataArrayGiven;
});

  main.variable(observer()).define(["md"], _1);

  main.variable().define("viewof Assets", ["Inputs"], _Assets);
  main.variable().define("Assets", ["Generators", "viewof Assets"], (G, _) => G.input(_));
  main.variable(observer("viewof sort")).define("viewof sort", ["Inputs"], _sort);
  main.variable().define("sort", ["Generators", "viewof sort"], (G, _) => G.input(_));

  main.variable(observer()).define(["Plot", "sort", "fails", "Assets"], _4);

  main.variable().define(["__query", "fails", "invalidation"], _5); // Hide fails output
  // variable csv name main.variable().define("fails", ["FileAttachment", "parseDate", "parseAssets", "adjustForInflation","csvName"], _fails); // Hide fails raw data view
  main.variable().define("fails", ["dataArray", "parseDate", "parseAssets", "adjustForInflation"], _fails); // Hide fails raw data view

  // *** Remove observer("name") if you won't want to see the defintion!
  main.variable().define("parseDate", ["d3"], _parseDate);
  main.variable().define("parseAssets", _parseAssets);
  main.variable().define("cpiaucsl", ["__query", "FileAttachment", "invalidation"], _cpiaucsl);
  main.variable().define("findCpi", ["d3", "cpiaucsl"], _findCpi);
  main.variable().define("adjustForInflation", ["findCpi"], _adjustForInflation);

  /*
   */

  return main;
}
