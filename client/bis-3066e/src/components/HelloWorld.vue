<template>
  <v-container>
    <div id='viewerchart'>
      <apexchart type="bar" height="750" :options="viewerChartOptions" :series="viewerChartseries"></apexchart>
    </div> 
    <div id="tournamentchart">
      <apexchart type="bar" height="750" :options="tournementChartOptions" :series="tournementChartSeries"></apexchart>
    </div>
    <div id="avgplacechart">
      <apexchart type="bar" height="750" :options="avgPlaceOptions" :series="avgPlaceSeries"></apexchart>
    </div>
  </v-container>
</template>

<script>
  import VueApexCharts from 'vue-apexcharts'
  export default {
    name: 'HelloWorld',
    components: {
      'apexchart': VueApexCharts,
    },
    props: {
      viewerdata: Array, 
      teamdata: Array, 
      tournamentdata: Array
    },
    data: () => ({
      showTop : 25,
      placementThreshold: 4,
      teams: [],
      tournamentResults: [],
      viewerChartseries: [{name: 'Average Viewers', data: []}, {name: 'Peak Viewers', data: []}],
      viewerChartOptions: { 
        chart: { type: 'bar', height: 750 },
        plotOptions: { bar: { horizontal: false, columnWidth: '55%', endingShape: 'rounded'}, },
        dataLabels: { enabled: false },
        stroke: { show: true, width: 2, colors: ['transparent'] },
        xaxis: { categories: [], },
        yaxis: { title: { text: 'Viewers' } },
        fill: { opacity: 1 },
        tooltip: { y: { formatter: function (val) { return val + " Viewers" } } }
      },
      tournementChartSeries: [ { name: 'Top 4 Placements', data: [
        {
          x: '2011',
          y: 12,
          goals: [{name: 'Wins', value: 14, strokeWidth: 5, strokeColor: '#775DD0'}]
        }
      ]}],
      tournementChartOptions: {
        chart: { height: 750, type: 'bar' },
        plotOptions: { bar: { horizontal: true, } },
        colors: ['#00E396'],
        dataLabels: {
          formatter: function(val, opt) {
            const goals = opt.w.config.series[opt.seriesIndex].data[opt.dataPointIndex].goals;
            if (goals && goals.length) {
              return `${goals[0].value} / ${val}`;
            }
            return val
          }
        },
        legend: {
          show: true,
          showForSingleSeries: true,
          customLegendItems: ['Top 4 Placements', 'Wins'],
          markers: {
            fillColors: ['#00E396', '#775DD0']
          }
        }
      },
      avgPlaceSeries: [{ data: [400, 430, 448, 470, 540, 580, 690, 1100, 1200, 1380] }],
      avgPlaceOptions: {
        chart: { type: 'bar', height: 750 },
        plotOptions: { bar: { borderRadius: 4, horizontal: true, } },
        dataLabels: { enabled: false },
        xaxis: { categories: [], }
      },
    }),
    methods : {
      makeViewerList() {
        this.viewerdata.forEach(element => {
          element.matches.forEach(match => {
            if(match.viewers >= 0) {
              this.getTeams(match.teams).forEach(team => {
              if (this.teams.some(t => t.name === team)) {
                this.teams.find(obj => {
                  return obj.name === team
                }).viewers.push(match.viewers);
              } else {
                  this.teams.push({
                    name: team,
                    viewers: [
                      match.viewers,
                    ]
                  });
                } 
              }); 
            }
          })
        });
        this.teams.forEach(team => {
          let i = 0; 
          let sum = 0; 
          for(i = 0; i < team.viewers.length; i++) {
              team.viewers[i] = parseInt(team.viewers[i]); 
              sum += team.viewers[i]; 
          }
          team.totalViewers = sum;
          team.averageViewers = (sum / i).toFixed(0);
          team.viewers.sort((a,b)=>b-a);
        }); 
        this.teams.sort((a,b)=>b.averageViewers-a.averageViewers); 
        console.log(this.teams); 
      },
      populateViewerGraph() {
        let newData = JSON.parse(JSON.stringify(this.viewerChartseries));
        let newOptions = JSON.parse(JSON.stringify(this.viewerChartOptions));
        newData[0].data = []; 
        newOptions.xaxis.categories = []; 
        for(var i = 0; i < this.showTop; i++) {
          newData[0].data.push(this.teams[i].averageViewers);
          newData[1].data.push(this.teams[i].viewers[0]);
          newOptions.xaxis.categories.push(this.teams[i].name);
        }
        this.viewerChartseries = newData; 
        this.viewerChartOptions = newOptions;
      },
      makeTournamentList() {
        this.tournamentdata.forEach(tournament => {
          Array.from(tournament[Object.keys(tournament)[0]]).forEach(placement => {
            this.getTeams(placement.teams).forEach(team => {
              if (this.tournamentResults.some(t => t.team === team)) {
                let entry = this.tournamentResults.find(obj => {
                  return obj.team === team
                }); 
                let place = parseInt(this.getBestPlacement(placement.place));
                entry.placements.push(place);
                entry.topX += place <= this.placementThreshold ? 1 : 0; 
                entry.wins += place == 1 ? 1 : 0; 
                entry.sumPlace += place;
                entry.averagePlace = entry.sumPlace / entry.placements.length;
              } else {
                let place = parseInt(this.getBestPlacement(placement.place)); 
                this.tournamentResults.push({
                  team: team, 
                  placements: [place],
                  topX: place <= this.placementThreshold ? 1 : 0,
                  wins: place == 1 ? 1 : 0,
                  averagePlace : place,
                  sumPlace: place,
                });
              } 
            });
          }); 
        });
        this.tournamentResults.sort((a,b)=>b.topX-a.topX); 
        console.log(this.tournamentResults); 
      },
      populateTournamentGraph() {
        this.tournamentResults.sort((a,b)=>b.topX-a.topX); 
        let newData = JSON.parse(JSON.stringify(this.tournementChartSeries));
        newData[0].data = []; 
        for(var i = 0; i < this.showTop; i++) {
          newData[0].data.push({
            x: this.tournamentResults[i].team,
            y: this.tournamentResults[i].topX,
            goals: [{name: 'Wins', value: this.tournamentResults[i].wins, strokeWidth: 5, strokeColor: '#775DD0'}]
          }); 
        }
        this.tournementChartSeries = newData; 
        //average wins
        this.tournamentResults.sort((a,b)=>a.averagePlace-b.averagePlace); 
        newData = JSON.parse(JSON.stringify(this.avgPlaceSeries));
        let newOptions = JSON.parse(JSON.stringify(this.avgPlaceOptions));
        newData[0].data = []; 
        newOptions.xaxis.categories = []; 
        for(var j = 0; j < this.showTop; j++) {
          newData[0].data.push(this.tournamentResults[j].averagePlace);
          newOptions.xaxis.categories.push(this.tournamentResults[j].team);
        }
        this.avgPlaceSeries = newData; 
        this.avgPlaceOptions = newOptions; 
      },
      getTeams(teams) {
        return teams.split('|'); 
      }, 
      getBestPlacement(placement) {
        return placement.split('-')[0];
      }
    },
    mounted() {
      this.makeViewerList(); 
      this.populateViewerGraph(); 
      this.makeTournamentList();
      this.populateTournamentGraph(); 
    }
  }
</script>
