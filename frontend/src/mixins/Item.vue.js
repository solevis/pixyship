import plotly from "plotly.js-dist"

export default {

  data() {
    return {
      showStarbux: true,
      showGas: false,
      showMineral: false,
      charts: [],
    }
  },

  methods: {
    formatBonus(item) {
      let formatedBonus = ""

      if (item.disp_enhancement != null && item.bonus) {
        formatedBonus = item.short_disp_enhancement + ' +' + item.bonus
      }

      return formatedBonus
    },

    formatExtraBonus(item) {
      let formatedBonus = ""

      if (item.module_extra_disp_enhancement != null && item.module_extra_enhancement_bonus) {
        formatedBonus = item.module_extra_short_disp_enhancement + ' +' + item.module_extra_enhancement_bonus
      }

      return formatedBonus
    },

    priceFormat(prices, price) {
      const formatFunc = function (x) {
        if (Math.max(prices.p25, prices.p50, prices.p75) > 999999) {
          return parseFloat((x / 1000000).toFixed(1)) + "M"
        } else if (Math.max(prices.p25, prices.p50, prices.p75) > 999) {
          return parseFloat((x / 1000).toFixed(1)) + "K"
        } else {
          return x.toFixed(0)
        }
      }

      return formatFunc(price)
    },

    updatePlot(chartElementId = null, showMainTitle = true) {
      for (var i = 0; i < this.charts.length; i++) {
        this.plotData(this.charts[i], chartElementId, showMainTitle)
      }
    },

    plotData(item, chartElementId = null, showMainTitle = true) {
      const history = item.priceHistory

      if (Object.keys(history).length > 0) {
        const series = {}
        const currencies = []

        if (this.showStarbux) currencies.push("Starbux")
        if (this.showGas) currencies.push("Gas")
        if (this.showMineral) currencies.push("Mineral")

        const currencyDetails = {
          Starbux: { color: "122,255,185", short: "$", side: "left" },
          Gas: { color: "168,89,190", short: "G", side: "right" },
          Mineral: { color: "6,152,193", short: "M", side: "right" },
        }

        // Get the data series indicated
        currencies.map((currency) => {
          if (currency in history) {
            series[currency] = {}
            series[currency].dates = Object.keys(history[currency])
            series[currency].p25 = Object.entries(history[currency]).map(
              (e) => e[1].p25
            )
            series[currency].p50 = Object.entries(history[currency]).map(
              (e) => e[1].p50
            )
            series[currency].p75 = Object.entries(history[currency]).map(
              (e) => e[1].p75
            )
            series[currency].count = Object.entries(history[currency]).map(
              (e) => e[1].count
            )
          }
        })

        let data = []
        currencies.map((currency) => {
          const line = {
            shape: "spline",
            color: "rgba(" + currencyDetails[currency].color + ",1)",
          }
          const bound = {
            shape: "spline",
            color: "rgba(" + currencyDetails[currency].color + ",0.3)",
          }
          const fill = "rgba(" + currencyDetails[currency].color + ",0.2)"

          if (currency in series) {
            let serie = series[currency]
            let currencyDetail = currencyDetails[currency]

            data.push({
              x: serie.dates,
              y: serie.count,
              type: "scatter",
              name: currencyDetail.short + " Vol",
              line: line,
              xaxis: "x",
              yaxis: "y2",
            })

            const p25 = {
              x: serie.dates,
              y: serie.p25,
              type: "scatter",
              name: currencyDetail.short + " 25%",
              line: bound,
            }

            const p75 = {
              x: serie.dates,
              y: serie.p75,
              type: "scatter",
              name: currencyDetail.short + " 75%",
              line: bound,
              fill: "tonextx",
              fillcolor: fill,
            }

            const p50 = {
              x: serie.dates,
              y: serie.p50,
              type: "scatter",
              name: currencyDetail.short + " 50%",
              line: line,
            }

            if (currencyDetail.side === "right") {
              p25.yaxis = "y3"
              p50.yaxis = "y3"
              p75.yaxis = "y3"
            }

            data.push(p25)
            data.push(p75)
            data.push(p50)
          }
        })

        let layout = {
          autosize: true,
          legend: {
            traceorder: "reversed",
            orientation: "h"
          },
          yaxis2: {
            domain: [0, 0.3],
            title: "Volume",
            gridcolor: "#9e9e9e47",
          },

          xaxis: {
            showgrid: false,
          },

          paper_bgcolor: "#1f1f1f",
          plot_bgcolor: "#1f1f1f",
          margin: { t: 35, b: 30 },
          font: { color: "white" },
          title: showMainTitle ? `${item.name} prices` : '',
        }

        if (this.showStarbux) {
          layout.yaxis = {
            domain: [0.3, 1],
            title: "Starbux",
            gridcolor: "#9e9e9e47",
          }

          layout.yaxis3 = {
            title: "Gas/Mineral",
            overlaying: "y",
            side: "right",
          }
        } else {
          layout.yaxis3 = {
            domain: [0.3, 1],
            title: "Gas/Mineral",
            gridcolor: "#9e9e9e47",
          }
        }

        const options = {
          responsive: true,
          displaylogo: false,
          displayModeBar: true,
          modeBarButtonsToRemove: [
            'hoverClosestCartesian',
            'hoverCompareCartesian',
            'toggleSpikelines',
            'resetScale2d',
            'zoomIn2d',
            'zoomOut2d'
          ]
        }

        if (chartElementId === null) {
          chartElementId = "chart-" + item.id
        }

        plotly.newPlot(
          document.getElementById(chartElementId),
          data,
          layout,
          options
        )
      }
    },

    resizePlot(item, chartElementId = null) {
      if (chartElementId === null) {
        chartElementId = "chart-" + item.id
      }

      plotly.relayout(chartElementId, {
        'xaxis.autorange': true,
        'yaxis.autorange': true
      })
    },
  }
}