<template>
  <div>
    <v-app dark>
      <ps-header/>
      Compare crew by searching with a comma separated list
      <br/>
      Crew
      <br/>
      <div class="center">
        <v-layout row>
          <v-flex xs1 offset-xs1 class="px-2">
            <v-text-field
              v-model="level"
              type="number"
              label="Level"
              min="1"
              max="40"
              :value="level"
            ></v-text-field>
          </v-flex>
          <v-flex xs9>
            <v-text-field
              v-model="search"
              append-icon="search"
              id="search"
              label="Search"
              placeholder="search name and ability"
            ></v-text-field>
          </v-flex>
        </v-layout>
        <!--<v-slider-->
          <!--v-model="level"-->
          <!--:min="1"-->
          <!--:max="40"-->
          <!--always-dirty-->
          <!--thumb-label="always"-->
          <!--ticks-->
          <!--label="Level"-->
        <!--&gt;</v-slider>-->
        <br/>
        <v-data-table
          :headers="headers"
          :items="crew"
          :rows-per-page-items="[10,20,50,100,200,{'text':'$vuetify.dataIterator.rowsPerPageAll','value':-1}]"
          :search="search"
          :pagination.sync="pagination"
          :custom-filter="fieldFilter"
          :filter="multipleFilter"
        >
          <template slot="items" slot-scope="i">
            <td><!-- Order -->
              <div class="center char-sprite">
                <crew :char="i.item" :tip="false"/>
              </div>
            </td>
            <td><!-- Name -->
              <div :class="[i.item.rarity, 'lh-9', 'name']">
                <div class="text-xs-left">{{ i.item.name }}</div>
              </div>
            </td>
            <td>
              <div class="ps-left equip">
                <div v-for="(s, k) in i.item.equipment">
                  <div v-if="s.name"
                    :title="`${k}: +${s.bonus} ${s.enhancement} ${s.extra_bonus ? '+' + s.extra_bonus : ''} ${s.extra_enhancement}`">
                    <div class="char-item" :style="spriteStyle(s.sprite)"></div>
                    {{ s.name }}
                  </div>
                  <template v-else>
                    <div class="unused">{{ k }}</div>
                  </template>
                </div>
              </div>
            </td>
            <td>
              <div :class="['rarity', i.item.rarity]">{{ i.item.rarity }}</div>
            </td>
            <td>
              <div
                v-if="i.item.collection_sprite"
                :style="spriteStyle(i.item.collection_sprite)"
                :title="i.item.collection_name"
                class="center"
              ></div>
            </td>
            <td>
              <div class="stat">{{ i.item.hp[2] | statFormat(0) }}<br/>
                <span>{{ i.item.hp[0] }}</span>
              </div>
            </td>
            <td>
              <div class="stat">{{ i.item.attack[2] | statFormat() }}<br/>
                <span>{{ i.item.attack[0] }}</span>
              </div>
            </td>
            <td>
              <div class="stat">{{ i.item.repair[2] | statFormat() }}<br/>
                <span>{{ i.item.repair[0] }}</span>
              </div>
            </td>
            <td>
              <div class="special-ability">
                <div :style="spriteStyle(i.item.ability_sprite)" :title="i.item.special_ability"></div>
              </div>
            </td>
            <td>
              <div class="stat">{{ i.item.ability[2] | statFormat() }}<br/>
                <span>{{ i.item.ability[0] }}</span>
              </div>
            </td>
            <td>
              <div class="stat">{{ i.item.pilot[2] | statFormat() }}<br/>
                <span>{{ i.item.pilot[0] }}</span>
              </div>
            </td>
            <td>
              <div class="stat">{{ i.item.science[2] | statFormat() }}<br/>
                <span>{{ i.item.science[0] }}</span>
              </div>
            </td>
            <td>
              <div class="stat">{{ i.item.research[2] | statFormat() }}<br/>
                <span>{{ i.item.research[0] }}</span>
              </div>
            </td>
            <td>
              <div class="stat">{{ i.item.engine[2] | statFormat() }}<br/>
                <span>{{ i.item.engine[0] }}</span>
              </div>
            </td>
            <td>
              <div class="stat">{{ i.item.weapon[2] | statFormat() }}<br/>
                <span>{{ i.item.weapon[0] }}</span>
              </div>
            </td>
            <td>{{ i.item.fire_resist }}</td>
            <td>{{ i.item.training_limit }}</td>
            <td>
              <div>{{ `${i.item.walk}:${i.item.run}` }}</div>
            </td>
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
import Crew from './Crew'
import Header from './Header'
import 'vuetify/dist/vuetify.min.css'
import mixins from './Common.vue.js'
require('../assets/common.css')

Vue.component('crew', Crew)
Vue.component('ps-header', Header)

Vue.use(VueAnalytics, {
  id: 'UA-67866007-2',
  checkDuplicatedScript: true
})
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
      crew: [],
      headers: [
        {text: 'Order', align: 'center', value: 'id'},
        {text: 'Name', align: 'center', value: 'name'},
        {text: 'Equip', align: 'center', value: 'equipment'},
        {text: 'Rarity', align: 'center', value: 'rarity_order'},
        {text: 'Set', align: 'center', value: 'collection'},
        {text: 'HP', align: 'center', value: 'hp[2]'},
        {text: 'Attack', align: 'center', value: 'attack[2]'},
        {text: 'Repair', align: 'center', value: 'repair[2]'},
        {text: 'Special', align: 'center', value: 'special_ability'},
        {text: 'Ability', align: 'center', value: 'ability[2]'},
        {text: 'Pilot', align: 'center', value: 'pilot[2]'},
        {text: 'Science', align: 'center', value: 'science[2]'},
        {text: 'Research', align: 'center', value: 'research[2]'},
        {text: 'Engine', align: 'center', value: 'engine[2]'},
        {text: 'Weapon', align: 'center', value: 'weapon[2]'},
        {text: 'Fire', align: 'center', value: 'fire_resist'},
        {text: 'Training', align: 'center', value: 'training_limit'},
        {text: 'Speed', align: 'center', value: 'run'}
      ],
      level: 40,
      search: '',
      pagination: {'sortBy': 'rarity_order', 'descending': true, 'rowsPerPage': 20}
    }
  },

  watch: {
    level (val) {
      this.updateCurrentLevel()
    }
  },

  components: {
  },

  created: function () {
    this.getCrew()
  },

  filters: {
    statFormat (value, maxDigits = 1) {
      return value.toLocaleString('en-US', {maximumFractionDigits: maxDigits})
    }
  },

  methods: {
    interpolateStat (type, stat) {
      let p = 1 // Linear
      if (type === 'EaseIn') {
        p = 2
      } else if (type === 'EaseOut') {
        p = 0.5
      }
      stat[2] = stat[0] + (stat[1] - stat[0]) * ((this.level - 1) / 39) ** p
    },

    updateCurrentLevel () {
      this.crew.map(c => {
        this.interpolateStat(c.progression_type, c.hp)
        this.interpolateStat(c.progression_type, c.attack)
        this.interpolateStat(c.progression_type, c.repair)
        this.interpolateStat(c.progression_type, c.ability)
        this.interpolateStat(c.progression_type, c.pilot)
        this.interpolateStat(c.progression_type, c.science)
        this.interpolateStat(c.progression_type, c.research)
        this.interpolateStat(c.progression_type, c.engine)
        this.interpolateStat(c.progression_type, c.weapon)
      })
    },

    getCrew: async function () {
      const r = await axios.get(this.crewEndpoint)
      let crew = []
      for (const k in r.data.data) {
        const v = r.data.data[k]
        crew.push(v)
      }
      crew.sort((a, b) => b.rarity_order - a.rarity_order)
      this.crew = crew
      this.updateCurrentLevel()
      return this.crew
    },

    spriteStyle (s) {
      return styleFromSprite(s)
    },

    fieldFilter (items, search, filter) {
      search = search.toString().toLowerCase()
      return items.filter(row =>
        filter(row['name'], search) ||
        filter(row['special_ability'], search) ||
        filter(row['collection_name'], search) ||
        filter(row['rarity'], search)
      )
    }
  }
}
</script>

<style>
  .layout.row{
    display: flex;
  }

  html, body {
    background-color: black;
    color: white;
  }

  table.v-table tbody td {
    font-size: unset !important;
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
  }

  .v-datatable tbody tr:hover {
    background-color: #222 !important;
  }

  .main {
    margin-top: 10px;
  }

  .center {
    margin: 0 auto;
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

</style>
