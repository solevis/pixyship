<template>
  <v-card :loading="isLoading" class="full-height">
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
      :expanded.sync="charts"
      :sortDesc="true"
      :footer-props="{
        itemsPerPageOptions: [10, 20, 50, 100, 200, -1],
      }"
      multi-sort
      loading-text="Loading..."
      class="elevation-1 px-3"
    >
      <template v-slot:item="{ item, expand, isExpanded }">
        <v-tooltip bottom color="blue-grey" :disabled="isExpanded || !item.market_price">
          <template v-slot:activator="{ on, attrs }">
        <tr @click="expand(!isExpanded)" v-bind="attrs" v-on="on">
          <!-- Image -->
          <td>
            <item :item="item" :tip="false"/>
          </td>

          <!-- Name -->
          <td>
            <div class="text-xs-left">
              <a
                :class="[item.rarity, 'lh-9', 'name']"
                :href="`/item/${item.id}`"
                >{{ item.name }}
              </a>
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
          <item-market :item="item" :showTitle="true" class="ma-3"/>
        </td>
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
import axios from "axios";
import mixins from "@/mixins/PixyShip.vue.js";
import itemMixins from "@/mixins/Item.vue.js";
import Item from "@/components/Item.vue";
import ItemMarket from '../components/ItemMarket.vue';

export default {
  mixins: [mixins, itemMixins],

  components: {
    Item,
    ItemMarket,
  },

  data() {
    return {
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
        { 
          text: "Order by ID", 
          align: "start",
          value: "id",           
          filterable: false 
        },
        { text: "Name", align: "center", value: "name", filterable: true },
        {
          text: "Rarity",
          align: "center",          
          value: "rarity",
          filter: (value) => {
            return this.filterCombobox(value, this.searchRarity);
          },
          sort: this.sortRarity,
        },
        {
          text: "Savy Price",
          align: "center",          
          value: "market_price",
          filterable: false,
        },
        {
          text: "Market Prices (48h)",
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

.bonus {
  min-width: 100px;
}

.recipe {
  min-width: 55px;
}
</style>