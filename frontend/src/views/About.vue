<template>
  <v-card class="px-5 pb-1">
    <v-card-title class="overline right"></v-card-title>
    
    <v-card class="mb-4" elevation="2" outlined>
      <v-card-title>Donators</v-card-title>

      <v-card-text>
        <p class="font-weight-bold">A special thanks to all of the <a href="https://www.okpal.com/pixyship/#/" target="_blank">crowfunding campaign</a> crontributors, and especially to:</p>
        <p>Admiral Col, Albathoor, Alisrassa, Baradum, GudegLezat, Human Fly, Jean, JustcallmeDr, Maccinae, Matthew-II, Muinmacar, Phinie, Ruthless Rhino, Sahara Fleet, Scorpio99, ShadowfireAngel, Solphaen, Spaceman Spiff, The Flying Brick, The worst. and YankeeDood</p>
        <div class="mt-5" @click="buyMeACoffee" style="cursor: pointer; width: 300px;">
          <v-img
            :src="require('../assets/img/Solevis.png')"
            max-height="78"
            max-width="48"
            contain
            class="d-inline-block"
            style="vertical-align: middle"
          ></v-img>
          <p class="ml-2 font-weight-bold d-inline-block" style="vertical-align: middle">
            You like PixyShip?
            <br>
            <a href="https://www.buymeacoffee.com/solevis">Why not buy my captain a coffee?</a> <v-icon>mdi-coffee</v-icon>
            <br>
            
          </p>
        </div>
      </v-card-text>
    </v-card>
    
    <v-card class="mb-4" elevation="2" outlined>
      <v-card-title>Developpers</v-card-title>
      <v-card-text>
        <p>Main Developper: Solevis <a href="mailto:contact@pixyship.com">&lt;contact@pixyship.com&gt;</a></p>
        <p>Contributor: Bril</p>
        <p>First version by Sokitume </p>
        <p><v-icon class="mr-1">mdi-discord</v-icon><a href="https://discord.gg/R49rqhzYrh">Discord</a></p>
        <p><v-icon class="mr-1">mdi-github</v-icon><a href="https://github.com/solevis/pixyship/">GitHub</a></p>
      </v-card-text>
    </v-card>
  </v-card>
</template>

<script>
export default {
  created() {
    document.title = 'PixyShip - ' + this.$route.name
  },

  methods: {
    buyMeACoffee () {
      window.open('https://www.buymeacoffee.com/solevis');
    }
  }
}
</script>