<template>
  <v-card :loading="isLoading">
    <v-card-title class="overline">> Collections </v-card-title>
    <v-card-subtitle>All crew collections infos (crews, bonus, skill, ...) of Pixel Starships</v-card-subtitle>

    <!-- Filters -->
    <v-card-subtitle v-if="loaded">
      <v-row>
        <v-col cols="12" sm="6" md="9">
          <v-text-field
            v-model="searchName"
            append-icon="mdi-magnify"
            label="Name"
            hint='For example: "Ardent", Cat'
            clearable
            outlined
          ></v-text-field>
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <v-combobox
            v-model="searchSkill"
            :items="skills"
            label="Skill"
            clearable
            multiple
            small-chips
            hide-details
            outlined
          ></v-combobox>
        </v-col>
      </v-row>
    </v-card-subtitle>

    <!-- Table -->
    <v-data-table
      v-if="loaded"
      mobile-breakpoint="0"
      :headers="headers"
      :items="collections"
      :search="searchName"
      :custom-filter="multipleFilterWithNegative"
      :items-per-page="20"
      :loading="isLoading"
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
            <div :style="spriteStyle(item.icon_sprite)"></div>
          </td>
          <td class="name">{{ item.name }}</td>
          <td>{{ item.ability_name }}</td>
          <td>
            <div v-if="item.chars.length > 0">
              <div
                v-for="crew in item.chars"
                :key="crew.id"
                class="center char-sprite block"
              >
                <crew :char="crew" tipPosition="right" />
              </div>
            </div>
          </td>
          <td>{{ `${item.min} - ${item.max}` }}</td>
          <td>{{ item.base_enhancement }}</td>
          <td>{{ item.step_enhancement }}</td>
          <td>{{ item.CollectionDescription }}</td>
        </tr>
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
import axios from "axios";
import mixins from "@/mixins/PixyShip.vue.js";
import Crew from "@/components/Crew.vue";

export default {
  mixins: [mixins],

  components: {
    Crew,
  },

  data() {
    return {
      searchName: "",
      searchSkill: [],
      skills: [],
      loaded: false,
      headers: [
        { text: "Image", align: "center", class: 'sticky-header', sortable: false, filterable: false },
        { text: "Name", align: "left", class: 'sticky-header', value: "name" },
        {
          text: "Skill",
          align: "left",
          class: 'sticky-header',
          value: "ability_name",
          filter: (value) => {
            return this.filterCombobox(value, this.searchSkill);
          },
        },
        { text: "Chars", align: "left", class: 'sticky-header', sortable: false, filterable: false },
        {
          text: "Required (Min - Max)",
          align: "center",
          class: 'sticky-header',
          value: "min",
          filterable: false,
        },
        {
          text: "Base Bonus",
          align: "right",
          class: 'sticky-header',
          value: "base_enhancement",
          filterable: false,
        },
        {
          text: "Step Bonus",
          align: "right",
          class: 'sticky-header',
          value: "step_enhancement",
          filterable: false,
        },
        {
          text: "Description",
          align: "left",
          class: 'sticky-header',
          value: "CollectionDescription",
          filterable: false,
        },
      ],
      collections: [],
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
    this.getCollections();
  },
  
  methods: {
    getCollections: async function () {
      const response = await axios.get(this.collectionsEndpoint);

      let collections = Object.entries(response.data.data).map(
        (collection) => collection[1]
      );
      collections.sort((a, b) => b.name - a.name);

      this.collections = collections;
      this.updateFilters();

      this.loaded = true;
      return this.collections;
    },

    updateFilters() {
      this.skills = Array.from(
        new Set(this.collections.map((collection) => collection.ability_name))
      );
    },
  },
};
</script>

<style scoped src="@/assets/css/common.css"></style>
<style scoped src="@/assets/css/stickyheader.css"></style>
<style scoped>
.center {
  margin: 0 auto;
}

.block {
  display: inline-block;
}

.name {
  font-weight: bold;
}

a.name {
  text-decoration: none;
}
</style>