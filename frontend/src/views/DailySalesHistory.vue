<template>
  <v-card :loading="isLoading" class="full-height">
    <v-card-title class="overline">> Daily Sales History</v-card-title>
    <v-card-subtitle>{{ viewDescription }}</v-card-subtitle>

    <!-- Filters -->
    <v-card-subtitle v-if="loaded">
      <v-row>
        <v-col cols="12" sm="6" md="3">
          <v-text-field
              v-model="searchName"
              append-icon="mdi-magnify"
              label='Name'
              clearable
              outlined
          ></v-text-field>
        </v-col>

        <v-col cols="12" sm="6" md="3">
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

        <v-col cols="12" sm="6" md="3">
          <v-autocomplete
              v-model="searchCurrency"
              :items="currencies"
              label="Currency"
              clearable
              outlined
              multiple
              small-chips
              hide-details
              :value-comparator="filterValueComparator"
          ></v-autocomplete>
        </v-col>

        <v-col cols="12" sm="6" md="3">
          <v-menu
              v-model="menu"
              :close-on-content-click="false"
              :nudge-right="40"
              transition="scale-transition"
              offset-y
              min-width="auto"
          >
            <template v-slot:activator="{ on, attrs }">
              <v-text-field
                  v-model="searchDate"
                  label="Until"
                  readonly
                  v-bind="attrs"
                  v-on="on"
                  clearable
                  outlined
              ></v-text-field>
            </template>
            <v-date-picker
                v-model="searchDate"
                @input="menu = false"
            ></v-date-picker>
          </v-menu>
        </v-col>
      </v-row>
    </v-card-subtitle>


    <!-- Table -->
    <v-data-table
        v-if="loaded"
        mobile-breakpoint="0"
        :headers="headers"
        :items="dailysales"
        :search="searchName"
        :custom-filter="multipleFilterWithNegative"
        :loading="isLoading"
        :footer-props="{
          itemsPerPageOptions: [10, 20, 50, 100, 200, -1],
        }"
        :sort-by.sync="globalSortBy"
        :sort-desc.sync="globalSortDesc"
        multi-sort
        loading-text="Loading..."
        class="elevation-1 px-3"
        :items-per-page="itemsPerPage"
    >
      <template v-slot:item="{ item }">
        <tr>
          <td>
            <crew v-if="item.type === 'character'" :char="item.char" tipPosition="right"/>
            <item v-else-if="item.type === 'item'" :item="item.item"/>
            <div v-else :style="spriteStyleScaledWrapper(item.sprite, 300)">
              <div class="block my-1 ma-auto" :style="spriteStyleScaled(item.sprite, 300)"></div>
            </div>
          </td>

          <td style="min-width: 250px">
            <span v-if="item.type === 'character'" :class="[item.char.rarity]"><a :href="makeLink(item.type, item.id)">{{ item.name }}</a></span>
            <span v-else-if="item.type === 'item'" :class="[item.item.rarity]"><a :href="makeLink(item.type, item.id)">{{ item.name }}</a></span>
            <span v-else-if="item.type !== 'sprite'"><a :href="makeLink(item.type, item.id)">{{ item.name }}</a></span>
            <span v-else><a :href="getSpriteUrl(item.sprite)" >{{ item.name }}</a></span>
          </td>

          <td>
            {{ formatType(item.type) }}
          </td>

          <td>
            {{ item.price }}
          </td>

          <td>
              <div
                  class="d-inline-block"
                  :style="currencySprite(item.currency)"
              />
          </td>

          <td style="min-width: 150px">{{ item.moment }}</td>
        </tr>
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
import axios from "axios"
import moment from 'moment'
import PixyShipMixin from "../mixins/PixyShip.vue.js"
import DataTableMixin from "../mixins/DataTable.vue.js"
import Crew from "../components/Crew.vue"
import Item from "../components/Item.vue"
import "../assets/css/override.css"
import _ from 'lodash'

export default {
  mixins: [PixyShipMixin, DataTableMixin],

  components: {
    Crew,
    Item,
  },

  data() {
    return {
      viewDescription: "Daily sales history of Pixel Starships",
      itemsPerPage: 20,
      searchName: '',
      defaultSearchDate: new Date().toISOString().substr(0, 10),
      searchDate: '',
      menu: false,
      searchType: [],
      searchCurrency: [],
      types: [],
      currencies: [],
      loaded: false,
      saleFrom: this.$route.params.from,
      dailysales: [],
      headers: [
        {
          text: 'Image',
          align: 'left',
          sortable: false,
          filterable: false
        },
        {
          text: 'Name',
          value: 'name',
          align: 'left'
        },
        {
          text: 'Type',
          value: 'type',
          align: 'left',
          filter: value => {
            return this.filterCombobox(this.formatType(value), this.searchType, false)
          }
        },
        {
          text: 'Price',
          value: 'price',
          align: 'left'
        },
        {
          text: 'Currency',
          value: 'currency',
          align: 'left',
          filter: value => {
            return this.filterCombobox(value, this.searchCurrency, false)
          }
        },
        {
          text: 'Date', value: 'moment', align: 'left', filter: value => {
            if (this.searchDate) {

              return value <= this.searchDate
            }

            return true
          }
        },
      ],
    }
  },

  computed: {
    isLoading: function () {
      return !this.loaded
    },
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
    this.getDailySales()
  },

  watch: {
    searchName: _.debounce(function(value){
      this.updateQueryFromFilter('name', value)
    }, 250),

    searchDate(value) {
      if (value === this.defaultSearchDate) {
        value = null
      }

      this.updateQueryFromFilter('date', value)
    },

    searchType(value) {
      this.updateQueryFromFilter('type', value)
    },

    searchCurrency(value) {
      this.updateQueryFromFilter('currency', value)
    },
  },

  methods: {
    initFilters() {
      this.searchName = this.$route.query.name
      this.searchDate = this.$route.query.date ? this.$route.query.date : this.defaultSearchDate

      if (this.$route.query.type) {
        this.searchType = this.$route.query.type.split(',').map(function (value) {
          return value.trim()
        })
      }

      if (this.$route.query.currency) {
        this.searchCurrency = this.$route.query.currency.split(',').map(function (value) {
          return value.trim()
        })
      }
    },

    getDailySales: async function () {
      const response = await axios.get(this.lastSalesBySaleFromEndpoint(this.saleFrom))

      let dailysales = response.data.data.map(dailysale => {
        dailysale.moment = moment.utc(dailysale.changed_at).format('YYYY-MM-DD')
        return dailysale
      })

      this.dailysales = dailysales

      this.updateFilters()
      this.loaded = true

      return this.dailysales
    },

    formatType: function (type) {
      if (type === 'character') {
        return 'Crew'
      }

      return type.charAt(0).toUpperCase() + type.slice(1)
    },

    updateFilters() {
      this.types = Array.from(new Set(this.dailysales.map((dailysale) => this.formatType(dailysale.type)))).sort(this.sortAlphabeticallyExceptNone)
      this.currencies = Array.from(new Set(this.dailysales.map((dailysale) => dailysale.currency))).sort(this.sortAlphabeticallyExceptNone)
    },
  },
}
</script>

<style scoped src="@/assets/css/common.css"></style>
