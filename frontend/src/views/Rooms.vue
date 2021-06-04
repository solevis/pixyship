<template>
  <v-card :loading="isLoading">
    <v-card-title class="overline">> Rooms </v-card-title>
    <v-card-subtitle>All Pixel Starships rooms (click on a row to display more infos)</v-card-subtitle>

    <!-- Filters -->
    <v-card-subtitle v-if="loaded">
      <v-row>
        <v-col cols="12" sm="12" md="4">
          <v-text-field
            v-model="searchName"
            append-icon="mdi-magnify"
            label='Name'
            hint='For example: Bedroom, -Destroyed, SPL'
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
            v-model="searchShipLevel"
            :items="shipLevels"
            label="Min Ship Level"
            clearable
            outlined
            multiple
            small-chips
            hide-details
          ></v-autocomplete>
        </v-col>
        <v-col cols="12" sm="6" md="2">
          <v-autocomplete
            v-model="searchSize"
            :items="sizes"
            label="Size"
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
      :items="rooms"
      :items-per-page="20"
      :search="searchName"
      :custom-filter="multipleFilterWithNegative"
      :loading="isLoading"
      :sortDesc="true"
      :footer-props="{
        itemsPerPageOptions: [10, 20, 50, 100, 200, -1],
      }"
      multi-sort
      loading-text="Loading..."
      class="elevation-1 px-3"
      dense
    >
      <template v-slot:item="{ item, expand, isExpanded }">
        <v-tooltip bottom color="blue-grey" :disabled="isExpanded">
          <template v-slot:activator="{ on, attrs }">
            <tr @click="expand(!isExpanded)" v-bind="attrs" v-on="on">
              <!-- Image -->
              <td class="pa-1">
                <div :style="spriteStyle(item.sprite)"></div>
              </td>

              <!-- Name -->
              <td>
                <div :class="[item.rarity, 'lh-9', 'name']">
                  {{ item.name }}
                </div>
              </td>

              <td>
                <div :class="[item.rarity, 'lh-9', 'name']">
                  <span>{{ item.short_name }}</span>
                </div>
              </td>

              <td>{{ item.type }}</td>
              <td>{{ `${item.width}x${item.height}` }}</td>

              <td>{{ item.level }}</td>
              <td>{{ item.min_ship_level }}</td>
              
              <td>
                <div
                  :class="[
                    item.power_gen - item.power_use >= 0
                      ? 'positive'
                      : 'negative',
                  ]"
                >
                  {{ formatPower(item) }}
                </div>
              </td>
              <td align="center">
                <table v-if="item.purchasable">
                  <tr class="nobreak">
                    <td>
                      <div :style="currencySprite(item.upgrade_currency)" />
                    </td>
                    <td>{{ item.upgrade_cost }}</td>
                  </tr>
                </table>
              </td>
              <td>{{ formatTime(item.upgrade_seconds) }}</td>
              <td>{{ item.description }}</td>
            </tr>
          </template>
          <span>Click to display more infos</span>
        </v-tooltip>
      </template>

      <template v-slot:expanded-item="{ headers, item }">
        <td :colspan="headers.length" align="center" style="border-bottom: 10px solid #393939;">
          <v-row class="ma-3">
            <v-col>
              <v-card
                elevation="3"
                class="px-6 pb-6 pt-2"
                outlined
                shaped
              >
                <v-card-subtitle>
                  <div class="overline">
                    PRIMARY STATS
                  </div>
                </v-card-subtitle>

                <v-simple-table dense style="width: 500px">
                  <template v-slot:default>
                    <thead>
                      <tr>
                        <th class="text-left" style="width: 300px">
                          Stat
                        </th>
                        <th class="text-left">
                          Value
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      
                      <tr v-show="item.enhancement_type != 'None'">
                        <td>Support Stat</td>
                        <td>{{ item.enhancement_type }}</td>
                      </tr>

                      <tr v-show="item.reload">
                        <td>Reload</td>
                        <td>{{ item.reload }} ({{ `${Math.ceil(item.reload / 40 * 100) / 100}s` }})</td>
                      </tr>

                      <tr v-show="item.capacity">
                        <td>Capacity</td>
                        <td>{{ item.capacity }}</td>
                      </tr>

                      <tr v-show="item.refill_cost">
                        <td>Refill cost</td>
                        <td>{{ item.refill_cost }}</td>
                      </tr>

                      <tr v-show="item.manufacture_type !== 'None'">
                        <td>Manufacture Type</td>
                        <td>{{ item.manufacture_type }}</td>
                      </tr>

                      <tr v-show="item.manufacture_rate">
                        <td>Manufacture Rate</td>
                        <td>{{ `${Math.ceil(item.manufacture_rate * 3600)}/hour` }}</td>
                      </tr>

                      <tr v-show="item.manufacture_capacity">
                        <td>{{ item.manufacture_capacity_label == null ? 'Manufacture Capacity' : item.manufacture_capacity_label }}</td>
                        <td>{{ item.manufacture_capacity }}</td>
                      </tr>

                      <tr v-show="item.defense">
                        <td>Defense</td>
                        <td>{{ item.defense }} ({{ (1 - 100 / (100 + item.defense)).toLocaleString("en-US", { style: "percent", }) }})</td>
                      </tr>

                      <tr v-show="item.cooldown_time">
                        <td>Cooldown</td>
                        <td>{{ item.cooldown_time }} ({{ `${item.cooldown_time / 40}s` }})</td>
                      </tr>

                      <tr v-if="item.requirement !== null">
                        <td>{{ item.requirement.type }} requirement</td>
                        <td>
                           
                        <table>
                          <tr>
                            <td>x{{ item.requirement.count }} {{ item.requirement.object.name }}</td>
                            <td><div :style="spriteStyle(item.requirement.object.sprite)" class="ml-1"></div></td>
                          </tr>
                        </table>
                        </td>
                      </tr>

                      <tr v-if="!item.purchasable">
                        <td>Daily offer, event reward or dove ship</td>
                        <td>Yes</td>
                      </tr>

                      <tr>
                        <td>Placeable in the ship extended area</td>
                        <td v-if="item.extension_grids">Yes</td>
                        <td v-else>No</td>
                      </tr>
                    </tbody>
                  </template>
                </v-simple-table>
              </v-card>
            </v-col>

            <v-col>
              <v-card
                elevation="3"
                class="px-6 pb-6 pt-2"
                outlined
                shaped
                v-show="item.has_weapon_stats"
              >

              <v-card-subtitle>
                <div class="overline">
                  WEAPON STATS
                </div>
              </v-card-subtitle>

                <v-simple-table dense style="width: 500px">
                  <template v-slot:default>
                    <thead>
                      <tr>
                        <th class="text-left" style="width: 300px">
                          Stat
                        </th>
                        <th class="text-left">
                          Value
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-show="item.character_damage">
                        <td>Crew Dmg (dps)</td>
                        <td>{{ item.character_damage }} ({{ `${computeDps(item.character_damage, item)}/s` }})</td>
                      </tr>

                      <tr v-show="item.hull_damage">
                        <td>Hull Dmg (dps)</td>
                        <td>{{ item.hull_damage }} ({{ `${computeDps(item.hull_damage, item)}/s` }})</td>
                      </tr>

                      <tr v-show="item.hull_percentage_damage">
                        <td>Hull % Dmg</td>
                        <td>{{ item.hull_percentage_damage }}%</td>
                      </tr>

                      <tr v-show="item.shield_damage">
                        <td>Shield Dmg (dps)</td>
                        <td>{{ item.shield_damage }} ({{ `${computeDps(item.shield_damage, item)}/s` }})</td>
                      </tr>

                      <tr v-show="item.system_damage">
                        <td>System Dmg (dps)</td>
                        <td>{{ item.system_damage }} ({{ `${computeDps(item.system_damage, item)}/s` }})</td>
                      </tr>

                      <tr v-show="item.direct_system_damage">
                        <td>AP Dmg (dps)</td>
                        <td>{{ item.direct_system_damage }} ({{ `${computeDps(item.direct_system_damage, item)}/s` }})</td>
                      </tr>

                      <tr v-show="item.volley">
                        <td>Volley</td>
                        <td>{{ item.volley }}</td>
                      </tr>

                      <tr v-show="item.volley_delay">
                        <td>V. Delay</td>
                        <td>{{ item.volley_delay }} ({{ `${item.volley_delay / 40}s` }})</td>
                      </tr>

                      <tr v-show="item.speed">
                        <td>Speed</td>
                        <td>{{ item.speed }}px/s</td>
                      </tr>

                      <tr v-show="item.fire_length">
                        <td>Incendiary</td>
                        <td>{{ item.fire_length }} ({{ `${item.fire_length / 40}s` }})</td>
                      </tr>

                      <tr v-show="item.emp_length">
                        <td>EMP</td>
                        <td>{{ item.emp_length }} ({{ `${item.emp_length / 40}s` }})</td>
                      </tr>

                      <tr v-show="item.stun_length">
                        <td>Stun</td>
                        <td>{{ item.stun_length }} ({{ `${item.stun_length / 40}s` }})</td>
                      </tr>
                    </tbody>
                  </template>
                </v-simple-table>
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
import "@/assets/css/override.css";

export default {
  mixins: [mixins],

  components: {},

  data() {
    return {
      searchName: "",
      searchLevel: [],
      searchShipLevel: [],
      searchSize: [],
      searchType: [],
      levels: [],
      shipLevels: [],
      types: [],
      sizes: [],
      loaded: false,
      headers: [
        { text: "Image", align: "center", sortable: false, filterable: false },
        { text: "Name", align: "left", value: "name", width: 200 },
        { text: "Short", align: "left", value: "short_name" },
        {
          text: "Type",
          align: "left",          
          value: "type",
          filter: (value) => {
            return this.filterCombobox(value, this.searchType);
          },
        },
        {
          text: "Size",
          align: "center",          
          sortable: false,
          filter: (value, search, item) => {
            value = `${item.width}x${item.height}`;
            return this.filterCombobox(value, this.searchSize);
          },
        },
        {
          text: "Level",
          align: "center",          
          value: "level",
          filter: (value) => {
            return this.filterCombobox(value.toString(), this.searchLevel);
          },
        },
        {
          text: "Min Ship Level",
          align: "center",          
          value: "min_ship_level",
          filter: (value) => {
            return this.filterCombobox(value.toString(), this.searchShipLevel);
          },
        },
        { text: "Power", align: "center", sortable: false, filterable: false },
        {
          text: "Cost",
          align: "center",          
          value: "upgrade_cost",
          filterable: false,
        },
        {
          text: "Time",
          align: "center",          
          value: "upgrade_seconds",
          width: 150,
          filterable: false,
        },
        {
          text: "Description",
          align: "center",          
          value: "description",
          filterable: false,
          sortable: false,
        },
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
    this.getRooms();
  },

  methods: {
    computeDps(damage, room) {
      let volley = room.volley
      if (volley == 0) {
        volley = 1
      }

      let volley_delay = room.volley_delay
      if (volley_delay == 0) {
        volley_delay = 1
      }

      let reload = room.reload / 40
      let cooldown = room.cooldown_time ? room.cooldown_time / 40 : 0

      let dps = (damage * volley) / (reload + (volley - 1) * volley_delay + cooldown)
      return Math.ceil(dps * 100) / 100
    },

    getRooms: async function () {
      const response = await axios.get(this.roomsEndpoint);

      let rooms = [];
      for (const itemId in response.data.data) {
        const room = response.data.data[itemId];
        
        if (!room.purchasable) {
          room.upgrade_cost = 0
        }

        rooms.push(room);
      }

      rooms.sort((a, b) => b.name - a.name);

      this.rooms = rooms;
      this.updateFilters();

      this.loaded = true;

      return this.rooms;
    },

    updateFilters() {
      this.shipLevels = Array.from(
        new Set(
          this.rooms.map((room) =>
            !room.min_ship_level ? 0 : room.min_ship_level
          )
        )
      ).sort(this.sortAlphabeticallyExceptNone);

      this.levels = Array.from(
        new Set(this.rooms.map((room) => (!room.level ? 0 : room.level)))
      ).sort(this.sortAlphabeticallyExceptNone);

      this.sizes = Array.from(
        new Set(this.rooms.map((room) => `${room.width}x${room.height}`))
      ).sort();

      this.types = Array.from(
        new Set(this.rooms.map((room) => (!room.type ? "None" : room.type)))
      ).sort(this.sortAlphabeticallyExceptNone);
    },

    formatPower(item) {
      let comsumption = item.power_gen - item.power_use

      if (!comsumption) { return '' }

      let sign = comsumption >= 0 ? '+' : '-'
      return sign + Math.abs(comsumption)
    }
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

.positive {
  color: #1be600;
}

.negative {
  color: #f44336;
}

.name span {
  color: #9e9e9e;
}
</style>