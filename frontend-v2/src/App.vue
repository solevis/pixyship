<template>
  <v-app>

    <v-app-bar app dense>
      <v-toolbar-title>
        <router-link to="/">
          <v-img
            :src="require('./assets/img/pixyship.svg')"
            max-height="57"
            max-width="150"
            contain
          ></v-img>
        </router-link>
      </v-toolbar-title>

      <v-spacer></v-spacer>

      <v-btn text to="/players">Players</v-btn>
      <v-btn text to="/builder">Builder</v-btn>
      <v-btn text to="/changes">Changes</v-btn>
      <v-btn text to="/crews">Crews</v-btn>
      <v-btn text to="/items">Items</v-btn>
      <v-btn text to="/rooms">Rooms</v-btn>
      <v-btn text to="/ships">Ships</v-btn>
      <v-btn text to="/collections">Collections</v-btn>
      <v-btn text to="/researches">Researches</v-btn>
      <v-btn text to="/about">About</v-btn>
    </v-app-bar>

    <v-main>
      <v-container fluid>
        <router-view></router-view>
      </v-container>
    </v-main>

    <v-footer app padless>
      <!--  -->
    </v-footer>
  </v-app>
</template>

<script>
export default {
  name: "App",
};
</script>

<style lang="sass">
    @import '../node_modules/typeface-roboto/index.css'
  </style>