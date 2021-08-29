<template>
  <v-card :loading="isLoading">
    <v-card-title v-if="!loaded"> Loading... </v-card-title>

    <!-- Item sprite -->
    <v-card-title v-if="loaded">
      <div class="mx-auto">
        <item :item="item" :tip="false" name="bottom" />
      </div>
    </v-card-title>

    <v-row justify="center" v-if="loaded">
        <v-col cols="8">
          <div class="text-center">
            <q class="font-italic">{{ item.description }}</q>
          </div>
        </v-col>
    </v-row>

    <v-row v-if="loaded" justify="center">
      <v-col cols="8">
        <v-simple-table v-if="loaded" class="px-3">
          <template v-slot:default>
            <thead>
              <tr>
                <th class="text-left">Rarity</th>
                <th class="text-left">Type</th>
                <th class="text-left">Subtype</th>
                <th class="text-left">Bonus</th>
                <th class="text-left">Recipe</th>
                <th class="text-left">Savy Price</th>
                <th class="text-left">Market Prices (48h)</th>
              </tr>
            </thead>

            <tbody>
              <tr>
                <!-- Rarity -->
                <td>
                  <div :class="['rarity', item.rarity]">
                    {{ item.rarity }}
                  </div>
                </td>

                <!-- Type -->
                <td>{{ item.type }}</td>

                <!-- Subtype -->
                <td>{{ item.slot }}</td>

                <!-- Bonus -->
                <td>
                  {{ formatBonus(item) }}
                  <template v-if="item.module_extra_disp_enhancement != null">
                    <br> {{ formatExtraBonus(item) }}
                  </template>
                </td>

                <!-- Recipe -->
                <td>
                  <table v-if="item.recipe.length > 0">
                    <tr
                      v-for="ingredient in item.recipe"
                      :key="'item' + item.id + '-recipe-' + ingredient.id"
                      class="nobreak"
                    >
                      <td>
                        <item :item="ingredient" />
                      </td>
                      <td>x{{ ingredient.count }}</td>
                    </tr>
                  </table>
                </td>

                <!-- Savy Price -->
                <td>
                  <table v-show="item.market_price">
                    <tr>
                      <td>
                        <div class="block" :style="currencySprite('Starbux')" />
                      </td>
                      <td class="text-xs-left">{{ item.market_price }}</td>
                    </tr>
                  </table>
                </td>

                <!-- Market Prices -->
                <td>
                  <table v-if="item.prices" class="market-table">
                  <thead>
                    <tr>
                      <td class="text-center"></td>
                      <td class="text-center">#</td>
                      <td class="text-center">25%</td>
                      <td class="text-center">50%</td>
                      <td class="text-center">75%</td>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="(prices, currency, ind) in item.prices"
                      :key="'item' + item.id + '-price-' + ind"
                      class="nobreak"
                    >
                      <td><div class="block" :style="currencySprite(currency)" /></td>
                      <td><div class="block" />{{ prices.count }}</td>
                      <td class="text-xs-left" v-html="priceFormat(prices, prices.p25)"></td>
                      <td class="text-xs-left" v-html="priceFormat(prices, prices.p50)"></td>
                      <td class="text-xs-left" v-html="priceFormat(prices, prices.p75)"></td>
                    </tr>
                  </tbody>
                </table>
                </td>
              </tr>
            </tbody>
          </template>
        </v-simple-table>
      </v-col>
    </v-row>

    <v-row v-if="loaded && item.lastSales.length > 0" class="pt-4" justify="center">
        <v-col class="text-center" cols="8">
        <span class="text-h6">Last 10 sales</span>

        <v-simple-table class="px-3" dense>
          <template v-slot:default>
            <thead>
              <tr>
                <th class="text-center">Date</th>
                <th class="text-center">Quantity</th>
                <th class="text-center">Currency</th>
                <th class="text-center">Price</th>
                <th class="text-center">Buyer</th>
                <th class="text-center">Seller</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="sale in item.lastSales" :key="'sale-' + sale.id">
                <td>{{ nowTime(sale.date) }}</td>
                <td>x{{ sale.quantity }}</td>
                <td><div class="d-inline-block" :style="currencySprite(sale.currency)" /></td>
                <td>{{ sale.price }}</td>
                <td>{{ sale.buyer }}</td>
                <td>{{ sale.seller }}</td>
              </tr>
            </tbody>
          </template>
        </v-simple-table>
      </v-col>
    </v-row>

    <v-row v-if="loaded && Object.keys(item.priceHistory).length > 0" class="pt-4" justify="center">
      <v-col class="text-center">
        <span class="text-h6">Market history</span>
      </v-col>
    </v-row>

    <v-row v-if="loaded && Object.keys(item.priceHistory).length > 0" justify="center">
        <v-switch
          class="px-3"
          v-model="showGas"
          label="Gas"
          color="purple lighten-2"
          @click.native="updatePlot('item-chart', false)"
        ></v-switch>
        <v-switch
          class="px-3"
          v-model="showMineral"
          label="Mineral"
          color="blue lighten-2"
          hide-details
          @click.native="updatePlot('item-chart', false)"
        ></v-switch>
        <v-switch
          class="px-3"
          v-model="showStarbux"
          label="Starbux"
          color="green lighten-2"
          hide-details
          @click.native="updatePlot('item-chart', false)"
        ></v-switch>
    </v-row>

    <div id="item-chart"></div>
  </v-card>
</template>

<script>
import axios from "axios";
import mixins from "@/mixins/PixyShip.vue.js";
import itemMixins from "@/mixins/Item.vue.js";
import Item from "@/components/Item.vue";

export default {
  mixins: [mixins, itemMixins],

  components: {
    Item,
  },

  data() {
    return {
      loaded: false,
      itemId: this.$route.params.id,
      item: {},
    };
  },

  computed: {
    isLoading: function () {
      return !this.loaded;
    },
  },

  beforeMount: function () {
    this.getItem();
  },

  methods: {
    getItem: async function () {
      const response = await axios.get(this.itemDetailEndpoint(this.itemId));

      this.item = response.data.data;
      this.item.priceHistory = response.data.priceHistory.prices
      this.item.lastSales = response.data.lastSales
      document.title = 'PixyShip - ' + this.item.name

      this.loaded = true;

      this.charts.push(this.item)
      this.plotData(this.item, "item-chart", false)
    },
  }
}
</script>

<style scoped src="@/assets/css/common.css"></style>
<style scoped>
.rarity {
  text-transform: capitalize;
}

.item-chart {
  width: 100%;
}

.market-table {
  border-spacing: 0;
}

.market-table thead th {
  padding-right: 10px;
  padding-left: 10px;
  font-weight: bold;
}

.market-table tbody td {
  padding-right: 10px;
  padding-left: 10px;
  text-align: center;
}
</style>