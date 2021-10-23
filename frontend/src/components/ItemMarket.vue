<template>
  <v-card flat>
    <v-row
      v-if="loaded && Object.keys(item.priceHistory).length > 0"
      justify="center"
    >
      <v-switch
        class="px-3"
        v-model="showGas"
        label="Gas"
        color="purple lighten-2"
        @click.native="updatePlot('chart-' + item.id, showTitle)"
      ></v-switch>
      <v-switch
        class="px-3"
        v-model="showMineral"
        label="Mineral"
        color="blue lighten-2"
        hide-details
        @click.native="updatePlot('chart-' + item.id, showTitle)"
      ></v-switch>
      <v-switch
        class="px-3"
        v-model="showStarbux"
        label="Starbux"
        color="green lighten-2"
        hide-details
        @click.native="updatePlot('chart-' + item.id, showTitle)"
      ></v-switch>
    </v-row>

    <v-row v-else-if="!item.saleable" class="pt-4">
      <v-col>
        <div class="text-center">This item cannot be sold.</div>
      </v-col>
    </v-row>

    <v-row v-else>
      <v-col>
        <div class="text-center">No data</div>
      </v-col>
    </v-row>

    <div :id="'chart-' + this.item.id" :key="'chart-' + this.item.id"></div>
  </v-card>
</template>

<script>
import axios from "axios"
import mixins from "@/mixins/PixyShip.vue.js"
import itemMixins from "@/mixins/Item.vue.js"
import _ from 'lodash'

export default {
  mixins: [mixins, itemMixins],

  props: {
    item: null,
    showTitle: {
      type: Boolean,
      default: true
    }
  },

  data() {
    return {
      loaded: false,
      priceHistory: {},
    }
  },

  computed: {
    isLoading: function () {
      return !this.loaded
    },
  },

  beforeMount: function () {
    this.getItemMarket()
  },

  beforeDestroy: function () {
    window.removeEventListener('resize', this.triggerResize)
  },

  mounted() {
    window.addEventListener('resize', this.triggerResize);
  },

  methods: {
    triggerResize: _.debounce(async function () {
      this.resizePlot(this.item)
    }, 250),

    getItemMarket: async function () {
      const response = await axios.get(this.itemPricesEndpoint(this.item.id))
      this.item.priceHistory = response.data.data.prices

      this.loaded = true
      this.initMarketChart()
    },

    initMarketChart: function () {
      if (this.charts.length > 0) {
        return
      }

      this.charts.push(this.item)
      this.plotData(this.item, null, this.showTitle)
    }
  }
}
</script>

<style scoped src="@/assets/css/common.css"></style>
