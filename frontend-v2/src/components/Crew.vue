<template>
  <v-tooltip :disabled="!show" :right="right" :left="left">
    <template v-slot:activator="{ on, attrs }">
      <a :href="`/crew/${char.id}`" v-bind="attrs" v-on="on">
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

        <div
          v-if="name === 'left'"
          class="name pull-right"
          :class="[char.rarity]"
        >
          {{ char.name }}
        </div>
        <div
          v-if="name === 'right'"
          class="name pull-left"
          :class="[char.rarity]"
        >
          {{ char.name }}
        </div>
        <div v-if="name === 'bottom'" class="name" :class="[char.rarity]">
          {{ char.name }}
        </div>
      </a>
    </template>

    <div>
      <span :class="[char.rarity, 'font-weight-bold']">{{ char.name }}</span>
      <table>
        <tr>
          <td class="text-xs-right">HP:</td>
          <td class="text-xs-left">{{ char.hp[0] }} - {{ char.hp[1] }}</td>
        </tr>
        <tr>
          <td class="text-xs-right">Attack:</td>
          <td class="text-xs-left">
            {{ char.attack[0] }} - {{ char.attack[1] }}
          </td>
        </tr>
        <tr>
          <td class="text-xs-right">Repair:</td>
          <td class="text-xs-left">
            {{ char.repair[0] }} - {{ char.repair[1] }}
          </td>
        </tr>
        <tr>
          <td class="text-xs-right">Special:</td>
          <td class="text-xs-left">
            <div
              :style="spriteStyle(char.ability_sprite)"
              :title="char.special_ability"
            ></div>
          </td>
        </tr>
        <tr>
          <td class="text-xs-right">Ability:</td>
          <td class="text-xs-left">
            {{ char.ability[0] }} - {{ char.ability[1] }}
          </td>
        </tr>
        <tr>
          <td class="text-xs-right">Equip:</td>
          <td>
            <div v-for="(s, k) in char.equipment" :key="'crew-tooltip-' + k">
              <div class="small text-xs-left">{{ k }}</div>
            </div>
          </td>
        </tr>
      </table>
    </div>
  </v-tooltip>
</template>

<script>
import mixins from "@/mixins/PixyShip.vue.js";

export default {
  mixins: [mixins],

  props: {
    char: null,
    name: null,
    tip: { default: true },
  },

  data: function () {
    return {
      show: this.tip,
    };
  },

  computed: {
    right: function () {
      return this.name == "right";
    },

    left: function () {
      return this.name == "left";
    },
  },
};
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

a {
  text-decoration: none;
}
</style>
