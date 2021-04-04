<template>
  <v-card :loading="isLoading">
    <v-card-title v-if="!loaded"> Loading... </v-card-title>

    <!-- Filters -->
    <v-card-title v-if="loaded">
      <v-row>
        <v-col cols="9">
          <v-text-field
            v-model="searchName"
            append-icon="mdi-magnify"
            label="Name"
            hint='For example: "Argent", Cat'
            clearable
          ></v-text-field>
        </v-col>
        <v-col cols="3">
          <v-combobox
            v-model="searchSkill"
            :items="skills"
            label="Skill"
            clearable
            multiple
            small-chips
            hide-details
          ></v-combobox>
        </v-col>
      </v-row>
    </v-card-title>

    <!-- Table -->
    <v-data-table
      v-if="loaded"
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
      class="elevation-1"
      dense
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
        { text: "Image", align: "center", sortable: false, filterable: false },
        { text: "Name", align: "left", value: "name" },
        {
          text: "Skill",
          align: "left",
          value: "ability_name",
          filter: (value) => {
            return this.filterCombobox(value, this.searchSkill);
          },
        },
        { text: "Chars", align: "left", sortable: false, filterable: false },
        {
          text: "Required (Min - Max)",
          align: "center",
          value: "min",
          filterable: false,
        },
        {
          text: "Base Bonus",
          align: "right",
          value: "base_enhancement",
          filterable: false,
        },
        {
          text: "Step Bonus",
          align: "right",
          value: "step_enhancement",
          filterable: false,
        },
        {
          text: "Description",
          align: "left",
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