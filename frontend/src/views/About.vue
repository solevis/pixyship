<template>
  <v-card class="px-5 pb-1 full-height">
    <v-card-title class="overline right"></v-card-title>

    <!-- Backers -->
    <v-card class="mb-4" elevation="2" outlined>
      <v-card-title>Donators</v-card-title>

      <v-card-text>
        <!-- Backers -->
        <p class="font-weight-bold">
          A special thanks to all of the
          <a href="https://www.okpal.com/pixyship/#/" target="_blank"
            >crowfunding campaign</a
          >
          contributors, and especially to:
        </p>
        <p>
          Admiral Col, Albathoor, Alisrassa, Baradum, GudegLezat, Harmony,
          hex1337, Human Fly, Jean, JustcallmeDr, Maccinae, Matthew-II,
          Muinmacar, Phinie, Ruthless Rhino, Sahara Fleet, Scorpio99,
          ShadowfireAngel, Solphaen, Spaceman Spiff, The Flying Brick, The
          worst. and YankeeDood
        </p>

        <!-- Donation -->
        <div
          v-if="donationUrl"
          class="mt-5"
          @click="buyMeACoffee"
          style="cursor: pointer; width: 300px"
        >
          <v-img
            :src="require('../assets/img/Solevis.png')"
            max-height="78"
            max-width="48"
            contain
            class="d-inline-block"
            style="vertical-align: middle"
          ></v-img>
          <p
            class="ml-2 font-weight-bold d-inline-block"
            style="vertical-align: middle"
          >
            You like PixyShip?
            <br />
            <a href="javascript:void(0);">Why not buy my captain a coffee?</a>
            <br />
            <v-icon>mdi-coffee</v-icon>
          </p>
        </div>
      </v-card-text>
    </v-card>

    <!-- Dev Team -->
    <v-card class="mb-4" elevation="2" outlined>
      <v-card-title>Developers</v-card-title>
      <v-card-text>
        <p>
          Main Developer: {{ mainDeveloper }}
          <a :href="`mailto:${mainDeveloperEmail}`"
            >&lt;{{ mainDeveloperEmail }}&gt;</a
          >
        </p>
        <p>Contributor: {{ contributors }}</p>
        <p>First version by Sokitume</p>
        <p v-if="discordUrl">
          <v-icon class="mr-1">mdi-discord</v-icon
          ><a :href="discordUrl">Discord</a>
        </p>
        <p v-if="githubUrl">
          <v-icon class="mr-1">mdi-github</v-icon
          ><a :href="githubUrl">GitHub</a>
        </p>
      </v-card-text>
    </v-card>

    <!-- Changelog -->
    <changelog></changelog>
  </v-card>
</template>

<script>
import Changelog from "../components/Changelog";
export default {
  components: {Changelog},

  metaInfo() {
    return {
      title: this.$route.name,
      meta: [
        {
          vmid: 'google-title',
          itemprop: 'name',
          content: `PixyShip - ${this.$route.name}`
        },
        {
          vmid: 'og-title',
          property: 'og:title',
          content: `PixyShip - ${this.$route.name}`
        },
        {
          vmid: 'twitter-title',
          name: 'twitter:title',
          content: `PixyShip - ${this.$route.name}`
        },
      ]
    }
  },

  data() {
    return {
      mainDeveloper: "Solevis",
      mainDeveloperEmail: "contact@pixyship.com",
      contributors: "Bril, The worst.",
      donationUrl: process.env.VUE_APP_DONATION_URL,
      discordUrl: process.env.VUE_APP_PIXYSHIP_DISCORD_URL,
      githubUrl: process.env.VUE_APP_PIXYSHIP_GITHUB_URL,
    }
  },

  methods: {
    buyMeACoffee() {
      window.open(this.donationUrl)
    },
  },
}
</script>