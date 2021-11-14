<template>
  <v-app>

    <v-app-bar app ref="toolbar">
      <v-app-bar-nav-icon v-if="$vuetify.breakpoint.smAndDown" aria-label="Menu" @click="drawer = true"></v-app-bar-nav-icon>

      <v-toolbar-title v-if="$vuetify.breakpoint.smAndDown || $vuetify.breakpoint.lgAndUp">
        <router-link to="/">
          <v-img
            :src="require('./assets/img/pixyship.svg')"
            max-height="57"
            max-width="150"
            contain
            alt="PixyShip logo"
          ></v-img>
        </router-link>
      </v-toolbar-title>

      <v-toolbar-title v-else>
        <router-link to="/">
          <v-img
            :src="require('./assets/img/pixyship_logo.svg')"
            max-height="40"
            max-width="40"
            class="mr-2"
            contain
          ></v-img>
        </router-link>
      </v-toolbar-title>

      <v-spacer></v-spacer>

      <template v-if="$vuetify.breakpoint.mdAndUp">
        <v-btn text to="/players">Players</v-btn>
        <v-btn text to="/builder">Builder</v-btn>
        <v-btn text to="/changes">Changes</v-btn>
        <v-btn text to="/crews">Crews</v-btn>
        <v-btn text to="/items">Items</v-btn>
        <v-btn text to="/rooms">Rooms</v-btn>
        <v-btn text to="/ships">Ships</v-btn>
        <v-btn text to="/collections">Collections</v-btn>
        <v-btn text to="/researches">Researches</v-btn>
        <v-btn aria-label="About" icon to="/about"><v-icon>mdi-help-circle-outline</v-icon></v-btn>
      </template>
    </v-app-bar>

    <v-navigation-drawer
        v-if="$vuetify.breakpoint.smAndDown"
        v-model="drawer"
        temporary
        app
      >
        <v-list
          nav
          dense
        >
          <v-list-item-group>
             <v-list-item to="/"><v-list-item-title>Home</v-list-item-title></v-list-item>
            <v-list-item to="/players"><v-list-item-title>Players</v-list-item-title></v-list-item>
            <v-list-item to="/builder"><v-list-item-title>Builder</v-list-item-title></v-list-item>
            <v-list-item to="/changes"><v-list-item-title>Changes</v-list-item-title></v-list-item>
            <v-list-item to="/crews"><v-list-item-title>Crews</v-list-item-title></v-list-item>
            <v-list-item to="/items"><v-list-item-title>Items</v-list-item-title></v-list-item>
            <v-list-item to="/rooms"><v-list-item-title>Rooms</v-list-item-title></v-list-item>
            <v-list-item to="/ships"><v-list-item-title>Ships</v-list-item-title></v-list-item>
            <v-list-item to="/collections"><v-list-item-title>Collections</v-list-item-title></v-list-item>
            <v-list-item to="/researches"><v-list-item-title>Researches</v-list-item-title></v-list-item>
            <v-list-item to="/about"><v-list-item-title>About</v-list-item-title></v-list-item>
          </v-list-item-group>
        </v-list>
      </v-navigation-drawer>

    <v-main>
      <v-container fluid class="full-height">
        <router-view></router-view>
      </v-container>
    </v-main>

    <v-footer
    padless
  >
    <v-row
      justify="center"
      no-gutters
    >
      <v-col
        class="py-1 text-center white--text"
        cols="12"
      >
        <strong>PixyShip</strong> — <a class="white--text" href="/changelog">v2.2.5</a>
      </v-col>
    </v-row>
  </v-footer>
  </v-app>
</template>

<script>
export default {
  mounted () {
    this.onMutate()
  },

  methods: {
    onMutate () {
      let height = 0
      const toolbar = this.$refs.toolbar
      
      if (toolbar) {
        height = `${toolbar.$el.offsetHeight}px`
      }

      document.documentElement.style.setProperty('--headerHeight', height)
    }
  },

  name: "App",
  data: () => ({
    drawer: false,
  }),
}
</script>

<style lang="sass">
  @import '../node_modules/typeface-roboto/index.css'
</style>

 <style>
  html {
    overflow-y: auto !important;
  }

  .full-height {
    height: 100%;
  }
</style>