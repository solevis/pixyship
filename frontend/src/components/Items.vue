<template>
  <div>
    <v-app dark>
      <ps-header/>
      Items - 48 hour market prices. Click a row for charts.
      <div class="center">
        <v-text-field
          v-model="search"
          append-icon="search"
          id="search"
          label="Search"
          placeholder="search name, slot/type, enhancement, description"
        ></v-text-field>
        <br/>
        <v-data-table
          :headers="headers"
          :items="items"
          :rows-per-page-items="[10,20,50,100,200,{'text':'$vuetify.dataIterator.rowsPerPageAll','value':-1}]"
          :pagination.sync="pagination"
          :search="search"
          :custom-filter="fieldFilter"
          :filter="multipleFilter"
          item-key="id"
        >
          <template slot="items" slot-scope="i">
            <tr @click="toggleExpand(i)">
              <td>
                <div :style="spriteStyle(i.item.sprite)"></div>
              </td>
              <td><!-- Name -->
                <div :class="[i.item.rarity, 'lh-9', 'name', 'text-xs-left']">
                  {{ i.item.name }}<br/>
                </div>
              </td>
              <td class="text-xs-right">{{ i.item.market_price }}</td>
              <td>
                <table>
                <tr v-for="(price, k, ind) in i.item.prices" class="nobreak">
                  <td>{{ prePriceFormat(price) }}<div class="block" :style="currencySprite(k)"/></td>
                  <td>{{ price.count }}</td>
                  <td class="text-xs-left" v-html="priceFormat(price)"></td>
                </tr>
                </table>
              </td>
              <td class="stat">
                {{ i.item.slot || i.item.type }}
                <span v-if="i.item.slot"><br/>{{ i.item.type }}</span>
              </td>
              <td class="text-xs-right">{{ i.item.bonus || '' }}</td>
              <td class="text-xs-left text-capitalize">{{ i.item.enhancement === 'none' ? '' : i.item.enhancement}}</td>
              <td style="min-width: 55px">
                <template v-for="j in i.item.recipe">
                  <div>
                    {{ j.count }}
                    <div class="block" :style="spriteStyle(j.sprite)" :title="j.name"></div>
                  </div>
                </template>
              </td>
              <td class="text-xs-left caption">{{ i.item.description }}</td>
            </tr>
          </template>
          <template slot="expand" slot-scope="i">
            <v-container class="my-0 py-0">
              <v-layout justify-center>
                <v-switch v-model="showGas" label="Gas" color="purple" @click.native="updatePlot"></v-switch>
                <v-switch v-model="showMineral" label="Mineral" color="blue" hide-details
                  @click.native="updatePlot"></v-switch>
                <v-switch v-model="showStarbux" label="Starbux" color="green" hide-details
                  @click.native="updatePlot"></v-switch>
              </v-layout>
            </v-container>
            <div :id="'chart-' + i.item.id" class="center"></div>
          </template>
        </v-data-table>
      </div>
      <br/>
      <div></div>
      <div>
        <a href="http://www.pixelstarships.com">Pixel Starships</a>
      </div>
    </v-app>
  </div>
</template>

<script>

import axios from 'axios'
import Vue from 'vue'
import BootstrapVue from 'bootstrap-vue'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import Header from './Header'
import 'vuetify/dist/vuetify.min.css'
import mixins from './Common.vue.js'
import plotly from 'plotly.js-dist'
require('../assets/common.css')

Vue.component('ps-header', Header)

Vue.use(BootstrapVue)

function styleFromSprite (s, color = '', border = 0, ninepatch = 0) {
  if (Object.keys(s).length === 0) {
    return {}
  }
  let obj = {
    background: `${color} url('//pixelstarships.s3.amazonaws.com/${s.source}.png') -${s.x}px -${s.y}px`,
    width: `${s.width}px`,
    height: `${s.height}px`,
    border: `${border}px solid lightgrey`,
    imageRendering: 'pixelated'
  }
  return obj
}

export default {
  mixins: [mixins],

  data () {
    return {
      devMode: process.env.NODE_ENV === 'development',
      items: [],
      search: '',
      headers: [
        {text: 'Image', align: 'center', sortable: false},
        {text: 'Name', align: 'center', value: 'name'},
        {text: 'Savy Price', align: 'center', value: 'market_price'},
        {text: 'Market $ | # | 25-50-75%', align: 'center', value: 'offers'},
        {text: 'Type', align: 'center', value: 'slot'},
        {text: 'Bonus', align: 'center', value: 'bonus'},
        {text: 'Enhancement', align: 'center', value: 'enhancement'},
        {text: 'Recipie', align: 'center', sortable: false},
        {text: 'Description', align: 'center', value: 'description'}
      ],
      pagination: {'sortBy': 'offers', 'descending': true, 'rowsPerPage': 20},
      showStarbux: true,
      showGas: false,
      showMineral: false,
      openRow: null
    }
  },

  components: {
  },

  created: function () {
    this.init()
  },

  methods: {
    updatePlot () {
      if (this.openRow) this.plotData(this.openRow)
    },

    plotData (row) {
      const h = this.items[row.item.id].priceHistory
      if (Object.keys(h).length > 0) {
        const series = {}
        const currency = []
        if (this.showStarbux) currency.push('starbux')
        if (this.showGas) currency.push('gas')
        if (this.showMineral) currency.push('mineral')

        const cDetails = {
          starbux: {color: '122,255,185', short: '$', side: 'left'},
          gas: {color: '168,89,190', short: 'G', side: 'right'},
          mineral: {color: '6,152,193', short: 'M', side: 'right'}
        }

        // Get the data series indicated
        currency.map(f => {
          if (f in h) {
            series[f] = {}
            series[f].dates = Object.keys(h[f])
            series[f].p25 = Object.entries(h[f]).map(e => e[1].p25)
            series[f].p50 = Object.entries(h[f]).map(e => e[1].p50)
            series[f].p75 = Object.entries(h[f]).map(e => e[1].p75)
            series[f].count = Object.entries(h[f]).map(e => e[1].count)
          }
        })

        let data = []
        currency.map(c => {
          const line = {shape: 'spline', color: 'rgba(' + cDetails[c].color + ',1)'}
          const bound = {shape: 'spline', color: 'rgba(' + cDetails[c].color + ',0.3)'}
          const fill = 'rgba(' + cDetails[c].color + ',0.2)'
          if (c in series) {
            data.push({
              x: series[c].dates,
              y: series[c].count,
              type: 'scatter',
              name: cDetails[c].short + ' Vol',
              line: line,
              xaxis: 'x',
              yaxis: 'y2'
            })
            const p25 = {
              x: series[c].dates,
              y: series[c].p25,
              type: 'scatter',
              name: cDetails[c].short + ' 25%',
              line: bound
            }
            const p75 = {
              x: series[c].dates,
              y: series[c].p75,
              type: 'scatter',
              name: cDetails[c].short + ' 75%',
              line: bound,
              fill: 'tonextx',
              fillcolor: fill
            }
            const p50 = {
              x: series[c].dates,
              y: series[c].p50,
              type: 'scatter',
              name: cDetails[c].short + ' 50%',
              line: line
            }
            if (cDetails[c].side === 'right') {
              p25.yaxis = 'y3'
              p50.yaxis = 'y3'
              p75.yaxis = 'y3'
            }
            data.push(p25)
            data.push(p75)
            data.push(p50)
          }
        })
        let layout = {
          legend: {traceorder: 'reversed'},
          yaxis2: {
            domain: [0, 0.3],
            title: 'Volume',
            gridcolor: '#222'
          },
          xaxis: {
            showgrid: false
          },
          paper_bgcolor: 'black',
          plot_bgcolor: 'black',
          margin: {t: 35, b: 30},
          font: {color: 'white'},
          title: `${row.item.name} prices`
        }
        if (this.showStarbux) {
          layout.yaxis = {
            domain: [0.3, 1],
            title: 'Starbux',
            gridcolor: '#222'
          }
          layout.yaxis3 = {title: 'Gas/Mineral', overlaying: 'y', side: 'right'}
        } else {
          layout.yaxis3 = {domain: [0.3, 1], title: 'Gas/Mineral'}
        }
        const options = {displayModeBar: false}
        plotly.newPlot(document.getElementById('chart-' + row.item.id), data, layout, options)
      }
    },

    toggleExpand: async function (row) {
      row.expanded = !row.expanded
      if (row.expanded) {
        // Fetch data if needed
        if (!this.items[row.item.id].priceHistory) {
          // TODO: Make the transform once then
          const r = await axios.get(this.itemPricesEndpoint(row.item.id))
          this.items[row.item.id].priceHistory = r.data.data.prices
        } else {
          await new Promise(resolve => setTimeout(resolve, 1))
        }
        this.openRow = row

        this.plotData(row)
      }
    },

    init: async function () {
      const r = await axios.get(this.itemsEndpoint)
      let data = []
      for (const k in r.data.data) {
        const v = r.data.data[k]
        v.id = Number(k)
        data.push(v)
      }
      data.forEach(x => {
        x.offers = x.prices
          ? Object.keys(x.prices).map(k => x.prices[k].count).reduce((c, s) => c + s)
          : 0
      })
      this.items = data
      return this.items
    },

    shipSelected () {
      if (typeof this.searchString === 'string') {
        this.getChar(this.searchString)
      } else {
        this.getChar(this.searchString.name)
      }
    },

    onSearch (search, loading) {
      if (search.length >= 2) {
        this.getNames(search)
      } else {
        this.getNames('')
      }
    },

    spriteStyle (s) {
      return styleFromSprite(s)
    },

    priceFormat (p) {
      const formatFunc = (Math.max(p.p25, p.p50, p.p75) > 999)
        ? x => (x / 1000).toFixed(1)
        : x => x.toFixed(0)
      return [p.p25, p.p50, p.p75].map(x => formatFunc(x)).join(' - ')
    },

    prePriceFormat (p) {
      return (Math.max(p.p25, p.p50, p.p75) > 999) ? 'K' : ' '
    },

    currencySprite (currency) {
      switch (currency) {
        case 'starbux':
          return this.buxSprite()
        case 'gas':
          return this.gasSprite()
        case 'mineral':
          return this.mineralSprite()
        case 'supply':
          return this.supplySprite()
        default:
          return ''
      }
    },

    onImageLoad (event) {
      // get real image size from img element
      // This still isn't working on Safari
      const imageEle = event.path[0]
      const img = new Image()
      img.onload = () => {
        imageEle.setAttribute('width', img.naturalWidth)
        imageEle.setAttribute('height', img.naturalHeight)
      }
      img.src = imageEle.href.baseVal
    },

    fieldFilter (items, search, filter) {
      search = search.toString().toLowerCase()
      return items.filter(row =>
        filter(row['name'], search) ||
        filter(row['slot'], search) ||
        filter(row['type'], search) ||
        filter(row['enhancement'], search) ||
        filter(row['description'], search)
      )
    }
  }
}
</script>

<style>
  .nobreak {
    word-break: keep-all;
    white-space: nowrap;
  }

  .application.theme--dark {
    background-color: black;
  }

  .v-datatable, .v-datatable__actions {
    background-color: inherit !important;
  }

  .v-datatable td {
    height: unset !important;
  }

  .v-datatable td,
  .v-datatable th {
    padding: 0 5px !important;
    color: white !important;
  }

  .v-datatable tr {
    height: unset !important;
  }

  .v-datatable tbody tr:hover {
    background-color: #222 !important;
  }

  .v-datatable tr.v-datatable__expand-row:hover {
    background-color: #000 !important;
  }

  html, body {
    background-color: black;
    color: white;
  }

  .main {
    margin-top: 10px;
  }

  .center {
    margin: 0 auto;
  }

  /* this doesn't work except on multiple lines */
  .name {
    line-height: 1;
    font-weight: bold;
  }

  .stat span {
    color: gray;
    font-size: 60%;
  }

  .stat {
    line-height: .7;
  }

  :visited {
    color: #24E3FF;
  }

  :link {
    color: #FF5656;
    text-decoration: none;
  }

  .block {
    display: inline-block;
  }

</style>
