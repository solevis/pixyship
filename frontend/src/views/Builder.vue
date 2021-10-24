<template>
  <v-card :loading="isLoading" class="full-height">
    <v-card-title class="overline">> Builder </v-card-title>
    <v-card-subtitle>Design and optimize your ship without breaking it in the game</v-card-subtitle>

    <!-- Filters -->
    <v-card-subtitle v-if="loaded">
      <v-row justify="center">
        <v-col cols="12" sm="12" md="4">
          <v-autocomplete
          v-model="selectedShip"
          :items="shipList"
          label="Ship Hull"
          placeholder="Type to search ships"
          @input="selectShip()"
          item-text="name"
          return-object
          outlined
        >
          <template slot-scope="s" slot="item">
            <div
              class="block mr-2"
              :style="spriteStyle(s.item.mini_ship_sprite)"
              align="center"
            ></div>
            <div class="text-xs-left lh-1">
              {{ s.item.name }}
              <br />
              <div class="caption">
                <span>Level {{ s.item.level }}</span>
                <span class="ml-2">{{ s.item.ship_type }}</span>
                <span class="ml-2">{{ s.item.hp }} hp</span>
              </div>
            </div>
          </template>
          </v-autocomplete>
        </v-col>

        <v-col cols="12" sm="6" md="2">
          <v-autocomplete
            v-model="selectedRoomType"
            :items="roomTypeList"
            label="Room type"
            placeholder="Type to search"
            item-text="name"
            return-object
            outlined
          >
          </v-autocomplete>
        </v-col>

        <v-col cols="12" sm="6" md="4">
          <v-autocomplete
            v-model="selectedRoom"
            :items="filteredRoomList"
            label="Room"
            placeholder="Type to search rooms"
            item-text="name"
            return-object
            outlined
          >
            <template slot-scope="r" slot="item">
              <div
                class="block mr-2"
                :style="spriteStyle(r.item.sprite)"
                align="center"
              ></div>
              <div class="text-xs-left lh-1">
                {{ r.item.name }}
                <br />
                <div class="caption">
                  <span>Ship level {{ r.item.min_ship_level }}</span>
                  <span class="ml-2">{{ r.item.type }}</span>
                </div>
              </div>
            </template>
          </v-autocomplete>
        </v-col>
      </v-row>
    </v-card-subtitle>

    <!-- Recent rooms -->
    <v-row justify="center" v-if="loaded">
        <v-col cols="12" sm="12" md="10">
          <v-data-iterator
            :items="recentRooms"
            row
            no-data-text=""
            hide-default-footer
            :items-per-page="10"
            class="text-center"
          >

          <div slot="item" slot-scope="props" class="block recent-room">
              <div
                draggable="true"
                class=""
                :style="spriteStyle(props.item.sprite)"
                v-on:dragstart="roomDragStart"
                v-on:dragend="roomDragEnd"
                :data-roomid="props.item.id"
                align="center">
              </div>
              <span class="room-name passthrough" x="2" y="9">{{ props.item.short_name || props.item.name }}</span>
            </div>
          </v-data-iterator>
        </v-col>
    </v-row>

    <!-- Ship -->
    <div id="ship" v-if="loaded">
      <svg class="mb-5" v-if="selectedShip" :height="selectedShip.interior_sprite.height" :width="selectedShip.interior_sprite.width" v-on:dragover="allowDrop" v-on:drop="shipOnDrop" v-on:dragleave.self="removeDragRoom">
        <!-- Ship interior -->
        <image 
          :xlink:href="getSpriteUrl(selectedShip.interior_sprite)" 
          x="0" y="0" 
          :height="selectedShip.interior_sprite.height" 
          :width="selectedShip.interior_sprite.width" 
        />

        <!-- Outer Grid -->
        <!-- <template v-for="r in (selectedShip.rows)" >
          <template v-for="c in (selectedShip.columns)" >
            <rect 
              :key="'outergrid-' + r + '-' + c"
              v-if="selectedShip.mask[selectedShip.columns * (r-1) + (c-1)] == '0'" :x="25 * c - 25" :y="25 * r - 25"
              width="25" height="25" stroke="#fff" stroke-opacity="0.1" fill-opacity="0%">
            </rect>
          </template>
        </template> -->

        <!-- Ship Grid -->
        <template v-for="r in selectedShip.rows" >
          <template v-for="c in selectedShip.columns" >
            <rect 
              :key="'grid-' + r + '-' + c"
              v-if="selectedShip.mask[selectedShip.columns * (r-1) + (c-1)] === '1'" :x="25 * c - 25" :y="25 * r - 25"
              width="25" height="25" stroke="#fff" fill="#0004">
            </rect>
          </template>
        </template>

        <template v-for="r in selectedShip.rows" >
          <template v-for="c in selectedShip.columns" >
            <rect 
              :key="'grid-' + r + '-' + c"
              v-if="selectedShip.mask[selectedShip.columns * (r-1) + (c-1)] === '2'" :x="25 * c - 25" :y="25 * r - 25"
              width="25" height="25" stroke="#ff8000" fill="#0004">
            </rect>
          </template>
        </template>

        <!-- drop zone -->
        <rect v-if="dropLoc" :x="25 * dropLoc.x" :y="25 * dropLoc.y" class="passthrough"
          :width="draggedRoom.width * 25" :height="draggedRoom.height * 25"
          stroke="#0f0" fill="#0f08">
        </rect>

        <!-- undrop zone -->
        <rect v-if="undropLoc" :x="25 * undropLoc.x" :y="25 * undropLoc.y" class="passthrough"
          :width="draggedRoom.width * 25" :height="draggedRoom.height * 25"
          stroke="#f00" fill="#F008">
        </rect>

        <!-- Swap zone -->
        <rect v-if="swapLoc" :x="25 * swapLoc.x" :y="25 * swapLoc.y" class="passthrough"
          :width="draggedRoom.width * 25" :height="draggedRoom.height * 25"
          stroke="#00F" fill="#00F8">
        </rect>

        <!-- Rooms -->
        <g v-for="(r, index) in shipRooms" :key="'room-' + r.roomId + '-'+ index+ '-' + r.x + '-' + r.y">
          <svg :x="`${r.x * 25}px`" :y="`${r.y * 25}px`"
            :viewbox="`${r.room.sprite.x} ${r.room.sprite.y} ${r.room.sprite.width} ${r.room.sprite.height}`"
            :width="`${r.room.sprite.width}px`" :height="`${r.room.sprite.height}px`">
            
            <!-- Room sprite -->
            <foreignObject class="room" width="125" height="75">
              <body xmlns="http://www.w3.org/1999/xhtml">
                <div :style="spriteStyle(r.room.sprite)" :class="r.allowed ? '' : 'disallowed'"
                  draggable="true"
                  v-on:dragstart="shipRoomDragStart"
                  v-on:dragend="roomDragEnd"
                  :data-roomid="r.roomId"
                  :data-x="r.x"
                  :data-y="r.y"
                  :x="r.x*25" 
                  :y="r.y*25"
                  >
                </div>
              </body>
            </foreignObject>

            <!-- Room name -->
            <text class="room-name passthrough" x="2" y="9">{{ r.room.short_name }}</text>

            <!-- HP -->
            <text class="defense passthrough" v-if="r.room.armor && (r.room.power_use + r.room.power_gen > 0)" x="2"
              y="19">
              {{ (1 - 100 / (100 + r.room.defense + r.room.armor)).toLocaleString('en-US', {style: 'percent'})
              }}
            </text>

            <!-- Power -->
            <text class="power-use passthrough" v-if="r.room.power_use > 0" :x="r.room.width * 25 - 7" y="9">
              {{ r.room.power_use}}
            </text>
            <text class="power-gen passthrough" v-if="r.room.power_gen > 0" :x="r.room.width * 25 - 9" y="9">
              {{ r.room.power_gen }}
            </text>
          </svg>
        </g>
      </svg>
    </div>

    <div id="ship-canva-wrapper" v-if="loaded && selectedShip" :style="`width: ${this.selectedShip.interior_sprite.width + 25 * 2}px; height: ${this.selectedShip.interior_sprite.height + 25 * 2}px;`">
      <v-stage v-if="loaded && selectedShip" :config="configKonva">

        <v-layer>
          <v-rect
              :config="konvaBackgroundConfig"
          ></v-rect>
        </v-layer>

        <v-layer>
          <template v-for="r in ((selectedShip.interior_sprite.height + 25 * 2) / 25)">
            <template v-for="c in ((selectedShip.interior_sprite.width + 25 * 2) / 25)">
              <v-rect
                  :key="'grid-1-' + r + '-' + c"
                  :config="getDefaultGridKonvaConfig(r, c)"
              >
              </v-rect>
            </template>
          </template>
        </v-layer>

        <v-layer :config="{x:25, y:25}">
          <v-image :config="konvaShipBackgroundConfig" :key="konvaShipBackgroundKey"></v-image>
        </v-layer>

        <v-layer :config="{x:25, y:25}">
          <template v-for="r in selectedShip.rows">
            <template v-for="c in selectedShip.columns">
              <v-rect
                  :key="'grid-2-' + r + '-' + c"
                  v-if="selectedShip.mask[selectedShip.columns * (r-1) + (c-1)] === '1' || selectedShip.mask[selectedShip.columns * (r-1) + (c-1)] === '2'"
                  :config="getGridKonvaConfig(r, c)"
              >
              </v-rect>
            </template>
          </template>
        </v-layer>

        <v-layer>
          <v-rect
              :config="{width: 25*3, height: 25*2, draggable: true, fill: 'white'}"
              v-on:dragstart="moveRoomStart"
              v-on:dragend="moveRoomEnd"
              v-on:dragmove="moveRoom"
          ></v-rect>

          <v-rect
              :config="{width: 25*3, height: 25*2, draggable: true, fill: 'white'}"
              v-on:dragstart="moveRoomStart"
              v-on:dragend="moveRoomEnd"
              v-on:dragmove="moveRoom"
          ></v-rect>
        </v-layer>
      </v-stage>
    </div>

    <v-row justify="center" v-if="loaded">
      <v-col cols="1">
        <v-btn v-if="selectedShip" @click="copyUrl">Copy Link</v-btn>
      </v-col>
    </v-row>

    <!-- Stats -->
    <v-row class="pb-15" justify="center" v-if="loaded">
        <v-col cols="12" sm="12" md="10">
          <v-card 
            v-if="selectedShip"
            outlined
            shaped
            class="pb-3 pt-3"
          >
            <v-row justify="center" no-gutters>
              <v-col cols="2">
                <b>{{ selectedShip.name }}</b>
              </v-col>
              <v-col cols="2">
                <span class="grey--text">Level </span><b>{{ selectedShip.level }}</b>
              </v-col>
              <v-col cols="2">
                <b>{{ selectedShip.hp }}</b><span class="grey--text"> HP</span>
              </v-col>
              <v-col cols="2">
                <b>{{ shipRooms.length }}</b><span class="grey--text"> Rooms</span>
              </v-col>
            </v-row>

            <v-divider class="mt-2 mb-2"></v-divider>

            <v-row justify="center" no-gutters>
              <v-col cols="2">
                <b>{{ systemDps.toLocaleString('en-US', {maximumFractionDigits: 2}) }}</b><span class="grey--text"> System DPS</span>
              </v-col>
              <v-col cols="2">
                <b>{{ hullDps.toLocaleString('en-US', {maximumFractionDigits: 2}) }}</b><span class="grey--text"> Hull DPS</span>
              </v-col>
              <v-col cols="2">
                <b>{{ characterDps.toLocaleString('en-US', {maximumFractionDigits: 2}) }}</b><span class="grey--text"> Character DPS</span>
              </v-col>
              <v-col cols="2">
                <b>{{ antiAirDps.toLocaleString('en-US', {maximumFractionDigits: 2}) }}</b><span class="grey--text"> Anticraft DPS</span>
              </v-col>
            </v-row>

            <v-row justify="center" no-gutters>
              <v-col cols="2">
                <b>{{ missileRate.toLocaleString('en-US', {maximumFractionDigits: 2}) }}</b><span class="grey--text"> Missiles /s</span>
              </v-col>
              <v-col cols="2">
                <b>{{ craftRate.toLocaleString('en-US', {maximumFractionDigits: 2}) }}</b><span class="grey--text"> Craft /s</span>
              </v-col>
              <v-col cols="2">
                <b>{{ botRate.toLocaleString('en-US', {maximumFractionDigits: 2}) }}</b><span class="grey--text"> Androids /s</span>
              </v-col>
              <v-col cols="2">
                <b>{{ teleportRate.toLocaleString('en-US', {maximumFractionDigits: 2}) }}</b><span class="grey--text"> Teleports /s</span>
              </v-col>
            </v-row>

            <v-row justify="center" no-gutters>
              <v-col cols="2">
                <b>{{ missileCapacity.toLocaleString('en-US', {maximumFractionDigits: 2}) }}</b><span class="grey--text"> Missile Storage</span>
              </v-col>
              <v-col cols="2">
                <b>{{ craftCapacity.toLocaleString('en-US', {maximumFractionDigits: 2}) }}</b><span class="grey--text"> Craft Storage</span>
              </v-col>
              <v-col cols="2">
                <b>{{ botCapacity.toLocaleString('en-US', {maximumFractionDigits: 2}) }}</b><span class="grey--text"> Android Storage</span>
              </v-col>
              <v-col cols="2">
              </v-col>
            </v-row>

            <v-divider class="mt-2 mb-2"></v-divider>

            <v-row justify="center" no-gutters>
              <v-col cols="2">
                <b>{{ selectedShip.space }}</b><span class="grey--text"> Spaces</span>
              </v-col>
              <v-col cols="2">
                <b>{{ usedSpace }}</b><span class="grey--text"> Used</span>
              </v-col>
              <!--<v-col cols="2">-->
              <!--<b>{{ selectedShip.space - usedSpace }}</b> Free-->
              <!--</v-col>-->
              <v-col cols="2">
                <b>{{ armor.toLocaleString('en-US', {maximumFractionDigits: 2}) }}</b><span class="grey--text"> Armor</span>
              </v-col>
              <v-col cols="2">
                <b>{{ effectiveArmor }}</b><span class="grey--text"> Effective Armor</span>
              </v-col>
            </v-row>

            <v-row justify="center" no-gutters>
              <v-col cols="2">
                <b>{{ powerGen }}</b><span class="grey--text"> Power Generated</span>
              </v-col>
              <v-col cols="2">
                <b>{{ powerUsed }}</b><span class="grey--text"> Power Used</span>
              </v-col>
              <v-col cols="2">
                <b>{{ shieldCapacity }}</b><span class="grey--text"> Shield</span>
              </v-col>
              <v-col cols="2">
                <b>{{ shieldReload.toLocaleString('en-US', {maximumFractionDigits: 2}) }}</b><span class="grey--text"> Shield /s</span>
              </v-col>
            </v-row>

            <v-row justify="center" no-gutters>
              <v-col cols="2">
                <b>{{ mineralCapacity }}</b><span class="grey--text"> Max Mineral</span>
              </v-col>
              <v-col cols="2">
                <b>{{ gasCapacity }}</b><span class="grey--text"> Max Gas</span>
              </v-col>
              <v-col cols="2">
                <b>{{ storageCapacity }}</b><span class="grey--text"> Max Equipment</span>
              </v-col>
              <v-col cols="2">
                <b>{{ beds }}</b><span class="grey--text"> Beds</span>
              </v-col>
            </v-row>
          </v-card>
        </v-col>
    </v-row>
    
  </v-card>
</template>

<script>
import axios from 'axios'
import mixins from "@/mixins/PixyShip.vue.js"
import Vue from 'vue'
import VueClipboard from 'vue-clipboard2'
import "@/assets/css/override.css"
import VueKonva from 'vue-konva'
require('../js/DragDropTouch')

Vue.use(VueKonva)
Vue.use(VueClipboard)

export default {
  mixins: [mixins],

  computed: {
    isLoading: function () {
      return !this.loaded
    },

    configKonva: function () {
      return {
        width: this.selectedShip.interior_sprite.width + 25 * 2,
        height: this.selectedShip.interior_sprite.height + 25 * 2
      }
    },

    konvaShipBackgroundConfig() {
      return {
        x: 0,
        y: 0,
        width: this.selectedShip.interior_sprite.width,
        height: this.selectedShip.interior_sprite.height,
        image: this.konvaShipBackground
      }
    },

    konvaBackgroundConfig() {
      return {
        x: 0,
        y: 0,
        width: this.selectedShip.interior_sprite.width + 25 * 2,
        height: this.selectedShip.interior_sprite.height + 25 * 2,
        fill: '#3057E1',
      }
    }
  },

  data() {
    return {
      ships: {},
      shipList: [],
      rooms: {},
      roomList: [],
      roomTypeList: [],
      recentRooms: [],
      filteredRoomList: [],
      selectedShip: null,
      selectedRoomType: null,
      selectedRoom: null,
      loaded: false,
      occupied: [0],
      shipRooms: [],
      dropLoc: null,
      undropLoc: null,
      swapLoc: null,
      toRemove: null,
      usedSpace: 0,
      powerGen: 0,
      powerUsed: 0,
      shieldCapacity: 0,
      shieldReload: 0,
      beds: 0,
      systemDps: 0,
      hullDps: 0,
      characterDps: 0,
      antiAirDps: 0,
      missileRate: 0,
      craftRate: 0,
      teleportRate: 0,
      botRate: 0,
      missileCapacity: 0,
      craftCapacity: 0,
      botCapacity: 0,
      gasCapacity: 0,
      mineralCapacity: 0,
      storageCapacity: 0,
      armor: 0,
      effectiveArmor: 0,
      konvaStageKey: 0,
      konvaShipBackground: new Image(),
      konvaShipBackgroundKey: 0
    }
  },

  beforeMount: function () {
    this.ships = this.getShips()
    this.rooms = this.getRooms()
  },

  watch: {
    selectedRoom (n) {
      this.addToRecentRooms(n)
    },

    selectedRoomType (n) {
      this.filteredRoomList = this.roomList.filter(room => room.type === n)
    }
  },

  methods: {
    getShips: async function () {
      const response = await axios.get(this.shipsEndpoint)
      this.ships = response.data.data

      this.shipList = Object.keys(this.ships)
        .map(shipId => this.ships[shipId])  // initialize shipList from ships
        .map(ship => {
          // compute ship space available, each 1 in mask is an empty space available
          ship.space = ship.mask
            .split('')
            .map(e => e === '0' ? 0 : 1)
            .reduce((c, a) => c + a)
          return ship
        })
        .sort((a, b) => {
          // first sort based on race
          const raceDiff = a.race - b.race
          if (raceDiff !== 0) {
            return raceDiff
          }

          // second sort based on ship level
          const levelDiff = a.level - b.level
          if (levelDiff !== 0) {
            return levelDiff
          }

          // finnaly sort on name
          return a.name.localeCompare(b.name)
        })

      // set the ship if one is passed in URL
      const query = this.$route.query
      if (query && query.ship) {
        const shipId = parseInt(query.ship)
        this.selectedShip = this.ships[shipId]
      }
    },

    getRooms: async function () {
      const response = await axios.get(this.roomsEndpoint)
      this.rooms = response.data.data

      this.roomList = Object.keys(this.rooms)
        .map(roomId => this.rooms[roomId]) // initialize roomList from rooms
        .map(room => {
          room['raw_name'] = room['name'].split(' ').slice(0, -1).join(' ')
          return room
        })
        .sort((a, b) => {
          // sort based on room type
          const typeDiff = a.type.localeCompare(b.type)
          if (typeDiff !== 0) {
            return typeDiff
          }

          // sort based on raw name (computed in previous map())
          const rawNameDiff = a.raw_name.localeCompare(b.raw_name)
          if (rawNameDiff !== 0) {
            return rawNameDiff
          }

          // sort based on room level
          return parseInt(a.level) - parseInt(b.level)
        })

      // initialize all distinct type of rooms
      this.roomTypeList = [...new Set(
        Object.keys(this.rooms).map(roomId => this.rooms[roomId]['type'])
      )].sort(this.sortAlphabeticallyExceptNone)

      // by default, select the first type of room
      this.selectedRoomType = this.roomTypeList[0]

      // if there's a rooms param, now we process it
      const query = this.$route.query
      if (query && query.rooms) {
        this.shipRooms = query.rooms.split('-').map(room => {
          const parts = room.split(',')
          const roomId = parseInt(parts[2])
          return {
            room: this.rooms[roomId],
            x: parseInt(parts[0]),
            y: parseInt(parts[1]),
            roomId: roomId,
            allowed: this.doesRoomFit(parseInt(parts[0]), parseInt(parts[1]), this.rooms[roomId])
          }
        })
      }

      // remove all rooms
      this.clearOccupied()

      // add rooms on ship
      for (let room = 0; room < this.shipRooms.length; room++) {
        let location = this.shipRooms[room]
        this.setOccupied(location.x, location.y, location.room, 1)
      }

      this.update()
      this.loaded = true
    },

    selectShip () {
      this.shipRooms = []
      this.clearOccupied()
      this.update()
    },

    clearOccupied () {
      if (this.selectedShip) {
        for (let row = 0; row < this.selectedShip.rows; row++) {
          for (let column = 0; column < this.selectedShip.columns; column++) {
            this.occupied[this.selectedShip.columns * row + column] = 0
          }
        }
      }
    },

    setOccupied (x, y, room, occupied) {
      for (let row = 0; row < room.height; row++) {
        for (let column = 0; column < room.width; column++) {
          this.occupied[this.selectedShip.columns * (row + y) + (column + x)] = occupied
        }
      }
    },

    isOccupied (x, y, room) {
      for (let row = 0; row < room.height; row++) {
        for (let column = 0; column < room.width; column++) {
          if  (this.occupied[this.selectedShip.columns * (row + y) + (column + x)] == 1) {
            return true
          }
        }
      }

      return false
    },

    update () {
      this.usedSpace = this.occupied.reduce((a, s) => a + s, 0)
      this.powerGen = this.shipRooms.map(location => location.room.power_gen).reduce((a, s) => a + s, 0)
      this.powerUsed = this.shipRooms.map(location => location.room.power_use).reduce((a, s) => a + s, 0)
      this.shieldCapacity = this.shipRooms
        .map(location => location.room.type === 'Shield' ? location.room.capacity : 0)
        .reduce((a, s) => a + s, 0)
      this.shieldReload = this.shipRooms
        .map(location => location.room.type === 'Shield' ? 40 / location.room.reload : 0)
        .reduce((a, s) => a + s, 0)
      this.beds = this.shipRooms
        .map(location => location.room.type === 'Bedroom' ? location.room.capacity : 0)
        .reduce((a, s) => a + s, 0)
      this.systemDps = this.shipRooms
        .map(location => location.room.type === 'Laser' || location.room.type === 'Cannon' ? 40 / location.room.reload * location.room.system_damage : 0)
        .reduce((a, s) => a + s, 0)
      this.hullDps = this.shipRooms
        .map(location => location.room.type === 'Laser' || location.room.type === 'Cannon' ? 40 / location.room.reload * location.room.hull_damage : 0)
        .reduce((a, s) => a + s, 0)
      this.characterDps = this.shipRooms
        .map(location => location.room.type === 'Laser' || location.room.type === 'Cannon' ? 40 / location.room.reload * location.room.character_damage : 0)
        .reduce((a, s) => a + s, 0)
      this.antiAirDps = this.shipRooms
        .map(location => location.room.type === 'AntiCraft' ? 40 / location.room.reload * location.room.system_damage : 0)
        .reduce((a, s) => a + s, 0)
      this.missileRate = this.shipRooms
        .map(location => location.room.type === 'Missile' ? 40 / location.room.reload : 0)
        .reduce((a, s) => a + s, 0)
      this.missileCapacity = this.shipRooms
        .map(location => location.room.type === 'Missile' ? location.room.capacity : 0)
        .reduce((a, s) => a + s, 0)
      this.craftRate = this.shipRooms
        .map(location => location.room.type === 'Carrier' ? 40 / location.room.reload : 0)
        .reduce((a, s) => a + s, 0)
      this.craftCapacity = this.shipRooms
        .map(location => location.room.type === 'Carrier' ? location.room.capacity : 0)
        .reduce((a, s) => a + s, 0)
      this.teleportRate = this.shipRooms
        .map(location => location.room.type === 'Teleport' ? 40 / location.room.reload : 0)
        .reduce((a, s) => a + s, 0)
      this.botRate = this.shipRooms
        .map(location => location.room.type === 'Android' ? 40 / location.room.reload : 0)
        .reduce((a, s) => a + s, 0)
      this.botCapacity = this.shipRooms
        .map(location => location.room.type === 'Android' ? location.room.capacity : 0)
        .reduce((a, s) => a + s, 0)
      this.armor = this.shipRooms
        .map(location => location.room.type === 'Armor' ? location.room.capacity : 0)
        .reduce((a, s) => a + s, 0)
      
      if (this.selectedShip) {
        this.mineralCapacity = Number(this.selectedShip.mineral_capacity) + this.shipRooms
          .map(location => location.room.type === 'Storage' && location.room.manufacture_type === 'Mineral' ? location.room.capacity : 0)
          .reduce((a, s) => a + s, 0)
        this.gasCapacity = Number(this.selectedShip.gas_capacity) + this.shipRooms
          .map(location => location.room.type === 'Storage' && location.room.manufacture_type === 'Gas' ? location.room.capacity : 0)
          .reduce((a, s) => a + s, 0)
        this.storageCapacity = Number(this.selectedShip.equipment_capacity) + this.shipRooms
          .map(location => location.room.type === 'Storage' && location.room.manufacture_type === 'Equipment' ? location.room.capacity : 0)
          .reduce((a, s) => a + s, 0)

        this.konvaShipBackground.src = this.getSpriteUrl(this.selectedShip.interior_sprite)
        this.konvaShipBackgroundKey += 1
      }

      this.effectiveArmor = this.calcRoomArmor()

      /*
       * Update URL
       */

      if (this.selectedShip) {
        let query = {
          ship: this.selectedShip.id
        }

        const roomsQuery = this.shipRooms.map(location => `${location.x},${location.y},${location.roomId}`).join('-')
        if (roomsQuery) {
          query.rooms = roomsQuery
        }

        this.$router.replace({
          path: '/builder',
          query
        }).catch(() => {})
      }
    },

    calcRoomArmor () {
      const armors = this.shipRooms.map(location => {
        const room = location.room
        let armor = 0

        if (room.power_gen + room.power_use > 0) {
          // check for armor on all sides
          for (let x = location.x; x < location.x + room.width; x++) {
            armor += this.getArmor(x, location.y - 1)
            armor += this.getArmor(x, location.y + room.height)
          }

          for (let y = location.y; y < location.y + room.height; y++) {
            armor += this.getArmor(location.x - 1, y)
            armor += this.getArmor(location.x + room.width, y)
          }
        }

        return armor
      })

      return armors.reduce((a, s) => a + s, 0)
    },

    getArmor (x, y) {
      const location = this.shipRooms.filter(location => location.x === x && location.y === y)
      
      if (location.length > 0) {
        if (location[0].room.type === 'Armor') {
          return location[0].room.capacity
        }
      }

      return 0
    },

    allowDrop (event) {
      const x = Math.trunc(event.target.getAttribute('x') / 25)
      const y = Math.trunc(event.target.getAttribute('y') / 25)

      if (this.doesRoomFit(x, y, this.draggedRoom)) {
        this.dropLoc = {x: x, y: y}
        this.undropLoc = null
        this.swapLoc = null
        event.preventDefault()
      } 
      // else if (this.isOccupied(x, y, this.draggedRoom)) {
      //   this.dropLoc = null
      //   this.undropLoc = null
      //   this.swapLoc = {x: x, y: y}
      //   event.preventDefault()
      // } else {
      //   this.dropLoc = null
      //   this.undropLoc = {x: x, y: y}
      //   this.swapLoc = null
      //   event.preventDefault()
      // }

      event.stopPropagation()
    },

    preventDrop () {
      this.dropLoc = null
      this.undropLoc = null
      this.swapLoc = null
    },

    roomDragStart (event) {
      event.dataTransfer.clearData()

      try {
        event.dataTransfer.setData('ignore', '')
      } catch (error) {
        // nothing
      }
      
      const id = parseInt(event.target.dataset.roomid)
      this.draggedRoom = this.rooms[id]
    },

    roomDragEnd (event) {
      this.removeRoom()
      event.target.style.opacity = 1
      this.dropLoc = null
      this.undropLoc = null
      this.swapLoc = null
      this.draggedRoom = null
    },

    shipOnDrop (event) {
      const roomId = this.draggedRoom.id
      const room = this.rooms[roomId]
      const x = Math.trunc(event.target.getAttribute('x') / 25)
      const y = Math.trunc(event.target.getAttribute('y') / 25)

      // place the new room
      const location = {
        room: room,
        x: x,
        y: y,
        roomId: roomId,
        allowed: this.doesRoomFit(x, y, room)
      }

      this.addRoomToShip(location)

      this.dropLoc = null
      this.undropLoc = null
      this.swapLoc = null
    },

    addToRecentRooms (newRoom) {
      // check that room isn't already in the list
      const matchCount = this.recentRooms.filter(recentRoom => recentRoom.id === newRoom.id).length
      
      if (!matchCount) {
        this.recentRooms.push(newRoom)
      }

      this.recentRooms = this.recentRooms.slice(-10)
    },

    removeRoom () {
      if (!this.toRemove) {
        return
      } 

      const x = this.toRemove.dataset.x
      const y = this.toRemove.dataset.y
      this.toRemove = null

      // look for room coord in list and remove it
      if (x != null && y != null) {
        // find the room with the given coord in the list and remove it
        const ind = this.shipRooms.findIndex(location => {
          return location.x == x && location.y == y
        })

        if (ind >= 0) {
          const placement = this.shipRooms[ind]
          const room = placement.room
          
          // free the space
          this.setOccupied(placement.x, placement.y, room, 0)
          this.shipRooms.splice(ind, 1)
          this.update()
        }
      }
    },

    doesRoomFit (x, y, room) {
      for (let row = 0; row < room.height; row++) {
        for (let column = 0; column < room.width; column++) {
          const serialInd = this.selectedShip.columns * (row + y) + (column + x)
          if (this.selectedShip.mask[serialInd] === '0' || this.occupied[serialInd]) {
            return false
          }
        }
      }

      return true
    },

    addRoomToShip (location) {
      this.setOccupied(location.x, location.y, location.room, 1)
      this.shipRooms.push(location)
      this.update()
    },

    shipRoomDragStart (event) {
      event.dataTransfer.clearData()
      
      try {
        event.dataTransfer.setData('ignore', '')
      } catch (error) {
        // nothing
      }

      const id = parseInt(event.target.dataset.roomid)
      event.target.style.opacity = 0.5
      this.toRemove = event.target
      this.draggedRoom = this.rooms[id]
      this.addToRecentRooms(this.draggedRoom)
    },

    removeDragRoom () {
      this.removeRoom(this.draggedRoom)
    },

    copyUrl () {
      this.$copyText(window.location.href)
    },

    getDefaultGridKonvaConfig(row, column) {
      return {
        x: 25 * column - 25,
        y: 25 * row - 25,
        width: 25,
        height: 25,
        stroke: "#4A6DE5",
        fill: "#0004",
      }
    },

    getGridKonvaConfig(row, column) {
      let insideShip = this.selectedShip.mask[this.selectedShip.columns * (row - 1) + (column - 1)] === '1'
      return {
        x: 25 * column - 25,
        y: 25 * row - 25,
        width: 25,
        height: 25,
        stroke: insideShip ? "rgba(180,180,180,0.51)" : "#b94848",
        fill: "#0004",
      }
    },

    moveRoomStart(event) {
      event.target.moveToTop()
    },

    moveRoomEnd(event) {
      event.target.fill('white')
      event.target.position({
        x: Math.round(event.target.x() / 25) * 25,
        y: Math.round(event.target.y() / 25) * 25
      })
    },

    moveRoom(event) {
      event.target.fill('green')
    }
  }
}
</script>

<style scoped>
  #ship {
    overflow-x: auto;
  }

  #ship > svg {
    margin: auto;
    display: block;
  }

  .recent-room {
    margin: 0 5px;
  }

  .block {
    display: inline-block;
  }

  .room-name {
    fill: white;
    font-size: 8px;
  }

  .passthrough {
    pointer-events: none;
  }

  .disallowed {
    border: 1px solid red !important;
  }

  .power-gen {
    fill: lime;
    font-weight: 700;
    font-size: 8px;
  }

  .power-use {
    fill: yellow;
    font-weight: 700;
    font-size: 8px;
  }

  #ship-canva-wrapper {
    margin: 0 auto;
  }
</style>