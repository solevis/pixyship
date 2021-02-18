<template>
  <div>
    <v-app dark>
      <ps-header/>
      Ships
      <br/><br/>
      <div class="center">
        <v-text-field
          v-model="search"
          append-icon="search"
          id="search"
          label="Search"
          placeholder="search room name, short name, and type"
        ></v-text-field>
        <br/>
        <v-data-table
          :headers="headers"
          :items="ships"
          :rows-per-page-items="[10,20,50,100,200,{'text':'$vuetify.dataIterator.rowsPerPageAll','value':-1}]"
          :pagination.sync="pagination"
          :search="search"
          :custom-filter="fieldFilter"
          :filter="multipleFilter"
        >
          <template slot="items" slot-scope="i">
            <td class="text-xs-left name bold">{{ i.item.name }}</td>
            <td class="text-xs-right">{{ i.item.level }}</td>
            <td class="text-xs-right">{{ i.item.space }}</td>
            <td class="text-xs-right">{{ i.item.hp }}</td>
            <td class="center char-sprite">
              <div :style="spriteStyle(i.item.interior_sprite, 1, 2)"></div>
            </td>
            <td class="text-xs-right">{{ i.item.repair_time }}</td>
            <td style="min-width: 100px">
              <template v-if="i.item.mineral_cost > 0">
                <div>{{ i.item.mineral_cost }}
                  <div class="block middle" :style="mineralSprite()"></div>
                </div>
              </template>
              <template v-if="i.item.starbux_cost > 0">
                <div>{{ i.item.starbux_cost }}
                  <div class="block middle" :style="buxSprite()"></div>
                </div>
              </template>
            </td>
            <td style="min-width: 100px">
              <template v-if="i.item.mineral_capacity > 0">
                <div>{{ i.item.mineral_capacity }}
                  <div class="block middle" :style="mineralSprite()"></div>
                </div>
              </template>
              <template v-if="i.item.gas_capacity > 0">
                <div>{{ i.item.gas_capacity }}
                  <div class="block middle" :style="gasSprite()"></div>
                </div>
              </template>
              <template v-if="i.item.equipment_capacity > 0">
                <div>{{ i.item.equipment_capacity }}
                  <div class="block middle" :style="supplySprite()"></div>
                </div>
              </template>
            </td>
            <td class="text-xs-left">{{ i.item.ship_type }}</td>
            <td class="text-xs-left">{{ i.item.description }}</td>
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
import VueAnalytics from 'vue-analytics'
import BootstrapVue from 'bootstrap-vue'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import Header from './Header'
import 'vuetify/dist/vuetify.min.css'
import mixins from './Common.vue.js'

Vue.component('ps-header', Header)
Vue.use(VueAnalytics, {
  id: 'UA-67866007-2',
  checkDuplicatedScript: true
})
Vue.use(BootstrapVue)

function styleFromSprite (s, color = '', border = 0, ninepatch = 0, scale = 1, portScale = 1) {
  if (Object.keys(s).length === 0) {
    return {}
  }
  const fillStr = portScale === 1 ? '' : '/ 100% 100%'
  let obj = {
    background: `${color} url('//pixelstarships.s3.amazonaws.com/${s.source}.png') -${s.x}px -${s.y}px ${fillStr}`,
    width: `${s.width / portScale}px`,
    height: `${s.height / portScale}px`,
    border: `${border}px solid lightgrey`,
    imageRendering: 'pixelated'
  }
  if (scale !== 1) obj.transform = `scale(${scale}, ${scale})`
  return obj
}

export default {
  mixins: [mixins],

  data () {
    return {
      devMode: process.env.NODE_ENV === 'development',
      showInside: true,
      ships: [],
      search: '',
      headers: [
        {text: 'Name', align: 'left', value: 'name'},
        {text: 'Level', align: 'right', value: 'level'},
        {text: 'Space', align: 'right', value: 'space'},
        {text: 'Health', align: 'right', value: 'hp'},
        {text: 'Image', align: 'center', sortable: false},
        {text: 'Secs/Repair', align: 'right', value: 'repair_time'},
        {text: 'Cost', align: 'center', value: 'starbux_cost'},
        {text: 'Capacity', align: 'center', value: 'defense'},
        {text: 'Type', align: 'left', value: 'ship_type'},
        {text: 'Description', align: 'left', value: 'description'}
      ],
      pagination: {'sortBy': 'name', 'descending': true, 'rowsPerPage': 10}
    }
  },

  created: function () {
    this.init()
  },

  methods: {
    init: async function () {
      const r = await axios.get(this.shipsEndpoint)
      let data = []
      for (const k in r.data.data) {
        const v = r.data.data[k]
        let space = 0
        for (let c of v.mask) {
          if (c !== '0') space++
        }
        v.space = space
        data.push(v)
      }
      data.sort((a, b) => b.rarity_order - a.rarity_order)
      this.ships = data
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

    spriteStyle (sprite, scale = 1, portScale = 1) {
      return styleFromSprite(sprite, '', 0, 0, scale, portScale)
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
        filter(row['ship_type'], search) ||
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

  .block {
    display: inline-block;
  }

  .main {
    margin-top: 10px;
  }

  .center {
    margin: 0 auto;
    padding: 0 5px;
  }

  /* this doesn't work except on multiple lines */
  .name {
    line-height: 1;
  }

  :visited {
    color: #24E3FF;
  }

  :link {
    color: #FF5656;
    text-decoration: none;
  }

  .bold {
    font-weight: bold;
  }

  .middle {
    vertical-align: middle;
  }

</style>
