<template>
  <v-card :loading="isLoading" class="full-height">
    <v-card-title class="overline">> Missiles </v-card-title>
    <v-card-subtitle>{{ viewDescription }}</v-card-subtitle>

    <!-- Filters -->
    <v-card-subtitle v-if="loaded">
      <v-row>
        <v-col cols="12">
          <v-text-field
              v-model="searchName"
              append-icon="mdi-magnify"
              label="Name"
              hint='For example: "Corsair Lv2", Fire'
              clearable
              outlined
          ></v-text-field>
        </v-col>
      </v-row>
    </v-card-subtitle>

    <!-- Table -->
    <v-data-table
        v-if="loaded"
        mobile-breakpoint="0"
        :headers="headers"
        :items="missiles"
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
        <tr>
          <td class="text-center">
            <div class="block my-1" :style="spriteStyle(item.sprite)"></div>
          </td>
          <td class="name">{{ item.name }}</td>
          <td>{{ item.build_time }}s<br><span class="damage-dps">{{ secondsToMinutesSeconds(item.build_time) }}</span></td>
          <td>
            <div class="d-flex">
              {{ item.manufacture_cost[0].data }}
              <div v-if="item.manufacture_cost[0].type === 'gas'" :style="gasSprite()"></div>
              <div v-else-if="item.manufacture_cost[0].type === 'mineral'" :style="mineralSprite()"></div>
            </div>
          </td>
          <td><span v-if="item.reload_modifier">{{ item.reload_modifier }}%</span></td>
          <td>{{ item.volley }}</td>
          <td>{{ item.volley_delay }}<br><span class="damage-dps">{{ `${item.volley_delay / 40}s` }}</span></td>
          <td>{{ item.system_damage }}</td>
          <td>{{ item.hull_damage }}</td>
          <td>{{ item.character_damage }}</td>
          <td>{{ item.shield_damage }}</td>
          <td>{{ item.direct_system_damage }}</td>
          <td>{{ item.speed }}<br><span class="damage-dps">{{ `${item.speed * 40}px/s` }}</span></td>
          <td>{{ item.fire_length }}<br><span class="damage-dps">{{ `${item.fire_length / 40}s` }}</span></td>
          <td>{{ item.emp_length }}<br><span class="damage-dps">{{ `${item.emp_length / 40}s` }}</span></td>
        </tr>
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
import axios from "axios"
import PixyShipMixin from "../mixins/PixyShip.vue.js"
import DataTableMixin from "../mixins/DataTable.vue.js"
import moment from 'moment'
import _ from 'lodash'

export default {
  mixins: [PixyShipMixin, DataTableMixin],

  data() {
    return {
      viewDescription: "All missiles infos of Pixel Starships",
      missiles: [],
      loaded: false,
      searchName: this.name,
      headers: [
        {
          text: "Order by ID",
          align: "center",
          value: "id",
          width: 95,
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
          align: "left",
          value: "name",
          width: 150,
          filterable: true
        },
        {
          text: "Build Time",
          align: "left",
          value: "build_time",
          filterable: true
        },
        {
          text: "Cost",
          align: "left",
          value: "manufacture_cost",
          filterable: true
        },
        {
          text: "Reload Speed",
          align: "left",
          value: "reload_modifier",
          filterable: true
        },
        {
          text: "Volley",
          align: "left",
          value: "volley",
          filterable: true
        },
        {
          text: "Volley Delay",
          align: "left",
          value: "volley_delay",
          filterable: true
        },
        {
          text: "System Dmg",
          align: "left",
          value: "system_damage",
          filterable: true
        },
        {
          text: "Hull Dmg",
          align: "left",
          value: "hull_damage",
          filterable: true
        },
        {
          text: "Crew Dmg",
          align: "left",
          value: "character_damage",
          filterable: true
        },
        {
          text: "Shield Dmg",
          align: "left",
          value: "shield_damage",
          filterable: true
        },
        {
          text: "AP Dmg",
          align: "left",
          value: "direct_system_damage",
          filterable: true
        },
        {
          text: "Ammo Speed",
          align: "left",
          value: "speed",
          filterable: true
        },
        {
          text: "Fire",
          align: "left",
          value: "fire_length",
          filterable: true
        },
        {
          text: "EMP",
          align: "left",
          value: "emp_length",
          filterable: true
        }
      ],
    }
  },

  computed: {
    isLoading: function () {
      return !this.loaded
    },
    pendingFilter: function () {
      return this.searchName
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
    this.getMissiles()
  },

  watch: {
    searchName: _.debounce(function(value){
      this.updateQueryFromFilter('name', value)
    }, 250)
  },

  methods: {
    initFilters() {
      this.searchName = this.$route.query.name
    },

    getMissiles: async function () {
      const response = await axios.get(this.missilesEndpoint)

      let missiles = Object.entries(response.data.data).map(
          (missile) => missile[1]
      )

      missiles.sort((a, b) => b.id - a.id)

      this.missiles = missiles

      this.loaded = true
      return this.missiles
    },

    secondsToMinutesSeconds: function (seconds) {
      return moment.utc(seconds*1000).format('mm:ss')
    }
  },
}
</script>

<style scoped src="@/assets/css/common.css"></style>
<style scoped>
.block {
  display: inline-block;
}

.name {
  font-weight: bold;
}

a.name {
  text-decoration: none;
}

.damage-dps {
  font-size: 0.9em;
  color: #9e9e9e;
}
</style>