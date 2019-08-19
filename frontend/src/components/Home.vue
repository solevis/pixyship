<template>
  <div>
    <v-app dark>
      <ps-header/>

      <v-container id="offers" v-if="!showData">
        <v-layout class="column align-center">
          <strong>Daily Offers</strong>
          <v-data-table
            :headers="offerHeaders"
            :items="offers"
            hide-actions
          >
            <template slot="items" slot-scope="i">
              <td :class="[isExpired(i.item.expires) ? 'expired' : '', 'text-xs-right']">{{ i.item.description }}</td>
              <td :class="[isExpired(i.item.expires) ? 'expired' : '', 'text-xs-right']">
                <template v-if="i.item.cost">
                  {{ i.item.cost.price }}
                  <div class="block middle" :style="currencySprite(i.item.cost.currency)"></div>
                </template>
              </td>
              <td>
                <div v-for="o in i.item.objects">
                  <template v-if="o.type === 'Item' || o.type === 'Room'">
                    {{ o.count }} <div class="block" :style="spriteStyle(o.object.sprite)"></div>
                    <div :class="[o.object.rarity, 'block', 'nowrap', 'bold']">{{ o.object.name }}</div>
                  </template>
                  <template v-else-if="o.type === 'Character'">
                    <crew :char="o.object" name="right"/>
                  </template>
                  <template v-else-if="o.type === 'Currency'">
                    {{ o.count }} <div class="block middle" :style="currencySprite(o.object.currency)"></div>
                  </template>
                  <template v-else>
                    <div>{{ o.type }}</div>
                  </template>
                </div>
              </td>
              <td :class="[isExpired(i.item.expires) ? 'expired' : '', 'text-xs-left']">
                <template v-for="d in i.item.details">
                  {{ d }}<br/>
                </template>
                <template vif="i.item.expires">
                  {{ nowTime(i.item.expires) }}
                </template>
              </td>
            </template>
          </v-data-table>
        </v-layout>

        <v-layout justify-center class="mt-4">
          <v-flex xs2>
            <strong><a href="/changes">Changes</a></strong>
          </v-flex>
        </v-layout>
        <v-layout justify-center>
          <v-flex xs1>
            <div>Most Recent</div>
            <Strong>{{ nowTime(changeLatest) }}</Strong>
          </v-flex>
          <v-flex xs1>
            <div># Today</div>
            <Strong>{{ changesToday }}</Strong>
          </v-flex>
          <!--<v-flex xs1>-->
            <!--<div># Yesterday</div>-->
            <!--<Strong>{{ changesYesterday }}</Strong>-->
          <!--</v-flex>-->
          <v-flex xs1>
            <div># This Week</div>
            <Strong>{{ changesThisWeek }}</Strong>
          </v-flex>
        </v-layout>

        <v-layout justify-center class="mt-4 text-xs-left">
          <v-flex xs6 v-if="news.news_moment">
            <h3>News</h3> ({{ news.news_moment.format('M/D LT') }})
            <p v-if="news.news_moment">{{ news.news }}
            <p class="small error">{{ news.maintenance }}</p>
          </v-flex>
        </v-layout>

        <!--<v-layout justify-center class="mt-4 text-xs-left">-->
          <!--<v-flex xs6 v-if="news.news_moment">-->
            <!--<h3>Announcement</h3>-->
            <!--<div>-->
              <!--Some things have changed, watch out for rough edges.-->
            <!--</div>-->
          <!--</v-flex>-->
        <!--</v-layout>-->

        <!--<v-layout justify-center class="mt-4 text-xs-left">-->
          <!--<v-flex xs6>-->
            <!--<h3>Tournament</h3>-->
            <!--<p>{{ news.tournament_news }}</p>-->
          <!--</v-flex>-->
        <!--</v-layout>-->

      </v-container>

      <!--<a href="https://discordapp.com/channels/458802127238725632/476911589987975172">PixyShip Discord</a>-->
    </v-app>
  </div>
</template>

<script>

import axios from 'axios'
import Vue from 'vue'
import {OrbitSpinner} from 'epic-spinners'
import VueAnalytics from 'vue-analytics'
import moment from 'moment'
import Crew from './Crew'
import Header from './Header'
import VueClipboard from 'vue-clipboard2'
import 'vuetify/dist/vuetify.min.css'
import mixins from './Common.vue.js'
require('../assets/common.css')
var convert = require('xml-js')

Vue.use(VueAnalytics, {
  id: 'UA-67866007-2',
  checkDuplicatedScript: true
})

Vue.component('crew', Crew)
Vue.component('ps-header', Header)
Vue.use(VueClipboard)

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

function embedSpriteStyle (s, color = '', border = 0) {
  s.style = styleFromSprite(s, color, border)
}

export default {
  mixins: [mixins],

  data () {
    return {
      devMode: process.env.NODE_ENV === 'development',
      searchString: '',
      selected: '',
      shipNames: [],
      shipSearch: null,
      message: '',
      chars: [],
      rooms: [],
      items: [],
      upgrades: [],
      user: {},
      ship: {},
      daily: {},
      offers: [],
      changes: [],
      changeLatest: null,
      changesToday: 0,
      changesYesterday: 0,
      changesThisWeek: 0,
      news: {},
      spinner: 'display: none',
      showData: false,
      errorMessage: '',
      shipData: [],
      shipList: {},
      userMinerals: null,
      userGas: null,
      confirmMessage: '',
      showRoomUpgrades: true,
      charHeaders: [
        {text: 'Order', align: 'center', sortable: false},
        {text: 'Level', align: 'left', sortable: false},
        {text: 'Name', align: 'left', sortable: false},
        {text: 'Equip', align: 'left', sortable: false},
        {text: 'Rarity', align: 'left', sortable: false},
        {text: 'HP', align: 'left', sortable: false},
        {text: 'Attack', align: 'left', sortable: false},
        {text: 'Repair', align: 'left', sortable: false},
        {text: 'Special', align: 'left', sortable: false},
        {text: 'Ability', align: 'left', sortable: false},
        {text: 'Pilot', align: 'left', sortable: false},
        {text: 'Science', align: 'left', sortable: false},
        {text: 'Engine', align: 'left', sortable: false},
        {text: 'Weapon', align: 'left', sortable: false},
        {text: 'Fire', align: 'left', sortable: false},
        {text: 'Stamina', align: 'left', sortable: false},
        {text: 'Training', align: 'left', sortable: false},
        {text: 'Speed', align: 'left', sortable: false}
      ],
      basicHeaders: [
        {text: 'Order', align: 'center', sortable: false},
        {text: 'Level', align: 'left', sortable: false},
        {text: 'Name', align: 'left', sortable: false},
        {text: 'Special', align: 'left', sortable: false}
      ],
      offerHeaders: [
        {text: 'Description', value: 'description', align: 'right', sortable: false},
        {text: 'Cost', value: 'cost', align: 'right', width: '100px', sortable: false},
        {text: 'Offer', value: 'offer', width: '250px', sortable: false},
        {text: 'Details', value: 'details', sortable: false}
      ],
      changeHeaders: [
        {text: 'Image', align: 'right', sortable: false},
        {text: 'Name', value: 'name'},
        {text: 'Date', value: 'moment', align: 'center'},
        {text: 'Change', value: 'change_type', align: 'center'}
      ],
      changePagination: {'sortBy': 'moment', 'descending': true},
      confirmDialog: false,
      tab: 0
    }
  },

  components: {
    OrbitSpinner
  },

  mounted () {
    if (localStorage.shipList) {
      try {
        this.shipList = JSON.parse(localStorage.getItem('shipList')) || {}
      } catch (e) {
        localStorage.removeItem('shipList')
      }
      // console.log(this.shipList);
      if (typeof this.shipList === 'string') {
        this.shipList = {}
      }
    }
    this.shipData = this.getShipData()

    const q = this.$route.query
    if (q && q.search) this.getChar(q.search)
  },

  created: function () {
    this.getDaily()
  },

  watch: {
  },

  methods: {
    getShipData () {
      return Object.values(this.shipList).map(v => ({
        last: 0,
        name: v.name,
        trophies: v.trophies,
        verified: v.verified
      }))
    },

    copyUrl () {
      this.$copyText(window.location.href)
    },

    openShipInBuilder () {
      if (!this.ship) return

      let path = '/builder?ship=' + this.ship.id
      if (this.rooms) {
        path += '&rooms=' + this.rooms.map(r => `${r.column},${r.row},${r.design_id}`).join('-')
      }
      window.location.href = path
    },

    getChar (searchName) {
      if (!searchName) {
        return
      }
      this.spinner = 'display: inline-block'
      this.showData = false
      this.errorMessage = ''
      const endpoint = this.shipEndpoint + encodeURIComponent(searchName)
      const key = this.getKeyFromName(searchName)
      axios.get(endpoint, {
        withCredentials: true,
        params: {key: key}
      })
        .then(r => {
          // this.shipData = getShipData();

          if (r.data.data.status === 'not found') {
            this.errorMessage = "Can't find a ship for \"" + searchName + '"'
          } else {
            this.chars = r.data.data.chars
            this.rooms = r.data.data.rooms
            this.items = r.data.data.items
            this.user = r.data.data.user
            this.upgrades = r.data.data.upgrades
            embedSpriteStyle(this.user.sprite, 'grey')
            embedSpriteStyle(this.user.alliance_sprite, 'grey')
            this.ship = r.data.data.ship
            embedSpriteStyle(this.ship.exterior_sprite)
            embedSpriteStyle(this.ship.interior_sprite)
            embedSpriteStyle(this.ship.logo_sprite, 'grey')
            this.showData = true
            if (this.user.confirmed) {
              this.columns = ['character_id', 'level', 'name', 'equipment', 'rarity_order', 'hp', 'attack', 'repair',
                'special_ability', 'ability', 'pilot', 'science', 'engine', 'weapon', 'fire_resist', 'stamina',
                'training', 'walk']
            } else {
              this.columns = ['character_id', 'level', 'name', 'special_ability']
              this.user.verified = false
              this.user.key = null
            }

            this.updateShipList(this.user.id, this.user)
          }
          this.spinner = 'display: none'
          this.$router.replace('/?search=' + searchName)
        })
        .catch(_ => {
          this.spinner = 'display: none'
          this.errorMessage = 'In space, no one can hear you scream.'
        })
    },

    getKeyFromName (name) {
      const key = Object
        .values(this.shipList)
        .filter(x => x.name === name)
        .map(x => x.key)
      return key[0]
    },

    updateShipList (id, data) {
      this.shipList[id] = {...(this.shipList[id] || {}), ...data}
      localStorage.setItem('shipList', JSON.stringify(this.shipList))
      this.shipData = this.getShipData()
    },

    getDaily: async function () {
      const r = await axios.get(this.dailyEndpoint)
      this.offers = r.data.data.offers
      this.news = r.data.data.news
      this.news.news_moment = moment.utc(this.news.news_date).local()
      const changes = await axios.get(this.changesEndpoint)
      this.changes = changes.data.data.map(x => {
        x.attributes = this.getAllAttributes(convert.xml2js(x.data).elements[0])
        x.oldAttributes = x.old_data ? this.getAllAttributes(convert.xml2js(x.old_data).elements[0]) : null
        x.moment = moment.utc(x.changed_at)
        x.changes = this.diffAttributes(x.attributes, x.oldAttributes)
        return x
      })
      const oneDay = moment().add(-1, 'days')
      const twoDay = moment().add(-2, 'days')
      const oneWeek = moment().add(-7, 'days')
      this.changesToday = this.changes.filter(c => c.moment > oneDay).length
      this.changesYesterday = this.changes.filter(c => c.moment > twoDay).length
      this.changesThisWeek = this.changes.filter(c => c.moment > oneWeek).length
      this.changeLatest = Math.max(...(this.changes.map(c => c.moment)))
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

    shipSelected () {
      if (typeof this.searchString === 'string') {
        this.getChar(this.searchString)
      } else if (this.searchString) {
        this.getChar(this.searchString.name)
      }
    },

    spriteStyle (s) {
      return styleFromSprite(s)
    },

    currencySprite (currency) {
      switch (currency.toLowerCase()) {
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

    isExpired (time) {
      if (!time) return false
      const res = moment.utc(time) < moment()
      return res
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
    }
  }
}
</script>

<style>
  .highlight {
    color: #24E3FF;
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

  #offers {
    margin: 0 auto;
    flex: unset;
    min-width: 600px;
  }

  table.v-datatable {
    background-color: black !important;
  }

  .v-list__tile {
    height: 25px;
  }

  .trophy-count {
    width: 40px;
  }

  .v-autocomplete {
    flex: unset;
  }

  .card__text {
    background-color: #333;
  }

  .application .theme--dark.table tbody tr:hover:not(.datatable__expand-row), .theme--dark .table tbody tr:hover:not(.datatable__expand-row) {
    background: #333;
  }

  table.table thead tr {
    height: inherit;
  }

  table.table tbody td, table.table tbody th {
    height: inherit;
  }

  table.table thead th {
    font-size: 14px;
    color: white;
    font-weight: bold;
  }

  table.table tbody td {
    font-size: 14px;
  }

  .application.theme--dark {
    background-color: black;
  }

  .theme--dark .table {
    background: black;
  }

  /*table.table tbody td:first-child {*/
    /*padding: 0 2px !important;*/
  /*}*/

  table.table tbody td, table.table thead th {
    padding: 0 2px !important;
  }

  /*table.table thead th {*/
    /*padding: 0 2px !important;*/
  /*}*/

  html {
    background-color: black;
    color: white;
  }

  .main {
    margin-top: 10px;
  }

  .center {
    margin: 0 auto;
  }

  td.center {
    text-align: center;
  }

  .char-part {
    margin: 0px auto;
  }

  .char {
    max-width: 25px;
    margin: 0px;
  }

  /* this doesn't work except on multiple lines */
  .name {
    line-height: .9;
  }

  span.name {
    display: inline-block;
    line-height: .9;
  }

  .fs-80p {
    font-size: 80%;
  }

  .lh-9 {
    line-height: .9;
  }

  .name span {
    color: gray;
    font-size: 60%;
  }

  .char-sprite {
    width: 40px;
    /*margin: 0 auto;*/
    display: table;
  }

  div.upgradable {
    color: #1be600;
  }

  rect.upgradable {
    fill: transparent;
    stroke-width: 2px;
    stroke: #1be600;
  }

  .power-gen{
    fill: lime;
    font-weight: 700;
    font-size: 8px;
  }

  .power-use {
    fill: yellow;
    font-weight: 700;
    font-size: 8px;
  }

  .room-name {
    fill: white;
    font-size: 8px;
  }

  .defense {
    fill: orange;
    font-weight: 700;
    font-size: 8px;
    text-shadow:
      -1px -1px 0 #000,
      1px -1px 0 #000,
      -1px 1px 0 #000,
      1px 1px 0 #000;
  }

  .room {
    margin: 0
  }

  .room > body {
    margin: 0
  }

  .row {
    display: none;
  }

  .stats {
    columns: 150px;
    max-width: 750px;
  }

  .stat-card {
    width: 150px;
  }

  .stat-card span {
    font-weight: bold;
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

  .VueTables__child-row-toggler {
    width: 16px;
    height: 16px;
    line-height: 16px;
    display: block;
    margin: auto;
    text-align: center;
    background-color: red;
  }

  .char-item {
    display: inline-block;
  }

  .orbit-spinner {
    margin-top: 20pt;
  }

  .items {
    columns: 225px;
    max-width: 750px;
  }

  .inline {
    display: inline-block;
    margin: 0 5px;
  }

  .block {
    display: inline-block;
  }

  .item div{
    display: inline-block;
    margin: 0 5px;
  }

  .rarity {
    text-transform: capitalize;
  }

  .special-ability {
    font-size: 80%;
  }

  /* Rarities*/
  .item {
    margin: 5px;
    min-width: 200px;
  }

  .name {
    font-weight: bold;
  }

  .name-link {
    font-weight: bold;
    padding: 0 5px;
    margin: 0 2px;
    background-color: #333;
    border-radius: 10px;
    color: white;
  }

  .verified {
    color: #d5aa2a;
  }

  .name-link:hover {
    cursor: pointer;
  }

  .logo {
    width: 200px;
  }

  .confirm {
    max-width: 75px;
  }

  .confirm-message {
    margin: 2px 10px;
    color: red;
  }

  .unused {
    color: grey;
  }

  .item-sprite {
    min-width: 40px;
  }

  .item-sprite div {
    display: table;
    margin: 0 auto;
  }

  .input-ship {
    max-width: 250px;
    margin: 0 auto;
  }

  .input-ship .selected-tag {
    display: none;
  }

  span.char-order {
    color: white;
    font-weight: 700;
    font-size: 9px;
    text-shadow:
      -1px -1px 0 #000,
      1px -1px 0 #000,
      -1px 1px 0 #000,
      1px 1px 0 #000;
    display: inline;
    z-index: 1;
    position: absolute;
    transform:translate(0, -10px);
  }

  .bold {
    font-weight: bold;
  }

  .alignleft {
    float: left;
  }

  .alignright {
    float: right;
  }

  input.confirm {
    color: white;
    background-color: black;
    border: 2px solid white;
    border-top-width: 0;
    border-left-width: 0;
    border-right-width: 0;
    border-radius: 4px;
  }

  .dark-button {
    color: white;
    border-width: 0px;
    border-radius: 4px;
    background : #333;
    filter : progid:DXImageTransform.Microsoft.gradient( startColorstr='#5f6166', endColorstr='#00060a',GradientType=0 );
  }

  :visited {
    color: #24E3FF;
  }

  :link {
    color: #FF5656;
    text-decoration: none;
  }

  .main-table td:nth-child(1){
    text-align: right;
    color: grey;
  }

  .ps-left {
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

  .upgrades td:nth-child(1){
    color: white;
  }

  table.upgrades {
    display: inline-block;
    vertical-align: top;
  }

  table > tr {
    vertical-align: top;
  }

  td > div {
    text-align: left;
    vertical-align: top;
    display: block;
  }

  figure {
    break-inside: avoid;
    background-color: white;
    -webkit-margin-start: 0;
    -webkit-margin-end: 0;
    text-align: center;
  }

  figure div {
    display: block;
    margin-left: auto;
    margin-right: auto;
  }

  .main-table {
    margin: 0px auto;
    vertical-align: top;
  }

  .five-margin {
    margin-left: 5px;
  }

  table.VueTables__table tr > td:nth-child(4) {
    text-align: left;
  }

  .example {
    margin-top: 20px;
  }

  .collapse.help .collapse-header {
    background: #333;
    padding: 0 20px 0 40px;
  }

  .collapse.help .collapse-content-box {
    padding: 10px;
    border: 0 none;
    max-width: 600px;
    text-align: left;
  }

  span.correct {
    color: #1be600;
  }

  span.wrong, .error {
    color: red;
  }

  .small {
    font-size: small;
  }

  .smaller {
    font-size: x-small;
  }

  .daily {
    display: inline-block;
    vertical-align: top;
    background-color: #222;
    border-radius: 4px;
    min-width: 100px;
    max-width: 180px;
    padding: 2px;
    margin: 2px;
  }

  .expired {
    opacity: 0.5;
  }

  .middle {
    vertical-align: middle;
  }

  .nowrap {
    white-space: nowrap;
  }

  .col-left-margin {
    padding-left: 10px;
  }

</style>
