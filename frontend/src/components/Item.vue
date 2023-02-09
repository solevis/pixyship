<template>
  <v-tooltip :disabled="!show" top color="grey darken-3">
    <template v-slot:activator="{ on, attrs }">
      <component :is="disableLink ? 'span' : 'a'" :href="`/item/${item.id}`" v-bind="attrs" v-on="on" :aria-label="item.name" class="item-link">
        <div :class="name === 'bottom' ? 'text-center' : ''">
          <div v-if="!name" :aria-label="item.name">
              <div class="item-sprite" :style="spriteStyle(item.sprite)"></div>
          </div>

          <table v-else :aria-label="item.name" class="d-inline-block">
            <tr v-if="name === 'top'" class="nobreak">
              <td>{{ count > 1 ? 'x' + count : '' }} <span :class="[item.rarity]">{{ item.name }}</span></td>
            </tr>
            <tr class="nobreak">
              <td v-if="name === 'left'">{{ count > 1 ? 'x' + count : '' }} <span :class="[item.rarity]">{{ item.name }}</span></td>
              <td><div :class="name === 'left' || name === 'right' ? 'mr-2' : 'item-sprite'" :style="spriteStyle(item.sprite)"></div></td>
              <td v-if="name === 'right'">{{ count > 1 ? 'x' + count : '' }} <span :class="[item.rarity]">{{ item.name }}</span></td>
            </tr>
            <tr v-if="name === 'bottom'" class="nobreak">
              <td>{{ count > 1 ? 'x' + count : '' }} <span :class="[item.rarity]">{{ item.name }}</span></td>
            </tr>
          </table>
        </div>
      </component>
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
            <span v-if="item.has_offstat">&nbsp;/&nbsp;??&nbsp;+??</span>
          </td>
        </tr>

        <tr v-if="item.training">
          <td class="text-xs-right" colspan="2">
            Training:
            <ul>
              <li v-if="item.training.xp != 0">
                  XP:&nbsp;{{ item.training.xp }}
              </li>
              <li v-if="item.training.fatigue">
                Fatigue:&nbsp;{{
                    item.training.fatigue
                  }}
              </li>

              <li v-if="item.training.hp != 0">
                <span :class="item.training.hp === mainTrainingStatValue ? 'font-weight-bold' : ''">HP:&nbsp;<span>{{ item.training.hp === mainTrainingStatValue ? item.training.minimum_guarantee : 0 }}%&ndash;</span>{{
                    item.training.hp
                  }}%
                </span>
              </li>
              <li v-if="item.training.attack != 0">
                <span :class="item.training.attack === mainTrainingStatValue ? 'font-weight-bold' : ''">Attack:&nbsp;<span>{{ item.training.attack === mainTrainingStatValue ? item.training.minimum_guarantee : 0 }}%&ndash;</span>{{
                    item.training.attack
                  }}%
                </span>
              </li>
              <li v-if="item.training.repair != 0">
                <span :class="item.training.repair === mainTrainingStatValue ? 'font-weight-bold' : ''">Repair:&nbsp;<span>{{ item.training.repair === mainTrainingStatValue ? item.training.minimum_guarantee : 0 }}%&ndash;</span>{{
                    item.training.repair
                  }}%
                </span>
              </li>
              <li v-if="item.training.ability != 0">
                <span :class="item.training.ability === mainTrainingStatValue ? 'font-weight-bold' : ''">Ability:&nbsp;<span>{{ item.training.ability === mainTrainingStatValue ? item.training.minimum_guarantee : 0 }}%&ndash;</span>{{
                    item.training.ability
                  }}%
                </span>
              </li>
              <li v-if="item.training.stamina != 0">
                <span :class="item.training.stamina === mainTrainingStatValue ? 'font-weight-bold' : ''">Stamina:&nbsp;<span>{{ item.training.stamina === mainTrainingStatValue ? item.training.minimum_guarantee : 0 }}%&ndash;</span>{{
                    item.training.stamina
                  }}%
                </span>
              </li>

              <li v-if="item.training.pilot != 0">
                <span :class="item.training.pilot === mainTrainingStatValue ? 'font-weight-bold' : ''">Pilot:&nbsp;<span>{{ item.training.pilot === mainTrainingStatValue ? item.training.minimum_guarantee : 0 }}%&ndash;</span>{{
                    item.training.pilot
                  }}%
                </span>
              </li>
              <li v-if="item.training.science != 0">
                <span :class="item.training.science === mainTrainingStatValue ? 'font-weight-bold' : ''">Science:&nbsp;<span>{{ item.training.science === mainTrainingStatValue ? item.training.minimum_guarantee : 0 }}%&ndash;</span>{{
                    item.training.science
                  }}%
                </span>
              </li>
              <li v-if="item.training.engine != 0">
                <span :class="item.training.engine === mainTrainingStatValue ? 'font-weight-bold' : ''">Engine:&nbsp;<span>{{ item.training.engine === mainTrainingStatValue ? item.training.minimum_guarantee : 0 }}%&ndash;</span>{{
                    item.training.engine
                  }}%
                </span>
              </li>
              <li v-if="item.training.weapon != 0">
                <span :class="item.training.weapon === mainTrainingStatValue ? 'font-weight-bold' : ''">Weapon:&nbsp;<span>{{ item.training.weapon === mainTrainingStatValue ? item.training.minimum_guarantee : 0 }}%&ndash;</span>{{
                    item.training.weapon
                  }}%
                </span>
              </li>
            </ul>
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

        <tr v-if="item.content && item.content.length > 0">
          <td class="text-xs" style="vertical-align: top;">
            Content, {{ item.number_of_rewards }} reward{{ item.number_of_rewards > 1 ? 's' : '' }} from:
            <ul>
              <li v-for="(content_item, index) in item.content"
                  :key="'item-cmp-' + item.id + '-content-' + index"
                >

                <template v-if="content_item.type === 'character'">
                  <div class="d-inline-block middle mr-1">{{ content_item.data.name }}</div>
                </template>

                <template v-else-if="content_item.type === 'item'">
                  <div class="d-inline-block middle mr-1">{{ content_item.data.name }}</div>
                  <div class="d-inline-block middle mr-1" :style="spriteStyle(content_item.data.sprite)"></div>
                </template>

                <template v-else-if="content_item.type === 'starbux'">
                  <div class="d-inline-block middle mr-1" :style="buxSprite()"></div>
                </template>

                <template v-else-if="content_item.type === 'points' || content_item.type === 'purchasePoints'">
                  <div class="d-inline-block middle mr-1" :style="doveSprite()"></div>
                </template>

                <div class="d-inline-block middle">x{{ content_item.count }}</div>
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
import PixyShipMixin from "../mixins/PixyShip.vue.js"
import ItemMixin from "../mixins/Item.vue.js"

export default {
  mixins: [PixyShipMixin, ItemMixin],

  props: {
    item: null,
    count: null,
    name: null,
    tipPosition: null,
    tip: { default: true },
    disableLink: {
      fast: Boolean
    }
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

    mainTrainingStatValue: function () {
      let mainTrainingStatValue = null

      if(this.item.training != null) {
        let max = 0
        for (const trainingKey in this.item.training) {
          // ignore special fields
          if (["xp", 'fatigue', 'minimum_guarantee', 'id', 'sprite'].includes(trainingKey)) {
            continue
          }

          if (this.item.training[trainingKey] > max) {
            mainTrainingStatValue = this.item.training[trainingKey]
            max = this.item.training[trainingKey]
          }
        }
      }

      return mainTrainingStatValue
    }
  },
}
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

.item-link {
  color: white;
}
</style>
