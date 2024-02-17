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
        <v-btn text small to="/players">Players</v-btn>
        <v-btn text small to="/builder">Builder</v-btn>
        <v-btn text small to="/changes">Changes</v-btn>
        <v-btn text small to="/crews">Crews</v-btn>
        <v-btn text small to="/items">Items</v-btn>
        <v-btn text small to="/rooms">Rooms</v-btn>
        <v-btn text small to="/skins">Skins</v-btn>
        <v-btn text small to="/crafts">Crafts</v-btn>
        <v-btn text small to="/missiles">Missiles</v-btn>
        <v-btn text small to="/ships">Ships</v-btn>
        <v-menu
          open-on-hover
          bottom
          offset-y
        >
          <template v-slot:activator="{ on, attrs }">
            <v-btn
              text
              small
              v-bind="attrs"
              v-on="on"
            >
              Misc
              <v-icon right>
                mdi-menu-down
              </v-icon>
            </v-btn>
          </template>

          <v-list>
            <v-list-item to="/collections">
              <v-list-item-title>Collections</v-list-item-title>
            </v-list-item>
            <v-list-item to="/achievements">
              <v-list-item-title>Pins</v-list-item-title>
            </v-list-item>
            <v-list-item to="/researches">
              <v-list-item-title>Researches</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
        <v-btn small aria-label="About" icon to="/about"><v-icon small>mdi-help-circle-outline</v-icon></v-btn>
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
            <v-list-item to="/skins"><v-list-item-title>Skins</v-list-item-title></v-list-item>
            <v-list-item to="/crafts"><v-list-item-title>Crafts</v-list-item-title></v-list-item>
            <v-list-item to="/missiles"><v-list-item-title>Missiles</v-list-item-title></v-list-item>
            <v-list-item to="/ships"><v-list-item-title>Ships</v-list-item-title></v-list-item>
            <v-list-item to="/collections"><v-list-item-title>Collections</v-list-item-title></v-list-item>
            <v-list-item to="/achievements"><v-list-item-title>Pins</v-list-item-title></v-list-item>
            <v-list-item to="/researches"><v-list-item-title>Researches</v-list-item-title></v-list-item>
            <v-list-item to="/about"><v-list-item-title>About</v-list-item-title></v-list-item>
          </v-list-item-group>
        </v-list>
      </v-navigation-drawer>

    <v-main>
      <v-container fluid class="full-height">
        <router-view :key="$route.fullPath"></router-view>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
export default {
  metaInfo: {
    title: '',
    titleTemplate: (titleChunk) => {
      return titleChunk ? `PixyShip - ${titleChunk}` : 'PixyShip';
    },
    meta: [
      {charset: 'utf-8'},
      {
        vmid: 'description',
        name: 'description',
        content: 'Daily offers, crews, prestiges recipes, items, market price and others resources of Pixel Starships game.'
      },
      {
        vmid: 'google-description',
        itemprop: 'description',
        content: 'Daily offers, crews, prestiges recipes, items, market price and others resources of Pixel Starships game.'
      },
      {
        vmid: 'google-title',
        itemprop: 'name',
        content: 'PixyShip'
      },
      {
        vmid: 'og-description',
        property: 'og:description',
        content: 'Daily offers, crews, prestiges recipes, items, market price and others resources of Pixel Starships game.'
      },
      {
        vmid: 'og-title',
        property: 'og:title',
        content: 'PixyShip'
      },
      {
        vmid: 'twitter-description',
        name: 'twitter:description',
        content: 'Daily offers, crews, prestiges recipes, items, market price and others resources of Pixel Starships game.'
      },
      {
        vmid: 'twitter-title',
        name: 'twitter:title',
        content: 'PixyShip'
      },
      {name: 'viewport', content: 'width=device-width,initial-scale=1.0'},
      {name: 'msapplication-TileColor', content: '#2b5797'},
      {name: 'msapplication-config', content: process.env.BASE_URL + 'browserconfig.xml'},
      {name: 'theme-color', content: '#000000'},
      {'http-equiv': 'X-UA-Compatible', content: 'IE=edge'},
    ]
  },

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