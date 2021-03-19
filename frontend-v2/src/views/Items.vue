<template>
  <v-card :loading="isLoading">
    <v-card-title v-if="!loaded"> Loading... </v-card-title>

    <!-- Filters -->
    <v-card-title v-if="loaded">
      <v-row>
        <v-col cols="6">
          <v-text-field
            v-model="searchName"
            append-icon="mdi-magnify"
            label='Name (example: "Sandbag", Barrier)'
            hide-details
          ></v-text-field>
        </v-col>
        <v-col cols="2">
          <v-combobox
            v-model="searchType"
            :items="types"
            label="Type"
            clearable
            multiple
            small-chips
            hide-details
          ></v-combobox>
        </v-col>
        <v-col cols="2">
          <v-combobox
            v-model="searchSlot"
            :items="slots"
            label="Slot"
            clearable
            multiple
            small-chips
            hide-details
          ></v-combobox>
        </v-col>
        <v-col cols="2">
          <v-combobox
            v-model="searchStat"
            :items="stats"
            label="Stat"
            clearable
            multiple
            small-chips
            hide-details
          ></v-combobox>
        </v-col>
      </v-row>
    </v-card-title>

    <!-- Table -->
    <v-data-table
      v-if="loaded"
      :headers="headers"
      :items="items"
      :search="searchName"
      :custom-filter="multipleFilterWithNegative"
      :items-per-page="20"
      :loading="isLoading"
      :footer-props="{
        itemsPerPageOptions: [10, 20, 50, 100, 200, -1],
      }"
      multi-sort
      loading-text="Loading..."
      class="elevation-1"
      dense
    >

      <template v-slot:item="{ item, expand, isExpanded }">
        <tr v-on:item-expanded="rowExpanded" @click="expand(!isExpanded)">
          

          <!-- Image -->
          <td>
            <div :style="spriteStyle(item.sprite)"></div>
          </td>

          <!-- Name -->
          <td>
            <div :class="[item.rarity, 'lh-9', 'name']">
              {{ item.name }}<br/>
            </div>
          </td>

          <!-- Savy price -->
          <td>{{ item.market_price }}</td>

          <!-- Market price 48h -->
          <td>
            <table>
              <tr v-for="(price, currency, ind) in item.prices" :key="'item' + item.id + '-price-' + ind" class="nobreak">
                <td><div class="block" :style="currencySprite(currency)"/></td>
                <td>{{ price.count }}</td>
                <td class="text-xs-left" v-html="priceFormat(price)"></td>
              </tr>
            </table>
          </td>

          <!-- Type -->
          <td class="stat">
            {{ item.type }}
          </td>

          <!-- SubType -->
          <td class="stat">
            {{ item.slot }}
          </td>

          <!-- Bonus -->
          <td class="text-xs-right">{{ formatBonus(item) }}</td>
          <td class="text-xs-left text-capitalize">{{ item.enhancement === 'none' ? '' : item.enhancement}}</td>
          
          <!-- Recipe -->
          <td style="min-width: 55px">
            <table>
              <tr v-for="ingredient in item.recipe" :key="'item' + item.id + '-recipe-' + ingredient.name" class="nobreak">
                <td><div class="block" :style="spriteStyle(ingredient.sprite)" :title="ingredient.name"/></td>
                <td>{{ ingredient.count }}</td>
              </tr>
            </table>
          </td>

          <!-- Description -->
          <td :colspan="headers.length">
            {{ item.description }}
          </td>
        </tr>
      </template>

      <template v-slot:expanded-item="{ headers, item }">
        <td :colspan="headers.length">
          <v-container class="my-0 py-0">
            <v-layout justify-center>
              <v-switch v-model="showGas" label="Gas" color="purple" @click.native="updatePlot"></v-switch>
              <v-switch v-model="showMineral" label="Mineral" color="blue" hide-details
                @click.native="updatePlot"></v-switch>
              <v-switch v-model="showStarbux" label="Starbux" color="green" hide-details
                @click.native="updatePlot"></v-switch>
            </v-layout>
          </v-container>
          <div :id="'chart-' + item.id" class="center"></div>
        </td>
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
import axios from "axios";
import mixins from "@/mixins/PixyShip.vue.js";
import plotly from 'plotly.js-dist'

export default {
  mixins: [mixins],

  components: {
  },

  data() {
    return {
      searchName: "",
      searchType: [],
      searchSlot: [],
      searchStat: [],
      stats: [],
      slots: [],
      types: [],
      loaded: false,
      headers: [
        {text: 'Image', align: 'center', sortable: false, filterable: false},
        {text: 'Name', align: 'center', value: 'name', filterable: true},
        {text: 'Savy Price', align: 'center', value: 'market_price', filterable: false},
        {text: 'Market $ (48h) | # | 25 - 50 - 75%', align: 'center', value: 'offers', filterable: false},
        {
          text: 'Type', 
          align: 'center', 
          value: 'type', 
          filter: value => { 
            return this.filterCombobox(value, this.searchType)
          }
        },
        {
          text: 'Slot', 
          align: 'center', 
          value: 'slot', 
          filter: value => { 
            return this.filterCombobox(value, this.searchSlot)
          }
        },
        {
          text: 'Bonus', 
          align: 'center', 
          value: 'bonus', 
          filterable: false,
        },
        {
          text: 'Stat', 
          align: 'center', 
          value: 'enhancement', 
          filter: value => { 
            return this.filterCombobox(value, this.searchStat)
          }
        },
        {text: 'Recipie', align: 'center', sortable: false, filterable: false},
        {text: 'Description', align: 'center', value: 'description', filterable: false, width: '300px'}
      ],
      items: [],
      showStarbux: true,
      showGas: false,
      showMineral: false,
      openRow: null
    };
  },

  computed: {
    isLoading: function () {
      return !this.loaded;
    },
  },

  beforeMount: function () {
    this.getItems();
  },

  methods: {
    getItems: async function () {
      const response = await axios.get(this.itemsEndpoint);

      let items = []
      for (const itemId in response.data.data) {
        const item = response.data.data[itemId]
        item.id = Number(itemId)
        items.push(item)
      }

      items.forEach(item => {
        item.offers = item.prices
          ? Object.keys(item.prices).map(k => item.prices[k].count).reduce((c, s) => c + s)
          : 0

        if (item.enhancement === 'none') {
          item.hiddenBonus = item.bonus
          item.bonus = 0
        }
      })

      this.items = items
      this.updateFilters()

      this.loaded = true;

      return this.items
    },

    formatBonus(item) {
      if (item.enhancement !== 'none' && item.bonus) {
        return '+' + item.bonus
      }

      if (item.hiddenBonus) {
        return item.hiddenBonus
      }

      return ''
    },

    updateFilters() {
      this.stats = Array.from(new Set(this.items.map((item) => item.enhancement === 'none' ? 'None' : item.enhancement[0].toUpperCase() + item.enhancement.slice(1)))).sort()
      this.slots = Array.from(new Set(this.items.map((item) => !item.slot ? 'None' : item.slot))).sort()
      this.types = Array.from(new Set(this.items.map((item) => !item.type ? 'None' : item.type))).sort()
    },

    currencySprite (currency) {
      switch (currency) {
        case 'Starbux':
          return this.buxSprite()
        case 'Gas':
          return this.gasSprite()
        case 'Mineral':
          return this.mineralSprite()
        case 'Supply':
          return this.supplySprite()
        default:
          return ''
      }
    },

    priceFormat (price) {
      const formatFunc = function (x) {
        if (Math.max(price.p25, price.p50, price.p75) > 999999) {
          return parseFloat((x / 1000000).toFixed(1)) + 'M'
        } else if (Math.max(price.p25, price.p50, price.p75) > 999) {
          return parseFloat((x / 1000).toFixed(1)) + 'K'
        } else {
          return x.toFixed(0)
        }
      }

      let formatedPrice = formatFunc(price.p25) +
        ' - ' + '<b>' + formatFunc(price.p50) + '</b>' +
        ' - ' + formatFunc(price.p75)

      return formatedPrice
    },

    rowExpanded: async function (item) {
        // Fetch data if needed
        if (!this.items[item.id].priceHistory) {
          // TODO: Make the transform once then
          const response = await axios.get(this.itemPricesEndpoint(item.id))
          this.items[item.id].priceHistory = response.data.data.prices
        } else {
          await new Promise(resolve => setTimeout(resolve, 1))
        }

        this.openRow = item
        this.plotData(item)
    },

    updatePlot () {
      if (this.openRow) {
        this.plotData(this.openRow)
      }
    },

    plotData (item) {
      const h = this.items[item.id].priceHistory
      if (Object.keys(h).length > 0) {
        const series = {}
        const currency = []
        if (this.showStarbux) currency.push('Starbux')
        if (this.showGas) currency.push('Gas')
        if (this.showMineral) currency.push('Mineral')

        const cDetails = {
          Starbux: {color: '122,255,185', short: '$', side: 'left'},
          Gas: {color: '168,89,190', short: 'G', side: 'right'},
          Mineral: {color: '6,152,193', short: 'M', side: 'right'}
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
          title: `${item.name} prices`
        }

        if (this.showStarbux) {
          layout.yaxis = {
            domain: [0.3, 1],
            title: 'Starbux',
            gridcolor: '#222'
          }

          layout.yaxis3 = {title: 'Gas/Mineral', overlaying: 'y', side: 'right'}
        } else {
          layout.yaxis3 = {
            domain: [0.3, 1],
            title: 'Gas/Mineral',
            gridcolor: '#222'
          }
        }

        const options = {displayModeBar: false}
        plotly.newPlot(document.getElementById('chart-' + item.id), data, layout, options)
      }
    },
  },
};
</script>

<style scoped src="@/assets/css/common.css"></style>
<style scoped>
.rarity {
  text-transform: capitalize;
}

.name {
  font-weight: bold;
}

a.name {
  text-decoration: none;
}

.equip {
  font-size: 90%;
}
</style>