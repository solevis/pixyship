<template>
  <v-card :loading="isLoading">
    <v-card-title class="overline">> Researches </v-card-title>
    <v-card-subtitle>All Pixel Starships researches</v-card-subtitle>

    <!-- Filters -->
    <v-card-subtitle v-if="loaded">
      <v-row>
        <v-col cols="12" sm="12" md="6">
          <v-text-field
            v-model="searchName"
            append-icon="mdi-magnify"
            label='Name'
            hint='For example: Missile, -Jungler, "Beer"'
            clearable
            outlined
          ></v-text-field>
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <v-combobox
            v-model="searchType"
            :items="types"
            label="Type"
            clearable
            outlined
            multiple
            small-chips
            hide-details
          ></v-combobox>
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <v-combobox
            v-model="searchLabLevel"
            :items="labLevels"
            label="Lab Level"
            clearable
            outlined
            multiple
            small-chips
            hide-details
          ></v-combobox>
        </v-col>
      </v-row>
    </v-card-subtitle>

    <!-- Table -->
    <v-data-table
      v-if="loaded"
      mobile-breakpoint="0"
      :headers="headers"
      :items="researches"
      :search="searchName"
      :custom-filter="multipleFilterWithNegative"
      :items-per-page="20"
      :loading="isLoading"
      :sortDesc="true"
      :footer-props="{
        itemsPerPageOptions: [10, 20, 50, 100, 200, -1],
      }"
      multi-sort
      loading-text="Loading..."
      class="elevation-1 px-3"
    >
      <template v-slot:item="{ item }">
        <tr>
          <td>
            <crew v-if="item.type === 'char'" :char="item.char"/>
            <div v-else class="block my-1" :style="spriteStyle(item.sprite)"></div>
          </td>
          <td class="name">
            {{ item.name }}
          </td>
          <td>{{ item.lab_level }}</td>
          <td>{{ item.required_research_name }}</td>
          <td>{{ item.research_type }}</td>
          <td>
            <table>
              <tr class="nobreak" v-if="item.gas_cost > 0">
                <td>
                  <div :style="gasSprite()" />
                </td>
                <td>{{ item.gas_cost }}</td>
              </tr>
              <tr class="nobreak" v-if="item.starbux_cost > 0">
                <td>
                  <div :style="buxSprite()" />
                </td>
                <td>{{ item.starbux_cost }}</td>
              </tr>
            </table>
          </td>
          <td>{{ formatTime(item.research_seconds) }}</td>
        </tr>
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
import axios from "axios";
import mixins from "@/mixins/PixyShip.vue.js";

export default {
  mixins: [mixins],

  components: {},

  data() {
    return {
      searchName: "",
      searchType: [],
      searchLabLevel: [],
      types: [],
      labLevers: [],
      loaded: false,
      headers: [
        {text: 'Image', class: 'sticky-header', sortable: false},
        {text: 'Name', class: 'sticky-header', value: 'name'},
        {
          text: 'Lab Level', 
          value: 'lab_level', 
          class: 'sticky-header',
          filter: (value) => {
            return this.filterCombobox(value, this.searchLabLevel);
          },
        },
        {text: 'Requirement', class: 'sticky-header', value: 'required_research_name'},
        {
          text: 'Type', 
          class: 'sticky-header',
          value: 'research_type',
          filter: (value) => {
            return this.filterCombobox(value, this.searchType);
          },
        },
        {text: 'Cost', class: 'sticky-header', value: 'cost'},
        {text: 'Upgrade Time', class: 'sticky-header', value: 'research_seconds'}
      ],
      researches: [],
    };
  },

  computed: {
    isLoading: function () {
      return !this.loaded;
    },
  },

  created() {
    document.title = 'PixyShip - ' + this.$route.name
  },

  beforeMount: function () {
    this.getResearches();
  },

  methods: {
    getResearches: async function () {
      const response = await axios.get(this.researchesEndpoint);

      let researches = Object.values(response.data.data)
      researches.forEach(research => {
        research.cost = research.gas_cost + research.starbux_cost
      })

      researches.sort((a, b) => b.name - a.name);

      this.researches = researches;
      this.updateFilters();

      this.loaded = true;
      return this.researches;
    },

    updateFilters() {
      this.types = Array.from(
        new Set(this.researches.map((research) => (!research.research_type ? "None" : research.research_type)))
      ).sort((a) => a === 'None' ? -1 : 1);

      this.labLevels = Array.from(
        new Set(this.researches.map((research) => (!research.lab_level ? "None" : research.lab_level)))
      ).sort((a, b) => a - b);
    },
  },
};
</script>

<style scoped src="@/assets/css/common.css"></style>
<style scoped src="@/assets/css/stickyheader.css"></style>
<style scoped>
.name {
  font-weight: bold;
}

a.name {
  text-decoration: none;
}
</style>