<template>
  <v-card :loading="isLoading" class="full-height">
    <v-card-title class="overline">> Crews </v-card-title>
    <v-card-subtitle>{{ viewDescription }} (click on crew name to see prestiges infos)</v-card-subtitle>

    <!-- Filters -->
    <v-card-subtitle v-if="loaded" class="pa-0 px-3">
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

    <v-card-subtitle class="pa-0">
    <v-card class="d-flex flex-row-reverse" flat tile>
      <v-card class="mr-5" flat tile>
        <v-switch
            v-model="showScoreStat"
            label="Display score"
        ></v-switch>
      </v-card>
    </v-card>
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
      :sort-by.sync="globalSortBy"
      :sort-desc.sync="globalSortDesc"
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
                    class="center"
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
          <td class="text-center">
            <span>{{ item.hp[2] | statFormat(0) }}</span>
            <v-progress-linear
                v-if="showScoreStat"
                class="mt-1"
                :value="item.scoreHP"
                :color="getScoreColor(item.scoreHP)"
            ></v-progress-linear>
          </td>
          <td class="text-center">
            <span>{{ item.attack[2] | statFormat() }}</span>
            <v-progress-linear
                v-if="showScoreStat"
                class="mt-1"
                :value="item.scoreAtk"
                :color="getScoreColor(item.scoreAtk)"
            ></v-progress-linear>
          </td>
          <td class="text-center">
            <span>{{ item.repair[2] | statFormat() }}</span>
            <v-progress-linear
                v-if="showScoreStat"
                class="mt-1"
                :value="item.scoreRpr"
                :color="getScoreColor(item.scoreRpr)"
            ></v-progress-linear>
          </td>
          <td class="text-center">
            <span>{{ item.ability[2] | statFormat() }}</span>
            <v-progress-linear
                v-if="showScoreStat"
                class="mt-1"
                :value="item.scoreAbl"
                :color="getScoreColor(item.scoreAbl)"
            ></v-progress-linear>
          </td>
          <td class="text-center">
            <span>{{ item.pilot[2] | statFormat() }}</span>
            <v-progress-linear
                v-if="showScoreStat"
                class="mt-1"
                :value="item.scorePlt"
                :color="getScoreColor(item.scorePlt)"
            ></v-progress-linear>
          </td>
          <td class="text-center">
            <span>{{ item.science[2] | statFormat() }}</span>
            <v-progress-linear
                v-if="showScoreStat"
                class="mt-1"
                :value="item.scoreSci"
                :color="getScoreColor(item.scoreSci)"
            ></v-progress-linear>
          </td>
          <td class="text-center">
            <span>{{ item.engine[2] | statFormat() }}</span>
            <v-progress-linear
                v-if="showScoreStat"
                class="mt-1"
                :value="item.scoreEng"
                :color="getScoreColor(item.scoreEng)"
            ></v-progress-linear>
          </td>
          <td class="text-center">
            <span>{{ item.weapon[2] | statFormat() }}</span>
            <v-progress-linear
                v-if="showScoreStat"
                class="mt-1"
                :value="item.scoreWpn"
                :color="getScoreColor(item.scoreWpn)"
            ></v-progress-linear>
          </td>

          <!-- Fire -->
          <td class="text-center">
            <span>{{ item.fire_resist }}</span>
            <v-progress-linear
                v-if="showScoreStat"
                class="mt-1"
                :value="item.scoreFire"
                :color="getScoreColor(item.scoreFire)"
            ></v-progress-linear>
          </td>

          <!-- Training -->
          <td class="text-center">
            <span>{{ item.training_limit }}</span>
            <v-progress-linear
                v-if="showScoreStat"
                class="mt-1"
                :value="item.scoreTraining"
                :color="getScoreColor(item.scoreTraining)"
            ></v-progress-linear>
          </td>

          <!-- Speed -->
          <td class="text-center">
            <span>{{ item.walk }}</span>
            <v-progress-linear
                v-if="showScoreStat"
                class="mt-1"
                :value="item.scoreWalk"
                :color="getScoreColor(item.scoreWalk)"
            ></v-progress-linear>
          </td>
          <td class="text-center">
            <span>{{ item.run }}</span>
            <v-progress-linear
                v-if="showScoreStat"
                class="mt-1"
                :value="item.scoreRun"
                :color="getScoreColor(item.scoreRun)"
            ></v-progress-linear>
          </td>
        </tr>
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
import axios from "axios"
import PixyShipMixin from "@/mixins/PixyShip.vue.js"
import DataTableMixin from "@/mixins/DataTable.vue.js"
import Crew from "@/components/Crew.vue"
import "@/assets/css/override.css"
import _ from 'lodash'

export default {
  mixins: [PixyShipMixin, DataTableMixin],

  components: {
    Crew,
  },

  data() {
    return {
      viewDescription: "All crew infos (sprite, stats, skill, collection...) of Pixel Starships",
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
      showScoreStat: true,
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
          align: "center",
          value: "special_ability", 
          filter: value => { 
            return this.filterCombobox(value, this.searchSpecial)
          } 
        },
        { 
          text: "Set", 
          align: "center",
          value: "collection_name", 
          filter: value => { 
            return this.filterCombobox(value, this.searchCollection)
          }
        },
        { 
          text: "HP", 
          align: "center",
          value: "hp[2]", 
          filterable: false 
        },
        {
          text: "ATK",
          align: "center",
          value: "attack[2]",
          filterable: false,
        },
        {
          text: "RPR",
          align: "center",
          value: "repair[2]",
          filterable: false,
        },
        {
          text: "ABL",
          align: "center",
          value: "ability[2]",
          filterable: false,
        },
        {
          text: "PLT",
          align: "center",
          value: "pilot[2]",
          filterable: false,
        },
        {
          text: "SCI",
          align: "center",
          value: "science[2]",
          filterable: false,
        },
        {
          text: "ENG",
          align: "center",
          value: "engine[2]",
          filterable: false,
        },
        {
          text: "WPN",
          align: "center",
          value: "weapon[2]",
          filterable: false,
        },
        {
          text: "Fire",
          align: "center",
          value: "fire_resist",
          filterable: false,
        },
        {
          text: "Training",
          align: "center",
          value: "training_limit",
          filterable: false,
        },
        { 
          text: "Walk",
          align: "center",
          value: "walk", 
          filterable: false
        },
        { 
          text: "Run",
          align: "center",
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

  metaInfo () {
    return {
      title: this.$route.name,
      meta: [
        {
          vmid: 'description',
          name: 'description',
          content: this.viewDescription
        },
      ]
    }
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

      crews.sort((a, b) => b.id - a.id)
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

      let maxHP = 0
      let maxAtk = 0
      let maxRpr = 0
      let maxAbl = []
      let maxPlt = 0
      let maxSci = 0
      let maxEng = 0
      let maxWpn = 0
      let maxFire = 0
      let maxTraining = 0
      let maxWalk = 0
      let maxRun = 0
      this.crews.map((crew) => {
        maxHP = Math.max(maxHP, crew.hp[2])
        maxAtk = Math.max(maxAtk, crew.attack[2])
        maxRpr = Math.max(maxRpr, crew.repair[2])

        if (!maxAbl[crew.special_ability]) {
          maxAbl[crew.special_ability] = crew.ability[2]
        } else {
          maxAbl[crew.special_ability] = Math.max(maxAbl[crew.special_ability], crew.ability[2])
        }

        maxPlt = Math.max(maxPlt, crew.pilot[2])
        maxSci = Math.max(maxSci, crew.science[2])
        maxEng = Math.max(maxEng, crew.engine[2])
        maxWpn = Math.max(maxWpn, crew.weapon[2])
        maxFire = Math.max(maxFire, crew.fire_resist)
        maxTraining = Math.max(maxTraining, crew.training_limit)
        maxWalk = Math.max(maxWalk, crew.walk)
        maxRun = Math.max(maxRun, crew.run)
      })


      this.crews.map((crew) => {
        crew.scoreHP = crew.hp[2] / maxHP * 100
        crew.scoreAtk = crew.attack[2] / maxAtk * 100
        crew.scoreRpr = crew.repair[2] / maxRpr * 100
        crew.scoreAbl = crew.ability[2] / maxAbl[crew.special_ability] * 100
        crew.scorePlt = crew.pilot[2] / maxPlt * 100
        crew.scoreSci = crew.science[2] / maxSci * 100
        crew.scoreEng = crew.engine[2] / maxEng * 100
        crew.scoreWpn = crew.weapon[2] / maxWpn * 100
        crew.scoreFire = crew.fire_resist / maxFire * 100
        crew.scoreTraining = crew.training_limit / maxTraining * 100
        crew.scoreWalk = crew.walk / maxWalk * 100
        crew.scoreRun = crew.run / maxRun * 100
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

    getScoreColor(scoreValue) {
      if (scoreValue < 20) {
        return 'red darken-3'
      }

      if (scoreValue < 40) {
        return 'lime darken-3'
      }

      if (scoreValue < 60) {
        return 'light-green darken-3'
      }

      if (scoreValue < 80) {
        return 'green darken-3'
      }

      return 'blue darken-3'
    }
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

.center {
  margin: 0 auto;
}
</style>