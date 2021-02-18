<template>
  <div>
    <v-app dark>
      <ps-header/>
      Collections
      <br/><br/>
      <div class="center">
        <v-data-table
          :headers="headers"
          :items="collections"
          :rows-per-page-items="[10,20,50,100,200,{'text':'$vuetify.dataIterator.rowsPerPageAll','value':-1}]"
          :pagination.sync="pagination"
          :search="search"
        >
          <template slot="items" slot-scope="i">
            <td>
              <div :style="spriteStyle(i.item.icon_sprite)"></div>
            </td>
            <!--<td><div :style="`background-color: rgb(${i.item.ColorString})`"></div></td>-->
            <td class="text-xs-left">{{ i.item.name }}</td>
            <td class="text-xs-left">{{ i.item.EnhancementType }}</td>
            <td class="text-xs-left">
              <div v-if="i.item.chars.length > 0" v-for="c in i.item.chars" class="center char-sprite block">
                <crew :char="c"/>
              </div>
            </td>
            <td>{{ `${i.item.min} - ${i.item.max}` }}</td>
            <td class="text-xs-right">{{ i.item.base_enhancement }}</td>
            <td class="text-xs-right">{{ i.item.step_enhancement }}</td>
            <td class="text-xs-left">{{ i.item.CollectionDescription }}</td>
          </template>
        </v-data-table>
      </div>
      <br/>
      <br/>
      <div></div>
      <div>
        <a href="http://www.pixelstarships.com">Pixel Starships</a>
      </div>
    </v-app>
  </div>
</template>

<script>

import axios from 'axios'
import Vue from 'vue'
import BootstrapVue from 'bootstrap-vue'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import Header from './Header'
import 'vuetify/dist/vuetify.min.css'
import mixins from './Common.vue.js'
import Crew from './Crew'

Vue.component('ps-header', Header)

Vue.use(BootstrapVue)

export default {
  mixins: [mixins],

  data () {
    return {
      devMode: process.env.NODE_ENV === 'development',
      collections: [],
      search: '',
      headers: [
        {text: 'Image', align: 'center', sortable: false},
        {text: 'Name', align: 'left', value: 'name'},
        {text: 'Skill', align: 'left', value: 'EnhancementType'},
        {text: 'Chars', align: 'left', sortable: false},
        {text: 'Required range', align: 'center', value: 'min'},
        {text: 'Base Bonus', align: 'right', value: 'base_enhancement'},
        {text: 'Step Bonus', align: 'right', value: 'step_enhancement'},
        {text: 'Description', align: 'left', value: 'CollectionDescription'}
      ],
      pagination: {'sortBy': 'name', 'descending': true, 'rowsPerPage': 20}
    }
  },

  components: {
    Crew
  },

  created: function () {
    this.init()
  },

  methods: {
    init: async function () {
      const r = await axios.get(this.collectionsEndpoint)
      this.collections = Object.entries(r.data.data).map(x => x[1])
    }
  }
}
</script>

<style>
  .block {
    display: inline-block;
  }

  .nobreak {
    word-break: keep-all;
    white-space: nowrap;
  }

  .application.theme--dark {
    background-color: black;
  }

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
    border: 2px solid black
  }

  .v-datatable tbody tr:hover {
    background-color: #222 !important;
  }

  html, body {
    background-color: black;
    color: white;
  }

  .form-group {
    margin-right: 10px;
  }

  .table-bordered th, .table-bordered td {
    border: 0;
  }

  .table th, .table td {
    padding: 3px;
    vertical-align: inherit;
  }

  .page-link, .page-item.disabled .page-link {
    background-color: inherit;
    border: 1px solid #222;
  }

  .form-control, .form-control:focus {
    background-color: black;
    color: white;
  }

  .main {
    margin-top: 10px;
  }

  .center {
    margin: 0 auto;
  }

  /* this doesn't work except on multiple lines */
  .name {
    line-height: .9;
  }

  .pull-left {
    float: left !important;
  }

  .pull-right {
    /*float: right!important;*/
  }

  .stat span {
    color: gray;
    font-size: 60%;
  }

  .stat {
    line-height: .7;
  }

  .equip {
    line-height: 1;
    font-size: 80%;
  }

  .rarity {
    text-transform: capitalize;
  }

  .name {
    font-weight: bold;
  }

  :visited {
    color: #24E3FF;
  }

  :link {
    color: #FF5656;
    text-decoration: none;
  }

  .positive {
    color: #1be600;
  }

  .negative {
    color: red;
  }

  .left {
    text-align: left;
  }

  .right {
    text-align: right;
  }

  .top {
    vertical-align: top;
  }

  .side-by-side {
    float: left
  }

  .bold {
    text-weight: bold;
  }

  .char-part {
    margin: 0px auto;
  }

  .char {
    max-width: 25px;
    margin: 0px;
    display: inline-block;
  }

  td.center > div {
    display: inline-block;
    vertical-align: top;
  }

  .name span {
    color: white;
    font-size: 60%;
  }

  td.smaller {
    font-size: x-small;
  }

</style>
