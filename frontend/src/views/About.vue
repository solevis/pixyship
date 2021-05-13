<template>
  <v-card class="px-5 pb-1">
    <v-card-title class="overline">> About</v-card-title>
    <v-card class="mb-4" elevation="2" outlined>
      <v-card-title>Developpers</v-card-title>

      <v-card-text>
        <p>Main Developper: Solevis <a href="mailto:contact@pixyship.net">&lt;contact@pixyship.net&gt;</a></p>
        <p>Contributor: Bril</p>
        <p>First version by Sokitume </p>
        <p><v-icon class="mr-1">mdi-discord</v-icon><a href="https://discord.gg/R49rqhzYrh">Discord</a></p>
        <p><v-icon class="mr-1">mdi-github</v-icon><a href="https://github.com/solevis/pixyship/">GitHub</a></p>
      </v-card-text>
    </v-card>

    <v-card class="mb-4" elevation="2" outlined>
      <v-card-title>Donate</v-card-title>

      <v-card-text>
        <a href="https://www.buymeacoffee.com/solevis" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-blue.png" alt="Buy Me A Beer" style="height: 60px !important;width: 217px !important;" ></a>
      </v-card-text>
    </v-card>
  </v-card>
</template>

<script>
export default {
  created() {
    document.title = 'PixyShip - ' + this.$route.name
  },
}
</script>