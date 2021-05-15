<template>
  <v-card :loading="isLoading" v-resize="onResize">
    <v-card-subtitle v-if="!loaded"> Loading... </v-card-subtitle>

    <!-- Filters -->
    <v-card-subtitle v-if="loaded">
      <v-row>
        <v-col cols="12" sm="12" md="8">
          <v-text-field
            v-model="searchName"
            append-icon="mdi-magnify"
            label='Name'
            hint='For example: "Starship", Cluck'
            clearable
          ></v-text-field>
        </v-col>
        <v-col cols="12" sm="6" md="2">
          <v-combobox
            v-model="searchLevel"
            :items="levels"
            label="Level"
            clearable
            multiple
            small-chips
            hide-details
          ></v-combobox>
        </v-col>
        <v-col cols="12" sm="6" md="2">
          <v-combobox
            v-model="searchType"
            :items="types"
            label="Type"
            clearable
            multiple
            small-chips
            hide-details
          ></v-combobox>
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
      dense
      fixed-header
      :height="tableHeight"
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
        <td :colspan="headers.length" align="center" class="pa-2">
          <v-row>
            <v-col cols="12">
              <v-card
                  elevation="3"
                  class="px-6 pb-6 pt-2"
                  outlined
                  shaped
                >

                <v-card-subtitle>
                  <div class="overline">
                    EXTERIOR
                  </div>
                </v-card-subtitle>

                <v-img class="ship-sprite"
                  :src="getSpriteUrl(item.exterior_sprite)"
                  :width="item.exterior_sprite.width"
                  :height="item.exterior_sprite.height"
                  contain
                ></v-img>
              </v-card>
            </v-col>
          </v-row>

          <v-row>
            <v-col cols="12">
              <v-card
                  elevation="3"
                  class="px-6 pb-6 pt-2"
                  outlined
                  shaped
                >

                <v-card-subtitle>
                  <div class="overline">
                    INTERIOR
                  </div>
                </v-card-subtitle>

                <v-img class="ship-sprite"
                  :src="getSpriteUrl(item.interior_sprite)"
                  :width="item.interior_sprite.width"
                  :height="item.interior_sprite.height"
                  contain
                ></v-img>
              </v-card>
            </v-col>
          </v-row>
        </td>
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
import axios from "axios";
import mixins from "@/mixins/PixyShip.vue.js";
import "../assets/css/override.css";

export default {
  mixins: [mixins],

  components: {},

  data() {
    return {
      tableHeight: 0,
      searchName: "",
      searchLevel: [],
      searchType: [],
      levels: [],
      types: [],
      loaded: false,
      headers: [
        { text: "Image", align: "center", sortable: false, filterable: false },
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

  mounted () {
    this.onResize()
  },

  methods: {
    onResize() {
      this.tableHeight = window.innerHeight - 250
    },

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
      ).sort((a, b) => a - b);

      this.types = Array.from(
        new Set(
          this.ships.map((ship) => (!ship.ship_type ? "None" : ship.ship_type))
        )
      ).sort((a) => (a === "None" ? -1 : 1));
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