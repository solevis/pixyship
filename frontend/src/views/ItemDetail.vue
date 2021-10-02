<template>
  <v-card :loading="isLoading" class="full-height">
    <v-card-title v-if="!loaded"> Loading... </v-card-title>

    <!-- Item sprite -->
    <v-card-title v-if="loaded">
      <div class="mx-auto">
        <item :item="item" :tip="false" name="bottom" :disableLink="true" />
      </div>
    </v-card-title>

    <v-row justify="center" v-if="loaded">
      <v-col cols="8">
        <div class="text-center">
          <q class="font-italic">{{ item.description }}</q>
        </div>
      </v-col>
    </v-row>

    <!-- Large screen (Table and prestiges side by side) -->
    <template v-if="loaded && $vuetify.breakpoint.mdAndUp">
      <v-row justify="center">
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
                      <br />
                      {{ formatExtraBonus(item) }}
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
                          <div
                            class="block"
                            :style="currencySprite('Starbux')"
                          />
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
                          <td>
                            <div
                              class="block"
                              :style="currencySprite(currency)"
                            />
                          </td>
                          <td>
                            <div class="block" />
                            {{ prices.count }}
                          </td>
                          <td
                            class="text-xs-left"
                            v-html="priceFormat(prices, prices.p25)"
                          ></td>
                          <td
                            class="text-xs-left"
                            v-html="priceFormat(prices, prices.p50)"
                          ></td>
                          <td
                            class="text-xs-left"
                            v-html="priceFormat(prices, prices.p75)"
                          ></td>
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
    </template>

    <!-- Small screen (infos as card and expandable prestiges) -->
    <v-row v-else-if="loaded" justify="center">
      <v-col>
        <v-card v-if="loaded" outlined class="mx-3">
          <v-card-title>Details</v-card-title>
          <v-card-text>
            <span>Rarity: <span :class="['rarity', item.rarity]">{{ item.rarity }}</span></span><br>
            <span>Type: {{ item.type }}</span><br>
            <span>Subtype: {{ item.slot }}</span><br>
            <span v-if="formatBonus(item)">Bonus: {{ formatBonus(item) }}<template v-if="item.module_extra_disp_enhancement != null"> / {{ formatExtraBonus(item) }}</template></span><br>
            <div v-if="item.recipe.length > 0">Recipe: 
              <ul>
              <li v-for="(ingredient) in item.recipe"
                  :key="'item-cmp-' + item.id + '-recipe-' + ingredient.id"
                >
                  
                  <div class="d-inline-block middle mr-1">{{ ingredient.name }}</div>
                  <div class="d-inline-block middle mr-1" :style="spriteStyle(ingredient.sprite)"></div>
                  <div class="d-inline-block middle">x{{ ingredient.count }}</div>

              </li>
            </ul>
            </div>
            <div v-if="item.market_price">
              <div class="d-inline-block middle mr-1">Savy Price: {{ item.market_price }}</div>
              <div class="d-inline-block middle" :style="currencySprite('Starbux')"></div>
            </div>
            <div class="mb-2" v-if="item.prices">Market Prices (48h):</div>
            <table v-if="item.prices" class="market-table market-table-center">
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
                  <td>
                    <div
                      class="block"
                      :style="currencySprite(currency)"
                    />
                  </td>
                  <td>
                    <div class="block" />
                    {{ prices.count }}
                  </td>
                  <td
                    class="text-xs-left"
                    v-html="priceFormat(prices, prices.p25)"
                  ></td>
                  <td
                    class="text-xs-left"
                    v-html="priceFormat(prices, prices.p50)"
                  ></td>
                  <td
                    class="text-xs-left"
                    v-html="priceFormat(prices, prices.p75)"
                  ></td>
                </tr>
              </tbody>
            </table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row justify="center">
      <v-col cols="12" sm="8">
        <v-tabs v-if="loaded" grow v-model="model" class="mt-4">
          <v-tab v-if="$vuetify.breakpoint.mdAndUp" href="#tab-market"
            ><v-icon left>mdi-chart-histogram</v-icon>Market History</v-tab
          >
          <v-tab href="#tab-sales"
            ><v-icon left>mdi-sale</v-icon><span v-if="$vuetify.breakpoint.mdAndUp">Last Sales</span></v-tab
          >
          <v-tab href="#tab-craft"
            ><v-icon left>mdi-sitemap</v-icon><span v-if="$vuetify.breakpoint.mdAndUp">Craft</span></v-tab
          >
        </v-tabs>
      </v-col>
    </v-row>
    
    <v-row justify="center">
      <v-col cols="10">
        <v-tabs-items v-model="model">
          <v-tab-item value="tab-sales">
            <v-card flat>
              <v-row
                v-if="loaded && lastSales.length > 0"
                justify="center"
                :class="$vuetify.breakpoint.mdAndUp ? 'pt-4' : ''"
              >
                <v-switch
                  class="px-3"
                  v-model="showLastSalesGas"
                  label="Gas"
                  color="purple lighten-2"
                ></v-switch>
                <v-switch
                  class="px-3"
                  v-model="showLastSalesMineral"
                  :label="$vuetify.breakpoint.mdAndUp ? 'Mineral' : 'Min'"
                  color="blue lighten-2"
                  hide-details
                ></v-switch>
                <v-switch
                  class="px-3"
                  v-model="showLastSalesStarbux"
                  :label="$vuetify.breakpoint.mdAndUp ? 'Starbux' : 'Bux'"
                  color="green lighten-2"
                  hide-details
                ></v-switch>
              </v-row>

              <v-row v-if="loaded && lastSales.length > 0" justify="center">
                <v-col class="text-center" cols="12" md="8" >
                  <v-data-table
                    mobile-breakpoint="0"
                    :headers="$vuetify.breakpoint.mdAndUp ? lastSalesHeaders : lastSalesMobileHeaders"
                    :items="lastSales"
                    :items-per-page="20"
                    :sortDesc="true"
                    :footer-props="{
                      itemsPerPageOptions: [10, 20, 50, 100, 200, -1],
                    }"
                    multi-sort
                    class="elevation-1"
                  >
                    <template v-slot:item="{ item }">
                      <tr>
                        <td v-if="$vuetify.breakpoint.mdAndUp">{{ nowTime(item.date) }}</td>
                        <td>x{{ item.quantity }}</td>
                        <td>
                          <div
                            class="d-inline-block"
                            :style="currencySprite(item.currency)"
                          />
                        </td>
                        <td>{{ item.price }}</td>
                        <td>{{ item.buyer }}</td>
                        <td>{{ item.seller }}</td>
                      </tr>
                    </template>
                  </v-data-table>
                </v-col>
              </v-row>

              <v-row v-else class="pt-4">
                <v-col>
                  <div class="text-center">No data</div>
                </v-col>
              </v-row>
            </v-card>
          </v-tab-item>

          <v-tab-item value="tab-market" v-if="$vuetify.breakpoint.mdAndUp">
            <item-market :item="item" :showTitle="false" class="mt-4" />
          </v-tab-item>

          <v-tab-item value="tab-craft">
            <v-card flat>
              <v-col>
                <v-row
                  v-if="loaded && item.recipe.length > 0"
                  justify="center"
                  class="pt-4"
                >
                  <v-treeview
                    v-model="tree"
                    hoverable
                    activatable
                    item-key="name"
                    item-children="recipe"
                    open-on-click
                    class="px-5"
                    :items="item.recipe"
                  >
                    <template v-slot:label="{ item }">
                      <item
                        :item="item"
                        name="right"
                        :disableLink="true"
                        :count="item.count"
                      />
                    </template>
                  </v-treeview>
                </v-row>

                <v-row v-else class="pt-4">
                  <v-col>
                    <div class="text-center">This item cannot be crafted.</div>
                  </v-col>
                </v-row>
              </v-col>
            </v-card>
          </v-tab-item>
        </v-tabs-items>
      </v-col>
    </v-row>
  </v-card>
</template>

<script>
import axios from "axios";
import mixins from "@/mixins/PixyShip.vue.js";
import itemMixins from "@/mixins/Item.vue.js";
import Item from "@/components/Item.vue";
import ItemMarket from "@/components/ItemMarket.vue";

export default {
  mixins: [mixins, itemMixins],

  components: {
    Item,
    ItemMarket,
  },

  data() {
    return {
      model: "tab-detail",
      loaded: false,
      itemId: this.$route.params.id,
      item: {},
      lastSales: [],
      showLastSalesStarbux: true,
      showLastSalesGas: true,
      showLastSalesMineral: true,
      lastSalesHeaders: [
        {
          text: "Date",
          align: "center",
          value: "date",
          filterable: false,
        },
        {
          text: "Quantity",
          align: "center",
          value: "quantity",
          filterable: true,
        },
        {
          text: "Currency",
          align: "center",
          value: "currency",
          filter: (value) => {
            if (this.searchLastSalesCurrency.length > 0) {
              return this.searchLastSalesCurrency.includes(value);
            }

            return false;
          },
        },
        {
          text: "Price",
          align: "center",
          value: "price",
          filterable: false,
        },
        {
          text: "Buyer",
          align: "center",
          value: "buyer",
          filterable: false,
        },
        {
          text: "Seller",
          align: "center",
          value: "saller",
          filterable: false,
        },
      ],
      lastSalesMobileHeaders: [
        {
          text: "Quantity",
          align: "center",
          value: "quantity",
          filterable: true,
        },
        {
          text: "Currency",
          align: "center",
          value: "currency",
          filter: (value) => {
            if (this.searchLastSalesCurrency.length > 0) {
              return this.searchLastSalesCurrency.includes(value);
            }

            return false;
          },
        },
        {
          text: "Price",
          align: "center",
          value: "price",
          filterable: false,
        },
        {
          text: "Buyer",
          align: "center",
          value: "buyer",
          filterable: false,
        },
        {
          text: "Seller",
          align: "center",
          value: "saller",
          filterable: false,
        },
      ],
      tree: [],
      recipes: [],
    };
  },

  computed: {
    isLoading: function () {
      return !this.loaded;
    },

    searchLastSalesCurrency: function () {
      let currencies = [];

      if (this.showLastSalesGas) {
        currencies.push("Gas");
      }

      if (this.showLastSalesMineral) {
        currencies.push("Mineral");
      }

      if (this.showLastSalesStarbux) {
        currencies.push("Starbux");
      }

      return currencies;
    },
  },

  beforeMount: function () {
    this.getItem();
  },

  methods: {
    getItem: async function () {
      const response = await axios.get(this.itemDetailEndpoint(this.itemId));

      this.item = response.data.data;
      this.lastSales = response.data.lastSales;
      document.title = "PixyShip - " + this.item.name;
      this.loaded = true;
    },
  },
};
</script>

<style scoped src="@/assets/css/common.css"></style>
<style scoped>
.rarity {
  text-transform: capitalize;
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

.market-table-center {
  margin: 0 auto;
}

.middle {
  vertical-align: middle;
}
</style>