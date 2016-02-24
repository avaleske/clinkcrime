var x_domain = [];

$(document).ready(function(event) {
  // initial x domain
  var now = new Date();
  x_domain = [
      new Date(now.getFullYear(), now.getMonth() - 1, 1).getTime(),
      now.getTime()];
  $(this).trigger('draw');
});

$('.start.back').click(function(event) {
  var start = new Date(x_domain[0]);
  x_domain[0] = new Date(start.getFullYear(), start.getMonth() - 1, 1).getTime();
  $(document).trigger('draw');
});

$('.end.back').click(function(event) {
  var end = new Date(x_domain[1]);
  x_domain[1] = new Date(end.getFullYear(), end.getMonth(), -1).getTime();
  $(document).trigger('draw');
});

$('.start.forward').click(function(event) {
  var now = new Date();
  var start = new Date(x_domain[0]);
  x_domain[0] = Math.min(
    new Date(start.getFullYear(), start.getMonth() + 1, 1).getTime(),
    new Date(now.getFullYear(), now.getMonth(), 1).getTime()
  );
  $(document).trigger('draw');
});

$('.end.forward').click(function(event) {
  var now = new Date();
  var end = new Date(x_domain[1]);
  x_domain[1] = Math.min(
    new Date(end.getFullYear(), end.getMonth() + 2, -1).getTime(),
    now.getTime()
  );
  $(document).trigger('draw');
});

$(document).on('draw', function(event) {
  // I'm not proud of this
  // but I don't have time to refactor this so I can
  // easily do proper d3 updates
  // so we're going nuclear and rebuilding every time...
  $('svg').remove();

  // hide the throbber at the end
  $('#throbber').on('chart_complete', function() {
    $(this).hide();
  });

  $('#throbber').show();

  // Set our margins for the chart
  var margin = {
      top: 200,
      right: 20,
      bottom: 50,
      left: 60
  };
  var width = 700 - margin.left - margin.right;
  var height = 550 - margin.top - margin.bottom;

  var svg = d3.select(".chart").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  // get crime data
  d3.csv('/api/grouped_crime/start/' + x_domain[0] + '/end/' + x_domain[1],
    type,
    function(error, crime_csv){

    if (error) throw error // todo: handle a server error

    // group data by days
    var data = d3.nest()
      .key(function(d) { return d.key; })
      .sortKeys(function(a,b){ return new Date(a)-new Date(b); })
      // and rearrange rows to be key value pairs of {group: count}
      .rollup(function(day_group) {
        obj = {};
        day_group.forEach(function(row, i, arr){
          obj[row.event_clearance_group] = row.count;
        });
        return obj;
      })
      .entries(crime_csv);

    // get unique crime types
    var crime_catagories = d3.keys(d3.map(crime_csv, function(d) {
                                      return d.event_clearance_group;
                                    })._).sort().reverse();

    // get colors
    var color = d3.scale.ordinal()
      //.domain([0, 36])
      .domain(crime_catagories)
      .range(color_scale);

      // add stack info. todo: combine this with the rollup function above
      data.forEach(function(d) {
        var y0 = 0;
        d.catagories = crime_catagories.map(function(catagory) {
          var y0_old = y0;
          y0 += typeof d.values[catagory] !== 'undefined' ? d.values[catagory] : 0;
          return {catagory: catagory, y0: y0_old, y1: y0};
        });
        d.total = d.catagories[d.catagories.length - 1].y1;
      });

    // define domains
    var x_domain = d3.extent(data, function(d) { return new Date(d.key); });
    var y_domain = [0, d3.max(data, function(d) { return d.total; })];

    // define scales
    var x = d3.time.scale()
            .domain(x_domain)
            .rangeRound([0, width]);

    var y = d3.scale.linear()
              .domain(y_domain)
              .range([height, 0]);

    // define axis
    var xAxis = d3.svg.axis()
                  .orient("bottom")
                  .scale(x)
                  // .ticks(d3.time.days(x_domain[0], x_domain[1]).length)
                  .tickFormat(d3.time.format("%d %b"));

    var yAxis = d3.svg.axis()
                  .orient("left")
                  .scale(y);

    // append x axis
    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0,"+ height + ")")
      .call(xAxis)
        .selectAll("text")
        .attr("y", 0)
        .attr("x", -40)
        .attr("dy", ".35em")
        .attr("transform", "rotate(-90)")
        .style("text-anchor", "start");

    // append y axis
    svg.append("g")
        .attr("class", "y axis")
        .attr("transform", "translate(-20, 0)")
        .call(yAxis)
      .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 4)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text("Crime Events");

    // build the initial legend
    var $legend = $('.legend');
    $legend.empty();
    crime_catagories.forEach(function(c) {
      $li = $('<li>').addClass('legend-item');
      $li.append(
          $('<span>').text(c.toLowerCase()).addClass('legend-label')
        ).append(
          $('<span>').css('background-color', color(c)).addClass('legend-color')
        ).append(
          $('<span>').text('').addClass('legend-count')
        );
      $legend.prepend($li);
    });

    // create day groups
    var day = svg.selectAll(".day")
        .data(data, function(d) { return d.key; })
      .enter().append("g")
        .attr("class", "day")
        .style({cursor: 'pointer', 'pointer-events':'all'})
        .attr("transform", function(d) {
          return "translate(" + (x(new Date(d.key)) - (width/data.length)/2) + ",0)"; })
        .on("click", function(d) {
          // destroy the legend and rebuild it
          // yes, I know there are better ways to do this
          // yes, I should've used react in this project...
          var $legend = $('.legend');
          $legend.empty();
          d.catagories.forEach(function(c) {
            $li = $('<li>').addClass('legend-item');
            $li.append(
                $('<span>').text(c.catagory.toLowerCase()).addClass('legend-label')
              ).append(
                $('<span>').css('background-color', color(c.catagory)).addClass('legend-color')
              ).append(
                $('<span>').text(c.y1-c.y0).addClass('legend-count')
              );
            $legend.prepend($li);
          });
        });

    // enter rectangle elements
    day.selectAll("rect")
        .data(function(d) { return d.catagories; })
      .enter().append("rect")
        .attr("width", width/data.length )
        .attr("y", function(d) { return y(d.y1); })
        .attr("height", function(d) { return y(d.y0) - y(d.y1); })
        .style("fill", function(d) { return color(d.catagory); });

    // get event data and process it
    // todo refactor so stuff isn't nesting forever
    d3.csv('/api/all_events', event_type, function(error, event_csv){
      if (error) throw error;

      event_data = event_csv.filter(function(d) {
        return d.location != 'CenturyLink Field Event Center'
          && d.event_datetime >= x_domain[0];
      });
      event_data.sort(function(a,b){ return a.event_datetime - b.event_datetime; });

      // create event day groups
      var event_day = svg.selectAll(".event-day")
          .data(event_data, function(d) { return d.key; })
        .enter().append("g")
          .attr("class", "event-day")
          .style({cursor: 'pointer', 'pointer-events':'none'})
          .attr("transform", function(d) {
            return "translate(" + (x(new Date(d.key)) - (width/data.length)/2) + ",0)"; });

      // create event day rects
      event_day.append("rect")
          .attr("class", "event-rect")
          .attr("width", width/data.length)
          .attr("y", 0 - margin.top)
          .attr("height", height + margin.bottom + margin.top);

      // and event labels
      event_day.append("text")
        .attr("class", "event-label")
          .attr("transform", "rotate(-90)")
          .attr("y", -(width/data.length/4))
          .attr("dy", width/data.length)
          .attr("x", 0 )
          .style("text-anchor", "start")
          .text(function(d) { return d.title; });

      $('#throbber').trigger('chart_complete')
    });
  });

  function type(d) {
    d.key = (new Date(+d.date)).toLocaleDateString();
    d.count = +d.count; // coerce to number
    d.date = new Date(+d.date);
    d.event_clearance_group = d.event_clearance_group;
    return d
  }

  function event_type(d) {
    d.key = (new Date(+d.event_datetime)).toLocaleDateString();
    d.trumba_id = +d.trumba_id;
    d.event_datetime = new Date(+d.event_datetime);
    // these two aren't strictly necessary, but including for completeness
    d.title = d.title;
    d.location = d.location;
    return d;
  }

  color_scale = [
    '#8c6d31',
    '#1f77b4',
    '#f7b6d2',
    '#aec7e8',
    '#ff7f0e',
    '#ffbb78',
    '#2ca02c',
    '#98df8a',
    '#d62728',
    '#ff9896',
    '#9467bd',
    '#2ca02c',
    '#c5b0d5',
    '#8c564b',
    '#bcbd22',
    '#c49c94',
    '#e377c2',
    '#06332c',
    '#7f7f7f',
    '#c7c7c7',
    '#bcbd22',
    '#f1bdc2',
    '#dbfb8d',
    '#17becf',
    '#9edae5',
    '#e7cb94',
    '#843c39',
    '#ff7f0e',
    '#87badf',
    '#e377c2',
    '#7f7f7f',
    '#637939',
    '#6baed6',
    '#393b79',
    '#e7ba52',
    '#969696',
    '#ce6dbd'
  ];

});
