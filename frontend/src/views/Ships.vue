<template>
  <v-card :loading="isLoading" class="full-height">
    <v-card-title class="overline">> Ships </v-card-title>
    <v-card-subtitle>{{ viewDescription }} (click on a row to see interior and exterior)</v-card-subtitle>

    <!-- Filters -->
    <v-card-subtitle v-if="loaded">
      <v-row>
        <v-col cols="12" sm="12" md="6">
          <v-text-field
            v-model="searchName"
            append-icon="mdi-magnify"
            label='Name'
            hint='For example: "Starship", Cluck, -Extended'
            clearable
            outlined
          ></v-text-field>
        </v-col>
        <v-col cols="12" sm="4" md="2">
          <v-autocomplete
            v-model="searchLevel"
            :items="levels"
            label="Level"
            clearable
            outlined
            multiple
            small-chips
            hide-details
            :value-comparator="filterValueComparator"
          ></v-autocomplete>
        </v-col>
        <v-col cols="12" sm="4" md="2">
          <v-autocomplete
            v-model="searchExtended"
            :items="['Yes', 'No']"
            label="Extended"
            clearable
            outlined
            small-chips
            hide-details
            :value-comparator="filterValueComparator"
          ></v-autocomplete>
        </v-col>
        <v-col cols="12" sm="4" md="2">
          <v-autocomplete
            v-model="searchType"
            :items="types"
            label="Type"
            clearable
            outlined
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
      :items="ships"
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
      <template v-slot:item="{ item, expand, isExpanded }">
        <v-tooltip bottom color="blue-grey" :disabled="isExpanded">
          <template v-slot:activator="{ on, attrs }">
            <tr @click="expand(!isExpanded)" v-bind="attrs" v-on="on">
              <!-- Image -->
              <td>
                <div :style="spriteStyle(item.mini_ship_sprite)"></div>
              </td>

              <!-- Name -->
              <td>
                <div :class="[item.rarity, 'lh-9', 'name']">
                  {{ item.name }}<br />
                </div>
              </td>

              <td class="text-xs-right">{{ item.level }}</td>
              <td class="text-xs-right">{{ item.space }}</td>
              <td class="text-xs-right">{{ item.spaceT1 }}</td>
              <td class="text-xs-right">{{ item.spaceT2 }}</td>
              <td class="text-xs-center">{{ item.extended ? 'Yes' : 'No' }}</td>
              <td class="text-xs-right">{{ item.hp }}</td>

              <td class="text-xs-right">{{ item.full_repair_time }}</td>

              <td style="min-width: 100px">
                <table>
                  <tr v-if="item.mineral_cost > 0" class="nobreak">
                    <td>
                      <div :style="mineralSprite()" />
                    </td>
                    <td>{{ item.mineral_cost }}</td>
                  </tr>

                  <tr v-if="item.starbux_cost > 0" class="nobreak">
                    <td>
                      <div :style="buxSprite()" />
                    </td>
                    <td>{{ item.starbux_cost }}</td>
                  </tr>

                  <tr v-if="item.points_cost > 0" class="nobreak">
                    <td>
                      <div :style="doveSprite()" />
                    </td>
                    <td>{{ item.points_cost }}</td>
                  </tr>
                </table>

                <item v-for="cost in item.items_cost" :key="item.id + '-' + cost.id" :item="cost" name="right" />
              </td>

              <td style="min-width: 100px">
                <table>
                  <tr v-if="item.mineral_capacity > 0" class="nobreak">
                    <td>
                      <div :style="mineralSprite()" />
                    </td>
                    <td>{{ item.mineral_capacity }}</td>
                  </tr>
                  <tr v-if="item.gas_capacity > 0" class="nobreak">
                    <td>
                      <div :style="gasSprite()" />
                    </td>
                    <td>{{ item.gas_capacity }}</td>
                  </tr>
                  <tr v-if="item.equipment_capacity > 0" class="nobreak">
                    <td>
                      <div :style="supplySprite()" />
                    </td>
                    <td>{{ item.equipment_capacity }}</td>
                  </tr>
                </table>
              </td>
              <td class="text-xs-left">{{ item.ship_type }}</td>
              <td class="text-xs-left">{{ item.description }}</td>
            </tr>
          </template>
          <span>Click to display more infos</span>
        </v-tooltip>
      </template>

      <template v-slot:expanded-item="{ headers, item }">
        <td :colspan="headers.length" align="center" >
          <v-card>
            <v-row class="ma-2">
              <v-col cols="12" sm="6">
                <v-card
                    elevation="3"
                    outlined
                    shaped
                  >

                  <v-card-subtitle>
                    <div class="overline">
                      INTERIOR
                    </div>
                  </v-card-subtitle>

                  <svg class="mb-5" :height="item.interior_sprite.height * getShipScalingRatio(item)" :width="item.interior_sprite.width * getShipScalingRatio(item) ">
                    <!-- Ship interior -->
                    <image 
                      :xlink:href="getSpriteUrl(item.interior_sprite)" 
                      x="0" y="0" 
                      :height="item.interior_sprite.height * getShipScalingRatio(item)" 
                      :width="item.interior_sprite.width * getShipScalingRatio(item)" 
                    />

                    <!-- Ship Grid -->
                    <template v-for="r in item.rows" >
                      <template v-for="c in item.columns" >
                        <rect 
                          :key="'grid-' + r + '-' + c"
                          v-if="item.mask[item.columns * (r-1) + (c-1)] === '1'" 
                          :x="(25 * getShipScalingRatio(item)) * c - (25 * getShipScalingRatio(item))" 
                          :y="(25 * getShipScalingRatio(item)) * r - (25 * getShipScalingRatio(item))"
                          :width="25 * getShipScalingRatio(item)" 
                          :height="25 * getShipScalingRatio(item)" 
                          stroke="#fff" fill="#0004">
                        </rect>
                      </template>
                    </template>

                    <template v-for="r in item.rows" >
                      <template v-for="c in item.columns" >
                        <rect 
                          :key="'grid-' + r + '-' + c"
                          v-if="item.mask[item.columns * (r-1) + (c-1)] === '2'" 
                          :x="(25 * getShipScalingRatio(item)) * c - (25 * getShipScalingRatio(item))" 
                          :y="(25 * getShipScalingRatio(item)) * r - (25 * getShipScalingRatio(item))"
                          :width="25 * getShipScalingRatio(item)" 
                          :height="25 * getShipScalingRatio(item)" 
                          stroke="#ff8000" fill="#0004">
                        </rect>
                      </template>
                    </template>
                  </svg>
                </v-card>
              </v-col>
              <v-col cols="12" sm="6">
                <v-card
                    elevation="3"
                    outlined
                    shaped
                  >

                  <v-card-subtitle>
                    <div class="overline">
                      EXTERIOR
                    </div>
                  </v-card-subtitle>

                  <svg class="mb-5" :height="item.exterior_sprite.height * getShipScalingRatio(item)" :width="item.exterior_sprite.width * getShipScalingRatio(item) ">
                    <!-- Ship interior -->
                    <image 
                      :xlink:href="getSpriteUrl(item.exterior_sprite)" 
                      x="0" y="0" 
                      :height="item.exterior_sprite.height * getShipScalingRatio(item)" 
                      :width="item.exterior_sprite.width * getShipScalingRatio(item)" 
                    />
                  </svg>
                </v-card>
              </v-col>
            </v-row>

            <v-row class="mx-2" v-if="item.requirements">
              <v-col cols="12">
                <v-card
                    elevation="3"
                    outlined
                    shaped
                  >

                  <v-card-subtitle>
                    <div class="overline">
                      Requirements
                    </div>
                  </v-card-subtitle>

                  <div class="px-4 pb-2">
                    <v-chip-group
                        column
                        max="0"
                        class="ma2"
                    >
                      <v-chip
                          v-for="requirement in item.requirements" :key="requirement.object.id"
                          link
                          outlined
                          :to="{ name: 'Rooms', query: { ids: requirement.object.id }}"
                      >
                        x{{ requirement.count }} {{ requirement.object.name }}
                      </v-chip>
                    </v-chip-group>
                  </div>
                </v-card>
              </v-col>
            </v-row>

            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="primary" text @click="openShipInBuilder(item.id)">Open in Builder</v-btn>
              <v-spacer></v-spacer>
            </v-card-actions>
          </v-card>
        </td>
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
import axios from "axios"
import PixyShipMixin from "../mixins/PixyShip.vue.js"
import DataTableMixin from "../mixins/DataTable.vue.js"
import Item from "../components/Item.vue"
import "../assets/css/override.css"
import _ from 'lodash'

export default {
  mixins: [PixyShipMixin, DataTableMixin],

  components: {
    Item,
  },

  data() {
    return {
      viewDescription: "All ships infos (sprite, type, requirement, spaces, HP...) of Pixel Starships",
      searchName: "",
      searchLevel: [],
      searchType: [],
      searchExtended: null,
      levels: [],
      types: [],
      loaded: false,
      rooms: [],
      headers: [
        { 
          text: "Order by ID", 
          align: "center", 
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
          text: "Level", 
          align: "right", 
          value: "level", 
          filter: (value) => {
            return this.filterCombobox(value.toString(), this.searchLevel)
          },
        },
        { 
          text: "Space", 
          align: "right", 
          value: "space", 
          filterable: false
        },
        { 
          text: "T1", 
          align: "right", 
          value: "spaceT1", 
          filterable: false 
        },
        { 
          text: "T2", 
          align: "right", 
          value: "spaceT2", 
          filterable: false 
        },
        {
          text: "Extended",
          align: "right",
          value: "extended",
          filter: (value) => {
            if (this.searchExtended !== null) {
              let search = this.searchExtended === 'Yes'
              return value === search
            }

            return true
          },
        },
        { 
          text: "Health", 
          align: "right", 
          value: "hp", 
          filterable: false 
        },
        { 
          text: "Repair Time",
          align: "right", 
          value: "full_repair_time",
          filterable: false 
        },
        { 
          text: "Cost", 
          align: "center", 
          value: "starbux_cost", 
          filterable: false
        },
        { 
          text: "Capacity", 
          align: "center", 
          value: "defense", 
          filterable: false
        },
        { 
          text: "Type", 
          align: "left", 
          value: "ship_type", filter: (value) => {
            return this.filterCombobox(value.toString(), this.searchType)
          }, 
        },
        { 
          text: "Description", 
          align: "left", 
          value: "description", 
          filterable: false
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
        || this.searchLevel.length > 0
        || this.searchType.length > 0
        || this.searchExtended !== null
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
    this.getShips()
  },

  watch: {
    searchName: _.debounce(function(value){
      this.updateQueryFromFilter('name', value)
    }, 250),

    searchType(value) {
      this.updateQueryFromFilter('type', value)
    },

    searchLevel(value) {
      this.updateQueryFromFilter('level', value)
    },

    searchExtended(value) {
      this.updateQueryFromFilter('extended', value)
    },
  },

  methods: {
    initFilters() {
      this.searchName = this.$route.query.name

      if (this.$route.query.level) {
        this.searchLevel = this.$route.query.level.split(',').map(function(value) {
          return parseInt(value.trim())
        })
      }

      if (this.$route.query.type) {
        this.searchType = this.$route.query.type.split(',').map(function(value) {
          return value.trim()
        })
      }

      if (this.$route.query.extended) {
        this.searchExtended = this.$route.query.extended.trim()
      }
    },

    getShips: async function () {
      const response = await axios.get(this.shipsEndpoint)

      let ships = []
      for (const itemId in response.data.data) {
        const ship = response.data.data[itemId]
        let spaceT1 = 0
        let spaceT2 = 0

        ship.extended = false
        for (let column of ship.mask) {
          if (column === "1") {
            spaceT1++
          }

          if (column === "2") {
            spaceT2++
            ship.extended = true
          }
        }

        ship.space = spaceT1 + spaceT2
        ship.spaceT1 = spaceT1
        ship.spaceT2 = spaceT2
        ships.push(ship)
      }

      ships.sort((a, b) => b.id - a.id)
      this.ships = ships
      this.updateFilters()

      this.loaded = true

      return this.ships
    },

    updateFilters() {
      this.levels = Array.from(
        new Set(this.ships.map((ship) => (!ship.level ? 0 : ship.level)))
      ).sort(this.sortAlphabeticallyExceptNone)

      this.types = Array.from(
        new Set(
          this.ships.map((ship) => (!ship.ship_type ? "None" : ship.ship_type))
        )
      ).sort(this.sortAlphabeticallyExceptNone)
    },

    openShipInBuilder(shipId) {
      let path = '/builder?ship=' + shipId
      this.$router.push({ path: path })
    },

    getShipScalingRatio(ship) {
      let baseRatio = this.$vuetify.breakpoint.xsOnly ? 1.1 : 2.5
      let scale = (window.innerWidth / baseRatio) / Math.max(ship.interior_sprite.width,ship.interior_sprite.height)
      scale = scale > 1 ? 1 : scale
      return scale
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
  text-decoration: none;
}

.name span {
  color: #9e9e9e;
}

.ship-sprite {
  image-rendering: pixelated;
}
</style>