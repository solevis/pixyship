<template>
  <v-card :loading="isLoading">
    <v-card-title class="overline">> Items </v-card-title>
    <v-card-subtitle>All Pixel Starships items and market history (click on a row to display more market data)</v-card-subtitle>

    <!-- Filters -->
    <v-card-subtitle v-if="loaded">
      <v-row>
        <v-col cols="12" sm="12" md="4">
          <v-text-field
            outlined
            v-model="searchName"
            append-icon="mdi-magnify"
            label='Name'
            hint='For example: "Sandbag", Barrier, -Energy'
            clearable
          ></v-text-field>
        </v-col>
        <v-col cols="12" sm="3" md="2">
          <v-autocomplete
            outlined
            v-model="searchRarity"
            :items="rarities"
            label="Rarity"
            clearable
            multiple
            small-chips
            hide-details
          ></v-autocomplete>
        </v-col>
        <v-col cols="12" sm="3" md="2">
          <v-autocomplete
            outlined
            v-model="searchType"
            :items="types"
            label="Type"
            clearable
            multiple
            small-chips
            hide-details
          ></v-autocomplete>
        </v-col>
        <v-col cols="12" sm="3" md="2">
          <v-autocomplete
            outlined
            v-model="searchSlot"
            :items="slots"
            label="Subtype"
            clearable
            multiple
            small-chips
            hide-details
          ></v-autocomplete>
        </v-col>
        <v-col cols="12" sm="3" md="2">
          <v-autocomplete
            outlined
            v-model="searchStat"
            :items="stats"
            label="Bonus"
            clearable
            multiple
            small-chips
            hide-details
          ></v-autocomplete>
        </v-col>
      </v-row>
    </v-card-subtitle>

    <!-- Table -->
    <v-data-table
      v-if="loaded"
      mobile-breakpoint="0"
      :headers="headers"
      :items="items"
      :search="searchName"
      :custom-filter="multipleFilterWithNegative"
      :items-per-page="20"
      :loading="isLoading"
      :single-expand="false"
      :expanded.sync="expanded"
      :sortDesc="true"
      :footer-props="{
        itemsPerPageOptions: [10, 20, 50, 100, 200, -1],
      }"
      multi-sort
      loading-text="Loading..."
      class="elevation-1 px-3"
      @item-expanded="rowExpanded"
    >
      <template v-slot:item="{ item, expand, isExpanded }">
        <v-tooltip bottom color="blue-grey" :disabled="isExpanded || !item.market_price">
          <template v-slot:activator="{ on, attrs }">
        <tr @click="expand(!isExpanded)" v-bind="attrs" v-on="on">
          <!-- Image -->
          <td>
            <div :style="spriteStyle(item.sprite)"></div>
          </td>

          <!-- Name -->
          <td>
            <div :class="[item.rarity, 'lh-9', 'name']">
              {{ item.name }}<br />
            </div>
          </td>

          <td>
            <div :class="['rarity', item.rarity]">{{ item.rarity }}</div>
          </td>

          <!-- Savy price -->
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

          <!-- Market price 48h -->
          <td class="market">
            <table>
              <tr
                v-for="(price, currency, ind) in item.prices"
                :key="'item' + item.id + '-price-' + ind"
                class="nobreak"
              >
                <td><div class="block" :style="currencySprite(currency)" /></td>
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
          <!-- <td class="text-xs-right">{{ formatBonus(item) }}</td> -->
          <td class="text-xs-left text-capitalize bonus">
            {{ formatBonus(item) }}
            <template v-if="item.module_extra_disp_enhancement != null">
              <br> {{ formatExtraBonus(item) }}
            </template>
          </td>

          <!-- Recipe -->
          <td class="recipe">
            <table>
              <tr
                v-for="ingredient in item.recipe"
                :key="'item' + item.id + '-recipe-' + ingredient.name"
                class="nobreak"
              >
                <td>
                  <v-tooltip bottom color="blue-grey">
                    <template v-slot:activator="{ on, attrs }">
                      <div
                        class="block"
                        v-bind="attrs"
                        v-on="on"
                        :style="spriteStyle(ingredient.sprite)"
                      ></div>
                    </template>
                    {{ ingredient.name }}
                  </v-tooltip>
                </td>
                <td>{{ ingredient.count }}</td>
              </tr>
            </table>
          </td>

          <!-- Description -->
          <td>
            {{ item.description }}
          </td>
        </tr>
        </template>
          <span>Click to display item market history</span>
        </v-tooltip>
      </template>

      <template v-slot:expanded-item="{ headers, item }">
        <td :colspan="headers.length" v-show="item.market_price" style="border-bottom: 10px solid #393939;">
          <v-container class="my-0 py-0">
            <v-layout justify-center>
              <v-switch
                class="px-3"
                v-model="showGas"
                label="Gas"
                color="purple lighten-2"
                @click.native="updatePlot"
              ></v-switch>
              <v-switch
                class="px-3"
                v-model="showMineral"
                label="Mineral"
                color="blue lighten-2"
                hide-details
                @click.native="updatePlot"
              ></v-switch>
              <v-switch
                class="px-3"
                v-model="showStarbux"
                label="Starbux"
                color="green lighten-2"
                hide-details
                @click.native="updatePlot"
              ></v-switch>
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
import plotly from "plotly.js-dist";

export default {
  mixins: [mixins],

  components: {},

  data() {
    return {
      expanded: [],
      searchName: "",
      searchRarity: [],
      searchSlot: [],
      searchType: [],
      searchStat: [],
      stats: [],
      slots: [],
      types: [],
      loaded: false,
      headers: [
        { text: "Image", align: "center", sortable: false, filterable: false },
        { text: "Name", align: "center", value: "name", filterable: true },
        {
          text: "Rarity",
          align: "center",          
          value: "rarity",
          filter: (value) => {
            return this.filterCombobox(value, this.searchRarity);
          },
        },
        {
          text: "Savy $",
          align: "center",          
          value: "market_price",
          filterable: false,
        },
        {
          text: "Market $ (48h) | # | 25 - 50 - 75%",
          align: "center",          
          value: "offers",
          filterable: false,
          width: 210,
        },
        {
          text: "Type",
          align: "center",          
          value: "type",
          sortable: false,
          filter: (value) => {
            return this.filterCombobox(value, this.searchType);
          },
        },
        {
          text: "Subtype",
          align: "center",          
          value: "slot",
          sortable: false,
          filter: (value) => {
            return this.filterCombobox(value, this.searchSlot);
          },
        },
        {
          text: "Bonus",
          align: "center",          
          value: "bonus",
          filter: (value, search, item) => {
            return this.filterCombobox(item.disp_enhancement, this.searchStat);
          },
        },
        {
          text: "Recipe",
          align: "center",          
          sortable: false,
          filterable: false,
        },
        {
          text: "Description",
          align: "center",          
          value: "description",
          filterable: false,
          sortable: false,
          width: "300px",
        },
      ],
      items: [],
      showStarbux: true,
      showGas: false,
      showMineral: false,
      openRow: null,
    };
  },

  computed: {
    isLoading: function () {
      return !this.loaded;
    },
  },

  created() {
    document.title = 'PixyShip - ' + this.$route.name
  },

  beforeMount: function () {
    this.getItems();
  },

  methods: {
    getItems: async function () {
      const response = await axios.get(this.itemsEndpoint);

      let items = [];
      for (const itemId in response.data.data) {
        const item = response.data.data[itemId];
        item.id = Number(itemId);
        items.push(item);
      }

      items.forEach((item) => {
        item.offers = item.prices
          ? Object.keys(item.prices)
              .map((k) => item.prices[k].count)
              .reduce((c, s) => c + s)
          : 0;

        if (item.disp_enhancement == null) {
          item.hiddenBonus = item.bonus;
          item.bonus = 0;
        }
      });

      items.sort((a, b) => b.offers - a.offers);

      this.items = items;
      this.updateFilters();

      this.loaded = true;

      return this.items;
    },

    formatBonus(item) {
      let formatedBonus = ""

      if (item.disp_enhancement != null && item.bonus) {
        formatedBonus = item.slot == 'Module' ? '' : '+'
        formatedBonus += item.bonus + " " + item.disp_enhancement
      } else if (item.hiddenBonus) {
        formatedBonus = item.hiddenBonus
      }

      return formatedBonus
    },

    formatExtraBonus(item) {
      let formatedBonus = ""

      if (item.module_extra_disp_enhancement != null && item.module_extra_enhancement_bonus) {
        formatedBonus = item.slot == 'Module' ? '' : '+'
        formatedBonus += item.module_extra_enhancement_bonus + " " + item.module_extra_disp_enhancement
      }

      return formatedBonus
    },

    updateFilters() {
      this.stats = Array.from(
        new Set(
          this.items.map((item) =>
            item.disp_enhancement == null
              ? "None"
              : item.disp_enhancement[0].toUpperCase() + item.disp_enhancement.slice(1)
          )
        )
      ).sort(this.sortAlphabeticallyExceptNone);

      this.slots = Array.from(
        new Set(this.items.map((item) => (!item.slot ? "None" : item.slot)))
      ).sort(this.sortAlphabeticallyExceptNone);

      this.types = Array.from(
        new Set(this.items.map((item) => (!item.type ? "None" : item.type)))
      ).sort(this.sortAlphabeticallyExceptNone);
      
      this.rarities = Array.from(
        new Set(
          this.items.map(
            (item) => item.rarity[0].toUpperCase() + item.rarity.slice(1)
          )
        )
      ).sort(this.sortRarity)
    },

    priceFormat(price) {
      const formatFunc = function (x) {
        if (Math.max(price.p25, price.p50, price.p75) > 999999) {
          return parseFloat((x / 1000000).toFixed(1)) + "M";
        } else if (Math.max(price.p25, price.p50, price.p75) > 999) {
          return parseFloat((x / 1000).toFixed(1)) + "K";
        } else {
          return x.toFixed(0);
        }
      };

      let formatedPrice =
        formatFunc(price.p25) +
        " - " +
        "<b>" +
        formatFunc(price.p50) +
        "</b>" +
        " - " +
        formatFunc(price.p75);

      return formatedPrice;
    },

    rowExpanded: async function (row) {
      let item = row.item;

      // fetch data if needed
      if ("priceHistory" in item) {
        await new Promise((resolve) => setTimeout(resolve, 1));
      } else {
        const response = await axios.get(this.itemPricesEndpoint(item.id));
        item.priceHistory = response.data.data.prices;
      }

      this.openRow = item;
      this.plotData(item);
    },

    updatePlot() {
      for (var i = 0; i < this.expanded.length; i++) {
        this.plotData(this.expanded[i]);
      }
    },

    plotData(item) {
      const history = item.priceHistory;

      if (Object.keys(history).length > 0) {
        const series = {};
        const currencies = [];

        if (this.showStarbux) currencies.push("Starbux");
        if (this.showGas) currencies.push("Gas");
        if (this.showMineral) currencies.push("Mineral");

        const currencyDetails = {
          Starbux: { color: "122,255,185", short: "$", side: "left" },
          Gas: { color: "168,89,190", short: "G", side: "right" },
          Mineral: { color: "6,152,193", short: "M", side: "right" },
        };

        // Get the data series indicated
        currencies.map((currency) => {
          if (currency in history) {
            series[currency] = {};
            series[currency].dates = Object.keys(history[currency]);
            series[currency].p25 = Object.entries(history[currency]).map(
              (e) => e[1].p25
            );
            series[currency].p50 = Object.entries(history[currency]).map(
              (e) => e[1].p50
            );
            series[currency].p75 = Object.entries(history[currency]).map(
              (e) => e[1].p75
            );
            series[currency].count = Object.entries(history[currency]).map(
              (e) => e[1].count
            );
          }
        });

        let data = [];
        currencies.map((currency) => {
          const line = {
            shape: "spline",
            color: "rgba(" + currencyDetails[currency].color + ",1)",
          };
          const bound = {
            shape: "spline",
            color: "rgba(" + currencyDetails[currency].color + ",0.3)",
          };
          const fill = "rgba(" + currencyDetails[currency].color + ",0.2)";

          if (currency in series) {
            let serie = series[currency];
            let currencyDetail = currencyDetails[currency];

            data.push({
              x: serie.dates,
              y: serie.count,
              type: "scatter",
              name: currencyDetail.short + " Vol",
              line: line,
              xaxis: "x",
              yaxis: "y2",
            });

            const p25 = {
              x: serie.dates,
              y: serie.p25,
              type: "scatter",
              name: currencyDetail.short + " 25%",
              line: bound,
            };

            const p75 = {
              x: serie.dates,
              y: serie.p75,
              type: "scatter",
              name: currencyDetail.short + " 75%",
              line: bound,
              fill: "tonextx",
              fillcolor: fill,
            };

            const p50 = {
              x: serie.dates,
              y: serie.p50,
              type: "scatter",
              name: currencyDetail.short + " 50%",
              line: line,
            };

            if (currencyDetail.side === "right") {
              p25.yaxis = "y3";
              p50.yaxis = "y3";
              p75.yaxis = "y3";
            }

            data.push(p25);
            data.push(p75);
            data.push(p50);
          }
        });

        let layout = {
          legend: { traceorder: "reversed" },
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
          title: `${item.name} prices`,
        };

        if (this.showStarbux) {
          layout.yaxis = {
            domain: [0.3, 1],
            title: "Starbux",
            gridcolor: "#9e9e9e47",
          };

          layout.yaxis3 = {
            title: "Gas/Mineral",
            overlaying: "y",
            side: "right",
          };
        } else {
          layout.yaxis3 = {
            domain: [0.3, 1],
            title: "Gas/Mineral",
            gridcolor: "#9e9e9e47",
          };
        }

        const options = { displayModeBar: false };
        plotly.newPlot(
          document.getElementById("chart-" + item.id),
          data,
          layout,
          options
        );
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

.market {
  min-width: 250px;
}

.bonus {
  min-width: 100px;
}

.recipe {
  min-width: 55px;
}
</style>