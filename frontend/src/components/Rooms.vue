<template>
  <div>
    <v-app dark>
      <ps-header/>
      Rooms
      <br/><br/>
      <div class="center">
        <v-text-field
          v-model="search"
          append-icon="search"
          id="search"
          label="Search"
          placeholder="search room name, short name, type and description"
        ></v-text-field>
        <br/>
        <v-data-table
          :headers="headers"
          :items="rooms"
          :rows-per-page-items="[10,20,50,100,200,{'text':'$vuetify.dataIterator.rowsPerPageAll','value':-1}]"
          :pagination.sync="pagination"
          :search="search"
          :custom-filter="fieldFilter"
          :filter="multipleFilter"
        >
          <template slot="items" slot-scope="i">
            <td>
              <div :style="spriteStyle(i.item.sprite)"></div>
            </td>
            <td><!-- Name -->
              <div :class="[i.item.rarity, 'lh-9', 'name', 'text-xs-left']">
                {{ i.item.name }}
                <span><br>{{ i.item.short_name }}</span>
              </div>
            </td>
            <td class="text-xs-right">{{ i.item.level }}</td>
            <td class="text-xs-right">{{ i.item.min_ship_level }}</td>
            <td class="stat">
              {{ i.item.reload ? `${i.item.reload / 40}s` : '' }}
              <span><br>{{ i.item.reload || '' }}</span>
            </td>
            <td class="text-xs-right">{{ i.item.capacity || '' }}</td>
            <td class="text-xs-right">{{ i.item.refill_cost || '' }}</td>
            <td class="stat">
              {{ i.item.defense ? (1 - 100 / (100 + i.item.defense)).toLocaleString('en-US', {style: 'percent'}) : '' }}
              <span><br>{{ i.item.defense || '' }}</span>
            </td>
            <td>
              <div :class="[i.item.power_gen - i.item.power_use >= 0 ? 'positive' : 'negative']">
                {{ i.item.power_gen - i.item.power_use || '' }}
              </div>
            </td>
            <td class="text-xs-left">{{ i.item.type }}</td>
            <td class="text-xs-right">{{ i.item.upgrade_cost }}</td>
            <td>
              <div :style="currencySprite(i.item.upgrade_currency)"/>
            </td>
            <td>{{ formatTime(i.item.upgrade_seconds) }}</td>
            <td>{{ `${i.item.width}x${i.item.height}`}}</td>
            <td class="text-xs-left" style="min-width: 200px">{{ i.item.description }}</td>
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

Vue.component('ps-header', Header)

Vue.use(BootstrapVue)

function styleFromSprite (s, color = '', border = 0, ninepatch = 0) {
  if (Object.keys(s).length === 0) {
    return {}
  }
  let obj = {
    background: `${color} url('//pixelstarships.s3.amazonaws.com/${s.source}.png') -${s.x}px -${s.y}px`,
    width: `${s.width}px`,
    height: `${s.height}px`,
    border: `${border}px solid lightgrey`,
    imageRendering: 'pixelated'
  }
  return obj
}

export default {
  mixins: [mixins],

  data () {
    return {
      devMode: process.env.NODE_ENV === 'development',
      rooms: [],
      search: '',
      headers: [
        {text: 'Image', align: 'center', sortable: false},
        {text: 'Name', align: 'left', value: 'name'},
        {text: 'Level', align: 'right', value: 'level'},
        {text: 'Ship Level', align: 'right', value: 'min_ship_level'},
        {text: 'Reload', align: 'center', value: 'reload'},
        {text: 'Capacity', align: 'right', value: 'capacity'},
        {text: 'Refill $', align: 'right', value: 'refill_cost'},
        {text: 'Defense', align: 'center', value: 'defense'},
        {text: 'Power', align: 'center', sortable: false},
        {text: 'Type', align: 'left', value: 'type'},
        {text: 'Cost', align: 'right', value: 'upgrade_cost'},
        {text: '$', align: 'left', value: 'upgrade_currency'},
        {text: 'Time', align: 'center', value: 'upgrade_seconds'},
        {text: 'Size', align: 'center', sortable: false},
        {text: 'Description', align: 'center', value: 'description'}
      ],
      pagination: {'sortBy': 'name', 'descending': true, 'rowsPerPage': 20}
    }
  },

  components: {
  },

  created: function () {
    this.init()
  },

  methods: {
    init: async function () {
      const r = await axios.get(this.roomsEndpoint)
      let data = []
      for (const k in r.data.data) {
        const v = r.data.data[k]
        data.push(v)
      }
      data.sort((a, b) => b.rarity_order - a.rarity_order)
      this.rooms = data
      return this.items
    },

    shipSelected () {
      if (typeof this.searchString === 'string') {
        this.getChar(this.searchString)
      } else {
        this.getChar(this.searchString.name)
      }
    },

    onSearch (search, loading) {
      if (search.length >= 2) {
        this.getNames(search)
      } else {
        this.getNames('')
      }
    },

    spriteStyle (s) {
      return styleFromSprite(s)
    },

    currencySprite (currency) {
      switch (currency) {
        case 'starbux':
          return this.buxSprite()
        case 'gas':
          return this.gasSprite()
        case 'mineral':
          return this.mineralSprite()
        case 'supply':
          return this.supplySprite()
        default:
          return ''
      }
    },

    onImageLoad (event) {
      // get real image size from img element
      // This still isn't working on Safari
      const imageEle = event.path[0]
      const img = new Image()
      img.onload = () => {
        imageEle.setAttribute('width', img.naturalWidth)
        imageEle.setAttribute('height', img.naturalHeight)
      }
      img.src = imageEle.href.baseVal
    },

    fieldFilter (items, search, filter) {
      search = search.toString().toLowerCase()
      return items.filter(row =>
        filter(row['name'], search) ||
        filter(row['type'], search) ||
        filter(row['short_name'], search) ||
        filter(row['description'], search)
      )
    }
  }
}
</script>

<style>
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
