<template>
  <v-card :loading="isLoading" class="full-height">
    <v-card-title class="overline">> Crews </v-card-title>
    <v-card-subtitle>All Pixel Starships crews (click on crew name to see prestiges infos)</v-card-subtitle>

    <!-- Filters -->
    <v-card-subtitle v-if="loaded">
      <v-row>
        <v-col cols="12" sm="4" md="1">
          <v-text-field
            v-model="level"
            type="number"
            label="Level"
            min="1"
            max="40"
            :value="level"
            outlined
          ></v-text-field>
        </v-col>
        <v-col cols="12" sm="8" md="3">
          <v-text-field
            v-model="searchName"
            append-icon="mdi-magnify"
            label='Name'
            hint='For example: "Zombie", Alien, -Pony'
            clearable
            outlined
          ></v-text-field>
        </v-col>
        <v-col cols="12" sm="6" md="2">
          <v-autocomplete
            v-model="searchEquipment"
            :items="equipments"
            label="Equip"
            clearable
            outlined
            multiple
            small-chips
            hide-details
            :value-comparator="filterValueComparator"
          ></v-autocomplete>
        </v-col>
        <v-col cols="12" sm="6" md="2">
          <v-autocomplete
            v-model="searchRarity"
            :items="rarities"
            label="Rarity"
            clearable
            outlined
            multiple
            small-chips
            hide-details
            :value-comparator="filterValueComparator"
          ></v-autocomplete>
        </v-col>
        <v-col cols="12" sm="6" md="2">
          <v-autocomplete
            v-model="searchSpecial"
            :items="abilities"
            label="Special"
            clearable
            outlined
            multiple
            small-chips
            hide-details
            :value-comparator="filterValueComparator"
          ></v-autocomplete>
        </v-col>
        <v-col cols="12" sm="6" md="2">
          <v-autocomplete
            v-model="searchCollection"
            :items="collections"
            label="Collection"
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
      :items="crews"
      :search="searchName"
      :custom-filter="multipleFilterWithNegative"
      :items-per-page="20"
      :loading="isLoading"
      :footer-props="{
        itemsPerPageOptions: [10, 20, 50, 100, 200, -1],
      }"
      multi-sort
      loading-text="Loading..."
      class="elevation-1 px-3"
    >
      <template v-slot:item="{ item }">
        <tr>
          <!-- Order -->
          <td>
            <div class="center char-sprite">
              <crew :char="item" :tip="false" />
            </div>
          </td>

          <!-- Name -->
          <td>
            <div class="text-xs-left">
              <a
                :class="[item.rarity, 'lh-9', 'name']"
                :href="`/crew/${item.id}`"
                >{{ item.name }}</a
              >
            </div>
          </td>

          <!-- Equip -->
          <td>
            <div class="ps-left equip">
              <div v-for="(s, k) in item.equipment" :key="k">
                <div
                  v-if="s.name"
                  :title="`${k}: +${s.bonus} ${s.enhancement} ${
                    s.extra_bonus ? '+' + s.extra_bonus : ''
                  } ${s.extra_enhancement}`"
                >
                  <div class="char-item" :style="spriteStyle(s.sprite)"></div>
                  {{ s.name }}
                </div>
                <template v-else>
                  <div class="unused">{{ k }}</div>
                </template>
              </div>
            </div>
          </td>

          <!-- Rarity -->
          <td>
            <div :class="['rarity', item.rarity]">{{ item.rarity }}</div>
          </td>

          <!-- Special -->
          <td>
            <div class="special-ability">
              <v-tooltip bottom color="blue-grey">
                <template v-slot:activator="{ on, attrs }">
                  <div
                    v-bind="attrs"
                    v-on="on"
                    :style="spriteStyle(item.ability_sprite)"
                  ></div>
                </template>
                {{ item.special_ability }}
              </v-tooltip>
            </div>
          </td>

          <!-- Collection -->
          <td>
            <v-tooltip v-if="item.collection_sprite" bottom color="blue-grey">
              <template v-slot:activator="{ on, attrs }">
                <div
                  v-bind="attrs"
                  v-on="on"
                  :style="spriteStyle(item.collection_sprite)"
                  class="center"
                ></div>
              </template>
              {{ item.collection_name }}
            </v-tooltip>
          </td>

          <!-- Stats -->
          <td>{{ item.hp[2] | statFormat(0) }}</td>
          <td>{{ item.attack[2] | statFormat() }}</td>
          <td>{{ item.repair[2] | statFormat() }}</td>
          <td>{{ item.ability[2] | statFormat() }}</td>
          <td>{{ item.pilot[2] | statFormat() }}</td>
          <td>{{ item.science[2] | statFormat() }}</td>
          <td>{{ item.engine[2] | statFormat() }}</td>
          <td>{{ item.weapon[2] | statFormat() }}</td>

          <!-- Fire -->
          <td>{{ item.fire_resist }}</td>

          <!-- Training -->
          <td>{{ item.training_limit }}</td>

          <!-- Speed -->
          <td> {{ item.walk }} </td>
          <td> {{ item.run }} </td>
        </tr>
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
import axios from "axios"
import mixins from "@/mixins/PixyShip.vue.js"
import Crew from "@/components/Crew.vue"
import "@/assets/css/override.css"
import _ from 'lodash'

export default {
  mixins: [mixins],

  components: {
    Crew,
  },

  data() {
    return {
      searchName: "",
      searchSpecial: [],
      searchRarity: [],
      searchCollection: [],
      searchEquipment: [],
      rarities: [],
      abilities: [],
      collections: [],
      equipments: [],
      loaded: false,
      crews: [],
      defaultLevel: 40,
      level: null,
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

            const ids = query.ids.split(',').map(function(id) {
              return parseInt(id.trim())
            })
            
            return ids.includes(value)
          }
        },
        { 
          text: "Name", 
          align: "start",          
          value: "name",
          filterable: true
        },
        {
          text: "Equip",
          align: "start",          
          value: "equipment",
          filter: value => { 
            return this.filterCombobox(Object.keys(value).toString(), this.searchEquipment, true)
          }
        },
        { 
          text: "Rarity", 
          align: "start",          
          value: "rarity", 
          filter: value => { 
            return this.filterCombobox(value, this.searchRarity)
          },
          sort: this.sortRarity,
        },
        { 
          text: "Special", 
          align: "start",          
          value: "special_ability", 
          filter: value => { 
            return this.filterCombobox(value, this.searchSpecial)
          } 
        },
        { 
          text: "Set", 
          align: "start",          
          value: "collection_name", 
          filter: value => { 
            return this.filterCombobox(value, this.searchCollection)
          }
        },
        { 
          text: "HP", 
          align: "start",          
          value: "hp[2]", 
          filterable: false 
        },
        {
          text: "ATK",
          align: "start",          
          value: "attack[2]",
          filterable: false,
        },
        {
          text: "RPR",
          align: "start",          
          value: "repair[2]",
          filterable: false,
        },
        {
          text: "ABL",
          align: "start",          
          value: "ability[2]",
          filterable: false,
        },
        {
          text: "PLT",
          align: "start",          
          value: "pilot[2]",
          filterable: false,
        },
        {
          text: "SCI",
          align: "start",          
          value: "science[2]",
          filterable: false,
        },
        {
          text: "ENG",
          align: "start",          
          value: "engine[2]",
          filterable: false,
        },
        {
          text: "WPN",
          align: "start",          
          value: "weapon[2]",
          filterable: false,
        },
        {
          text: "Fire",
          align: "start",          
          value: "fire_resist",
          filterable: false,
        },
        {
          text: "Training",
          align: "start",          
          value: "training_limit",
          filterable: false,
        },
        { 
          text: "Walk",
          align: "start",          
          value: "walk", 
          filterable: false
        },
        { 
          text: "Run",
          align: "start",          
          value: "run", 
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
        || this.searchSpecial.length > 0
        || this.searchRarity.length > 0
        || this.searchCollection.length > 0
        || this.searchEquipment.length > 0
    }
  },

  created() {
    document.title = 'PixyShip - ' + this.$route.name
  },

  beforeMount: function () {
    this.initFilters()
    this.getCrews()
  },

  watch: {
    level(value) {
      this.updateCurrentLevel()

      if (value == this.defaultLevel) {
        value = null
      }

      this.updateQueryFromFilter('level', value)
    },

    searchName(value) {
      this.updateQueryFromFilter('name', value)
    },

    searchSpecial(value) {
      this.updateQueryFromFilter('special', value)
    },

    searchEquipment(value) {
      this.updateQueryFromFilter('equipment', value)
    },

    searchRarity(value) {
      this.updateQueryFromFilter('rarity', value)
    },

    searchCollection(value) {
      this.updateQueryFromFilter('collection', value)
    },
  },

  filters: {
    statFormat(value, maxDigits = 1) {
      return value.toLocaleString("en-US", {
        maximumFractionDigits: maxDigits,
      })
    },
  },

  methods: {
    initFilters() {
      this.level = this.$route.query.level ? this.$route.query.level : this.defaultLevel
      this.searchName = this.$route.query.name

      if (this.$route.query.special) {
        this.searchSpecial = this.$route.query.special.split(',').map(function(value) {
          return value.trim()
        })
      }

      if (this.$route.query.equipment) {
        this.searchEquipment = this.$route.query.equipment.split(',').map(function(value) {
          return value.trim()
        })
      }

      if (this.$route.query.rarity) {
        this.searchRarity = this.$route.query.rarity.split(',').map(function(value) {
          return value.trim()
        })
      }

      if (this.$route.query.special) {
        this.searchSpecial = this.$route.query.special.split(',').map(function(value) {
          return value.trim()
        })
      }

      if (this.$route.query.collection) {
        this.searchCollection = this.$route.query.collection.split(',').map(function(value) {
          return value.trim()
        })
      }
    },

    getCrews: async function () {
      const response = await axios.get(this.crewEndpoint)

      let crews = []
      for (const k in response.data.data) {
        const crew = response.data.data[k]
        crews.push(crew)
      }

      crews.sort((a, b) => b.rarity_order - a.rarity_order)

      this.crews = crews

      this.updateCurrentLevel()
      this.updateFilters()

      this.loaded = true
      return this.crew
    },

    updateCurrentLevel() {
      this.crews.map((crew) => {
        this.interpolateStat(crew.progression_type, crew.hp)
        this.interpolateStat(crew.progression_type, crew.attack)
        this.interpolateStat(crew.progression_type, crew.repair)
        this.interpolateStat(crew.progression_type, crew.ability)
        this.interpolateStat(crew.progression_type, crew.pilot)
        this.interpolateStat(crew.progression_type, crew.science)
        this.interpolateStat(crew.progression_type, crew.engine)
        this.interpolateStat(crew.progression_type, crew.weapon)
      })
    },

    interpolateStat(type, stat) {
      let level = this.level
      if (_.isEmpty(level)) {
        level = this.defaultLevel
      }

      let p = 1 // Linear

      if (type === "EaseIn") {
        p = 2
      } else if (type === "EaseOut") {
        p = 0.5
      }

      stat[2] = stat[0] + (stat[1] - stat[0]) * ((level - 1) / 39) ** p
    },

    updateFilters() {
      this.rarities = Array.from(new Set(this.crews.map((crew) => crew.rarity[0].toUpperCase() + crew.rarity.slice(1) ))).sort(this.sortRarity)
      this.abilities = Array.from(new Set(this.crews.map((crew) => crew.special_ability.length === 0 ? 'None' : crew.special_ability))).sort(this.sortAlphabeticallyExceptNone)
      this.collections = Array.from(new Set(this.crews.map((crew) => crew.collection_name.length === 0 ? 'None' : crew.collection_name))).sort(this.sortAlphabeticallyExceptNone)

      let values = this.crews.map((crew) => Object.keys(crew.equipment).length === 0 ? ['None'] : Object.keys(crew.equipment))
      this.equipments =  Array.from(new Set(values.flat())).sort(this.sortAlphabeticallyExceptNone)
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

a.name:hover {
  text-decoration: underline;
}

.equip {
  font-size: 90%;
}
</style>