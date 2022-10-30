<template>
  <v-dialog
      v-model="dialog"
      fullscreen
      hide-overlay
      transition="dialog-bottom-transition"
  >
    <template v-slot:activator="{ on, attrs }">
      <div class="text-center">
        <v-btn
            color="primary"
            dark
            v-bind="attrs"
            v-on="on"
        >
          Zoom Sprite
        </v-btn>
      </div>
    </template>
    <v-card>
      <v-toolbar
          dark
          dense
      >
        <v-btn
            icon
            dark
            @click="dialog = false"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
        <v-toolbar-title>{{ this.object.name }}</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-btn-toggle v-model="lightSwitch" mandatory>
          <v-btn text :value="true">
            <v-icon>mdi-weather-sunny</v-icon>
          </v-btn>
          <v-btn text :value="false">
            <v-icon>mdi-weather-night</v-icon>
          </v-btn>
        </v-btn-toggle>
      </v-toolbar>
      <v-card-text>
        <v-slider
            v-model="zoom"
            append-icon="mdi-magnify-plus-outline"
            prepend-icon="mdi-magnify-minus-outline"
            @click:append="zoomIn"
            @click:prepend="zoomOut"
            max="20"
            min="1"
        ></v-slider>
      </v-card-text>

      <v-card-text v-if="this.type === 'char'" class="text-center">
        <div v-bind:style="scaleStyleObject">
          <div class="sprite" :style="spriteStyle(this.object.head_sprite)"></div>
          <div class="sprite" :style="spriteStyle(this.object.body_sprite)"></div>
          <div class="sprite" :style="spriteStyle(this.object.leg_sprite)"></div>
        </div>
      </v-card-text>

      <v-card-text v-if="this.type === 'item'" class="text-center">
        <div v-bind:style="scaleStyleObject">
          <div class="sprite" :style="spriteStyle(this.object.sprite)"></div>
        </div>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
import PixyShipMixin from "../mixins/PixyShip.vue.js"

export default {
  name: "SpritesButton",

  mixins: [PixyShipMixin],

  props: {
    type: null,
    object: null,
  },

  data() {
    return {
      dialog: false,
      zoom: 1,
      lightSwitch: false,
    }
  },

  computed: {
    scaleStyleObject: function () {
      return {
        transform: 'scale(' + this.zoom + ')',
        marginTop: (this.zoom / 0.07) + 'px',
        display: 'inline-block',
        overflow: 'scroll',
        background: this.lightSwitch ?  '#FFFFFF' : null,
      }
    }
  },

  methods: {
    zoomOut() {
      this.zoom = (this.zoom - 1) || 0
    },
    zoomIn() {
      this.zoom = (this.zoom + 1) || 100
    },
  },
}
</script>

<style scoped>
.sprite {
  margin: 0px auto;
}
</style>