<template>
  <v-tooltip :disabled="!show" top color="grey darken-3">
    <template v-slot:activator="{ on, attrs }">
      <div v-bind="attrs" v-on="on" :aria-label="item.name">
        
        <div v-if="name === 'top'" class="name">
          {{ count > 1 ? 'x' + count : '' }} <span :class="[item.rarity]">{{ item.name }}</span>
        </div>

        <div
          :class="[
            name === 'left' ? 'pull-right' : null,
            name === 'left' ? 'ml-1' : null,
            name === 'right' ? 'pull-left' : null,
            name === 'right' ? 'mr-2' : null,
          ]"
        >
          <div :style="spriteStyle(item.sprite)"></div>
        </div>

        <div
          v-if="name === 'left'"
          class="pull-right name"
        >
          {{ count > 1 ? 'x' + count : '' }} <span :class="[item.rarity]">{{ item.name }}</span>
        </div>

        <div
          v-if="name === 'right'"
          class="pull-left name"
        >
          {{ count > 1 ? 'x' + count : '' }} <span :class="[item.rarity]">{{ item.name }}</span>
        </div>

        <div v-if="name === 'bottom'" class="name">
          {{ count > 1 ? 'x' + count : '' }} <span :class="[item.rarity]">{{ item.name }}</span>
        </div>
      </div>
    </template>

    <div>
      <span :class="[item.rarity, 'font-weight-bold']">{{ item.name }}</span><br>
      <span :class="['font-weight-bold']">{{ item.type }} / {{ item.slot }} <span :class="[item.rarity]">({{item.rarity.charAt(0).toUpperCase() + item.rarity.slice(1) }})</span></span><br>
      <table style="min-width: 200px">
        <tr v-if="formatBonus(item)">
          <td class="text-xs-right">Bonus:</td>
          <td class="text-xs-left">
            <span>{{ formatBonus(item) }}</span>
            <span v-if="item.module_extra_disp_enhancement != null">&nbsp;/&nbsp;{{ formatExtraBonus(item) }}</span>
          </td>
        </tr>
        <tr v-if="item.prices">
          <td class="text-xs" style="vertical-align: top;">48h Market $:</td>
          <td>
            <table>
              <tr>
                <td class="text-center"></td>
                <td class="text-center">25% - 50% - 75%</td>
              </tr>
              <tr
                v-for="(price, currency, ind) in item.prices"
                :key="'item' + item.id + '-price-' + ind"
                class="nobreak"
              >
                <td><div class="block" :style="currencySprite(currency)" /></td>
                <td class="text-xs-left" v-html="priceFormat(price)"></td>
              </tr>
            </table>
          </td>
        </tr>
        <tr v-if="item.market_price">
          <td class="text-xs-right">Savy $:</td>
          <td class="text-xs-left">
            <table>
              <tr>
                <td>
                  <div class="block" :style="currencySprite('Starbux')" />
                </td>
                <td class="text-xs-left">{{ item.market_price }}</td>
              </tr>
            </table>
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
    item: null,
    count: null,
    name: null,
    tipPosition: null,
    tip: { default: true },
  },

  data: function () {
    return {
      show: this.tip,
    };
  },

  computed: {
    right: function () {
      return this.tipPosition === 'right' || (this.tipPosition == null && this.name == "right");
    },

    left: function () {
      return this.tipPosition === 'left' || (this.tipPosition == null && this.name == "left");
    },
  },

  methods: {
    formatBonus(item) {
      let formatedBonus = ""

      if (item.disp_enhancement != null && item.bonus) {
        formatedBonus = item.slot == 'Module' ? '' : '+'
        formatedBonus += item.bonus + " " + item.disp_enhancement
      } else if (item.hiddenBonus) {
        formatedBonus = item.hiddenBonus
      }

      return formatedBonus
    },

    priceFormat(price) {
      const formatFunc = function (x) {
        if (Math.max(price.p25, price.p50, price.p75) > 999999) {
          return parseFloat((x / 1000000).toFixed(1)) + "M";
        } else if (Math.max(price.p25, price.p50, price.p75) > 999) {
          return parseFloat((x / 1000).toFixed(1)) + "K";
        } else {
          return x.toFixed(0);
        }
      };

      let formatedPrice =
        formatFunc(price.p25) +
        " - " +
        "<b>" +
        formatFunc(price.p50) +
        "</b>" +
        " - " +
        formatFunc(price.p75);

      return formatedPrice;
    },
  }
};
</script>

<style scoped src="@/assets/css/common.css"></style>
<style scoped>
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
