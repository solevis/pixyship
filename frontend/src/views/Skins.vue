<template>
  <v-card :loading="isLoading" class="full-height">
    <v-card-title class="overline">> Skins </v-card-title>
    <v-card-subtitle>{{ viewDescription }}</v-card-subtitle>

    <!-- Filters -->
    <v-card-subtitle v-if="loaded">
      <v-row>
        <v-col cols="12" sm="12" md="8">
          <v-text-field
              v-model="searchName"
              append-icon="mdi-magnify"
              label="Name"
              hint='For example: "Turkey Launch Pad", Eggsamination'
              clearable
              outlined
          ></v-text-field>
        </v-col>
        <v-col cols="12" sm="6" md="2">
          <v-autocomplete
            v-model="searchSkinType"
            :items="skinTypes"
            label="Skin Type"
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
            v-model="searchRace"
            :items="races"
            label="Race"
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
        :items="skins"
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
          <td class="name">{{ item.description }}</td>
          <td class="name">{{ item.race }}</td>
          <td class="name">{{ item.skin_type }}</td>
        </tr>
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
import axios from "axios"
import PixyShipMixin from "../mixins/PixyShip.vue.js"
import DataTableMixin from "../mixins/DataTable.vue.js"
import _ from 'lodash'
import {useHead} from "@vueuse/head"

export default {
  mixins: [PixyShipMixin, DataTableMixin],

  data() {
    return {
      viewDescription: "All skins infos of Pixel Starships",
      skins: [],
      skinTypes: [],
      races: [],
      loaded: false,
      searchName: this.name,
      searchSkinType: [],
      searchRace: [],
      headers: [
        {
          text: "Order by ID",
          align: "center",
          value: "skinset_id",
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
          text: "Description",
          align: "left",
          value: "description",
          width: 150,
          filterable: true
        },
        {
          text: "Race",
          align: "left",
          value: "race",
          width: 150,
          filter: (value) => {
            return this.filterCombobox(value, this.searchRace)
          },
        },
        {
          text: "Skin Type",
          align: "left",
          value: "skin_type",
          width: 150,
          filter: (value) => {
            return this.filterCombobox(value, this.searchSkinType)
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
        || this.searchSkinType.length > 0
        || this.searchRace.length > 0
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
    this.getSkins()
  },

  watch: {
    searchName: _.debounce(function(value){
      this.updateQueryFromFilter('name', value)
    }, 250),

    searchSkinType(value) {
      this.updateQueryFromFilter('skintype', value)
    },

    searchRace(value) {
      this.updateQueryFromFilter('race', value)
    },
  },

  methods: {
    initFilters() {
      this.searchName = this.$route.query.name

       if (this.$route.query.skintype) {
        this.searchSkinType = this.$route.query.skintype.split(',').map(function(value) {
          return value.trim()
        })
      }

        if (this.$route.query.race) {
        this.searchRace = this.$route.query.race.split(',').map(function(value) {
          return value.trim()
        })
      }
    },

    updateFilters() {
      this.skinTypes = Array.from(
        new Set(
          this.skins.map((skin) => (!skin.skin_type ? "None" : skin.skin_type))
        )
      ).sort(this.sortAlphabeticallyExceptNone)

      this.races = Array.from(
        new Set(
          this.skins.map((skin) => (!skin.race ? "None" : skin.race))
        )
      ).sort(this.sortAlphabeticallyExceptNone)
    },

    getSkins: async function () {
      const response = await axios.get(this.skinsEndpoint)

      let skins = Object.entries(response.data.data).map(
          (skin) => skin[1]
      )

      skins.sort((a, b) => b.id - a.id)

      this.skins = skins
      this.updateFilters()

      this.loaded = true
      return this.skins
    },
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
</style>
