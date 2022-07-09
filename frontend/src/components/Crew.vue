<template>
  <v-tooltip :disabled="!show" :right="right" :left="left" color="grey darken-3">
    <template v-slot:activator="{ on, attrs }">
      <a :href="`/crew/${char.id}`" v-bind="attrs" v-on="on" :aria-label="char.name">
        <div v-if="name === 'top'" class="name" :class="[char.rarity]">
          {{ char.name }}
        </div>

        <div
          :class="[
            name === 'left' ? 'pull-right' : null,
            name === 'right' ? 'pull-left' : null,
          ]"
        >
          <div class="char-part" :style="spriteStyle(char.head_sprite)"></div>
          <div class="char-part" :style="spriteStyle(char.body_sprite)"></div>
          <div class="char-part" :style="spriteStyle(char.leg_sprite)"></div>
        </div>

        <div v-if="name === 'left'" class="name pull-right">
          <span class="count" v-if="count">&nbsp;{{ 'x' + count }}</span>
          <span :class="[char.rarity]">{{ char.name }}</span>
        </div>

        <div v-if="name === 'right'" class="name pull-left">
          <span :class="[char.rarity]">{{ char.name }}</span>
          <span class="count" v-if="count">&nbsp;{{ 'x' + count }}</span>
        </div>

        <div v-if="name === 'bottom'" class="name" :class="[char.rarity]">
          {{ char.name }}
        </div>
      </a>
    </template>

    <div>
      <span :class="[char.rarity, 'font-weight-bold']">{{ char.name }}</span>&nbsp;<span :class="[char.rarity]">({{char.rarity.charAt(0).toUpperCase() + char.rarity.slice(1) }})</span>
      <table style="min-width: 200px">
        <tr>
          <td class="text-xs-right">HP:</td>
          <td class="text-xs-left">{{ char.hp[1] }}</td>
          <td class="text-xs-right">PLT:</td>
          <td class="text-xs-left">{{ char.pilot[1] }}</td>
        </tr>
        <tr>
          <td class="text-xs-right">ATK:</td>
          <td class="text-xs-left">{{ char.attack[1] }}</td>
          <td class="text-xs-right">SCI:</td>
          <td class="text-xs-left">{{ char.science[1] }}</td>
        </tr>
        <tr>
          <td class="text-xs-right">RPR:</td>
          <td class="text-xs-left">{{ char.repair[1] }}</td>
          <td class="text-xs-right">ENG:</td>
          <td class="text-xs-left">{{ char.engine[1] }}</td>
        </tr>
        <tr>
          <td class="text-xs-right">ABL:</td>
          <td class="text-xs-left">{{ char.ability[1] }}</td>
          <td class="text-xs-right">WPN:</td>
          <td class="text-xs-left">{{ char.weapon[1] }}</td>
        </tr>
        <tr>
          <td class="text-xs-right">Fire:</td>
          <td class="text-xs-left">{{ char.fire_resist }}</td>
          <td class="text-xs-right">Walk:</td>
          <td class="text-xs-left">{{ char.walk }}/{{ char.run }}</td>
        </tr>
        <tr v-if="char.special_ability">
          <td class="text-xs-right">Special:</td>
          <td class="text-xs-left" colspan="3">
            <div
              :style="spriteStyle(char.ability_sprite)"
              :title="char.special_ability"
            ></div>
          </td>
        </tr>
        
        <tr v-if="Object.values(char.equipment).length > 0">
          <td class="text-xs-right">Equip:</td>
          <td colspan="3">
            {{ Object.values(char.equipment).join(", ") }}
          </td>
        </tr>
      </table>
    </div>
  </v-tooltip>
</template>

<script>
import PixyShipMixin from "@/mixins/PixyShip.vue.js"

export default {
  mixins: [PixyShipMixin],

  props: {
    char: null,
    name: null,
    count: null,
    tipPosition: null,
    tip: { default: true },
  },

  data: function () {
    return {
      show: this.tip,
    }
  },

  computed: {
    right: function () {
      return this.tipPosition === 'right' || (this.tipPosition == null && this.name == "right")
    },

    left: function () {
      return this.tipPosition === 'left' || (this.tipPosition == null && this.name == "left")
    },
  },
}
</script>

<style scoped src="@/assets/css/common.css"></style>
<style scoped>
.char-part {
  margin: 0px auto;
}

.pull-left {
  float: left;
}

.pull-right {
  float: right;
}

.name {
  display: block;
  white-space: nowrap;
  margin: 5px 5px 0 5px;
}

.count {
  color: rgba(255, 255, 255, 0.7);
}

a {
  text-decoration: none;
}
</style>
