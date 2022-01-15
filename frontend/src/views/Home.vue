<template>
  <v-card :loading="isLoading" class="full-height">
    <v-card-subtitle v-if="!loaded"> Loading... </v-card-subtitle>

    <v-card flat>
      <v-row v-if="loaded" justify="center">
        <!-- News -->
        <v-col cols="12" md="9">
          <v-card outlined class="not-offers">
            <div :class="$vuetify.breakpoint.smAndUp ?'news-sprite' : 'news-sprite-mobile'" :style="spriteStyle(this.news.sprite)"></div>
            <v-card-title class="overline mb-2"
              ><v-icon left>mdi-newspaper-variant</v-icon>Pixel Starships
              News</v-card-title
            >

            <v-card-subtitle v-if="news.news_moment">
              Stardate #{{ stardate }} ({{ news.news_moment.format('YYYY/MM/DD') }})
            </v-card-subtitle>
            <v-card-text>
              <br>
              <p v-if="news.news_moment">{{ news.news }}</p>
              <p class="small error">{{ news.maintenance }}</p>
            </v-card-text>


            <v-card-title class="overline mb-2" v-if="current_situation">
              <v-icon left>mdi-calendar</v-icon>

              <div class="block middle mr-1">Current event running</div>
              <div class="block middle mr-1" :style="spriteStyle(current_situation.sprite)"></div>
            </v-card-title>

            <v-card-subtitle v-if="current_situation">
              <div>{{ current_situation.name }} ({{ current_situation.description }})</div>
              <div>Left {{ current_situation.left }}</div>
            </v-card-subtitle>
          </v-card>
        </v-col>
      </v-row>

      <v-row v-if="loaded" justify="center">
        <!-- Tournament -->
        <v-col cols="12" md="5">
          <v-card outlined class="offers" :loading="isTournamentLoading">
            <v-card-title class="overline mb-2"
            ><v-icon left>mdi-tournament</v-icon>Tournament</v-card-title
            >
            <v-card-text v-if="this.tournament.started">
              End the {{ nowTime(this.tournament.end) }}<br>
              Left: {{ this.tournament.left }}
            </v-card-text>

            <v-card-text v-else>
              Start the {{ nowTime(this.tournament.start) }}<br>
              Left: {{ this.tournament.left }}
            </v-card-text>

            <v-card-text>
                {{ this.tournamentNews }}
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Changes on large screen -->
        <v-col md="4" v-if="$vuetify.breakpoint.mdAndUp">
          <v-card outlined class="offers" :loading="isChangesLoading">
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

      <v-row v-if="loaded" justify="center">
        <!-- Blue cargo -->
        <v-col cols="12" sm="6" md="3">
          <v-card outlined class="offers">
            <v-card-title class="overline mb-2">
              <div class="block mr-5 ml-4" :style="styleFromSprite(this.offers.blueCargo.sprite, '', 0, 3)"></div>Dropship
            </v-card-title>
            
            <v-card-text>
                <crew :char="this.offers.blueCargo.mineralCrew.object" name="right"/>

                <div style="clear: both" class="pt-2">
                    <div class="block middle mr-1">Cost: </div>
                    <div class="block middle" :style="mineralSprite()"></div>
                </div>

                <v-divider class="mt-4 mb-4"></v-divider>

                <crew :char="this.offers.blueCargo.starbuxCrew.object" name="right"/>

                <div style="clear: both" class="pt-2">
                    <div class="block middle mr-1">Cost: </div>
                    <div class="block middle" :style="buxSprite()"></div>
                </div>
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Daily reward -->
        <v-col cols="12" sm="6" md="3">
          <v-card outlined class="offers">
            <v-card-title class="overline mb-2">
              <div class="block mr-1" :style="styleFromSprite(this.offers.dailyRewards.sprite, '', 0, 0.8)"></div>Daily Reward
            </v-card-title>

            <v-card-text>
              <div v-for="(object, index) in this.offers.dailyRewards.objects" :key="'daily-reward-' + index">
                <v-divider v-if="index != 0" class="mt-4 mb-4"></v-divider>

                <div>
                  <template v-if="object.type === 'item'">
                    <item :item="object.object" :count="object.count" name="right"/>
                  </template>

                  <template v-else-if="object.type === 'room'">
                    <a :href="makeLink('room', object.object.id)">
                      {{ 'x' + object.count }} <div class="block mr-2 middle" :style="spriteStyle(object.object.sprite)"></div>
                      <div :class="[object.object.rarity, 'block', 'middle', 'nowrap', 'bold']">{{object.object.name }}</div>
                    </a>
                  </template>

                  <template v-else-if="object.type === 'character'">
                    <crew :char="object.object" name="right"/>
                  </template>

                  <template v-else-if="object.type === 'currency'">
                    {{ 'x' + object.count }} <div class="block middle" :style="currencySprite(object.object.currency)"></div>
                  </template>

                  <template v-else>
                    <div>{{ object.type }}</div>
                  </template>
                </div>

                <div style="clear: both" class="pt-2"></div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Shop -->
        <v-col cols="12" sm="6" md="3">
          <v-card outlined :class="[isExpired(this.offers.shop.expires) ? 'expired' : '', 'offers']">
            <v-card-title  class="overline mb-2" >
              <div class="block mr-2" :style="styleFromSprite(this.offers.shop.sprite, '', 0, 1)"></div>Shop
            </v-card-title>

            <v-card-text>
              <div>

                <template v-if="this.offers.shop.object.type === 'item'">
                  <item :item="this.offers.shop.object.object" :count="this.offers.shop.object.count" name="right"/>
                </template>

                <template v-else-if="this.offers.shop.object.type === 'room'">
                  <a :href="makeLink('room', this.offers.shop.object.object.id)">
                    {{this.offers.shop.object.count > 1 ? 'x' + this.offers.shop.object.count : '' }} <div class="block mr-2 middle" :style="spriteStyle(this.offers.shop.object.object.sprite)"></div>
                    <div :class="[this.offers.shop.object.object.rarity, 'block', 'middle', 'nowrap', 'bold']">{{this.offers.shop.object.object.name }}</div>
                  </a>
                </template>

                <template v-else-if="this.offers.shop.object.type === 'character'">
                  <crew :char="this.offers.shop.object.object" name="right"/>
                </template>

                <template v-else-if="this.offers.shop.object.type === 'currency'">
                  {{this.offers.shop.object.count }} <div class="block middle" :style="currencySprite(this.offers.shop.object.object.currency)"></div>
                </template>

                <template v-else>
                  <div>{{ this.offers.shop.object.type }}</div>
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
      </v-row>

      <v-row v-if="loaded" justify="center">
        <!-- Green cargo -->
        <v-col cols="12" sm="6" md="3">
          <v-card outlined :class="[isExpired(this.offers.greenCargo.expires) ? 'expired' : '', 'offers']">
            <v-card-title class="overline mb-2">
              <div class="block mr-5 ml-4" :style="styleFromSprite(this.offers.greenCargo.sprite, '', 0, 3)"></div>Merchant Ship
            </v-card-title>

            <v-card-text>
              <div v-for="(offer, index) in this.offers.greenCargo.items" :key="'green-cargo-' + index">
                <v-divider v-if="index != 0" class="mt-4 mb-4"></v-divider>

                <div>
                  <template v-if="offer.object.type === 'item'">
                    <item :item="offer.object.object" :count="offer.object.count" name="right"/>
                  </template>

                  <template v-else-if="offer.object.type === 'room'">
                    <a :href="makeLink('room', offer.object.object.id)">
                      {{ 'x' + offer.object.count }} <div class="block mr-2 middle" :style="spriteStyle(offer.object.object.sprite)"></div>
                      <div :class="[offer.object.object.rarity, 'block', 'middle', 'nowrap', 'bold']">{{offer.object.object.name }}</div>
                    </a>
                  </template>

                  <template v-else-if="offer.object.type === 'character'">
                    <crew :char="offer.object.object" name="right"/>
                  </template>

                  <template v-else-if="offer.object.type === 'currency'">
                    {{ 'x' + offer.object.count }} <div class="block middle" :style="currencySprite(offer.object.object.currency)"></div>
                  </template>

                  <template v-else>
                    <div>{ {offer.object.type }}</div>
                  </template>
                </div>

                <div style="clear: both" class="pt-2">
                  <template v-if="offer.cost && offer.cost.currency != 'item'">
                    <div class="block middle mr-1">Cost: {{ offer.cost.price }}</div>
                    <div class="block middle" :style="currencySprite(offer.cost.currency)"></div>
                  </template>
                  <template v-else-if="offer.cost && offer.cost.currency == 'item'">
                    <div class="block middle mr-1">Cost: {{ offer.cost.count }}</div>
                    <div class="block middle" :style="spriteStyle(offer.cost.object.sprite)" :title="offer.cost.object.name"
                    ></div>
                  </template>
                </div>

              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Daily Bundles -->
        <v-col cols="12" sm="6" md="3">
          <v-card outlined class="offers">
            <v-card-title class="overline mb-2">
              <div class="block mr-2" :style="styleFromSprite(this.offers.promotions.sprite, '', 0, 1)"></div>
              Bank (Daily Bundles)
            </v-card-title>

            <v-window v-model="currentDailyBundle" >
              <v-window-item
                  v-for="(object, i) in this.offers.promotions.objects"
                  :key="'promo-' + i"

              >
                <v-card :height="dailyBundlesMaxRewards * 40" flat tile>
                  <v-card-text>
                  <v-row
                      align="center"
                      justify="center"
                  >
                    <v-col>
                      <div v-for="reward in object.rewards" :key="'promo-' + i + '-' + reward.type + reward.id">
                        <template v-if="reward.type === 'starbux'">
                          {{ reward.data }}
                          <div class="block middle" :style="buxSprite()"></div>
                        </template>

                        <template v-else-if="reward.type === 'purchasePoints'">
                          {{ reward.data }}
                          <div class="block middle" :style="doveSprite()"></div>
                        </template>

                        <template v-else-if="reward.type === 'item'">
                          <item :item="reward.data" :count="reward.count" name="right"/>
                        </template>

                        <template v-else-if="reward.type === 'room'">
                          <a :href="makeLink('room', reward.data.id)">
                            {{ reward.count > 1 ? 'x' + reward.count : '' }}
                            <div class="block mr-2 middle" :style="spriteStyle(reward.data.sprite)"></div>
                            <div :class="[reward.data.rarity, 'block', 'middle', 'nowrap', 'bold']">{{
                                reward.data.name
                              }}
                            </div>
                          </a>
                        </template>

                        <template v-else-if="reward.type === 'character'">
                          <crew :char="reward.data" name="right"/>
                          <div style="clear: both"></div>
                        </template>

                        <template v-else>
                          <div>{{ reward.type }}</div>
                        </template>
                      </div>
                      <div style="clear: both" class="pt-2">
                        <div>Cost<span class="font-italic">*</span>: {{ formatDailyBundlePackCost(object.pack) }}</div>
                      </div>
                    </v-col>
                  </v-row>
                    </v-card-text>
                </v-card>
              </v-window-item>
            </v-window>

            <v-card-actions v-if="this.offers.promotions.objects.length > 1" class="justify-space-between">
              <v-btn
                  text
                  @click="prev"
              >
                <v-icon>mdi-chevron-left</v-icon>
              </v-btn>
              <v-item-group
                  v-model="currentDailyBundle"
                  class="text-center"
                  mandatory
              >
                <v-item
                    v-for="n in this.dailyBundlesLength"
                    :key="`btn-${n}`"
                    v-slot="{ active, toggle }"
                >
                  <v-btn
                      :input-value="active"
                      icon
                      @click="toggle"
                  >
                    <v-icon>mdi-record</v-icon>
                  </v-btn>
                </v-item>
              </v-item-group>
              <v-btn
                  text
                  @click="next"
              >
                <v-icon>mdi-chevron-right</v-icon>
              </v-btn>
            </v-card-actions>

            <v-card-text>
              <span class="small font-italic">*Price may differ depending of your country currency.</span>
            </v-card-text>

          </v-card>
        </v-col>

        <!-- Bank -->
        <v-col cols="12" sm="6" md="3">
          <v-card outlined class="offers">
            <v-card-title  class="overline mb-2" >
              <div class="block mr-2" :style="styleFromSprite(this.offers.sale.sprite, '', 0, 1)"></div>Bank (Daily Special)
            </v-card-title>

            <v-card-text v-if="this.offers.sale.object">
              <div>
                <template v-if="this.offers.sale.object.type === 'item'">
                  <item :item="this.offers.sale.object.object" :count="this.offers.sale.object.count" name="right"/>
                </template>

                <template v-else-if="this.offers.sale.object.type === 'room'">
                  <a :href="makeLink('room', this.offers.sale.object.object.id)">
                    {{this.offers.sale.object.count > 1 ? 'x' + this.offers.sale.object.count : '' }} <div class="block mr-2 middle" :style="spriteStyle(this.offers.sale.object.object.sprite)"></div>
                    <div :class="[this.offers.sale.object.object.rarity, 'block', 'middle', 'nowrap', 'bold']">{{this.offers.sale.object.object.name }}</div>
                  </a>
                </template>

                <template v-else-if="this.offers.sale.object.type === 'character'">
                  <crew :char="this.offers.sale.object.object" name="right"/>
                </template>

                <template v-else-if="this.offers.sale.object.type === 'currency'">
                  {{this.offers.sale.object.count }} <div class="block middle" :style="currencySprite(this.offers.sale.object.object.currency)"></div>
                </template>

                <template v-else-if="this.offers.sale.object.type === 'bonus'">
                  {{ this.offers.sale.bonus }}% Free Starbux
                </template>

                <template v-else>
                  <div>{{ this.offers.sale.object.type }}</div>
                </template>

                <div style="clear: both" class="pt-2">
                  <template v-if="this.offers.sale.options">
                    <div>Cost: {{ formatSaleOptions(this.offers.sale.options) }}</div>
                  </template>
                </div>
              </div>
            </v-card-text>

            <v-card-text v-else>
              No "Daily Special" sale today.
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Changes on small screen to the bottom -->
        <v-col cols="12" sm="6" v-if="$vuetify.breakpoint.smAndDown">
          <v-card outlined class="offers" :loading="isChangesLoading">
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
  </v-card>
</template>

<script>
import axios from "axios"
import moment from "moment"
import PixyShipMixin from "@/mixins/PixyShip.vue.js"
import Crew from "@/components/Crew.vue"
import Item from "@/components/Item.vue"
const convert = require("xml-js")

export default {
  metaInfo: {
    title: 'PixyShip',
    titleTemplate: null
  },

  mixins: [PixyShipMixin],

  components: {
    Crew,
    Item,
  },

  data() {
    return {
      loaded: false,
      tournamentLoaded: false,
      changesLoaded: false,
      daily: null,
      tournament: {},
      tournamentNews: null,
      offers: [],
      changes: [],
      changeLatest: null,
      changesToday: 0,
      changesYesterday: 0,
      changesThisWeek: 0,
      news: {},
      current_situation: {},
      stardate: 0,
      currentDailyBundle: 0,
      dailyBundlesLength: 0,
      dailyBundlesMaxRewards: 0,
    }
  },

  computed: {
    isLoading: function () {
      return !this.loaded
    },

    isTournamentLoading: function () {
      return !this.tournamentLoaded
    },

    isChangesLoading: function () {
      return !this.changesLoaded
    },
  },

  beforeMount: function () {
    this.getDaily()
  },

  mounted: function () {
    this.getTournament()
    this.getChanges()
  },

  methods: {
    getDaily: async function () {
      const response = await axios.get(this.dailyEndpoint)

      this.offers = response.data.data.offers
      this.dailyBundlesLength = this.offers.promotions.objects.length
      this.dailyBundlesMaxRewards = 0
      for (const objectIndex in this.offers.promotions.objects) {
        let object = this.offers.promotions.objects[objectIndex]
        this.dailyBundlesMaxRewards = Math.max(this.dailyBundlesMaxRewards, object.rewards.length)
      }


      this.stardate = response.data.data.stardate
      this.tournamentNews = response.data.data.tournament_news

      this.current_situation = response.data.data.current_situation

      this.news = response.data.data.news
      this.news.news_moment = moment.utc(this.news.news_date).local()

      this.loaded = true
    },

    getChanges: async function () {
      const changes = await axios.get(this.changesEndpoint)
      this.changes = changes.data.data.map((change) => {
        change.attributes = this.getAllAttributes(
          convert.xml2js(change.data).elements[0]
        )
        change.oldAttributes = change.old_data
          ? this.getAllAttributes(convert.xml2js(change.old_data).elements[0])
          : null
        change.moment = moment.utc(change.changed_at)
        change.changes = this.diffAttributes(
          change.attributes,
          change.oldAttributes
        )
        return change
      })

      const oneDay = moment().add(-1, "days")
      const twoDay = moment().add(-2, "days")
      const oneWeek = moment().add(-7, "days")

      this.changesToday = this.changes.filter(
        (change) => change.moment > oneDay
      ).length
      this.changesYesterday = this.changes.filter(
        (change) => change.moment > twoDay
      ).length
      this.changesThisWeek = this.changes.filter(
        (change) => change.moment > oneWeek
      ).length
      this.changeLatest = Math.max(
        ...this.changes.map((change) => change.moment)
      )

      this.changesLoaded = true
    },

    getTournament: async function () {
      const tournamentResponse = await axios.get(this.tournamentEndpoint)
      this.tournament = tournamentResponse.data.data

      this.tournamentLoaded = true
    },

    isExpired(time) {
      if (!time) return false
      const res = moment.utc(time) < moment()
      return res
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

        result += option.name + ' (' + option.value + ')'

        
      })

      return result
    },

    formatDailyBundlePackCost(pack) {
      if (pack === 1) {
        return '$1.99'
      }

      if (pack === 2) {
        return '$4.99'
      }

      if (pack === 3) {
        return '$9.99'
      }

      if (pack === 4) {
        return '$19.99'
      }

      if (pack === 5) {
        return '$49.99'
      }
    },

    next () {
      this.currentDailyBundle = this.currentDailyBundle + 1 === this.dailyBundlesLength
          ? 0
          : this.currentDailyBundle + 1
    },
    prev () {
      this.currentDailyBundle = this.currentDailyBundle - 1 < 0
          ? this.dailyBundlesLength - 1
          : this.currentDailyBundle - 1
    },
  },
}
</script>

<style scoped src="@/assets/css/common.css"></style>
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

.news-sprite {
  float: right;
  margin: 10px;
}

.news-sprite-mobile {
  margin: 20px auto 0;
}

a {
  color: white;
}
</style>