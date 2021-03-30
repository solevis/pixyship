<template>
  <v-card :loading="isLoading">
    <v-card-title v-if="!loaded"> Loading... </v-card-title>

    <!-- Filters -->
    <v-card-title v-if="loaded">
      <v-row>
        <v-col cols="4">
          <v-text-field
            v-model="searchName"
            append-icon="mdi-magnify"
            label='Name (example: "Lift Lv2", Vent)'
            hide-details
          ></v-text-field>
        </v-col>
        <v-col cols="2">
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
        <v-col cols="2">
          <v-combobox
            v-model="searchShipLevel"
            :items="shipLevels"
            label="Min Ship Level"
            clearable
            multiple
            small-chips
            hide-details
          ></v-combobox>
        </v-col>
        <v-col cols="2">
          <v-combobox
            v-model="searchSize"
            :items="sizes"
            label="Size"
            clearable
            multiple
            small-chips
            hide-details
          ></v-combobox>
        </v-col>
        <v-col cols="2">
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
    </v-card-title>

    <!-- Table -->
    <v-data-table
      v-if="loaded"
      :headers="headers"
      :items="rooms"
      :search="searchName"
      :custom-filter="multipleFilterWithNegative"
      :items-per-page="20"
      :loading="isLoading"
      sortBy="offers"
      :sortDesc="true"
      :footer-props="{
        itemsPerPageOptions: [10, 20, 50, 100, 200, -1],
      }"
      multi-sort
      loading-text="Loading..."
      class="elevation-1"
      dense
    >
      <template v-slot:item="{ item, expand, isExpanded }">
        <v-tooltip bottom color="blue-grey" :disabled="isExpanded">
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
                  {{ item.power_gen - item.power_use || "" }}
                </div>
              </td>
              <td>
                <table>
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
        <td :colspan="headers.length" align="center" class="pb-2">
          <v-card
            elevation="3"
            class="px-6 pb-6 pt-2"
          >
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
                  <tr v-show="item.reload">
                    <td>Reload</td>
                    <td>{{ item.reload }} ({{ `${item.reload / 40}s` }})</td>
                  </tr>

                  <tr v-show="item.defense">
                    <td>Defense</td>
                    <td>{{ item.defense }} ({{ (1 - 100 / (100 + item.defense)).toLocaleString("en-US", { style: "percent", }) }})</td>
                  </tr>

                  <tr v-show="item.character_damage">
                    <td>Crew Dmg</td>
                    <td>{{ item.character_damage }}</td>
                  </tr>

                  <tr v-show="item.hull_damage">
                    <td>Hull Dmg</td>
                    <td>{{ item.hull_damage }}</td>
                  </tr>

                  <tr v-show="item.shield_damage">
                    <td>Shield Dmg</td>
                    <td>{{ item.shield_damage }}</td>
                  </tr>

                  <tr v-show="item.system_damage">
                    <td>System Dmg</td>
                    <td>{{ item.system_damage }}</td>
                  </tr>

                  <tr v-show="item.direct_system_damage">
                    <td>AP Dmg</td>
                    <td>{{ item.direct_system_damage }}</td>
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
                    <td>{{ item.speed }} ({{ `${item.speed / 40}s` }})</td>
                  </tr>

                  <tr v-show="item.fire_length">
                    <td>Fire</td>
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

                  <tr v-show="item.capacity">
                    <td>Capacity</td>
                    <td>{{ item.capacity }}</td>
                  </tr>

                  <tr v-show="item.refill_cost">
                    <td>Refill cost</td>
                    <td>{{ item.refill_cost }}</td>
                  </tr>



                </tbody>
              </template>
            </v-simple-table>
          </v-card>
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
        { text: "Name", align: "left", value: "name" },
        {
          text: "Type",
          align: "left",
          value: "type",
          filter: (value) => {
            return this.filterCombobox(value.toString(), this.searchType);
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
          sortable: false
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

  beforeMount: function () {
    this.getRooms();
  },

  methods: {
    getRooms: async function () {
      const response = await axios.get(this.roomsEndpoint);

      let rooms = [];
      for (const itemId in response.data.data) {
        const room = response.data.data[itemId];
        rooms.push(room);
      }

      rooms.sort((a, b) => b.rarity_order - a.rarity_order);

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
      ).sort((a, b) => a - b);

      this.levels = Array.from(
        new Set(this.rooms.map((room) => (!room.level ? 0 : room.level)))
      ).sort((a, b) => a - b);

      this.sizes = Array.from(
        new Set(this.rooms.map((room) => `${room.width}x${room.height}`))
      ).sort();

      this.types = Array.from(
        new Set(this.rooms.map((room) => (!room.type ? "None" : room.type)))
      ).sort((a) => a === 'None' ? -1 : 1);
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

.equip {
  font-size: 90%;
}

.market {
  min-width: 200px;
}

.bonus {
  min-width: 100px;
}

.recipe {
  min-width: 55px;
}

.positive {
  color: #1be600;
}

.negative {
  color: #f44336;
}

.stat span {
  color: #9e9e9e;
}

.name span {
  color: #9e9e9e;
}
</style>