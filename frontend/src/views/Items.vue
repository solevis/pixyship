<template>
  <v-card :loading="isLoading" class="full-height">
    <v-card-title class="overline">> Items </v-card-title>
    <v-card-subtitle>{{ viewDescription }}:
      <ul>
        <li>click on item name to see market history, last players sales and craft tree</li>
      </ul>
    </v-card-subtitle>

    <!-- Filters -->
    <v-card-subtitle v-if="loaded">
      <v-row>
        <v-col cols="12" sm="12" md="2">
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
            :value-comparator="filterValueComparator"
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
            :value-comparator="filterValueComparator"
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
            :value-comparator="filterValueComparator"
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
            :value-comparator="filterValueComparator"
          ></v-autocomplete>
        </v-col>
        <v-col cols="12" sm="3" md="2">
          <v-autocomplete
            outlined
            v-model="searchTraining"
            :items="trainings"
            label="Main % Training"
            clearable
            multiple
            small-chips
            hide-details
            :value-comparator="filterValueComparator"
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
      :footer-props="{
        itemsPerPageOptions: [10, 20, 50, 100, 200, -1],
      }"
      :sort-by.sync="globalSortBy"
      :sort-desc.sync="globalSortDesc"
      multi-sort
      loading-text="Loading..."
      class="elevation-1 px-3"
    >
      <template v-slot:item="{ item }">
        <v-tooltip bottom color="grey darken-3">
          <template v-slot:activator="{ on, attrs }">
            <tr v-bind="attrs" v-on="on">
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

              <!-- Content -->
              <td class="content pa-2">
                <template v-if="item.content.length > 0">
                  <template v-if="item.number_of_rewards > 0">
                    {{ item.number_of_rewards }} reward{{ item.number_of_rewards > 1 ? 's' : '' }} from:
                  </template>
                  <table style="margin: 0 auto;" class="mt-1">
                    <tr
                      v-for="(content_item, index) in item.content"
                      :key="'item' + item.id + '-content-' + content_item.id + '-' + index"
                      class="nobreak"
                    >
                      <td>
                        <crew v-if="content_item.type === 'character'" :char="content_item.data" />
                        <item v-else-if="content_item.type === 'item'" :item="content_item.data"/>

                        <template v-else-if="content_item.type === 'starbux'">
                          <div class="d-inline-block middle mr-1" :style="buxSprite()"></div>
                        </template>

                        <template v-else-if="content_item.type === 'points' || content_item.type === 'purchasePoints'">
                          <div class="d-inline-block middle mr-1" :style="doveSprite()"></div>
                        </template>

                        <template v-else-if="content_item.type === 'skin'">
                          <a :href="makeLink(content_item.type, content_item.id)">
                            <div class="d-inline-block middle mr-1" :style="spriteStyle(content_item.data.sprite)"></div>
                          </a>
                        </template>
                      </td>
                      <td>x{{ content_item.count }}</td>
                    </tr>
                  </table>
                </template>
              </td>
            </tr>
          </template>
          <span>{{ item.description }}</span>
        </v-tooltip>
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
import axios from "axios"
import PixyShipMixin from "../mixins/PixyShip.vue.js"
import DataTableMixin from "../mixins/DataTable.vue.js"
import ItemMixin from "../mixins/Item.vue.js"
import Item from "../components/Item.vue"
import Crew from "../components/Crew.vue"
import _ from 'lodash'

export default {
  mixins: [PixyShipMixin, ItemMixin, DataTableMixin],

  components: {
    Item,
    Crew,
  },

  data() {
    return {
      viewDescription: "All Pixel Starships items (bonus, recipe, content...) and market history",
      searchName: "",
      searchRarity: [],
      searchSlot: [],
      searchType: [],
      searchStat: [],
      searchTraining: [],
      stats: [],
      trainings: [],
      slots: [],
      types: [],
      loaded: false,
      items: [],
      headers: [
        { 
          text: "Order by ID", 
          align: "start",
          value: "id",           
          filter: value => {
            const query = this.$route.query

            // no parameters
            if (!query.ids || this.pendingFilter) {
              return true
            }

            let ids = []
            if (typeof query.ids === 'number') {
              ids.push(query.ids)
            } else {
               ids = query.ids.split(',').map(function(id) {
                return parseInt(id.trim())
              })
            }
            
            return ids.includes(value)
          } 
        },
        { 
          text: "Name", 
          align: "center", 
          value: "name", 
          filterable: true 
        },
        {
          text: "Rarity",
          align: "center",          
          value: "rarity",
          filter: (value) => {
            return this.filterCombobox(value, this.searchRarity)
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
          text: "Type/Subtype",
          align: "center",          
          value: "typesubtype",
          sortable: true,
          filter: (value, search, item) => {
            // both filters
            if ((this.searchSlot !== null && this.searchSlot.length > 0)
                && (this.searchType !== null && this.searchType.length > 0)) {
              return this.filterCombobox(item.type, this.searchType) && this.filterCombobox(item.slot, this.searchSlot)
            }

            // only slot
            if (this.searchType === null || this.searchType.length === 0) {
              return this.filterCombobox(item.slot, this.searchSlot)
            }

            // only type
            return this.filterCombobox(item.type, this.searchType)
          },
        },
        {
          text: "Bonus",
          align: "center",          
          value: "bonus",
          filter: (value, search, item) => {
            let searchValue = item.disp_enhancement
            if (item.disp_enhancement !== null) {
              searchValue = item.disp_enhancement + ',' + item.module_extra_disp_enhancement
            }

            return this.filterCombobox(searchValue, this.searchStat)
          },
        },
        {
          text: "Training",
          align: "center",          
          value: "mainTrainingStatValue",
          width: 175,
          filter: (value, search, item) => {
            // in all stats
            // let keys = Object.keys(item.training)
            // let filtered = keys.filter(function(key) {
            //   return item.training[key] != 0 ? key : null
            // });

            let filtered = []
            if (item.mainTrainingStat !== null) {
              filtered = [item.mainTrainingStat]
            }

            return this.filterCombobox(filtered, this.searchTraining)
          },
        },
        {
          text: "Recipe",
          align: "center",          
          value: "recipe",
          filterable: false,
          sort: (a, b) => {
            if (a.length > 0 && b.length > 0) {
              return 0
            }

            if (a.length > 0 && b.length === 0) {
              return 1
            }

            return -1
          },
        },
        {
          text: "Content",
          align: "center",
          value: "content",
          filterable: false,
          sort: (a, b) => {
            if (a.length > 0 && b.length > 0) {
              return 0
            }

            if (a.length > 0 && b.length === 0) {
              return 1
            }

            return -1
          },
        },
      ],
    }
  },

  computed: {
    isLoading: function () {
      return !this.loaded
    },
    pendingFilter: function () {
      return this.searchName 
        || this.searchRarity.length > 0
        || this.searchSlot.length > 0
        || this.searchType.length > 0
        || this.searchStat.length > 0
        || this.searchTraining.length > 0
    }
  },

  metaInfo () {
    return {
      title: this.$route.name,
      meta: [
        {
          vmid: 'google-title',
          itemprop: 'name',
          content: `PixyShip - ${this.$route.name}`
        },
        {
          vmid: 'og-title',
          property: 'og:title',
          content: `PixyShip - ${this.$route.name}`
        },
        {
          vmid: 'twitter-title',
          name: 'twitter:title',
          content: `PixyShip - ${this.$route.name}`
        },
        {
          vmid: 'description',
          name: 'description',
          content: this.viewDescription
        },
        {
          vmid: 'twitter-description',
          name: 'twitter:description',
          content: this.viewDescription
        },
        {
          vmid: 'og-description',
          property: 'og:description',
          content: this.viewDescription
        },
        {
          vmid: 'google-description',
          itemprop: 'description',
          content: this.viewDescription
        },
      ]
    }
  },

  beforeMount: function () {
    this.initFilters()
    this.getItems()
  },

  watch: {
    searchName: _.debounce(function(value){
      this.updateQueryFromFilter('name', value)
    }, 250),

    searchType(value) {
      this.updateQueryFromFilter('type', value)
    },

    searchSlot(value) {
      this.updateQueryFromFilter('subtype', value)
    },

    searchRarity(value) {
      this.updateQueryFromFilter('rarity', value)
    },

    searchStat(value) {
      this.updateQueryFromFilter('bonus', value)
    },

    searchTraining(value) {
      this.updateQueryFromFilter('training', value)
    }
  },

  methods: {
    initFilters() {
      this.searchName = this.$route.query.name

      if (this.$route.query.rarity) {
        this.searchRarity = this.$route.query.rarity.split(',').map(function(value) {
          return value.trim()
        })
      }

      if (this.$route.query.type) {
        this.searchType = this.$route.query.type.split(',').map(function(value) {
          return value.trim()
        })
      }

      if (this.$route.query.subtype) {
        this.searchSlot = this.$route.query.subtype.split(',').map(function(value) {
          return value.trim()
        })
      }

      if (this.$route.query.bonus) {
        this.searchStat = this.$route.query.bonus.split(',').map(function(value) {
          return value.trim()
        })
      }

      if (this.$route.query.training) {
        this.searchTraining = this.$route.query.training.split(',').map(function(value) {
          return value.trim()
        })
      }
    },

    getItems: async function () {
      const response = await axios.get(this.itemsEndpoint)

      let items = []
      for (const itemId in response.data.data) {
        const item = response.data.data[itemId]

        // filter Craft and Missile, they already are in Crafts page
        if (item.type !== 'Craft' && item.type !== 'Missile') {
          item.id = Number(itemId)
          items.push(item)
        }
      }

      items.forEach((item) => {
        item.offers = item.prices
          ? Object.keys(item.prices)
              .map((k) => item.prices[k].count)
              .reduce((c, s) => c + s)
          : 0

        if (item.disp_enhancement === null) {
          item.bonus = 0
        }

        item.mainTrainingStat = null
        item.mainTrainingStatValue = 0

        if(item.training != null) {
          let max = 0
          for (const trainingKey in item.training) {
            // ignore special fields
            if (["xp", 'fatigue', 'minimum_guarantee', 'id', 'sprite'].includes(trainingKey)) {
              continue
            }

            if (item.training[trainingKey] > max) {
              item.mainTrainingStat = trainingKey
              item.mainTrainingStatValue = item.training[trainingKey]
              max = item.training[trainingKey]
            }
          }
        }

        item.typesubtype = item.type + item.slot
      })

      items.sort((a, b) => b.offers - a.offers)
      this.items = items
      this.updateFilters()

      this.loaded = true

      return this.items
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
      ).sort(this.sortAlphabeticallyExceptNone)

      this.trainings = ["Ability", "Attack", "Engine", "HP", "Pilot", "Repair", "Science", "Stamina", "Weapon"].sort(this.sortAlphabeticallyExceptNone)

      this.slots = Array.from(
        new Set(this.items.map((item) => (!item.slot ? "None" : item.slot)))
      ).sort(this.sortAlphabeticallyExceptNone)

      this.types = Array.from(
        new Set(this.items.map((item) => (!item.type ? "None" : item.type)))
      ).sort(this.sortAlphabeticallyExceptNone)
      
      this.rarities = Array.from(
        new Set(
          this.items.map(
            (item) => item.rarity[0].toUpperCase() + item.rarity.slice(1)
          )
        )
      ).sort(this.sortRarity)
    },
  },
}
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
  text-decoration: underline;
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
  min-width: 110px;
}

.recipe {
  min-width: 55px;
}

.content {
  min-width: 55px;
}
</style>