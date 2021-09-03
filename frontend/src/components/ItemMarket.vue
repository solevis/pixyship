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
        @click.native="updatePlot('item-chart', showTitle)"
      ></v-switch>
      <v-switch
        class="px-3"
        v-model="showMineral"
        label="Mineral"
        color="blue lighten-2"
        hide-details
        @click.native="updatePlot('item-chart', showTitle)"
      ></v-switch>
      <v-switch
        class="px-3"
        v-model="showStarbux"
        label="Starbux"
        color="green lighten-2"
        hide-details
        @click.native="updatePlot('item-chart', showTitle)"
      ></v-switch>
    </v-row>

    <v-row v-else>
      <v-col>
        <div class="text-center">No data</div>
      </v-col>
    </v-row>

    <div id="item-chart" key="item-chart"></div>
  </v-card>
</template>

<script>
import axios from "axios";
import mixins from "@/mixins/PixyShip.vue.js";
import itemMixins from "@/mixins/Item.vue.js";

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
      return !this.loaded;
    },
  },

  beforeMount: function () {
    this.getItemMarket();
  },

  methods: {
    getItemMarket: async function () {
      const response = await axios.get(this.itemPricesEndpoint(this.item.id));
      this.item.priceHistory = response.data.data.prices;

      this.loaded = true;
      this.initMarketChart()
    },

    initMarketChart: function () {
      if (this.charts.length > 0) {
        return
      }

      this.charts.push(this.item)
      this.plotData(this.item, "item-chart", this.showTitle)
    }
  }
}
</script>

<style scoped src="@/assets/css/common.css"></style>
<style scoped>
.item-chart {
  width: 100%;
}
</style>