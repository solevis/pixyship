<template>
  <v-card :loading="isLoading">
    <v-card-subtitle v-if="!loaded"> Loading... </v-card-subtitle>

    <v-row v-if="loaded" justify="center">
      <v-col cols="12" md="6">
        <v-card outlined class="not-offers" :style="backgroundNewsSprite(this.news.sprite)">
          <v-card-title class="overline mb-2"
            ><v-icon left>mdi-newspaper-variant</v-icon>Pixel Starships
            News</v-card-title
          >

          <v-card-subtitle v-if="news.news_moment">
            Stardate #{{ stardate }} ({{ news.news_moment.format('YYYY/MM/DD') }})
          </v-card-subtitle>
          <v-card-text>
            <p></p>
            <p v-if="news.news_moment">{{ news.news }}</p>
            <p class="small error">{{ news.maintenance }}</p>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="3">
        <v-card outlined class="not-offers" :loading="isTournamentLoading">
          <v-card-title class="overline mb-2"
            ><v-icon left>mdi-tournament</v-icon>Tournament</v-card-title
          >
          <v-card-text>
            <p>
              Start the {{ nowTime(this.tournament.start) }}<br>
              Left: {{ this.tournament.left }}
            </p>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row v-if="loaded" justify="center">
      <v-col cols="12" sm="6" md="3">
        <v-card outlined :class="[isExpired(this.offers.blueCargo.expires) ? 'expired' : '', 'offers']">
          <v-card-title class="overline mb-2">
            <div class="block mr-5 ml-4" :style="styleFromSprite(this.offers.blueCargo.sprite, '', 0, 3)"></div>Dropship
          </v-card-title>
          
          <v-card-text>
            <div v-for="(offer, index) in this.offers.blueCargo.items" :key="'blue-cargo-' + index">
              <v-divider v-if="index != 0" class="mt-4 mb-4"></v-divider>

              <crew :char="offer.objects[0].object" name="right"/>

              <div style="clear: both" class="pt-2">
                <template v-if="offer.description == 'Mineral Crew'">
                  <div class="block middle mr-1">Cost: </div>
                  <div class="block middle" :style="mineralSprite()"></div>
                </template>
                <template v-else-if="offer.description == 'Starbux Crew'">
                  <div class="block middle mr-1">Cost: </div>
                  <div class="block middle" :style="buxSprite()"></div>
                </template>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card outlined :class="[isExpired(this.offers.dailyRewards.expires) ? 'expired' : '', 'offers']">
          <v-card-title class="overline mb-2">
            <div class="block mr-1" :style="styleFromSprite(this.offers.dailyRewards.sprite, '', 0, 0.8)"></div>Daily Reward
          </v-card-title>

          <v-card-text>
            <div v-for="(object, index) in this.offers.dailyRewards.objects" :key="'daily-reward-' + index">
              <v-divider v-if="index != 0" class="mt-4 mb-4"></v-divider>

              <div>
                <template v-if="object.type === 'Item' ||object.type === 'Room'">
                  {{ 'x' + object.count }} <div class="block mr-2 middle" :style="spriteStyle(object.object.sprite)"></div>
                  <div :class="[object.object.rarity, 'block', 'middle', 'nowrap', 'bold']">{{object.object.name }}</div>
                </template>
                <template v-else-if="object.type === 'Character'">
                  <crew :char="object.object" name="right"/>
                </template>
                <template v-else-if="object.type === 'Currency'">
                  {{ 'x' + object.count }} <div class="block middle" :style="currencySprite(object.object.currency)"></div>
                </template>
                <template v-else>
                  <div>{{object.type }}</div>
                </template>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card outlined :class="[isExpired(this.offers.greenCargo.expires) ? 'expired' : '', 'offers']">
          <v-card-title class="overline mb-2">
            <div class="block mr-5 ml-4" :style="styleFromSprite(this.offers.greenCargo.sprite, '', 0, 3)"></div>Merchant Ship
          </v-card-title>
          
          
          <v-card-text>
            <div v-for="(offer, index) in this.offers.greenCargo.items" :key="'green-cargo-' + index">
              <v-divider v-if="index != 0" class="mt-4 mb-4"></v-divider>

              <div>
                <template v-if="offer.objects[0].type === 'Item' ||offer.objects[0].type === 'Room'">
                  {{ 'x' + offer.objects[0].count }} <div class="block mr-2 middle" :style="spriteStyle(offer.objects[0].object.sprite)"></div>
                  <div :class="[offer.objects[0].object.rarity, 'block', 'middle', 'nowrap', 'bold']">{{offer.objects[0].object.name }}</div>
                </template>
                <template v-else-if="offer.objects[0].type === 'Character'">
                  <crew :char="offer.objects[0].object" name="right"/>
                </template>
                <template v-else-if="offer.objects[0].type === 'Currency'">
                  {{ 'x' + offer.objects[0].count }} <div class="block middle" :style="currencySprite(offer.objects[0].object.currency)"></div>
                </template>
                <template v-else>
                  <div>{{offer.objects[0].type }}</div>
                </template>
              </div>

              <div style="clear: both" class="pt-2">
                <template v-if="offer.cost && offer.cost.currency != 'item'">
                  <div class="block middle mr-1">Cost: {{ offer.cost.price }}</div>
                  <div class="block middle" :style="currencySprite(offer.cost.currency)"></div>
                </template>
                <template v-else-if="offer.cost && offer.cost.currency == 'item'">
                  <div class="block middle mr-1">{{ offer.cost.count }}</div>
                  <div class="block middle" :style="spriteStyle(offer.cost.object.sprite)" :title="offer.cost.object.name"
                  ></div>
                </template>
              </div>

            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row v-if="loaded" justify="center">
      <v-col cols="12" sm="6" md="3">
        <v-card outlined :class="[isExpired(this.offers.shop.expires) ? 'expired' : '', 'offers']">
          <v-card-title  class="overline mb-2" >
            <div class="block mr-2" :style="styleFromSprite(this.offers.shop.sprite, '', 0, 1)"></div>Shop
          </v-card-title>

          <v-card-text>
            <div>
              <template v-if="this.offers.shop.objects[0].type === 'Item' ||this.offers.shop.objects[0].type === 'Room'">
                {{this.offers.shop.objects[0].count > 1 ? 'x' + this.offers.shop.objects[0].count : '' }} <div class="block mr-2 middle" :style="spriteStyle(this.offers.shop.objects[0].object.sprite)"></div>
                <div :class="[this.offers.shop.objects[0].object.rarity, 'block', 'middle', 'nowrap', 'bold']">{{this.offers.shop.objects[0].object.name }}</div>
              </template>
              <template v-else-if="this.offers.shop.objects[0].type === 'Character'">
                <crew :char="this.offers.shop.objects[0].object" name="right"/>
              </template>
              <template v-else-if="this.offers.shop.objects[0].type === 'Currency'">
                {{this.offers.shop.objects[0].count }} <div class="block middle" :style="currencySprite(this.offers.shop.objects[0].object.currency)"></div>
              </template>
              <template v-else>
                <div>{{this.offers.shop.objects[0].type }}</div>
              </template>
            </div>

            <div style="clear: both" class="pt-2">
              <template v-if="this.offers.shop.cost && this.offers.shop.cost.currency != 'item'">
                <div class="block middle mr-1">Cost: {{ this.offers.shop.cost.price }}</div>
                <div class="block middle" :style="currencySprite(this.offers.shop.cost.currency)"></div>
              </template>
              <template v-else-if="this.offers.shop.cost && this.offers.shop.cost.currency == 'item'">
                <div class="block middle mr-1">{{ this.offers.shop.cost.count }}</div>
                <div class="block middle" :style="spriteStyle(this.offers.shop.cost.object.sprite)" :title="this.offers.shop.cost.object.name"
                ></div>
              </template>
            </div>

            <div class="mt-2 text-right text--disabled">
              <div>{{ this.offers.shop.details.left }} left</div>
              <div>Expire at {{ nowTime(this.offers.shop.expires) }}</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card outlined :class="[isExpired(this.offers.sale.expires) ? 'expired' : '', 'offers']">
          <v-card-title  class="overline mb-2" >
            <div class="block mr-2" :style="styleFromSprite(this.offers.sale.sprite, '', 0, 1)"></div>Bank
          </v-card-title>

          <v-card-text>
            <div>
              <template v-if="this.offers.sale.objects[0].type === 'Item' || this.offers.sale.objects[0].type === 'Room'">
                {{this.offers.sale.objects[0].count > 1 ? 'x' + this.offers.sale.objects[0].count : '' }} <div class="block mr-2 middle" :style="spriteStyle(this.offers.sale.objects[0].object.sprite)"></div>
                <div :class="[this.offers.sale.objects[0].object.rarity, 'block', 'middle', 'nowrap', 'bold']">{{this.offers.sale.objects[0].object.name }}</div>
              </template>
              <template v-else-if="this.offers.sale.objects[0].type === 'Character'">
                <crew :char="this.offers.sale.objects[0].object" name="right"/>
              </template>
              <template v-else-if="this.offers.sale.objects[0].type === 'Currency'">
                {{this.offers.sale.objects[0].count }} <div class="block middle" :style="currencySprite(this.offers.sale.objects[0].object.currency)"></div>
              </template>
              <template v-else>
                <div>{{this.offers.sale.objects[0].type }}</div>
              </template>

              <div style="clear: both" class="pt-2">
                <template v-if="this.offers.sale.cost.options">
                  <div>Cost: {{ formatSaleOptions(this.offers.sale.cost.options) }}</div>
                </template>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card outlined class="not-offers" :loading="isChangesLoading">
          <v-card-title class="overline mb-2"
            ><v-icon left>mdi-circle-edit-outline</v-icon>Changes</v-card-title
          >
          <v-card-text>
            <p>
              Most Recent: {{ nowTime(this.changeLatest) }}<br />
              Today: {{ this.changesToday }}<br />
              This Week: {{ this.changesThisWeek }}
            </p>
          </v-card-text>

          <v-card-actions>
            <v-btn
              text
              to="/changes"
            >
              See changes
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-card>
</template>

<script>
import axios from "axios";
import moment from "moment";
import mixins from "@/mixins/PixyShip.vue.js";
import Crew from "@/components/Crew.vue";
const convert = require("xml-js");

export default {
  mixins: [mixins],

  components: {
    Crew,
  },

  data() {
    return {
      loaded: false,
      tournamentLoaded: false,
      changesLoaded: false,
      daily: null,
      tournament: {},
      offers: [],
      changes: [],
      changeLatest: null,
      changesToday: 0,
      changesYesterday: 0,
      changesThisWeek: 0,
      news: {},
      stardate: 0,
    };
  },

  computed: {
    isLoading: function () {
      return !this.loaded;
    },

    isTournamentLoading: function () {
      return !this.tournamentLoaded;
    },

    isChangesLoading: function () {
      return !this.changesLoaded;
    },
  },

  created() {
    document.title = 'PixyShip'
  },

  beforeMount: function () {
    this.getDaily();
  },

  mounted: function () {
    this.getTournament();
    this.getChanges();
  },

  methods: {
    getDaily: async function () {
      const response = await axios.get(this.dailyEndpoint);

      this.offers = response.data.data.offers;
      this.stardate = response.data.data.stardate

      this.news = response.data.data.news;
      this.news.news_moment = moment.utc(this.news.news_date).local();

      this.loaded = true;
    },

    getChanges: async function () {
      const changes = await axios.get(this.changesEndpoint);
      this.changes = changes.data.data.map((change) => {
        change.attributes = this.getAllAttributes(
          convert.xml2js(change.data).elements[0]
        );
        change.oldAttributes = change.old_data
          ? this.getAllAttributes(convert.xml2js(change.old_data).elements[0])
          : null;
        change.moment = moment.utc(change.changed_at);
        change.changes = this.diffAttributes(
          change.attributes,
          change.oldAttributes
        );
        return change;
      });

      const oneDay = moment().add(-1, "days");
      const twoDay = moment().add(-2, "days");
      const oneWeek = moment().add(-7, "days");

      this.changesToday = this.changes.filter(
        (change) => change.moment > oneDay
      ).length;
      this.changesYesterday = this.changes.filter(
        (change) => change.moment > twoDay
      ).length;
      this.changesThisWeek = this.changes.filter(
        (change) => change.moment > oneWeek
      ).length;
      this.changeLatest = Math.max(
        ...this.changes.map((change) => change.moment)
      );

      this.changesLoaded = true
    },

    getTournament: async function () {
      const tournamentResponse = await axios.get(this.tournamentEndpoint);
      this.tournament = tournamentResponse.data.data

      this.tournamentLoaded = true
    },

    isExpired(time) {
      if (!time) return false;
      const res = moment.utc(time) < moment();
      return res;
    },

    formatSaleOptions(options) {
      let result = ''
      let first = true

      options.forEach((option) => {
        if (!first) {
          result += ', '
        } else {
          first = false
        }

        result += option.name + '(' + option.value + ')'

        
      });

      return result
    },

    backgroundNewsSprite(sprite) {
      if (Object.keys(sprite).length === 0) {
        return {}
      }

      let obj = {
        background: `url('${this.getSpriteServer()}${sprite.source}.png') -${sprite.x}px -${sprite.y}px`,
        backgroundRepeat: 'no-repeat',
        backgroundPosition: 'right 10px top 10px',
        imageRendering: 'pixelated'
      }

      return obj
    },
  },
};
</script>

<style scoped>
.expired {
  opacity: 0.5;
}

.block {
  display: inline-block;
}

.middle {
  vertical-align: middle;
}

.offers {
  min-height: 250px;
}

.not-offers {
  min-height: 180px;
}
</style>