<template>
  <v-card :loading="isLoading" class="full-height">
    <v-card-title class="overline">> Pins </v-card-title>
    <v-card-subtitle>All pins/achievements infos of Pixel Starships</v-card-subtitle>

    <!-- Filters -->
    <v-card-subtitle v-if="loaded">
      <v-row>
        <v-col cols="12">
          <v-text-field
              v-model="searchName"
              append-icon="mdi-magnify"
              label="Name"
              hint='For example: "2020 Fleet Bronze", Individuals'
              clearable
              outlined
          ></v-text-field>
        </v-col>
      </v-row>
    </v-card-subtitle>

    <!-- Table -->
    <v-data-table
        v-if="loaded"
        mobile-breakpoint="0"
        :headers="headers"
        :items="achievements"
        :search="searchName"
        :custom-filter="multipleFilterWithNegative"
        :items-per-page="20"
        :loading="isLoading"
        :footer-props="{
        itemsPerPageOptions: [10, 20, 50, 100, 200, -1],
      }"
        :sort-by.sync="globalSortBy"
        :sort-desc.sync="globalSortDesc"
        multi-sort
        loading-text="Loading..."
        class="elevation-1 px-3"
    >
      <template v-slot:item="{ item }">
        <tr>
          <td class="text-center">
            <div class="block my-1" :style="spriteStyle(item.sprite)"></div>
          </td>
          <td class="name">{{ item.name }}</td>
          <td>{{ item.description }}</td>
          <td>
            <table>
              <tr v-if="item.mineral_reward > 0" class="nobreak">
                <td>
                  <div :style="mineralSprite()" />
                </td>
                <td>{{ item.mineral_reward }}</td>
              </tr>

              <tr v-if="item.starbux_reward > 0" class="nobreak">
                <td>
                  <div :style="buxSprite()" />
                </td>
                <td>{{ item.starbux_reward }}</td>
              </tr>

              <tr v-if="item.gas_reward > 0" class="nobreak">
                <td>
                  <div :style="gasSprite()" />
                </td>
                <td>{{ item.gas_reward }}</td>
              </tr>

              <tr v-if="item.pin_reward" class="nobreak">
                <td>
                  <div class="block my-1 middle" :style="spriteStyle(item.sprite)"></div>
                </td>
                <td>(pin)</td>
              </tr>
            </table>
          </td>
        </tr>
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
import axios from "axios"
import PixyShipMixin from "@/mixins/PixyShip.vue.js"
import DataTableMixin from "@/mixins/DataTable.vue.js"

export default {
  mixins: [PixyShipMixin, DataTableMixin],

  data() {
    return {
      achievements: [],
      loaded: false,
      searchName: this.name,
      headers: [
        {
          text: "Order by ID",
          align: "center",
          value: "id",
          width: 95,
          filter: value => {
            const query = this.$route.query

            // no parameters
            if (!query.ids || this.pendingFilter) {
              return true
            }

            const ids = query.ids.split(',').map(function(id) {
              return parseInt(id.trim())
            })

            return ids.includes(value)
          }
        },
        {
          text: "Name",
          align: "left",
          value: "name",
          filterable: true
        },
        {
          text: "Description",
          align: "left",
          value: "description",
          filterable: true
        },
        {
          text: "Reward",
          align: "left",
          value: "max_reward",
          sortable: true,
          filterable: false
        },
      ],
    }
  },

  computed: {
    isLoading: function () {
      return !this.loaded
    },
    pendingFilter: function () {
      return this.searchName
    }
  },

  created() {
    document.title = 'PixyShip - ' + this.$route.name
  },

  beforeMount: function () {
    this.initFilters()
    this.getAchievements()
  },

  watch: {
    searchName(value) {
      this.updateQueryFromFilter('name', value)
    },
  },

  methods: {
    initFilters() {
      this.searchName = this.$route.query.name
    },

    getAchievements: async function () {
      const response = await axios.get(this.achievementsEndpoint)

      let achievements = Object.entries(response.data.data).map(
          (achievement) => achievement[1]
      )

      achievements.sort((a, b) => b.id - a.id)

      this.achievements = achievements

      this.loaded = true
      return this.achievements
    },
  },
}
</script>

<style scoped src="@/assets/css/common.css"></style>
<style scoped>
.block {
  display: inline-block;
}

.middle {
  vertical-align: middle;
}

.name {
  font-weight: bold;
}

a.name {
  text-decoration: none;
}
</style>