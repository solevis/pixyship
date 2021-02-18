<template>
  <div>
    <ps-header/>
    Prestige recipies
    <br/><br/>
    <div class="center">
      <crew v-if="loaded" :char="chars[crewId]" name="bottom"/>
      <v-layout justify-center>
        <v-data-table
          id="target-stats"
          v-if="loaded"
          :headers="headers"
          :items="targetChar"
          hide-actions
        >
          <template slot="items" slot-scope="i">
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
              <div class="stat">{{ i.item.hp[1] }}<br/>
                <span>{{ i.item.hp[0] }}</span>
              </div>
            </td>
            <td>
              <div class="stat">{{ i.item.attack[1] }}<br/>
                <span>{{ i.item.attack[0] }}</span>
              </div>
            </td>
            <td>
              <div class="stat">{{ i.item.repair[1] }}<br/>
                <span>{{ i.item.repair[0] }}</span>
              </div>
            </td>
            <td>
              <div class="special-ability">
                <div :style="spriteStyle(i.item.ability_sprite)" :title="i.item.special_ability"></div>
              </div>
            </td>
            <td>
              <div class="stat">{{ i.item.ability[1] }}<br/>
                <span>{{ i.item.ability[0] }}</span>
              </div>
            </td>
            <td>
              <div class="stat">{{ i.item.pilot[1] }}<br/>
                <span>{{ i.item.pilot[0] }}</span>
              </div>
            </td>
            <td>
              <div class="stat">{{ i.item.science[1] }}<br/>
                <span>{{ i.item.science[0] }}</span>
              </div>
            </td>
            <td>
              <div class="stat">{{ i.item.research[1] }}<br/>
                <span>{{ i.item.research[0] }}</span>
              </div>
            </td>
            <td>
              <div class="stat">{{ i.item.engine[1] }}<br/>
                <span>{{ i.item.engine[0] }}</span>
              </div>
            </td>
            <td>
              <div class="stat">{{ i.item.weapon[1] }}<br/>
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
      </v-layout>
      <br/>
      <table class="center">
        <tr class="top">
          <td>
            <table class="curvable">
              <tr>
                <td v-if="loaded" colspan="2">Combine both for {{ chars[crewId].name }}</td>
              </tr>
              <tr v-for="(olist, t) in to">
                <td class="right-curve-border">
                  <table class="fill">
                    <tr v-for="o in olist">
                      <td>
                        <crew :char="chars[o]" name="left"/>
                      </td>
                    </tr>
                  </table>
                </td>
                <td>
                  <crew :char="chars[t]" name="right"/>
                </td>
              </tr>
            </table>
          </td>
          <td>
            <table class="curvable">
              <tr>
                <td v-if="loaded" colspan="2">Combine {{ chars[crewId].name }} with &laquo; to get &raquo;</td>
              </tr>
              <tr v-for="(olist, t) in from">
                <td class="right-curve-border">
                  <table class="fill">
                    <tr v-for="o in olist">
                      <td>
                        <crew :char="chars[o]" name="left"/>
                      </td>
                    </tr>
                  </table>
                </td>
                <td>
                  <crew :char="chars[t]" name="right"/>
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </div>
    <br/>
    <br/>
    <div></div>
    <div>
        <a href="http://www.pixelstarships.com">Pixel Starships</a>
      </div>
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
      crewId: this.$route.params.id,
      chars: [],
      targetChar: [],
      from: [],
      to: [],
      data: null,
      loaded: false,
      headers: [
        // {text: 'Order', align: 'center', value: 'id'},
        // {text: 'Name', align: 'center', value: 'name'},
        {text: 'Equip', align: 'center', value: 'equipment', sortable: false},
        {text: 'Rarity', align: 'center', value: 'rarity_order', sortable: false},
        {text: 'HP', align: 'center', value: 'hp[1]', sortable: false},
        {text: 'Attack', align: 'center', value: 'attack[1]', sortable: false},
        {text: 'Repair', align: 'center', value: 'repair[1]', sortable: false},
        {text: 'Special', align: 'center', value: 'special_ability', sortable: false},
        {text: 'Ability', align: 'center', value: 'ability[1]', sortable: false},
        {text: 'Pilot', align: 'center', value: 'pilot[1]', sortable: false},
        {text: 'Science', align: 'center', value: 'science[1]', sortable: false},
        {text: 'Research', align: 'center', value: 'research[1]', sortable: false},
        {text: 'Engine', align: 'center', value: 'engine[1]', sortable: false},
        {text: 'Weapon', align: 'center', value: 'weapon[1]', sortable: false},
        {text: 'Fire', align: 'center', value: 'fire_resist', sortable: false},
        {text: 'Training', align: 'center', value: 'training_limit', sortable: false},
        {text: 'Speed', align: 'center', value: 'run', sortable: false}
      ]
    }
  },

  components: {
  },

  created: function () {
    this.getCrew()
    // console.log(this.$route)
  },

  methods: {
    getCrew: async function () {
      const r = await axios.get(this.prestigeEndpoint + this.crewId)
      // TODO: This is ugly, fix it
      let charMap = {}
      for (let c of r.data.data.chars) {
        charMap[c.id] = c
      }
      this.chars = charMap
      this.from = r.data.data.from
      this.to = r.data.data.to
      this.data = r.data.data
      this.targetChar = [this.chars[this.crewId]]
      this.loaded = true
    },

    spriteStyle (s) {
      return styleFromSprite(s)
    }
  }
}
</script>

<style>
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

  .page-link, .page-item.disabled .page-link  {
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

  :visited {
    color: #24E3FF;
  }

  :link {
    color: #FF5656;
    text-decoration: none;
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

  .bottom {
    vertical-align: bottom;
  }

  .fill {
    width: 100%;
  }

  .side-by-side {
    float: left
  }

  .bold {
    text-weight: bold;
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

  td.show-height {
    border-left: solid 5px #666;
    border-radius: 12px;
  }

  td.right-curve-border {
    border-right: solid 5px #666;
    border-radius: 12px;
    padding: 5px;
  }

  table.curvable {
    border-collapse: separate;
  }
</style>
