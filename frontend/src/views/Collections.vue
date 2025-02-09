<template>
  <v-card :loading="isLoading" class="full-height">
    <v-card-title class="overline">> Collections </v-card-title>
    <v-card-subtitle>{{ viewDescription }}</v-card-subtitle>

    <!-- Filters -->
    <v-card-subtitle v-if="loaded">
      <v-row>
        <v-col cols="12" sm="6" md="9">
          <v-text-field
            v-model="searchName"
            append-icon="mdi-magnify"
            label="Name"
            hint='For example: "Ardent", Cat'
            clearable
            outlined
          ></v-text-field>
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <v-autocomplete
            v-model="searchSkill"
            :items="skills"
            label="Skill"
            clearable
            multiple
            small-chips
            hide-details
            outlined
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
      :items="collections"
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
          <td>
            <div :style="spriteStyle(item.icon_sprite)"></div>
          </td>
          <td class="name">{{ item.name }}</td>
          <td>
            <div class="d-flex flex-row">
            <div :style="spriteStyle(item.ability_sprite)" class="mr-1"></div>
            {{ item.ability_name }}
            </div>
          </td>
          <td>
            <p>
              {{ item.trigger_description }}
              <br>
              {{ item.ability_description }}
            </p>
            <p class="small font-italic description">
              {{ item.description }}
            </p>
          </td>
          <td>{{ item.step_enhancement === 999999 ? '∞' : item.step_enhancement }}</td>
          <td>{{ item.step_chance }}%</td>
          <td>{{ `${item.min} - ${item.max}` }}</td>
          <td>
            <div v-if="item.chars.length > 0">
              <div
                v-for="crew in item.chars"
                :key="crew.id"
                class="center char-sprite block"
              >
                <crew :char="crew" tipPosition="right" />
              </div>
            </div>
          </td>
        </tr>
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
import axios from "axios"
import PixyShipMixin from "../mixins/PixyShip.vue.js"
import DataTableMixin from "../mixins/DataTable.vue.js"
import Crew from "../components/Crew.vue"
import _ from 'lodash'
import {useHead} from "@vueuse/head"

export default {
  mixins: [PixyShipMixin, DataTableMixin],

  components: {
    Crew,
  },

  data() {
    return {
      viewDescription: "All crew collections infos (crews, bonus, skill...) of Pixel Starships",
      searchName: this.name,
      searchSkill: [],
      skills: [],
      loaded: false,
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
          align: "left",
          value: "name",
          filterable: true
        },
        {
          text: "Skill",
          align: "left",
          value: "ability_name",
          filter: (value) => {
            return this.filterCombobox(value, this.searchSkill)
          },
        },
        {
          text: "Description",
          align: "left",
          value: "description",
          filterable: false,
        },
        {
          text: "Step Bonus",
          align: "right",
          value: "step_enhancement",
          filterable: false,
        },
        {
          text: "Step Chance",
          align: "right",
          value: "step_chance",
          filterable: false,
        },
        {
          text: "Required",
          align: "center",
          value: "min",
          filterable: false,
        },
        {
          text: "Chars",
          align: "left",
          sortable: false,
          filterable: false
        },
      ],
      collections: [],
    }
  },

  computed: {
    isLoading: function () {
      return !this.loaded
    },
    pendingFilter: function () {
      return this.searchName
        || this.searchSkill.length > 0
    }
  },

  mounted() {
    useHead({
      title: this.$route.name,
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
  },

  beforeMount: function () {
    this.initFilters()
    this.getCollections()
  },

  watch: {
    searchName: _.debounce(function(value){
      this.updateQueryFromFilter('name', value)
    }, 250),

    searchSkill(value) {
      this.updateQueryFromFilter('skill', value)
    },
  },

  methods: {
    initFilters() {
      this.searchName = this.$route.query.name

      if (this.$route.query.skill) {
        this.searchSkill = this.$route.query.skill.split(',').map(function(value) {
          return value.trim()
        })
      }
    },

    getCollections: async function () {
      const response = await axios.get(this.collectionsEndpoint)

      let collections = Object.entries(response.data.data).map(
        (collection) => collection[1]
      )

      collections.sort((a, b) => b.id - a.id)

      this.collections = collections
      this.updateFilters()

      this.loaded = true
      return this.collections
    },

    updateFilters() {
      this.skills = Array.from(
        new Set(this.collections.map((collection) => collection.ability_name))
      ).sort(this.sortAlphabeticallyExceptNone)
    },
  },
}
</script>

<style scoped src="@/assets/css/common.css"></style>
<style scoped>
.center {
  margin: 0 auto;
}

.block {
  display: inline-block;
}

.name {
  font-weight: bold;
}

a.name {
  text-decoration: none;
}

.description {
  font-size: 0.9em;
  color: #9e9e9e;
}
</style>
