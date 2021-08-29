<template>
  <v-tooltip :disabled="!show" top color="grey darken-3">
    <template v-slot:activator="{ on, attrs }">
      <div v-bind="attrs" v-on="on">
        <div v-if="!name" :aria-label="item.name">
          <div class="item-sprite" :style="spriteStyle(item.sprite)"></div>
        </div>

        <table v-else :aria-label="item.name">
          <tr v-if="name === 'top'" class="nobreak">
            <td>{{ count > 1 ? 'x' + count : '' }} <span :class="[item.rarity]">{{ item.name }}</span></td>
          </tr>
          <tr class="nobreak">
            <td v-if="name === 'left'">{{ count > 1 ? 'x' + count : '' }} <span :class="[item.rarity]">{{ item.name }}</span></td>
            <td><div class=" mr-2" :style="spriteStyle(item.sprite)"></div></td>
            <td v-if="name === 'right'">{{ count > 1 ? 'x' + count : '' }} <span :class="[item.rarity]">{{ item.name }}</span></td>
          </tr>
          <tr v-if="name === 'bottom'" class="nobreak">
            <td>{{ count > 1 ? 'x' + count : '' }} <span :class="[item.rarity]">{{ item.name }}</span></td>
          </tr>
        </table>
      </div>
    </template>

    <div>
      <span :class="[item.rarity, 'font-weight-bold']">{{ item.name }}</span>&nbsp;<span :class="[item.rarity]">({{item.rarity.charAt(0).toUpperCase() + item.rarity.slice(1) }})</span><br>
      <span :class="['font-weight-bold']">{{ item.type }} / {{ item.slot }}</span><br>
      <table style="min-width: 200px">
        <tr v-if="formatBonus(item)">
          <td class="text-xs-right" colspan="2">
            Bonus:
            <span>{{ formatBonus(item) }}</span>
            <span v-if="item.module_extra_disp_enhancement != null">&nbsp;/&nbsp;{{ formatExtraBonus(item) }}</span>
          </td>
        </tr>

        <tr v-if="item.recipe.length > 0">
          <td class="text-xs" style="vertical-align: top;">
            Recipe:
            <ul>
              <li v-for="(ingredient) in item.recipe"
                  :key="'item-cmp-' + item.id + '-recipe-' + ingredient.id"
                >
                  
                  <div class="d-inline-block middle mr-1">{{ ingredient.name }}</div>
                  <div class="d-inline-block middle mr-1" :style="spriteStyle(ingredient.sprite)"></div>
                  <div class="d-inline-block middle">x{{ ingredient.count }}</div>

              </li>
            </ul>
          </td>
        </tr>

        <tr v-if="item.market_price">
          <td colspan="2">
            <div class="d-inline-block middle mr-1">Savy $: {{ item.market_price }}</div>
            <div class="d-inline-block middle" :style="currencySprite('Starbux')"></div>
          </td>
        </tr>

        <tr v-if="item.prices" style="height: 3px"><td colspan="2">Market Prices (48h):</td></tr>
        <tr v-if="item.prices">
          <td>
            <table class="market-table">
              <thead>
                <tr>
                  <td class="text-center"></td>
                  <td class="text-center">25%</td>
                  <td class="text-center">50%</td>
                  <td class="text-center">75%</td>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(prices, currency, ind) in item.prices"
                  :key="'item' + item.id + '-price-' + ind"
                  class="nobreak"
                >
                  <td><div class="block" :style="currencySprite(currency)" /></td>
                  <td class="text-xs-left" v-html="priceFormat(prices, prices.p25)"></td>
                  <td class="text-xs-left" v-html="priceFormat(prices, prices.p50)"></td>
                  <td class="text-xs-left" v-html="priceFormat(prices, prices.p75)"></td>
                </tr>
              </tbody>
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

    formatExtraBonus(item) {
      let formatedBonus = ""

      if (item.module_extra_disp_enhancement != null && item.module_extra_enhancement_bonus) {
        formatedBonus = item.slot == 'Module' ? '' : '+'
        formatedBonus += item.module_extra_enhancement_bonus + " " + item.module_extra_disp_enhancement
      }

      return formatedBonus
    },

    priceFormat(prices, price) {
      const formatFunc = function (x) {
        if (Math.max(prices.p25, prices.p50, prices.p75) > 999999) {
          return parseFloat((x / 1000000).toFixed(1)) + "M";
        } else if (Math.max(prices.p25, prices.p50, prices.p75) > 999) {
          return parseFloat((x / 1000).toFixed(1)) + "K";
        } else {
          return x.toFixed(0);
        }
      };

      return formatFunc(price);
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

.item-sprite {
  margin: 0px auto;
}

.market-table {
  border-spacing: 0;
}

.market-table thead th {
  padding-right: 10px;
  padding-left: 10px;
  font-weight: bold;
}

.market-table tbody td {
  padding-right: 10px;
  padding-left: 10px;
  border-right: 1px solid rgb(232 232 232);
  text-align: center;
}

.middle {
  vertical-align: middle;
}
</style>