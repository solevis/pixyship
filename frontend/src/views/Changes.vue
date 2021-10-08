<template>
  <v-card :loading="isLoading" class="full-height">
    <v-card-title class="overline">> Changes </v-card-title>
    <v-card-subtitle>API changes for common assets of Pixel Starships</v-card-subtitle>

    <!-- Filters -->
    <v-card-subtitle v-if="loaded">
      <v-row>
        <v-col cols="12" sm="4" md="6">
          <v-text-field
            v-model="searchName"
            append-icon="mdi-magnify"
            label='Name'
            clearable
            outlined
          ></v-text-field>
        </v-col>

        <v-col cols="12" sm="4" md="3">
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

        <v-col
          cols="12" sm="4" md="3"
        >
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


    <v-card-text v-if="loaded">
      Legend: <span class="success--text">New value</span> / <span class="warning--text">Changed value</span> / <span class="error--text">Removed value</span>
    </v-card-text>

    <!-- Table -->
    <v-data-table
      v-if="loaded"
      mobile-breakpoint="0"
      :headers="headers"
      :items="changes"
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
      :items-per-page="itemsPerPage"
    >
      <template v-slot:item="{ item }">
        <tr>
          <td>
            <crew v-if="item.type === 'char'" :char="item.char" tipPosition="right" />
            <item v-else-if="item.type === 'item'" :item="item.item" />
            <div v-else class="block my-1 ma-auto" :style="spriteStyle(item.sprite)"></div>
          </td>

          <td style="min-width: 250px">
            <span v-if="item.type === 'char'" :class="[item.char.rarity]"><a :href="makeLink(item.type, item.id)">{{ item.name }}</a></span>
            <span v-else-if="item.type === 'item'" :class="[item.item.rarity]"><a :href="makeLink(item.type, item.id)">{{ item.name }}</a></span>
            <span v-else-if="item.type !== 'sprite'"><a :href="makeLink(item.type, item.id)">{{ item.name }}</a></span>
            <span v-else>{{ item.name }}</span>
          </td>

          <td>
            {{ formatType(item.type) }}
          </td>

          <td style="min-width: 150px">{{ item.moment }}</td>
          <td>
            <table v-if="item.change_type === 'Changed'">
              <tr v-for="change in item.changes.new" class="nobreak" :key="change.id">
                <td style="vertical-align: top; text-align: right; padding-right: 10px"><div class="success--text">{{ change[0].replace('_', ' ') }}:</div></td>
                <td><div :title="change[1]" class="success--text text-truncate record-field">{{ change[1] }}</div></td>
              </tr>

              <tr v-for="change in item.changes.changed" class="nobreak" :key="change.id">
                <td style="vertical-align: top; text-align: right; padding-right: 10px"><div class="warning--text">{{ change[0].replace('_', ' ') }}:</div></td>
                <td v-if="change[1].length > 50 || change[2].length > 50">
                  <div :title="change[1]" style="min-width: 400px; max-width: 600px" class="grey--text record-field"> {{ change[1] }}</div>
                  <div :title="change[2]" style="min-width: 400px; max-width: 600px" class="record-field warning--text">{{ change[2] }}</div>
                </td>
                <td v-else>
                  <span :title="change[1]" class="grey--text text-truncate record-field"> {{ change[1] }}</span>
                  &rarr;
                  <span :title="change[2]" class="warning--text text-truncate record-field"> {{ change[2] }}</span>
                </td>
              </tr>

              <tr v-for="change in item.changes.removed" class="nobreak" :key="change.id">
                <td style="vertical-align: top; text-align: right; padding-right: 10px"><div class="error--text">{{ change[0].replace('_', ' ') }}:</div></td>
                <td><div :title="change[1]" class="error--text text-truncate record-field">{{ change[1] }}</div></td>
              </tr>
            </table>
            <span v-else class="ml-2 success--text">{{ item.change_type }}</span>
          </td>
        </tr>
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
import axios from "axios";
import moment from 'moment';
import mixins from "@/mixins/PixyShip.vue.js";
import Crew from "@/components/Crew.vue";
import Item from "@/components/Item.vue";
import "@/assets/css/override.css";

const convert = require('xml-js')

export default {
  mixins: [mixins],

  components: {
    Crew,
    Item,
  },

  data() {
    return {
      itemsPerPage: 20,
      searchName: "",
      searchDate: new Date().toISOString().substr(0, 10),
      menu: false,
      searchType: [],
      searchLabLevel: [],
      types: [],
      labLevers: [],
      loaded: false,
      headers: [
        {text: 'Image', align: 'left', sortable: false, filterable: false},
        {text: 'Name', value: 'name', align: 'left'},
        {
          text: 'Type', 
          value: 'type', 
          align: 'left', 
          filter: value => { 
            return this.filterCombobox(this.formatType(value), this.searchType, false)
          }
        },
        {text: 'Date', value: 'moment', align: 'left', filter: value => { 
            if (this.searchDate) {
              return value <= this.searchDate
            }

            return true
          }
        },
        {text: 'Change', value: 'change_type', align: 'center', filterable: false}
      ],
      changes: [],
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
    this.getChanges();
  },

  methods: {
    getChanges: async function () {
      const response = await axios.get(this.changesEndpoint);

      let changes = response.data.data.map(change => {
        change.attributes = this.getAllAttributes(convert.xml2js(change.data).elements[0])
        change.oldAttributes = change.old_data ? this.getAllAttributes(convert.xml2js(change.old_data).elements[0]) : null
        
        change.moment = moment.utc(change.changed_at).format('YYYY-MM-DD')
        change.changes = this.diffAttributes(change.attributes, change.oldAttributes)

        return change
      })

      this.changes = changes;
      this.updateFilters()

      this.loaded = true;

      return this.changes;
    },

    formatType: function (type) {
      if (type === 'char') {
        return 'Crew'
      }

      return type.charAt(0).toUpperCase() + type.slice(1);
    },

    updateFilters() {
      this.types = Array.from(new Set(this.changes.map((change) => this.formatType(change.type)))).sort(this.sortAlphabeticallyExceptNone)
    },

    makeLink(type, id) {
      if (type === 'char') {
        return `/crew/${id}`
      }

      if (type === 'item') {
        return `/item/${id}`
      }

      if (type === 'room') {
        return `/rooms?ids=${id}`
      }

      if (type === 'ship') {
        return `/ships?ids=${id}`
      }

      if (type === 'collection') {
        return `/collections?ids=${id}`
      }

      if (type === 'research') {
        return `/researches?ids=${id}`
      }
    }
  },
};
</script>

<style scoped src="@/assets/css/common.css"></style>
<style scoped>
.name {
  font-weight: bold;
}

a.name {
  text-decoration: none;
}
</style>