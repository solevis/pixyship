<template>
  <div>
    <v-app dark>
      <ps-header/>
      Changes
      <v-container v-if="!showData">
        <v-layout class="column">
          Latest Changes - Chars, Items, Rooms and Ships
          <v-data-table
            :headers="changeHeaders"
            :items="changes"
            :pagination.sync="changePagination"
          >
            <template slot="items" slot-scope="i">
              <td class="text-xs-right">
                <crew v-if="i.item.type === 'char'" :char="i.item.char"/>
                <div v-else class="block my-1" :style="spriteStyle(i.item.sprite)"></div>
              </td>
              <td class="text-xs-left">
                {{ i.item.name }}
              </td>
              <td class="text-xs-center">{{ nowTime(i.item.changed_at) }}</td>
              <td class="text-xs-left">
                <table v-if="i.item.change_type === 'Changed'">
                  <tr v-for="c in i.item.changes.new" class="nobreak">
                    <td><div class="success--text">{{ c[0].replace('_', ' ') }}</div></td>
                    <td></td>
                    <td><div :title="c[1]" class="success--text text-truncate record-field">{{ c[1] }}</div></td>
                  </tr>
                  <tr v-for="c in i.item.changes.changed" class="nobreak">
                    <td><div class="warning--text">{{ c[0].replace('_', ' ') }}</div></td>
                    <td><div :title="c[1]" class="grey--text text-truncate record-field">{{ c[1] }}</div></td>
                    <td><div :title="c[2]" class="warning--text text-truncate record-field">{{ c[2] }}</div></td>
                  </tr>
                  <tr v-for="c in i.item.changes.removed" class="nobreak">
                    <td><div class="error--text">{{ c[0].replace('_', ' ') }}</div></td>
                    <td><div :title="c[1]" class="error--text text-truncate record-field">{{ c[1] }}</div></td>
                  </tr>
                </table>
                <span v-else class="ml-2 success--text">{{ i.item.change_type }}</span>
              </td>
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
import moment from 'moment'
import Crew from './Crew'
import Header from './Header'
import 'vuetify/dist/vuetify.min.css'
import mixins from './Common.vue.js'
require('../assets/common.css')
const convert = require('xml-js')

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
      devMode: process.env.NODE_ENV === 'development',
      message: '',
      changes: [],
      showData: false,
      errorMessage: '',
      changeHeaders: [
        {text: 'Image', align: 'right', sortable: false},
        {text: 'Name', value: 'name'},
        {text: 'Date', value: 'moment', align: 'center'},
        {text: 'Change', value: 'change_type', align: 'center'}
      ],
      changePagination: {sortBy: 'moment', descending: true, rowsPerPage: 20},
      confirmDialog: false,
      tab: 0
    }
  },

  created: function () {
    this.getDaily()
  },

  methods: {
    getDaily: async function () {
      const changes = await axios.get(this.changesEndpoint)
      this.changes = changes.data.data.map(x => {
        x.attributes = this.getAllAttributes(convert.xml2js(x.data).elements[0])
        x.oldAttributes = x.old_data ? this.getAllAttributes(convert.xml2js(x.old_data).elements[0]) : null
        x.moment = moment.utc(x.changed_at)
        x.changes = this.diffAttributes(x.attributes, x.oldAttributes)
        return x
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
