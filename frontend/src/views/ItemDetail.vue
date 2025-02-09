<template>
  <v-card :loading="isLoading" class="full-height">
    <v-card-title v-if="!loaded"> Loading...</v-card-title>

    <!-- Item sprite -->
    <v-card-title v-if="loaded">
      <div class="mx-auto">
        <item :item="item" :tip="false" name="bottom" disableLink/>
        <sprites-button :object="item" type="item"/>
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
    <template v-if="loaded && display.mdAndUp.value">
      <v-row justify="center">
        <v-col cols="8">
          <v-simple-table v-if="loaded" class="px-3">
            <template v-slot:default>
              <thead>
              <tr>
                <th class="text-left">Rarity</th>
                <th class="text-left">Type/Subtype</th>
                <th class="text-left">Bonus</th>
                <th class="text-left">Training</th>
                <th class="text-left">Recipe</th>
                <th class="text-left">Content</th>
                <th class="text-left" v-if="item.requirement">Requirement</th>
                <th class="text-left">Item Space</th>
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
                <td>
                  {{ item.type }}<br>
                  {{ item.slot }}
                </td>

                <!-- Bonus -->
                <td class="text-xs-left text-capitalize bonus">
                  {{ formatBonus(item) }}
                  <template v-if="item.module_extra_disp_enhancement != null">
                    <br>{{ formatExtraBonus(item) }}
                  </template>
                  <template v-if="item.has_offstat">
                    <br>??&nbsp;+??
                  </template>
                </td>

                <!-- Training -->
                <td class="text-xs-left">
                  <ul v-if="item.training" class="pa-2">
                    <li v-if="item.training.xp != 0">
                      XP:&nbsp;{{ item.training.xp }}
                    </li>
                    <li v-if="item.training.fatigue">
                      Fatigue:&nbsp;{{
                        item.training.fatigue
                      }}
                    </li>

                    <li v-if="item.training.hp != 0">
                <span :class="item.training.hp === item.mainTrainingStatValue ? 'font-weight-bold' : ''">HP:&nbsp;<span>{{ item.training.hp === item.mainTrainingStatValue ? item.training.minimum_guarantee : 0 }}%&ndash;</span>{{
                    item.training.hp
                  }}%
                </span>
                    </li>
                    <li v-if="item.training.attack != 0">
                <span :class="item.training.attack === item.mainTrainingStatValue ? 'font-weight-bold' : ''">Attack:&nbsp;<span>{{ item.training.attack === item.mainTrainingStatValue ? item.training.minimum_guarantee : 0 }}%&ndash;</span>{{
                    item.training.attack
                  }}%
                </span>
                    </li>
                    <li v-if="item.training.repair != 0">
                <span :class="item.training.repair === item.mainTrainingStatValue ? 'font-weight-bold' : ''">Repair:&nbsp;<span>{{ item.training.repair === item.mainTrainingStatValue ? item.training.minimum_guarantee : 0 }}%&ndash;</span>{{
                    item.training.repair
                  }}%
                </span>
                    </li>
                    <li v-if="item.training.ability != 0">
                <span :class="item.training.ability === item.mainTrainingStatValue ? 'font-weight-bold' : ''">Ability:&nbsp;<span>{{ item.training.ability === item.mainTrainingStatValue ? item.training.minimum_guarantee : 0 }}%&ndash;</span>{{
                    item.training.ability
                  }}%
                </span>
                    </li>
                    <li v-if="item.training.stamina != 0">
                <span :class="item.training.stamina === item.mainTrainingStatValue ? 'font-weight-bold' : ''">Stamina:&nbsp;<span>{{ item.training.stamina === item.mainTrainingStatValue ? item.training.minimum_guarantee : 0 }}%&ndash;</span>{{
                    item.training.stamina
                  }}%
                </span>
                    </li>

                    <li v-if="item.training.pilot != 0">
                <span :class="item.training.pilot === item.mainTrainingStatValue ? 'font-weight-bold' : ''">Pilot:&nbsp;<span>{{ item.training.pilot === item.mainTrainingStatValue ? item.training.minimum_guarantee : 0 }}%&ndash;</span>{{
                    item.training.pilot
                  }}%
                </span>
                    </li>
                    <li v-if="item.training.science != 0">
                <span :class="item.training.science === item.mainTrainingStatValue ? 'font-weight-bold' : ''">Science:&nbsp;<span>{{ item.training.science === item.mainTrainingStatValue ? item.training.minimum_guarantee : 0 }}%&ndash;</span>{{
                    item.training.science
                  }}%
                </span>
                    </li>
                    <li v-if="item.training.engine != 0">
                <span :class="item.training.engine === item.mainTrainingStatValue ? 'font-weight-bold' : ''">Engine:&nbsp;<span>{{ item.training.engine === item.mainTrainingStatValue ? item.training.minimum_guarantee : 0 }}%&ndash;</span>{{
                    item.training.engine
                  }}%
                </span>
                    </li>
                    <li v-if="item.training.weapon != 0">
                <span :class="item.training.weapon === item.mainTrainingStatValue ? 'font-weight-bold' : ''">Weapon:&nbsp;<span>{{ item.training.weapon === item.mainTrainingStatValue ? item.training.minimum_guarantee : 0 }}%&ndash;</span>{{
                    item.training.weapon
                  }}%
                </span>
                    </li>
                  </ul>
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
                        <item :item="ingredient"/>
                      </td>
                      <td>x{{ ingredient.count }}</td>
                    </tr>
                  </table>
                </td>

                <!-- Content -->
                <td class="pa-2">
                  <template v-if="item.content.length > 0">
                    <template v-if="item.number_of_rewards > 0">
                    {{ item.number_of_rewards }} reward{{ item.number_of_rewards > 1 ? 's' : '' }} from:
                    </template>
                    <table style="margin: 0 auto;" class="mt-1">
                      <tr
                          v-for="(content_item, index) in item.content"
                          :key="'item' + item.id + '-content-' + index"
                          class="nobreak"
                      >
                        <td>
                          <crew v-if="content_item.type === 'character'" :char="content_item.data"/>
                          <item v-else-if="content_item.type === 'item'" :item="content_item.data"/>

                          <template v-else-if="content_item.type === 'starbux'">
                            <div class="d-inline-block middle mr-1" :style="buxSprite()"></div>
                          </template>

                          <template v-else-if="content_item.type === 'points' || content_item.type === 'purchasePoints'">
                            <div class="d-inline-block middle mr-1" :style="doveSprite()"></div>
                          </template>

                          <template v-else-if="content_item.type === 'skin'">
                            <a :href="makeLink(content_item.type, content_item.id)">
                              <div v-if="content_item.data.sprite" class="d-inline-block middle mr-1" :style="spriteStyle(content_item.data.sprite)"></div>
                              <template v-else>Skin</template>
                            </a>
                          </template>
                        </td>
                        <td>x{{ content_item.count }}</td>
                      </tr>
                    </table>
                  </template>
                </td>

                <!-- Requirement -->
                <td v-if="item.requirement">
                  {{ item.requirement }}
                </td>

                <!-- Item Space -->
                <td>
                  {{ item.item_space }}
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
                        <div class="block"/>
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

    <!-- Small screen (infos as card) -->
    <v-row v-else-if="loaded" justify="center">
      <v-col>
        <v-card v-if="loaded" outlined class="mx-3">
          <v-card-title>Details</v-card-title>
          <v-card-text>
            <span>Rarity: <span :class="['rarity', item.rarity]">{{ item.rarity }}</span></span><br>
            <span>Type/Subtype: {{ item.type }}/{{ item.slot }}</span><br>
            <template v-if="formatBonus(item)">
              <span>Bonus: {{ formatBonus(item) }}<template v-if="item.module_extra_disp_enhancement != null"> / {{ formatExtraBonus(item) }}</template><template v-if="item.has_offstat">&nbsp;/&nbsp;??&nbsp;+??</template></span><br>
            </template>

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

            <div v-if="item.content.length > 0">Content:
              <ul>
                <li v-for="(content_item, index) in item.content"
                    :key="'item-cmp-' + item.id + '-content-' + index"
                >

                  <template v-if="content_item.type === 'character'">
                    <crew :char="content_item.data" name="right" :count="content_item.count"/>
                    <div style="clear: both"></div>
                  </template>

                  <template v-else-if="content_item.type === 'item'">
                    <div class="d-inline-block middle mr-1">{{ content_item.data.name }}</div>
                    <div class="d-inline-block middle mr-1" :style="spriteStyle(content_item.data.sprite)"></div>
                    <div class="d-inline-block middle">x{{ content_item.count }}</div>
                  </template>

                  <template v-else-if="content_item.type === 'starbux'">
                    <div class="d-inline-block middle mr-1" :style="buxSprite()"></div>
                    <div class="d-inline-block middle">x{{ content_item.count }}</div>
                  </template>

                  <template v-else-if="content_item.type === 'points' || content_item.type === 'purchasePoints'">
                    <div class="d-inline-block middle mr-1" :style="doveSprite()"></div>
                    <div class="d-inline-block middle">x{{ content_item.count }}</div>
                  </template>

                  <template v-else-if="content_item.type === 'skin'">
                    <div v-if="content_item.data.sprite" class="d-inline-block middle mr-1" :style="spriteStyle(content_item.data.sprite)"></div>
                    <template v-else>Skin</template>
                    <div class="d-inline-block middle">x{{ content_item.count }}</div>
                  </template>
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
                  <div class="block"/>
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

    <v-row v-if="loaded" justify="center">
      <v-col cols="12" sm="8">
        <v-tabs v-if="loaded" grow show-arrows center-active v-model="activeTab" class="mt-4">
          <v-tab href="#tab-market"
          >
            <v-icon left>mdi-chart-histogram</v-icon>
            <span v-if="display.mdAndUp.value">Market History</span></v-tab
          >
          <v-tab href="#tab-last-sales"
          >
            <v-icon left>mdi-history</v-icon>
            <span v-if="display.mdAndUp.value">Last sales</span></v-tab
          >
          <v-tab href="#tab-players-sales"
          >
            <v-icon left>mdi-sale</v-icon>
            <span v-if="display.mdAndUp.value">Last players sales</span></v-tab
          >
          <v-tab href="#tab-craft"
          >
            <v-icon left>mdi-sitemap</v-icon>
            <span v-if="display.mdAndUp.value">Craft tree</span></v-tab
          >
          <v-tab href="#tab-upgrades"
          >
            <v-icon left>mdi-rice</v-icon>
            <span v-if="display.mdAndUp.value">Upgrades</span></v-tab
          >
        </v-tabs>
      </v-col>
    </v-row>

    <v-row v-if="loaded" justify="center">
      <v-col cols="12">
        <v-tabs-items v-model="activeTab" touchless>
          <v-tab-item value="tab-players-sales">
            <v-card flat>
              <v-row v-if="loaded && lastPlayersSales.length > 0" justify="center" :class="display.mdAndUp.value ? 'pt-4' : ''">
                <v-col class="text-center" cols="12" md="3">
                  <v-text-field
                      v-model="lastPlayersSalesSearch"
                      append-icon="mdi-magnify"
                      label="Search player name"
                      placeholder="Player name"
                      single-line
                      hide-details
                      dense
                  ></v-text-field>
                </v-col>

                <v-col cols="12" md="2">
                  <v-autocomplete
                    v-model="lastPlayersSalesOffstatSearch"
                    :items="lastPlayersSalesOffstats"
                    label="Offstat"
                    clearable
                    outlined
                    multiple
                    small-chips
                    hide-details
                    dense
                    :value-comparator="filterValueComparator"
                  ></v-autocomplete>
                </v-col>

                <v-col cols="12" md="2">
                  <v-autocomplete
                    v-model="lastPlayersSalesCurrencySearch"
                    :items="lastPlayersSalesCurrencies"
                    label="Currency"
                    clearable
                    outlined
                    multiple
                    small-chips
                    hide-details
                    dense
                    :value-comparator="filterValueComparator"
                  ></v-autocomplete>
                </v-col>
              </v-row>

              <v-row v-if="loaded && lastPlayersSales.length > 0" justify="center">
                <v-col class="text-center" cols="12" md="8">
                  <v-data-table
                      mobile-breakpoint="0"
                      :headers="display.mdAndUp.value ? lastPlayersSalesHeaders : lastPlayersSalesMobileHeaders"
                      :items="lastPlayersSales"
                      :items-per-page="20"
                      :footer-props="{
                      itemsPerPageOptions: [10, 20, 50, 100, 200, -1],
                    }"
                      multi-sort
                      class="elevation-1"
                      :search="lastPlayersSalesSearch"
                  >
                    <template v-slot:item="{ item }">
                      <tr>
                        <td v-if="display.mdAndUp.value">{{ nowTime(item.date) }}</td>
                        <td>x{{ item.quantity }}</td>
                        <td>
                          <div
                              class="d-inline-block"
                              :style="currencySprite(item.currency)"
                          />
                        </td>
                        <td>
                          <span>{{ item.price }}</span>
                        </td>
                        <td>
                          <span v-if="item.offstat" class="font-weight-light">
                            <span :title="item.offstat.bonus">+{{ item.offstat.value }} {{ item.offstat.short_bonus }}</span>
                          </span>
                        </td>
                        <td>{{ item.buyer }}</td>
                        <td>{{ item.seller }}</td>
                      </tr>
                    </template>
                  </v-data-table>
                </v-col>
              </v-row>

              <v-row v-if="loaded && lastPlayersSales.length > 0 && item.rarity_order >= 5" justify="center">
                <v-col class="" cols="12" md="8">
                  <p class="font-weight-light">
                    <span class="font-weight-bold">Offstats are still a feature in development.</span><br>
                    <span>Pixel Starships API doesn't permit to retrieve offstats after the item was sold. PixyShip tries to store offstats before the item is sold, but the market may updated too quickly and PixyShip won't be able to save the offstat before the sale (for example: sniped items, swaps).</span>
                  </p>
                </v-col>
              </v-row>

              <v-row v-else-if="!item.saleable" class="pt-4">
                <v-col>
                  <div class="text-center">This item cannot be sold.</div>
                </v-col>
              </v-row>

              <v-row v-else class="pt-4">
                <v-col>
                  <div class="text-center">No data</div>
                </v-col>
              </v-row>
            </v-card>
          </v-tab-item>

          <v-tab-item value="tab-market">
            <item-market :item="item" :showTitle="false" class="mt-4"/>
          </v-tab-item>

          <v-tab-item value="tab-last-sales">
            <v-card flat>
              <v-row justify="center">
                <v-col class="text-center" cols="12" md="8">
                  <last-sales type="item" :type-id="item.id"></last-sales>
                </v-col>
              </v-row>
            </v-card>
          </v-tab-item>

          <v-tab-item value="tab-craft">
            <v-card flat>
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
                        disableLink
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
            </v-card>
          </v-tab-item>

          <v-tab-item value="tab-upgrades">
            <v-card flat>

              <v-row
                  v-if="loaded && upgrades.length > 0"
                  justify="center"
                  class="pt-4"
              >
                <v-col cols="7">
                  <v-chip-group
                      column
                      max="0"
                  >
                    <v-chip
                        v-for="upgrade in upgrades" :key="upgrade.id"
                        link
                        outlined
                        :to="{ name: 'ItemDetail', params: { id: upgrade.id }}"
                    >
                      <item :item="upgrade" name="right" disable-link="true"></item>
                    </v-chip>
                  </v-chip-group>
                </v-col>
              </v-row>

              <v-row v-else class="pt-4">
                <v-col>
                  <div class="text-center">This item cannot be upgraded.</div>
                </v-col>
              </v-row>
            </v-card>
          </v-tab-item>
        </v-tabs-items>
      </v-col>
    </v-row>
  </v-card>
</template>

<script>
import axios from "axios"
import PixyShipMixin from "../mixins/PixyShip.vue.js"
import DataTableMixin from "../mixins/DataTable.vue.js"
import ItemMixin from "../mixins/Item.vue.js"
import Item from "../components/Item.vue"
import Crew from "../components/Crew.vue"
import ItemMarket from "../components/ItemMarket.vue"
import LastSales from "../components/LastSales";
import SpritesButton from "@/components/SpritesButton";
import _ from "lodash";
import {useHead} from "@vueuse/head"
import {useDisplay} from "vuetify"

export default {
  mixins: [PixyShipMixin, ItemMixin, DataTableMixin],

  components: {
    Item,
    ItemMarket,
    Crew,
    LastSales,
    SpritesButton,
  },

  data() {
    return {
      display: useDisplay(),
      activeTab: "tab-detail",
      loaded: false,
      itemId: this.$route.params.id,
      item: {},
      lastPlayersSales: [],
      upgrades: [],
      tree: [],
      recipes: [],
      lastPlayersSalesSearch: '',
      lastPlayersSalesOffstatSearch: [],
      lastPlayersSalesOffstats: [],
      lastPlayersSalesCurrencySearch: [],
      lastPlayersSalesCurrencies: [],
      lastPlayersSalesHeaders: [
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
          filterable: false,
        },
        {
          text: "Currency",
          align: "center",
          value: "currency",
          filter: (value) => {
            return this.filterCombobox(value, this.lastPlayersSalesCurrencySearch)
          },
        },
        {
          text: "Price",
          align: "center",
          value: "price",
          filterable: false
        },
        {
          text: "Offstat",
          align: "center",
          value: "offstat.value",
          filter: (value, search, item) => {
            let filtered = null;
            if (item.offstat !== null) {
              filtered = item.offstat.short_bonus
            }

            return this.filterCombobox(filtered, this.lastPlayersSalesOffstatSearch)
          },
        },
        {
          text: "Buyer",
          align: "center",
          value: "buyer",
          filterable: true,
        },
        {
          text: "Seller",
          align: "center",
          value: "seller",
          filterable: true,
        },
      ],
      lastPlayersSalesMobileHeaders: [
        {
          text: "Quantity",
          align: "center",
          value: "quantity",
          filterable: false,
        },
        {
          text: "Currency",
          align: "center",
          value: "currency",
          filter: (value) => {
            return this.filterCombobox(value, this.lastPlayersSalesCurrencySearch)
          },
        },
        {
          text: "Price",
          align: "center",
          value: "price",
          filterable: false
        },
        {
          text: "Offstat",
          align: "center",
          value: "offstat.value",
          filter: (value, search, item) => {
            let filtered = null;
            if (item.offstat !== null) {
              filtered = item.offstat.short_bonus
            }

            return this.filterCombobox(filtered, this.lastPlayersSalesOffstatSearch)
          },
        },
        {
          text: "Buyer",
          align: "center",
          value: "buyer",
          filterable: true,
        },
        {
          text: "Seller",
          align: "center",
          value: "seller",
          filterable: true,
        },
      ],
    }
  },

  computed: {
    isLoading: function () {
      return !this.loaded
    },
  },

  beforeMount: function () {
    this.getItem()
  },

  mounted: function () {
    useHead({
      title: this.item.name,
      meta: [
        {
          itemprop: 'name',
          content: `PixyShip - ${this.$route.name}`
        },
        {
          property: 'og:title',
          content: `PixyShip - ${this.$route.name}`
        },
        {
          name: 'twitter:title',
          content: `PixyShip - ${this.$route.name}`
        },
        {
          name: 'description',
          content: this.viewDescription
        },
        {
          name: 'twitter:description',
          content: this.viewDescription
        },
        {
          property: 'og:description',
          content: this.viewDescription
        },
        {
          itemprop: 'description',
          content: this.viewDescription
        }
      ]
    })
    if (this.$route.query.activeTab) {
      this.activeTab = this.$route.query.activeTab.trim();
    }
  },

  methods: {
    getItem: async function () {
      const response = await axios.get(this.itemDetailEndpoint(this.itemId))

      this.item = response.data.data

      this.item.mainTrainingStat = null
      this.item.mainTrainingStatValue = 0

      if (this.item.training != null) {
        let max = 0
        for (const trainingKey in this.item.training) {
          // ignore special fields
          if (["xp", 'fatigue', 'minimum_guarantee', 'id', 'sprite'].includes(trainingKey)) {
            continue
          }

          if (this.item.training[trainingKey] > max) {
            this.item.mainTrainingStat = trainingKey
            this.item.mainTrainingStatValue = this.item.training[trainingKey]
            max = this.item.training[trainingKey]
          }
        }
      }

      this.lastPlayersSales = response.data.lastPlayersSales
      await this.updateLastPlayersSalesFilters()

      this.upgrades = response.data.upgrades

      this.loaded = true
    },

    updateLastPlayersSalesFilters: async function () {
      this.lastPlayersSalesOffstats = this.itemStats
      this.lastPlayersSalesOffstats.push('None')
      this.lastPlayersSalesOffstats.sort(this.sortAlphabeticallyExceptNone)

      this.lastPlayersSalesCurrencies = this.currencies
      this.lastPlayersSalesCurrencies.sort(this.sortAlphabeticallyExceptNone)
    }
  },

  watch: {
    activeTab(value) {
      let searchParams = new URLSearchParams(window.location.search)

      // no need to append activeTab to URL on default one or empty value
      if (_.isEmpty(value) || value === 'tab-market') {
        searchParams.delete('activeTab')
      } else {
        searchParams.set('activeTab', value)
      }

      let queryString = searchParams.toString()
      if (queryString) {
        queryString = '?' + queryString
      }

      if (window.location.search !== queryString) {
        window.history.pushState('', '', this.$route.path + queryString)
      }
    }
  }

}
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
