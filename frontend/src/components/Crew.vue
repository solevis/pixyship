<template>
  <v-tooltip left :color="tip ? 'grey darken-4' : 'transparent'">
    <a :href="`/crew/${char.id}`" slot="activator">
      <div v-if="name === 'top'" class="name" :class="[char.rarity]">{{ char.name }}</div>
      <div :class="[name === 'left' ? 'pull-right' : null, name === 'right' ? 'pull-left' : null, 'ctooltip']">
        <div class="char-part" :style="spriteStyle(char.head_sprite)"></div>
        <div class="char-part" :style="spriteStyle(char.body_sprite)"></div>
        <div class="char-part" :style="spriteStyle(char.leg_sprite)"></div>
      </div>
      <div v-if="name === 'left'" class="name pull-right" :class="[char.rarity]">{{ char.name }}</div>
      <div v-if="name === 'right'" class="name pull-left" :class="[char.rarity]">{{ char.name }}</div>
      <div v-if="name === 'bottom'" class="name" :class="[char.rarity]">{{ char.name }}</div>
    </a>
    <div v-if="tip" class="tooltiptext">
      <span :class="[char.rarity, 'font-weight-bold']">{{char.name}}</span>
      <table>
        <tr>
          <td class="text-xs-right">HP:</td>
          <td class="text-xs-left">{{char.hp[0]}} - {{char.hp[1]}}</td>
        </tr>
        <tr>
          <td class="text-xs-right">Attack:</td>
          <td class="text-xs-left">{{char.attack[0]}} - {{char.attack[1]}}</td>
        </tr>
        <tr>
          <td class="text-xs-right">Repair:</td>
          <td class="text-xs-left">{{char.repair[0]}} - {{char.repair[1]}}</td>
        </tr>
        <tr>
          <td class="text-xs-right">Special:</td>
          <td class="text-xs-left">
            <div :style="spriteStyle(char.ability_sprite)" :title="char.special_ability"></div>
          </td>
        </tr>
        <tr>
          <td class="text-xs-right">Ability:</td>
          <td class="text-xs-left">{{char.ability[0]}} - {{char.ability[1]}}</td>
        </tr>
        <tr>
          <td class="text-xs-right">Equip:</td>
          <td>
            <div v-for="(s, k) in char.equipment">
              <div class="small text-xs-left">{{ k }}</div>
            </div>
          </td>
        </tr>
      </table>
    </div>
  </v-tooltip>
</template>

<script>
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

export default {
  props: {
    char: null,
    name: null,
    tip: {default: true}
  },

  data: function () {
    return {
    }
  },

  methods: {
    spriteStyle (s) {
      return styleFromSprite(s)
    }
  }
}
</script>

<style>
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
</style>
