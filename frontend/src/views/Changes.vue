<template>
  <v-card :loading="isLoading" v-resize="onResize">
    <v-card-subtitle v-if="!loaded"> Loading... </v-card-subtitle>

    <!-- Filters -->
    <v-card-subtitle v-if="loaded">
      <v-row>
        <v-col cols="8">
          <v-text-field
            v-model="searchName"
            append-icon="mdi-magnify"
            label='Name'
            clearable
            dense
          ></v-text-field>
        </v-col>

        <v-col
          cols="4"
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
                label="Date"
                prepend-icon="mdi-calendar"
                readonly
                v-bind="attrs"
                v-on="on"
                clearable
                dense
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
      class="elevation-1"
      dense
      fixed-header
      :height="tableHeight"
      :page.sync="page"
      :items-per-page="itemsPerPage"
      hide-default-footer
      @page-count="pageCount = $event"
    >
      <template v-slot:item="{ item }">
        <tr>
          <td>
            <crew v-if="item.type === 'char'" :char="item.char"/>
            <div v-else class="block my-1" :style="spriteStyle(item.sprite)"></div>
          </td>

          <td style="min-width: 250px">
            {{ item.name }}
          </td>

          <td style="min-width: 150px">{{ item.moment }}</td>
          <td>
            <table v-if="item.change_type === 'Changed'">
              <tr v-for="change in item.changes.new" class="nobreak" :key="change.id">
                <td style="vertical-align: top; text-align: right; padding-right: 10px"><div class="success--text">{{ change[0].replace('_', ' ') }}</div></td>
                <td><div :title="change[1]" class="success--text text-truncate record-field">{{ change[1] }}</div></td>
              </tr>

              <tr v-for="change in item.changes.changed" class="nobreak" :key="change.id">
                <td style="vertical-align: top; text-align: right; padding-right: 10px"><div class="warning--text">{{ change[0].replace('_', ' ') }}</div></td>
                <td>
                  <div :title="change[1]" class="grey--text text-truncate record-field"> {{ change[1] }}</div>
                  <div :title="change[2]" class="warning--text text-truncate record-field"> {{ change[2] }}</div>
                  </td>
              </tr>

              <tr v-for="change in item.changes.removed" class="nobreak" :key="change.id">
                <td style="vertical-align: top; text-align: right; padding-right: 10px"><div class="error--text">{{ change[0].replace('_', ' ') }}</div></td>
                <td><div :title="change[1]" class="error--text text-truncate record-field">{{ change[1] }}</div></td>
              </tr>
            </table>
            <span v-else class="ml-2 success--text">{{ item.change_type }}</span>
          </td>
        </tr>
      </template>
    </v-data-table>
    <div class="text-center pt-2">
      <v-pagination
        v-model="page"
        :length="pageCount"
      ></v-pagination>
    </div>
  </v-card>
</template>

<script>
import axios from "axios";
import moment from 'moment';
import mixins from "@/mixins/PixyShip.vue.js";
const convert = require('xml-js')

export default {
  mixins: [mixins],

  components: {},

  data() {
    return {
      page: 1,
      pageCount: 0,
      itemsPerPage: 20,
      tableHeight: 0,
      searchName: "",
      searchDate: null,
      menu: false,
      searchType: [],
      searchLabLevel: [],
      types: [],
      labLevers: [],
      loaded: false,
      headers: [
        {text: 'Image', align: 'left', sortable: false, filterable: false},
        {text: 'Name', value: 'name', align: 'left'},
        {text: 'Date', value: 'moment', align: 'left', filter: value => { 
            if (this.searchDate) {
              return value === this.searchDate
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

  beforeMount: function () {
    this.getChanges();
  },

  mounted () {
    this.onResize()
  },

  methods: {
    onResize() {
      this.tableHeight = window.innerHeight - 230
    },

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
      this.loaded = true;

      return this.changes;
    },
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