<template>
  <div>
    <v-app dark>
      <ps-header/>
      <v-container v-if="!showData">
        <v-layout class="column align-center">
          Research
          <v-text-field
            v-model="search"
            append-icon="search"
            id="search"
            label="Search"
          ></v-text-field>
          <br/>

          <v-data-table
            :headers="changeHeaders"
            :items="research"
            :pagination.sync="changePagination"
            :search="search"
          >
            <template slot="items" slot-scope="i">
              <td class="text-xs-right">
                <crew v-if="i.item.type === 'char'" :char="i.item.char"/>
                <div v-else class="block my-1" :style="spriteStyle(i.item.sprite)"></div>
              </td>
              <td class="text-xs-left">
                {{ i.item.name }}
              </td>
              <td class="text-xs-right">{{ i.item.lab_level }}</td>
              <td class="text-xs-left">{{ i.item.required_research_name }}</td>
              <td class="text-xs-left">{{ i.item.research_type }}</td>
              <td>
                <template v-if="i.item.gas_cost > 0">
                  <div class="text-xs-right">{{ i.item.gas_cost }}
                    <div class="block middle" :style="gasSprite()"></div>
                  </div>
                </template>
                <template v-if="i.item.starbux_cost > 0">
                  <div class="text-xs-right">{{ i.item.starbux_cost }}
                    <div class="block middle" :style="buxSprite()"></div>
                  </div>
                </template>
              </td>
              <td class="text-xs-right">{{ formatTime(i.item.research_seconds) }}</td>
            </template>
          </v-data-table>
        </v-layout>
      </v-container>
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
import Crew from './Crew'
import Header from './Header'
import 'vuetify/dist/vuetify.min.css'
import mixins from './Common.vue.js'
require('../assets/common.css')

Vue.use(VueAnalytics, {
  id: 'UA-67866007-2',
  checkDuplicatedScript: true
})

Vue.component('crew', Crew)
Vue.component('ps-header', Header)

function styleFromSprite (s, color = '', border = 0, ninepatch = 0) {
  if (Object.keys(s).length === 0) {
    return {}
  }
  return {
    background: `${color} url('//pixelstarships.s3.amazonaws.com/${s.source}.png') -${s.x}px -${s.y}px`,
    width: `${s.width}px`,
    height: `${s.height}px`,
    border: `${border}px solid lightgrey`,
    imageRendering: 'pixelated'
  }
}

export default {
  mixins: [mixins],

  data () {
    return {
      search: '',
      devMode: process.env.NODE_ENV === 'development',
      research: [],
      showData: false,
      changeHeaders: [
        {text: 'Image', align: 'center', sortable: false},
        {text: 'Name', value: 'name'},
        {text: 'Lab Level', value: 'lab_level', align: 'right'},
        {text: 'Requirement', value: 'required_research_name', align: 'left'},
        {text: 'Type', value: 'research_type', align: 'left'},
        {text: 'Cost', value: 'cost', align: 'right'},
        {text: 'Upgrade Time', value: 'research_seconds', align: 'right'}
      ],
      changePagination: {sortBy: 'lab_level', rowsPerPage: 25}
    }
  },

  created: function () {
    this.getData()
  },

  methods: {
    getData: async function () {
      const res = await axios.get(this.researchEndpoint)
      this.research = Object.values(res.data.data)
      this.research.forEach(x => {
        x.cost = x.gas_cost + x.starbux_cost
      })
    },

    getAllAttributes (element) {
      let attr = element.attributes
      if (element.elements) {
        element.elements.map(e => {
          if (!('elements' in e)) {
            Object.entries(e.attributes).map(a => {
              attr[e.name + '_' + a[0]] = a[1]
            })
          };
        })
      }
      return attr
    },

    diffAttributes (newAttr, oldAttr) {
      let changes = {
        new: [],
        changed: [],
        removed: []
      }
      if (!oldAttr) {
        changes.new = Object.entries(newAttr)
      } else {
        Object.entries(newAttr).map(v => {
          if (!(v[0] in oldAttr)) {
            changes.new.push(v)
          } else if (v[1] !== oldAttr[v[0]]) {
            changes.changed.push([v[0], oldAttr[v[0]], v[1]])
            delete oldAttr[v[0]]
          } else {
            delete oldAttr[v[0]]
          }
        })
      }
      changes.removed = oldAttr ? Object.entries(oldAttr) : []
      return changes
    },

    spriteStyle (s) {
      return styleFromSprite(s)
    }
  }
}
</script>

<style>
  .record-field {
    max-width: 250px;
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
