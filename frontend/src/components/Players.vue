<template>
  <div>
    <v-app dark>
      <ps-header/>
      Players
      <v-container v-if="!showData">
        <v-layout class="column">
          <v-autocomplete
            v-model="search"
            :items="data"
            :search-input.sync="searchText"
            label="Search"
            placeholder="search by name"
            :no-filter="true"
            item-text="name">
            <template slot-scope="s" slot="item">
              <div class="text-xs-right lh-1 mr-2" style="width: 3em">{{ s.item.trophies}}</div>
              <div class="text-xs-left lh-1 mr-5" style="width: 10em">{{ s.item.name }}</div>
              <div class="block my-1 mr-1" :style="spriteStyle(s.item.alliance_sprite)"></div>
              {{ s.item.alliance }}
            </template>
          </v-autocomplete>
          <br/>
        </v-layout>
      </v-container>
      <div>
        <a href="http://www.pixelstarships.com">Pixel Starships</a> - The game
      </div>
    </v-app>
  </div>
</template>

<script>

import axios from 'axios'
import Vue from 'vue'
import VueAnalytics from 'vue-analytics'
import Crew from './Crew'
import Header from './Header'
import 'vuetify/dist/vuetify.min.css'
import mixins from './Common.vue.js'
import _ from 'lodash'
require('../assets/common.css')

Vue.use(VueAnalytics, {
  id: 'UA-67866007-2',
  checkDuplicatedScript: true
})

Vue.component('crew', Crew)
Vue.component('ps-header', Header)

export default {
  mixins: [mixins],

  data () {
    return {
      confirmDialog: false,
      data: [],
      errorMessage: '',
      headers: [
        {text: 'Trophies', value: 'trophies', align: 'right', sortable: false},
        {text: 'Name', value: 'name', sortable: false},
        {text: 'Alliance', value: 'alliance', sortable: false}
      ],
      message: '',
      pagination: {sortBy: 'trophies', descending: true, rowsPerPage: 100},
      search: '',
      searchText: '',
      showData: false,
      tab: 0
    }
  },

  created: function () {
    this.getData()
  },

  watch: {
    searchText(val) {
      console.log(val)
      this.getData()
      console.log(this.data.length)
    },

    search(val) {
      this.searchText(val)
      // This is when we try to get the
    }
  },

  methods: {
    getData: _.debounce(async function () {
      const res = await axios.get(
        this.playersEndpoint,
        {params: {search: this.searchText}}
      )
      this.data = res.data
    }, 250),
  }
}
</script>

<style>
  /*.record-field {*/
  /*  max-width: 250px;*/
  /*}*/

  .v-datatable, .v-datatable__actions {
    background-color: inherit !important;
  }

  .v-datatable td {
    height: unset !important;
  }

  .v-datatable td,
  .v-datatable th {
    padding: 0 5px !important;
    color: white !important;
  }

  .v-datatable tr {
    height: unset !important;
  }

  .application.theme--dark {
    background-color: black;
  }

  .block {
    display: inline-block;
  }

  :visited {
    color: #24E3FF;
  }

  :link {
    color: #FF5656;
    text-decoration: none;
  }

  td > div {
    text-align: left;
    vertical-align: top;
  }

  .v-list__tile {
    height: 24px;
  }

</style>
