<template>
  <div>
    <v-app dark>
      <ps-header/>
      Players
      <v-container v-if="!showData">
        <v-layout class="column">
          <v-text-field
            v-model="search"
            append-icon="search"
            id="search"
            label="Search"
            placeholder="search by name"
          ></v-text-field>
          <br/>
          <v-data-table
            :items="data"
            :headers="headers"
            :pagination.sync="pagination"
            :rows-per-page-items="[10,20,50,100]"
          >
            <template slot="items" slot-scope="i">
              <td class="text-xs-right">
                {{ i.item.trophies }}
              </td>
              <td class="text-xs-left">{{ i.item.name }}</td>
<!--                <a :href="'/?search=' + i.item.name"></a>-->
<!--              </td>-->
              <td class="text-xs-left">
                <div class="block my-1" :style="spriteStyle(i.item.alliance_sprite)"></div>
                {{ i.item.alliance }}
              </td>
            </template>
          </v-data-table>
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
      showData: false,
      tab: 0
    }
  },

  created: function () {
    this.getData()
  },

  watch: {
    search(val) {
      this.getData()
    }
  },

  methods: {
    getData: _.debounce(async function () {
      const res = await axios.get(
        this.playersEndpoint,
        {params: {search: this.search}}
      )
      this.data = res.data
    }, 500),
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

</style>
