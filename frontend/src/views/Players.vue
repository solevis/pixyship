<template>
  <v-card :loading="isLoading" class="full-height">
    <v-card-title class="overline">> Players </v-card-title>
    <v-card-subtitle>Search top players and see their layout (click the gear icon for options)</v-card-subtitle>

    <v-card flat>
      <v-toolbar v-if="loaded" flat color="#1E1E1E">
        <v-autocomplete
          v-model="searchPlayer"
          :search-input.sync="searchText"
          :items="players"
          clearable
          placeholder="Search player by name"
          item-text="name"
          item-value="name"
          hide-no-data
          hide-details
          outlined
          class="mt-2"
        >
        
          <template v-slot:item="data" v-if="$vuetify.breakpoint.xs">
            <div style="width: 10em" class="ml-2">{{ data.item.name }}</div>
          </template>
          <template v-slot:item="data" v-else>
            <div style="width: 5em" class="mr-2"><v-icon style="font-size: 16px" class="mr-2">mdi-trophy-outline</v-icon>{{ data.item.trophies}}</div>
            <div style="width: 10em" class="ml-2">{{ data.item.name }}</div>
            <div class="block my-1 mr-1" :style="spriteStyle(data.item.alliance_sprite)"></div>
            {{ data.item.alliance }}
          </template>
        </v-autocomplete>

        <v-menu 
          v-model="menu"
          :close-on-content-click="false"
          offset-y
        >
          <template v-slot:activator="{ on, attrs }">
            <v-btn
              class="mt-2 mx-1"
              v-bind="attrs"
              v-on="on"
              icon
              large
              aria-label="Options"
            >
              <v-icon>mdi-cog</v-icon>
            </v-btn>
          </template>
          
          <v-card>
            <v-list>
              <v-list-item>
                <v-list-item-action>
                  <v-switch
                    v-model="showUpgrades"
                  ></v-switch>
                </v-list-item-action>
                <v-list-item-title>Show upgrades</v-list-item-title>
              </v-list-item>

              <v-list-item>
                <v-list-item-action>
                  <v-switch
                    v-model="showTrueColor"
                  ></v-switch>
                </v-list-item-action>
                <v-list-item-title>Show true color</v-list-item-title>
              </v-list-item>

              <v-list-item>
                <v-list-item-action>
                  <v-switch
                    v-model="showExterior"
                  ></v-switch>
                </v-list-item-action>
                <v-list-item-title>Show exterior</v-list-item-title>
              </v-list-item>
            </v-list>

            <v-card-actions>
              <v-spacer></v-spacer>

              <v-btn
                text
                @click="menu = false"
              >
                Close
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-menu>
      </v-toolbar>

      <v-row justify="center">
        <v-col cols="6" class="text-center">
          <v-progress-circular
            class="mt-5"
            :size="200"
            color="blue-grey"
            indeterminate
            v-if="shipLoading"
          ></v-progress-circular>
        </v-col>
      </v-row>

      <v-row justify="center" v-if="showShip">
        <v-col cols="6" class="text-center">
          Level {{ ship.level }} / {{ ship.name }} <v-btn class="ml-4" elevation="1" outlined small @click="openShipInBuilder">Edit in Builder</v-btn>
        </v-col>
      </v-row>

      <v-row v-if="showShip">
        <v-col cols="12" class="ship-panel">
          <!-- ############################################################################### -->
          <!-- Create 4 SVG, because conditional filter inside SVG is broken for some browsers -->
          <!-- ############################################################################### -->

            <svg v-show="!showExterior && showTrueColor" class="ship" :height="ship.interior_sprite.height" :width="ship.interior_sprite.width">
              <!-- Ship color -->
              <filter id="interior-color-filter">
                <feColorMatrix in="SourceGraphic" result="hue-filter" type="matrix" color-interpolation-filters="sRGB" :values="hueRotate(ship.interior_sprite.trueColorStyle.filter.hue)" />
                <feColorMatrix in="hue-filter" result="saturate-filter" type="saturate" :values="ship.interior_sprite.trueColorStyle.filter.saturate" />
                <feComponentTransfer in="saturate-filter" result="contrast-filter">
                  <feFuncR type="linear" :slope="ship.interior_sprite.trueColorStyle.filter.brightness"></feFuncR>
                  <feFuncG type="linear" :slope="ship.interior_sprite.trueColorStyle.filter.brightness"></feFuncG>
                  <feFuncB type="linear" :slope="ship.interior_sprite.trueColorStyle.filter.brightness"></feFuncB>
                </feComponentTransfer>
              </filter>

              <!-- Ship sprite -->
              <image 
                :xlink:href="getSpriteUrl(ship.interior_sprite)" 
                x="0" y="0" 
                :height="ship.interior_sprite.height" 
                :width="ship.interior_sprite.width" 
                filter="url(#interior-color-filter)"
              />

              <!-- Rooms -->
              <g v-for="room in rooms" :key="room.id">
                <svg 
                  :x="`${room.column * 25}px`" 
                  :y="`${room.row * 25}px`"
                  :viewbox="`${room.sprite.x} ${room.sprite.y} ${room.sprite.width} ${room.sprite.height}`"
                  :width="`${room.sprite.width}px`" 
                  :height="`${room.sprite.height}px`"
                  >

                  <!-- Room in upgrade -->
                  <foreignObject v-if="showUpgrades && room.construction" class="room" :width="room.sprite.width" :height="room.sprite.height">
                    <body xmlns="http://www.w3.org/1999/xhtml">
                    <div :style="spriteStyle(room.construction_sprite)"></div>
                    </body>
                  </foreignObject>

                  <!-- Room sprite -->
                  <foreignObject v-else class="room" :width="room.sprite.width" :height="room.sprite.height" :filter="!room.show_frame ? 'url(#interior-color-filter)' : ''">
                    <body xmlns="http://www.w3.org/1999/xhtml">
                    <div :style="spriteStyle(room.sprite)"></div>
                    </body>
                  </foreignObject>

                  <!-- Room name -->
                  <text class="room-name" x="2" y="9">{{ room.short_name }}</text>

                  <!-- Power used -->
                  <text class="power-use" v-if="room.power_use > 0" :x="room.width * 25 - 7" y="9">
                    {{ room.power_use}}
                  </text>

                  <!-- Power generated -->
                  <text class="power-gen" v-if="room.power_gen > 0" :x="room.width * 25 - 9" y="9">
                    {{ room.power_gen }}
                  </text>
                </svg>
              </g>
            </svg>

            <svg v-show="!showExterior && !showTrueColor" class="ship" :height="ship.interior_sprite.height" :width="ship.interior_sprite.width">
              <!-- Ship sprite -->
              <image 
                :xlink:href="getSpriteUrl(ship.interior_sprite)" 
                x="0" y="0" 
                :height="ship.interior_sprite.height" 
                :width="ship.interior_sprite.width" 
              />

              <!-- Rooms -->
              <g v-for="room in rooms" :key="room.id">
                <svg 
                  :x="`${room.column * 25}px`" 
                  :y="`${room.row * 25}px`"
                  :viewbox="`${room.sprite.x} ${room.sprite.y} ${room.sprite.width} ${room.sprite.height}`"
                  :width="`${room.sprite.width}px`" :height="`${room.sprite.height}px`">

                  <!-- Room in upgrade -->
                  <foreignObject v-if="showUpgrades && room.construction" class="room" :width="room.sprite.width" :height="room.sprite.height">
                    <body xmlns="http://www.w3.org/1999/xhtml">
                    <div :style="spriteStyle(room.construction_sprite)"></div>
                    </body>
                  </foreignObject>

                  <!-- Room sprite -->
                  <foreignObject v-else class="room" :width="room.sprite.width" :height="room.sprite.height">
                    <body xmlns="http://www.w3.org/1999/xhtml">
                    <div :style="spriteStyle(room.sprite)"></div>
                    </body>
                  </foreignObject>

                  <!-- Room name -->
                  <text class="room-name" x="2" y="9">{{ room.short_name }}</text>

                  <!-- Power used -->
                  <text class="power-use" v-if="room.power_use > 0" :x="room.width * 25 - 7" y="9">
                    {{ room.power_use}}
                  </text>

                  <!-- Power generated -->
                  <text class="power-gen" v-if="room.power_gen > 0" :x="room.width * 25 - 9" y="9">
                    {{ room.power_gen }}
                  </text>
                </svg>
              </g>
            </svg>

            <svg v-show="showExterior && showTrueColor" class="ship" :height="ship.exterior_sprite.height" :width="ship.exterior_sprite.width">
              <!-- Ship color -->
              <filter id="exterior-color-filter">
                <feColorMatrix in="SourceGraphic" result="hue-filter" type="matrix" color-interpolation-filters="sRGB" :values="hueRotate(ship.interior_sprite.trueColorStyle.filter.hue)" />
                <feColorMatrix in="hue-filter" result="saturate-filter" type="saturate" :values="ship.exterior_sprite.trueColorStyle.filter.saturate" />
                <feComponentTransfer in="saturate-filter" result="contrast-filter">
                  <feFuncR type="linear" :slope="ship.exterior_sprite.trueColorStyle.filter.brightness"></feFuncR>
                  <feFuncG type="linear" :slope="ship.exterior_sprite.trueColorStyle.filter.brightness"></feFuncG>
                  <feFuncB type="linear" :slope="ship.exterior_sprite.trueColorStyle.filter.brightness"></feFuncB>
                </feComponentTransfer>
              </filter>

              <!-- Ship sprite -->
              <image 
                :xlink:href="getSpriteUrl(ship.exterior_sprite)" 
                x="0" y="0" 
                :height="ship.exterior_sprite.height" 
                :width="ship.exterior_sprite.width" 
                filter="url(#exterior-color-filter)"
              />

              <!-- Rooms -->
              <g v-for="room in rooms" :key="room.id">
                <svg 
                  v-if="room.exterior_sprite"
                  :x="`${room.column * 25}px`" 
                  :y="`${room.row * 25}px`"
                  :viewbox="`${room.exterior_sprite.x} ${room.exterior_sprite.y} ${room.exterior_sprite.width} ${room.exterior_sprite.height}`"
                  :width="`${room.exterior_sprite.width}px`" 
                  :height="`${room.exterior_sprite.height}px`">

                  <!-- Room sprite -->
                  <foreignObject class="room" :width="room.exterior_sprite.width" :height="room.exterior_sprite.height" filter="url(#exterior-color-filter)">
                    <body xmlns="http://www.w3.org/1999/xhtml">
                    <div :style="spriteStyle(room.exterior_sprite)"></div>
                    </body>
                  </foreignObject>
                </svg>
              </g>
            </svg>

            <svg v-show="showExterior && !showTrueColor" class="ship" :height="ship.exterior_sprite.height" :width="ship.exterior_sprite.width">
              <!-- Ship sprite -->
              <image 
                :xlink:href="getSpriteUrl(ship.exterior_sprite)" 
                x="0" y="0" 
                :height="ship.exterior_sprite.height" 
                :width="ship.exterior_sprite.width" 
              />

              <!-- Rooms -->
              <g v-for="room in rooms" :key="room.id">
                <svg 
                  v-if="room.exterior_sprite"
                  :x="`${room.column * 25}px`" 
                  :y="`${room.row * 25}px`"
                  :viewbox="`${room.exterior_sprite.x} ${room.exterior_sprite.y} ${room.exterior_sprite.width} ${room.exterior_sprite.height}`"
                  :width="`${room.exterior_sprite.width}px`" :height="`${room.exterior_sprite.height}px`">

                  <!-- Room sprite -->
                  <foreignObject class="room" :width="room.exterior_sprite.width" :height="room.exterior_sprite.height">
                    <body xmlns="http://www.w3.org/1999/xhtml">
                    <div :style="spriteStyle(room.exterior_sprite)"></div>
                    </body>
                  </foreignObject>
                </svg>
              </g>
            </svg>
        </v-col>
      </v-row>

      <v-row justify="center">
        <v-col cols="12" sm="12" md="6">
          <v-card
            v-if="showShip"
            outlined
            shaped
          >

            <v-card-title>
              {{ user.name}}
            </v-card-title>

            <v-card-subtitle>
              {{ ship.name }} (Level {{ ship.level }})
            </v-card-subtitle>

            <v-simple-table dense class="px-6 pb-6 pt-2">
              <template v-slot:default>
                <tbody>
                  <tr v-show="user.alliance_name">
                    <td>Alliance (Rank)</td>
                    <td>{{ user.alliance_name }} ({{ user.alliance_membership }})</td>
                  </tr>

                  <tr v-show="user.alliance_name">
                    <td>Alliance Join Date</td>
                    <td>{{ nowTime(user.alliance_join_date) }}</td>
                  </tr>

                  <tr v-show="user.alliance_name">
                    <td>Crews Donated/Borrowed</td>
                    <td>{{ user.crew_donated }} / {{ user.crew_received }}</td>
                  </tr>

                  <tr>
                    <td>Trophies</td>
                    <td>{{ user.trophies }} (highest: {{ user.highest_trophy }})</td>
                  </tr>

                  <tr>
                    <td>Attacks Win/Loss/Draw</td>
                    <td>{{ user.pvpattack_wins }} / {{ user.pvpattack_losses }} / {{ user.pvpattack_draws }} ({{ user.pvpattack_ratio }}%)</td>
                  </tr>

                  <tr>
                    <td>Defenses Win/Loss/Draw</td>
                    <td>{{ user.pvpdefence_wins }} / {{ user.pvpdefence_losses }} / {{ user.pvpdefence_draws }} ({{ user.pvpdefence_ratio }}%)</td>
                  </tr>

                  <tr>
                    <td>Faction</td>
                    <td>{{ user.race }}</td>
                  </tr>

                  <tr>
                    <td>Last Login</td>
                    <td>{{ nowTime(user.last_login_date) }}</td>
                  </tr>

                  <tr>
                    <td>Account Creation</td>
                    <td>{{ nowTime(user.creation_date) }}</td>
                  </tr>
                </tbody>
              </template>
            </v-simple-table>
          </v-card>
        </v-col>
      </v-row>
    </v-card>
  </v-card>
</template>

<script>
import axios from "axios";
import mixins from "@/mixins/PixyShip.vue.js";
import _ from 'lodash'

export default {
  mixins: [mixins],

  components: {},

  data() {
    return {
      menu: false,
      searchPlayer: "",
      searchText: "",
      showUpgrades: true,
      showTrueColor: false,
      showExterior: false,
      loaded: false,
      players: [],
      showShip: false,
      shipLoading: false,
      ship: {},
    };
  },

  watch: {
    searchPlayer(val) {
      this.showShip = !!val
      this.getShip(val)
    },

    searchText() {
        this.getPlayers()
    },
  },

  computed: {
    isLoading: function () {
      return !this.loaded;
    },
  },

  created() {
    document.title = 'PixyShip - ' + this.$route.name
  },

  beforeMount: function () {
    this.getPlayers();
  },

  methods: {
    getPlayers: _.debounce(async function () {
      const response = await axios.get(
        this.playersEndpoint,
        {params: {search: this.searchText}}
      )
      this.players = response.data
      this.loaded = true
    }, 250),

    getShip: async function(searchName) {
      if (!searchName) {
        return
      }

      this.shipLoading = true;
      this.showShip = false;
      const endpoint = this.shipEndpoint + encodeURIComponent(searchName);

      const response = await axios.get(
        endpoint,
        {params: {key: this.searchName}}
      )

      if (response.data.data.status !== 'not found') {
        this.rooms = response.data.data.rooms;
        this.user = response.data.data.user;
        this.ship = response.data.data.ship;

        this.embedSpriteStyle(this.user.sprite, 'grey');
        this.embedSpriteStyle(this.user.alliance_sprite, 'grey');
        this.embedSpriteStyle(this.ship.exterior_sprite);
        this.embedTrueColorSpriteStyle(this.ship.exterior_sprite, this.ship.hue, this.ship.saturation, this.ship.brightness);
        this.embedSpriteStyle(this.ship.interior_sprite);
        this.embedTrueColorSpriteStyle(this.ship.interior_sprite, this.ship.hue, this.ship.saturation, this.ship.brightness);
        this.embedSpriteStyle(this.ship.logo_sprite, 'grey');

        this.shipLoading = false;
        this.showShip = true;
      }
    },

    embedSpriteStyle (sprite, color = '', border = 0) {
      sprite.style = this.styleFromSprite(sprite, color, border)
    },

    embedTrueColorSpriteStyle (sprite, hue, saturation, brightness) {
      sprite.trueColorStyle = {
        filter: {
          hue: parseFloat(hue) * 360,
          brightness: (parseFloat(brightness) * 5) + 1,
          saturate: parseFloat(saturation) + 1
        }
      }
    },

    openShipInBuilder () {
      if (!this.ship) {
        return
      }

      let path = '/builder?ship=' + this.ship.id
      if (this.rooms) {
        path += '&rooms=' + this.rooms.map(r => `${r.column},${r.row},${r.design_id}`).join('-')
      }

      this.$router.push({ path: path })
    },

    hueRotate(rotation) {
      rotation = (rotation || 0) / 180 * Math.PI;
      let cosR = Math.cos(rotation),
        sinR = Math.sin(rotation),
        sqrt = Math.sqrt;

      let w = 1 / 3, sqrW = sqrt(w);
      let a00 = cosR + (1.0 - cosR) * w;
      let a01 = w * (1.0 - cosR) - sqrW * sinR;
      let a02 = w * (1.0 - cosR) + sqrW * sinR;
      let a10 = w * (1.0 - cosR) + sqrW * sinR;
      let a11 = cosR + w * (1.0 - cosR);
      let a12 = w * (1.0 - cosR) - sqrW * sinR;
      let a20 = w * (1.0 - cosR) - sqrW * sinR;
      let a21 = w * (1.0 - cosR) + sqrW * sinR;
      let a22 = cosR + w * (1.0 - cosR);

      let matrix = [
        a00, a01, a02, 0, 0,
        a10, a11, a12, 0, 0,
        a20, a21, a22, 0, 0,
        0, 0, 0, 1, 0,
      ];

      return matrix.join(' ');
    },
  },
};
</script>

<style scoped src="@/assets/css/common.css"></style>
<style scoped>
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

.ship {
  display: block;
  margin: 0px auto;
}

.ship-panel {
  overflow: auto;
}
</style>