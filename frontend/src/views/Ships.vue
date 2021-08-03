<template>
  <v-card :loading="isLoading">
    <v-card-title class="overline">> Ships </v-card-title>
    <v-card-subtitle>All Pixel Starships ships infos and sprites (click on a row to see interior and exterior)</v-card-subtitle>

    <!-- Filters -->
    <v-card-subtitle v-if="loaded">
      <v-row>
        <v-col cols="12" sm="12" md="8">
          <v-text-field
            v-model="searchName"
            append-icon="mdi-magnify"
            label='Name'
            hint='For example: "Starship", Cluck, -Extended'
            clearable
            outlined
          ></v-text-field>
        </v-col>
        <v-col cols="12" sm="6" md="2">
          <v-autocomplete
            v-model="searchLevel"
            :items="levels"
            label="Level"
            clearable
            outlined
            multiple
            small-chips
            hide-details
          ></v-autocomplete>
        </v-col>
        <v-col cols="12" sm="6" md="2">
          <v-autocomplete
            v-model="searchType"
            :items="types"
            label="Type"
            clearable
            outlined
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
      :items="ships"
      :search="searchName"
      :custom-filter="multipleFilterWithNegative"
      :items-per-page="20"
      :loading="isLoading"
      :sortDesc="true"
      :footer-props="{
        itemsPerPageOptions: [10, 20, 50, 100, 200, -1],
      }"
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
              <td class="text-xs-right">{{ item.hp }}</td>

              <td class="text-xs-right">{{ item.repair_time }}</td>

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
                  <tr v-for="cost in item.item_cost" :key="item.id + '-' + cost.id" class="nobreak">
                    <td><div :style="spriteStyle(cost.sprite)"></div></td>
                    <td>{{ cost.name }}</td>
                  </tr>
                </table>
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
import axios from "axios";
import mixins from "@/mixins/PixyShip.vue.js";
import "@/assets/css/override.css";

export default {
  mixins: [mixins],

  components: {},

  data() {
    return {
      searchName: "",
      searchLevel: [],
      searchType: [],
      levels: [],
      types: [],
      loaded: false,
      headers: [
        { text: "", align: "center", sortable: false, filterable: false },
        { text: "Name", align: "center", value: "name", filterable: true },
        { text: "Level", align: "right", value: "level", filter: (value) => {
            return this.filterCombobox(value.toString(), this.searchLevel);
          },
        },
        { text: "Space", align: "right", value: "space", filterable: false },
        { text: "T1", align: "right", value: "spaceT1", filterable: false },
        { text: "T2", align: "right", value: "spaceT2", filterable: false },
        { text: "Health", align: "right", value: "hp", filterable: false },
        { text: "Secs/Repair", align: "right", value: "repair_time", filterable: false },
        { text: "Cost", align: "center", value: "starbux_cost", filterable: false },
        { text: "Capacity", align: "center", value: "defense", filterable: false },
        { text: "Type", align: "left", value: "ship_type", filter: (value) => {
            return this.filterCombobox(value.toString(), this.searchType);
          }, },
        { text: "Description", align: "left", value: "description", filterable: false },
      ],
      rooms: [],
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
    this.getShips()
  },

  methods: {
    getShips: async function () {
      const response = await axios.get(this.shipsEndpoint);

      let ships = [];
      for (const itemId in response.data.data) {
        const ship = response.data.data[itemId];
        let spaceT1 = 0;
        let spaceT2 = 0;

        for (let c of ship.mask) {
          if (c === "1") spaceT1++;
          if (c === "2") spaceT2++;
        }

        ship.space = spaceT1 + spaceT2;
        ship.spaceT1 = spaceT1;
        ship.spaceT2 = spaceT2;
        ships.push(ship);
      }

      ships.sort((a, b) => b.name - a.name);

      this.ships = ships;
      this.updateFilters();

      this.loaded = true;

      return this.ships;
    },

    updateFilters() {
      this.levels = Array.from(
        new Set(this.ships.map((ship) => (!ship.level ? 0 : ship.level)))
      ).sort(this.sortAlphabeticallyExceptNone);

      this.types = Array.from(
        new Set(
          this.ships.map((ship) => (!ship.ship_type ? "None" : ship.ship_type))
        )
      ).sort(this.sortAlphabeticallyExceptNone);
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

.name span {
  color: #9e9e9e;
}

.ship-sprite {
  image-rendering: pixelated;
}
</style>