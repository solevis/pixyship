<template>
  <div>
    <v-app dark>
      <ps-header/>
      Players
      <v-container>
        <v-layout class="column">
          <v-autocomplete
            v-model="search"
            :items="data"
            :search-input.sync="searchText"
            label="Search"
            placeholder="search by name"
            :no-filter="true"
            item-text="name">
            <template slot-scope="p" slot="item">
              <div class="text-xs-right lh-1 mr-2" style="width: 3em">{{ p.item.trophies}}</div>
              <div class="text-xs-left lh-1 mr-5" style="width: 10em">{{ p.item.name }}</div>
              <div class="block my-1 mr-1" :style="spriteStyle(p.item.alliance_sprite)"></div>
              {{ p.item.alliance }}
            </template>
          </v-autocomplete>
          <br/>

          <table class="main-table" v-if="showData">
            <tr>
              <td class="ps-left">
                Level {{ ship.level }}
<!--                <div :style="ship.logo_sprite.style" class="middle block"></div>-->
                {{ ship.name }}
<!--                <v-btn @click="copyUrl">Copy Link</v-btn>-->
                <v-btn @click="openShipInBuilder">Edit in Builder</v-btn>
                <br/>
                <template v-if="ship.char_attack">
                  <input v-model="showRoomUpgrades" type="checkbox" v-on:click="confirmOwnership"> Show Upgradable Rooms</input>
                  <br/>
                </template>
              </td>
            </tr>
            <tr>
              <td>
                <svg :style="ship.interior_sprite.style">
                  <g v-for="r in rooms">
                    <svg :x="`${r.column * 25}px`" :y="`${r.row * 25}px`"
                      :viewbox="`${r.sprite.x} ${r.sprite.y} ${r.sprite.width} ${r.sprite.height}`"
                      :width="`${r.sprite.width}px`" :height="`${r.sprite.height}px`">
<!--                      <foreignObject v-if="r.construction" class="room" width="125" height="75">-->
<!--                        <body xmlns="http://www.w3.org/1999/xhtml">-->
<!--                        <div :style="spriteStyle(r.construction_sprite)"></div>-->
<!--                        </body>-->
<!--                      </foreignObject>-->
<!--v-else-->
<!--                      <foreignObject v-if="r.show_frame" class="room" width="125" height="75" x="1" y="11"-->
<!--                        :transform="`scale(1 ${r.height/2})`">-->
<!--                        <body xmlns="http://www.w3.org/1999/xhtml">-->
<!--                        <div class="door" :style="spriteStyle(ship.left_door_sprite)"></div>-->
<!--                        </body>-->
<!--                      </foreignObject>-->
<!--                      <foreignObject v-if="r.show_frame" class="room" width="125" height="75" x="3" y="11"-->
<!--                        :transform="`scale(1 ${r.height/2})`">-->
<!--                        <body xmlns="http://www.w3.org/1999/xhtml">-->
<!--                        <div class="door" :style="spriteStyle(ship.right_door_sprite)"></div>-->
<!--                        </body>-->
<!--                      </foreignObject>-->
                      <foreignObject v-if="r.show_frame" class="room" width="125" height="75"
                        :transform="`scale(${r.sprite.width/75} ${r.sprite.height/50})`">
                        <body xmlns="http://www.w3.org/1999/xhtml">
                        <div :style="spriteStyle(ship.frame_sprite)"></div>
                        </body>
                      </foreignObject>
                      <foreignObject class="room" width="125" height="75">
                        <body xmlns="http://www.w3.org/1999/xhtml">
                        <div :style="spriteStyle(r.sprite)"></div>
                        </body>
                      </foreignObject>
                      <rect v-if="r.upgradable && showRoomUpgrades" class="upgradable" x="1" y="1" :width="r.width * 25 - 2" :height="r.height * 25 - 2"></rect>
                      <text class="room-name" x="2" y="9">{{ r.short_name }}</text>
                      <text class="defense" v-if="r.armor && (r.power_use + r.power_gen > 0)" x="2" y="19">
                        {{ (1 - 100 / (100 + r.defense + r.armor)).toLocaleString('en-US', {style: 'percent'}) }}
                      </text>
                      <text class="power-use" v-if="r.power_use > 0" :x="r.width * 25 - 7" y="9">
                        {{ r.power_use}}
                      </text>
                      <text class="power-gen" v-if="r.power_gen > 0" :x="r.width * 25 - 9" y="9">
                        {{ r.power_gen }}
                      </text>
                    </svg>
                  </g>
                </svg>
              </td>
            </tr>
          </table>

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
      tab: 0, // TODO Check/Remove
      ship: {}
    }
  },

  created: function () {
    this.getData()
  },

  watch: {
    searchText(val) {
        this.getData()
    },

    search(val) {
      // this.searchText(val)
      this.showData = !!val
      this.getChar(val)
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

    // getKeyFromName(name) {
    //   const key = Object
    //     .values(this.shipList)
    //     .filter(x => x.name === name)
    //     .map(x => x.key)
    //   return key[0]
    // },

    getChar(searchName) {
      if (!searchName) {
        return
      }
      this.spinner = 'display: inline-block';
      this.showData = false;
      this.errorMessage = '';
      const endpoint = this.shipEndpoint + encodeURIComponent(searchName);
      console.log(endpoint)
      // const key = this.getKeyFromName(searchName);
      axios.get(endpoint, {
        withCredentials: true,
        params: {key: searchName}
      })
        .then(r => {
          // this.shipData = getShipData();

          if (r.data.data.status === 'not found') {
            this.errorMessage = "Can't find a ship for \"" + searchName + '"'
          } else {
            this.rooms = r.data.data.rooms;
            this.user = r.data.data.user;
            // this.upgrades = r.data.data.upgrades;
            embedSpriteStyle(this.user.sprite, 'grey');
            embedSpriteStyle(this.user.alliance_sprite, 'grey');
            this.ship = r.data.data.ship;
            embedSpriteStyle(this.ship.exterior_sprite);
            embedSpriteStyle(this.ship.interior_sprite);
            embedSpriteStyle(this.ship.logo_sprite, 'grey');
            this.showData = true;
            if (this.user.confirmed) {
              this.columns = ['character_id', 'level', 'name', 'equipment', 'rarity_order', 'hp', 'attack', 'repair',
                'special_ability', 'ability', 'pilot', 'science', 'engine', 'weapon', 'fire_resist', 'stamina',
                'training', 'walk']
            } else {
              this.columns = ['character_id', 'level', 'name', 'special_ability'];
              this.user.verified = false;
              this.user.key = null;
            }

            this.updateShipList(this.user.id, this.user)
          }
          this.spinner = 'display: none';
          this.$router.replace('/?search=' + searchName)
        })
        .catch(_ => {
          this.spinner = 'display: none';
          this.errorMessage = 'In space, no one can hear you scream.'
        })
    },
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

  .room-name {
    fill: white;
    font-size: 8px;
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
</style>
