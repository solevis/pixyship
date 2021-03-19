<template>
  <div>
    <v-app dark>
      <v-content>
        <v-container grid-list-sm>
          <ps-header/>
          Select ships and rooms. Position rooms by dragging.
          <v-container fluid grid-list-md>
            <v-layout wrap align-center>
              <v-flex xs12 sm5 d-flex>
                <v-autocomplete
                  v-model="ship"
                  :items="shipList"
                  label="Ship Hull"
                  placeholder="Type to search ships"
                  @input="selectShip()"
                  item-text="name"
                  return-object>
                  <template slot-scope="s" slot="item">
                    <div class="block mr-2" :style="spriteStyle(s.item.mini_ship_sprite)" align="center"></div>
                    <div class="text-xs-left lh-1">{{ s.item.name }}
                      <br/>
                      <div class="caption">
                        <span>Level {{ s.item.level }}</span>
                        <span class="ml-2">{{ s.item.ship_type }}</span>
                        <span class="ml-2">{{ s.item.hp }} hp</span>
                      </div>
                    </div>
                  </template>
                </v-autocomplete>
              </v-flex>
              <v-flex xs12 sm2 d-flex>
                <v-autocomplete
                  v-model="selectedRoomType"
                  :items="roomTypeList"
                  label="Room type"
                  placeholder="Type to search"
                  item-text="name"
                  return-object>
                </v-autocomplete>
              </v-flex>
              <v-flex xs12 sm5 d-flex>
                <v-autocomplete
                  v-model="selectedRoom"
                  :items="filteredRoomList"
                  label="Room"
                  placeholder="Type to search rooms"
                  item-text="name"
                  return-object>
                  <template slot-scope="r" slot="item">
                    <div class="block mr-2" :style="spriteStyle(r.item.sprite)" align="center"></div>
                    <div class="text-xs-left lh-1">{{ r.item.name }}
                      <br/>
                      <div class="caption">
                        <span>Ship level {{ r.item.min_ship_level }}</span>
                        <span class="ml-2">{{ r.item.type}}</span>
                      </div>
                    </div>
                  </template>
                </v-autocomplete>
              </v-flex>
            </v-layout>
          </v-container>

          <!-- Recent rooms -->
          <v-data-iterator
            :items="recentRooms"
            row
            no-data-text=""
            :hide-actions="true"
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

          <!-- THE SHIP -->
          <div id="ship">
            <svg v-if="ship" :style="spriteStyle(ship.interior_sprite)" v-on:dragover="preventDrop">
              <!-- grid -->
              <template v-for="r in ship.rows">
                <template v-for="c in ship.columns">
                  <rect v-if="ship.mask[ship.columns * (r-1) + (c-1)] > '0'" :x="25 * c - 25" :y="25 * r - 25"
                    width="25" height="25" stroke="#fff" fill="#0004"
                    v-on:drop="shipOnDrop"
                    v-on:dragover="allowDrop">
                  </rect>
                </template>
              </template>
              <!-- drop zone -->
              <rect v-if="dropLoc" :x="25 * dropLoc.x" :y="25 * dropLoc.y" class="passthrough"
                :width="draggedRoom.width * 25" :height="draggedRoom.height * 25"
                stroke="#0f0" fill="#0f08"
                v-on:drop="shipOnDrop"
                v-on:dragenter="allowDrop"
                v-on:dragover="allowDrop">
              </rect>
              <!-- rooms -->
              <g v-for="r in shipRooms">
                <svg :x="`${r.x * 25}px`" :y="`${r.y * 25}px`"
                  :viewbox="`${r.room.sprite.x} ${r.room.sprite.y} ${r.room.sprite.width} ${r.room.sprite.height}`"
                  :width="`${r.room.sprite.width}px`" :height="`${r.room.sprite.height}px`">
                  <foreignObject class="room" width="125" height="75">
                    <body xmlns="http://www.w3.org/1999/xhtml">
                      <div :style="spriteStyle(r.room.sprite)"
                        draggable="true"
                        v-on:dragstart="shipRoomDragStart"
                        v-on:dragend="roomDragEnd"
                        :data-roomid="r.roomId"
                        :data-x="r.x"
                        :data-y="r.y">
                      </div>
                    </body>
                  </foreignObject>
                  <text class="room-name passthrough" x="2" y="9">{{ r.room.short_name }}</text>
                  <text class="defense passthrough" v-if="r.room.armor && (r.room.power_use + r.room.power_gen > 0)" x="2"
                    y="19">
                    {{ (1 - 100 / (100 + r.room.defense + r.room.armor)).toLocaleString('en-US', {style: 'percent'})
                    }}
                  </text>
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
          <template v-if="ship">
            <hr class="grey darken-1"/>
            <v-layout justify-center class="subheading text-xs-left">
              <v-flex xs2>
                <b>{{ ship.name }}</b>
              </v-flex>
              <v-flex xs2>
                <span class="grey--text">Level </span><b>{{ ship.level }}</b>
              </v-flex>
              <v-flex xs2>
                <b>{{ ship.hp }}</b><span class="grey--text"> HP</span>
              </v-flex>
              <v-flex xs2>
                <b>{{ shipRooms.length }}</b><span class="grey--text"> Rooms</span>
              </v-flex>
            </v-layout>
            <hr class="grey darken-3"/>
            <v-layout justify-center class="subheading text-xs-left">
              <v-flex xs2>
                <b>{{ systemDps.toLocaleString('en-US', {maximumFractionDigits: 2}) }}</b><span class="grey--text"> System DPS</span>
              </v-flex>
              <v-flex xs2>
                <b>{{ hullDps.toLocaleString('en-US', {maximumFractionDigits: 2}) }}</b><span class="grey--text"> Hull DPS</span>
              </v-flex>
              <v-flex xs2>
                <b>{{ characterDps.toLocaleString('en-US', {maximumFractionDigits: 2}) }}</b><span class="grey--text"> Character DPS</span>
              </v-flex>
              <v-flex xs2>
                <b>{{ antiAirDps.toLocaleString('en-US', {maximumFractionDigits: 2}) }}</b><span class="grey--text"> Anticraft DPS</span>
              </v-flex>
            </v-layout>
            <v-layout justify-center class="subheading text-xs-left">
              <v-flex xs2>
                <b>{{ missileRate.toLocaleString('en-US', {maximumFractionDigits: 2}) }}</b><span class="grey--text"> Missiles /s</span>
              </v-flex>
              <v-flex xs2>
                <b>{{ craftRate.toLocaleString('en-US', {maximumFractionDigits: 2}) }}</b><span class="grey--text"> Craft /s</span>
              </v-flex>
              <v-flex xs2>
                <b>{{ botRate.toLocaleString('en-US', {maximumFractionDigits: 2}) }}</b><span class="grey--text"> Androids /s</span>
              </v-flex>
              <v-flex xs2>
                <b>{{ teleportRate.toLocaleString('en-US', {maximumFractionDigits: 2}) }}</b><span class="grey--text"> Teleports /s</span>
              </v-flex>
            </v-layout>
            <v-layout justify-center class="subheading text-xs-left">
              <v-flex xs2>
                <b>{{ missileCapacity.toLocaleString('en-US', {maximumFractionDigits: 2}) }}</b><span class="grey--text"> Missile Storage</span>
              </v-flex>
              <v-flex xs2>
                <b>{{ craftCapacity.toLocaleString('en-US', {maximumFractionDigits: 2}) }}</b><span class="grey--text"> Craft Storage</span>
              </v-flex>
              <v-flex xs2>
                <b>{{ botCapacity.toLocaleString('en-US', {maximumFractionDigits: 2}) }}</b><span class="grey--text"> Android Storage</span>
              </v-flex>
              <v-flex xs2>
              </v-flex>
            </v-layout>
            <hr class="grey darken-3"/>
            <v-layout justify-center class="subheading text-xs-left">
              <v-flex xs2>
                <b>{{ ship.space }}</b><span class="grey--text"> Spaces</span>
              </v-flex>
              <v-flex xs2>
                <b>{{ usedSpace }}</b><span class="grey--text"> Used</span>
              </v-flex>
              <!--<v-flex xs2>-->
              <!--<b>{{ ship.space - usedSpace }}</b> Free-->
              <!--</v-flex>-->
              <v-flex xs2>
                <b>{{ armor.toLocaleString('en-US', {maximumFractionDigits: 2}) }}</b><span class="grey--text"> Armor</span>
              </v-flex>
              <v-flex xs2>
                <b>{{ effectiveArmor }}</b><span class="grey--text"> Effective Armor</span>
              </v-flex>
            </v-layout>
            <v-layout justify-center class="subheading text-xs-left">
              <v-flex xs2>
                <b>{{ powerGen }}</b><span class="grey--text"> Power Generated</span>
              </v-flex>
              <v-flex xs2>
                <b>{{ powerUsed }}</b><span class="grey--text"> Power Used</span>
              </v-flex>
              <v-flex xs2>
                <b>{{ shieldCapacity }}</b><span class="grey--text"> Shield</span>
              </v-flex>
              <v-flex xs2>
                <b>{{ shieldReload.toLocaleString('en-US', {maximumFractionDigits: 2}) }}</b><span class="grey--text"> Shield /s</span>
              </v-flex>
            </v-layout>
            <v-layout justify-center class="subheading text-xs-left">
              <v-flex xs2>
                <b>{{ mineralCapacity }}</b><span class="grey--text"> Max Mineral</span>
              </v-flex>
              <v-flex xs2>
                <b>{{ gasCapacity }}</b><span class="grey--text"> Max Gas</span>
              </v-flex>
              <v-flex xs2>
                <b>{{ storageCapacity }}</b><span class="grey--text"> Max Equipment</span>
              </v-flex>
              <v-flex xs2>
                <b>{{ beds }}</b><span class="grey--text"> Beds</span>
              </v-flex>
            </v-layout>
          </template>

          <v-btn @click="copyUrl">Copy Link</v-btn>
          <!--<v-textarea-->
            <!--solo-->
            <!--name="input-7-4"-->
            <!--label="Debug text"-->
            <!--value=""-->
          <!--&gt;-->
            <!--<span v-html="debugLines"></span>-->
          <!--</v-textarea>-->
        </v-container>
      </v-content>
      <!--<v-footer app></v-footer>-->
    </v-app>

  </div>
</template>

<script>
import axios from 'axios'
import Vue from 'vue'
import {OrbitSpinner} from 'epic-spinners'
import Collapse from 'vue-collapse'
import moment from 'moment'
import Crew from '@/components/Crew'
import Header from '@/components/Header'
import 'vuetify/dist/vuetify.min.css'
import virtualList from 'vue-virtual-scroll-list'
import VueClipboard from 'vue-clipboard2'
import mixins from '@/mixins/Common.vue.js'
require('../js/DragDropTouch')
require('../assets/common.css')

Vue.component('crew', Crew)
Vue.component('ps-header', Header)

Vue.use(VueClipboard)

function styleFromSprite (s, color = '', border = 0) {
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

  components: {
    OrbitSpinner,
    Collapse,
    virtualList
  },

  data () {
    return {
      ships: {},
      shipList: [],
      rooms: {},
      roomList: [],
      filteredRoomList: [],
      roomTypeList: [],
      ship: null,
      selectedRoom: null,
      selectedRoomType: null,
      shipRooms: [],
      recentRooms: [],
      occupied: [0],
      dropLoc: null,
      draggedRoom: null,
      toRemove: null,
      debugLines: '',
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
      effectiveArmor: 0
    }
  },

  created: function () {
    this.ships = this.getShips()
    this.rooms = this.getRooms()
  },

  watch: {
    selectedRoom (n, o) {
      this.addToRecentRooms(n)
    },
    selectedRoomType (n, o) {
      this.filteredRoomList = this.roomList.filter(x => x.type === n)
    }
  },

  methods: {
    addToRecentRooms (room) {
      // Check that room isn't already in the list
      const matchCount = this.recentRooms.filter(r => r.id === room.id).length
      if (!matchCount) this.recentRooms.push(room)
      this.recentRooms = this.recentRooms.slice(-10)
    },

    copyUrl () {
      this.$copyText(window.location.href)
    },

    dl (msg) {
      // console.log(msg);
      // this.debugLines += msg + '<br>';
    },

    allowDrop (e) {
      const x = Math.trunc(e.target.getAttribute('x') / 25)
      const y = Math.trunc(e.target.getAttribute('y') / 25)
      if (this.doesRoomFit(x, y, this.draggedRoom)) {
        this.dropLoc = {x: x, y: y}
        e.preventDefault()
      } else {
        this.dropLoc = null
      }
      e.stopPropagation()
    },

    preventDrop (e) {
      this.dropLoc = null
    },

    roomDragStart (e) {
      e.dataTransfer.clearData()
      try {
        e.dataTransfer.setData('ignore', '')
      } catch (error) {}
      const id = parseInt(e.target.dataset.roomid)
      this.draggedRoom = this.rooms[id]
    },

    roomDragEnd (e) {
      this.removeRoom()
      e.target.style.opacity = 1
      this.dropLoc = null
      this.draggedRoom = null
    },

    shipRoomDragStart (e) {
      e.dataTransfer.clearData()
      try {
        e.dataTransfer.setData('ignore', '')
      } catch (error) {}
      const id = parseInt(e.target.dataset.roomid)
      e.target.style.opacity = 0.5
      this.toRemove = e.target
      this.draggedRoom = this.rooms[id]
      this.addToRecentRooms(this.draggedRoom)
    },

    removeRoom () {
      if (!this.toRemove) return

      const x = this.toRemove.dataset.x
      const y = this.toRemove.dataset.y
      this.toRemove = null
      // Look for room coord in list and remove it
      if (x != null && y != null) {
        // Find the room with the given coord in the list and remove it
        const ind = this.shipRooms.findIndex(e => {
          return e.x == x && e.y == y // eslint-disable-line eqeqeq
        })

        if (ind >= 0) {
          const placement = this.shipRooms[ind]
          const room = placement.room
          // Free the space
          this.setOccupied(placement.x, placement.y, room, 0)
          this.shipRooms.splice(ind, 1)
          this.update()
        }
      }
    },

    addRoomToShip (roomLoc) {
      this.setOccupied(roomLoc.x, roomLoc.y, roomLoc.room, 1)
      this.shipRooms.push(roomLoc)
      this.update()
    },

    doesRoomFit (x, y, room) {
      for (let r = 0; r < room.height; r++) {
        for (let c = 0; c < room.width; c++) {
          const serialInd = this.ship.columns * (r + y) + (c + x)
          if (this.ship.mask[serialInd] === '0' || this.occupied[serialInd]) {
            return false
          }
        }
      }
      return true
    },

    shipOnDrop (e) {
      const roomId = this.draggedRoom.id
      const room = this.rooms[roomId]
      const x = Math.trunc(e.target.getAttribute('x') / 25)
      const y = Math.trunc(e.target.getAttribute('y') / 25)

      if (this.doesRoomFit(x, y, room)) {
        // Place the new room
        const roomLoc = {
          room: room,
          x: x,
          y: y,
          roomId: roomId
        }
        this.addRoomToShip(roomLoc)
      }
      this.dropLoc = null
    },

    update () {
      this.usedSpace = this.occupied.reduce((a, s) => a + s, 0)
      this.powerGen = this.shipRooms.map(r => r.room.power_gen).reduce((a, s) => a + s, 0)
      this.powerUsed = this.shipRooms.map(r => r.room.power_use).reduce((a, s) => a + s, 0)
      this.shieldCapacity = this.shipRooms
        .map(r => r.room.type === 'Shield' ? r.room.capacity : 0)
        .reduce((a, s) => a + s, 0)
      this.shieldReload = this.shipRooms
        .map(r => r.room.type === 'Shield' ? 40 / r.room.reload : 0)
        .reduce((a, s) => a + s, 0)
      this.beds = this.shipRooms
        .map(r => r.room.type === 'Bedroom' ? r.room.capacity : 0)
        .reduce((a, s) => a + s, 0)
      this.systemDps = this.shipRooms
        .map(r => r.room.type === 'Laser' || r.room.type === 'Cannon' ? 40 / r.room.reload * r.room.system_damage : 0)
        .reduce((a, s) => a + s, 0)
      this.hullDps = this.shipRooms
        .map(r => r.room.type === 'Laser' || r.room.type === 'Cannon' ? 40 / r.room.reload * r.room.hull_damage : 0)
        .reduce((a, s) => a + s, 0)
      this.characterDps = this.shipRooms
        .map(r => r.room.type === 'Laser' || r.room.type === 'Cannon' ? 40 / r.room.reload * r.room.character_damage : 0)
        .reduce((a, s) => a + s, 0)
      this.antiAirDps = this.shipRooms
        .map(r => r.room.type === 'AntiCraft' ? 40 / r.room.reload * r.room.system_damage : 0)
        .reduce((a, s) => a + s, 0)
      this.missileRate = this.shipRooms
        .map(r => r.room.type === 'Missile' ? 40 / r.room.reload : 0)
        .reduce((a, s) => a + s, 0)
      this.missileCapacity = this.shipRooms
        .map(r => r.room.type === 'Missile' ? r.room.capacity : 0)
        .reduce((a, s) => a + s, 0)
      this.craftRate = this.shipRooms
        .map(r => r.room.type === 'Carrier' ? 40 / r.room.reload : 0)
        .reduce((a, s) => a + s, 0)
      this.craftCapacity = this.shipRooms
        .map(r => r.room.type === 'Carrier' ? r.room.capacity : 0)
        .reduce((a, s) => a + s, 0)
      this.teleportRate = this.shipRooms
        .map(r => r.room.type === 'Teleport' ? 40 / r.room.reload : 0)
        .reduce((a, s) => a + s, 0)
      this.botRate = this.shipRooms
        .map(r => r.room.type === 'Android' ? 40 / r.room.reload : 0)
        .reduce((a, s) => a + s, 0)
      this.botCapacity = this.shipRooms
        .map(r => r.room.type === 'Android' ? r.room.capacity : 0)
        .reduce((a, s) => a + s, 0)
      this.armor = this.shipRooms
        .map(r => r.room.type === 'Wall' ? r.room.capacity : 0)
        .reduce((a, s) => a + s, 0)
      if (this.ship) {
        this.mineralCapacity = Number(this.ship.mineral_capacity) + this.shipRooms
          .map(r => r.room.type === 'Storage' && r.room.manufacture_type === 'Mineral' ? r.room.capacity : 0)
          .reduce((a, s) => a + s, 0)
        this.gasCapacity = Number(this.ship.gas_capacity) + this.shipRooms
          .map(r => r.room.type === 'Storage' && r.room.manufacture_type === 'Gas' ? r.room.capacity : 0)
          .reduce((a, s) => a + s, 0)
        this.storageCapacity = Number(this.ship.equipment_capacity) + this.shipRooms
          .map(r => r.room.type === 'Storage' && r.room.manufacture_type === 'Equipment' ? r.room.capacity : 0)
          .reduce((a, s) => a + s, 0)
      }
      this.effectiveArmor = this.calcRoomArmor()

      let params = []
      if (this.ship) params.push('ship=' + this.ship.id)
      const d = this.shipRooms.map(r => `${r.x},${r.y},${r.roomId}`).join('-')
      if (d) params.push('rooms=' + d)

      const paramString = params ? '?' + params.join('&') : ''
      this.$router.replace('/builder' + paramString)
    },

    calcRoomArmor () {
      const armors = this.shipRooms.map(l => {
        const r = l.room
        let armor = 0
        if (r.power_gen + r.power_use > 0) {
          // Check for armor on all sides
          for (let x = l.x; x < l.x + r.width; x++) {
            armor += this.getArmor(x, l.y - 1)
            armor += this.getArmor(x, l.y + r.height)
          }
          for (let y = l.y; y < l.y + r.height; y++) {
            armor += this.getArmor(l.x - 1, y)
            armor += this.getArmor(l.x + r.width, y)
          }
        }
        return armor
      })
      return armors.reduce((a, s) => a + s, 0)
    },

    getArmor (x, y) {
      const r = this.shipRooms.filter(l => l.x === x && l.y === y)
      if (r.length > 0) {
        if (r[0].room.type === 'Wall') return r[0].room.capacity
      }
      return 0
    },

    clearOccupied () {
      if (this.ship) {
        for (let r = 0; r < this.ship.rows; r++) {
          for (let c = 0; c < this.ship.columns; c++) {
            this.occupied[this.ship.columns * r + c] = 0
          }
        }
      }
    },

    setOccupied (x, y, room, occupied) {
      for (let r = 0; r < room.height; r++) {
        for (let c = 0; c < room.width; c++) {
          this.occupied[this.ship.columns * (r + y) + (c + x)] = occupied
        }
      }
    },

    selectShip () {
      this.shipRooms = []
      this.clearOccupied()
      this.update()
    },

    getShips: async function () {
      const r = await axios.get(this.shipsEndpoint)
      this.ships = r.data.data

      this.shipList = Object.keys(this.ships)
        .map(x => this.ships[x])
        .map(x => {
          x.space = x.mask
            .split('')
            .map(e => e === '0' ? 0 : 1)
            .reduce((c, a) => c + a)
          return x
        })
        .sort((a, b) => {
          const r = a.race - b.race
          if (r !== 0) return r
          const l = a.level - b.level
          if (l !== 0) return l
          return a.name.localeCompare(b.name)
        })

      // Set the ship if one is passed
      const q = this.$route.query
      if (q && q.ship) {
        const shipId = parseInt(q.ship)
        this.ship = this.ships[shipId]
      }
    },

    getRooms: async function () {
      const r = await axios.get(this.roomsEndpoint)
      this.rooms = r.data.data

      this.roomList = Object.keys(this.rooms)
        .map(x => this.rooms[x])
        .map(x => {
          x['raw_name'] = x['name'].split(' ').slice(0, -1).join(' ')
          return x
        })
        .sort((a, b) => {
          const t = a.type.localeCompare(b.type)
          if (t !== 0) return t
          const n = a.raw_name.localeCompare(b.raw_name)
          if (n !== 0) return n
          return parseInt(a.level) - parseInt(b.level)
        })

      this.roomTypeList = [...new Set(
        Object.keys(this.rooms).map(x => this.rooms[x]['type'])
      )]
      this.selectedRoomType = this.roomTypeList[0]

      // If there's a rooms param, now we process it
      const q = this.$route.query
      if (q && q.rooms) {
        this.shipRooms = q.rooms.split('-').map(r => {
          const parts = r.split(',')
          const roomId = parseInt(parts[2])
          return {
            room: this.rooms[roomId],
            x: parseInt(parts[0]),
            y: parseInt(parts[1]),
            roomId: roomId
          }
        })
      }

      this.clearOccupied()
      for (let r = 0; r < this.shipRooms.length; r++) {
        let loc = this.shipRooms[r]
        this.setOccupied(loc.x, loc.y, loc.room, 1)
      }
      this.update()
    },

    spriteStyle (s) {
      if (s) return styleFromSprite(s)
      return ''
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
    }
  }
}
</script>

<style>
  #ship {
    overflow-x: auto;
  }

  .recent-room {
    margin: 0 5px;
  }

  .lh-1 {
    line-height: 1;
  }

  [draggable=true] {
    -khtml-user-drag: element;
  }

  .passthrough {
    pointer-events: none;
  }

  /* vuetify overrides */
  .application.theme--dark {
    background-color: black;
  }

  .collapse.collapse-section .collapse-header {
    background: #333;
    padding: 0 20px 0 40px;
  }

  .collapse.collapse-section .collapse-content-box {
    padding: 10px;
    border: 0 none;
    max-width: 600px;
    text-align: left;
  }

  html {
    background-color: black;
    color: white;
  }

  span.name {
    display: inline-block;
    line-height: .9;
  }

  .name span {
    color: gray;
    font-size: 60%;
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

  .stat-card span {
    font-weight: bold;
  }

  .stat span {
    color: gray;
    font-size: 60%;
  }

  .block {
    display: inline-block;
  }

  .item div{
    display: inline-block;
    margin: 0 5px;
  }

  .item-sprite div {
    display: table;
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
    transform:translate(-10px, -10px);
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
    display: inline-block;
    vertical-align: top;
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

  table.VueTables__table tr > td:nth-child(4) {
    text-align: left;
  }

  .v-select .dropdown-menu .active>a {
    color: white;
    background-color: #FF5656;
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

  td.show-height {
    border-left: solid 5px #666;
    border-radius: 12px;
  }

</style>
