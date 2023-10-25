all_data = {}
BSs = [168, 171]
KPIs = []

$(function(){
    // set the dimensions and margins of the graph
    var margin = {top: 10, right: 30, bottom: 30, left: 60},
        width = 460 - margin.left - margin.right,
        height = 400 - margin.top - margin.bottom;

    // append the svg object to the body of the page
    var svg = d3.select("#my_dataviz")
      .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
      .append("g")
        .attr("transform",
              "translate(" + margin.left + "," + margin.top + ")");
    //Read the data
    BSs.forEach(bs =>{
        console.log(bs)
        all_data[bs] = {}
        KPIs.forEach(kpi =>
        d3.csv("https://raw.githubusercontent.com/ssinghjah/ssinghjah.github.io/main/files/" + bs + "_" + kpi + ".csv",
          function(data) {
            all_data[bs][kpi] = data
            console.log(data)
        })})
    })
})