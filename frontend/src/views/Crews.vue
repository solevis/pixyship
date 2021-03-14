<template>
  <v-card>
    <v-card-title>
      <v-layout row>
        <v-flex xs1 class="pl-3 pr-1">
          <v-text-field
            v-model="level"
            type="number"
            label="Level"
            min="1"
            max="40"
            :value="level"
          ></v-text-field>
        </v-flex>

        <v-flex xs11 class="pl-1 pr-3">
          <v-text-field
            v-model="search"
            append-icon="mdi-magnify"
            label="Search"
            placeholder="Name, Ability, Rarity or Collection"
            hide-details
          ></v-text-field>
        </v-flex>
      </v-layout>
    </v-card-title>

    <v-card-text>
      Tips: Find multiple occurrences by separating them with a comma, and exact
      term with double quotes (example: "Zombie", Eva)
    </v-card-text>

    <v-data-table
      :headers="headers"
      :items="crews"
      :search="search"
      :sort-by="['rarity_order']"
      :sort-desc="[true]"
      :custom-filter="multipleFilter"
      :items-per-page="20"
      :loading="isLoading"
      :footer-props="{
        itemsPerPageOptions: [10, 20, 50, 100, 200, -1],
      }"
      multi-sort
      dense
      loading-text="Loading..."
      class="elevation-1"
    >
      <template
        v-if="this.isLoading"
        v-slot:progress
      >
        <v-progress-linear
          color="cyan"
          :height="1"
          indeterminate
        ></v-progress-linear>
      </template>

      <template v-slot:body="{ items }">
        <tbody>
          <tr v-for="item in items" :key="item.id">
            <!-- Order -->
            <td>
              <div class="center char-sprite">
                <crew :char="item" :tip="false" />
              </div>
            </td>

            <!-- Name -->
            <td>
                <div class="text-xs-left"><a :class="[item.rarity, 'lh-9', 'name']" :href="`/crew/${item.id}`">{{ item.name }}</a></div>
            </td>

            <!-- Equip -->
            <td>
              <div class="ps-left equip">
                <div v-for="(s, k) in item.equipment" :key="k">
                  <div
                    v-if="s.name"
                    :title="`${k}: +${s.bonus} ${s.enhancement} ${
                      s.extra_bonus ? '+' + s.extra_bonus : ''
                    } ${s.extra_enhancement}`"
                  >
                    <div class="char-item" :style="spriteStyle(s.sprite)"></div>
                    {{ s.name }}
                  </div>
                  <template v-else>
                    <div class="unused">{{ k }}</div>
                  </template>
                </div>
              </div>
            </td>

            <!-- Rarity -->
            <td>
              <div :class="['rarity', item.rarity]">{{ item.rarity }}</div>
            </td>

            <td>
              <div class="special-ability">
                <v-tooltip bottom>
                  <template v-slot:activator="{ on, attrs }">
                    <div
                      v-bind="attrs" 
                      v-on="on"
                      :style="spriteStyle(item.ability_sprite)"
                    ></div>

                  </template>
                  {{ item.special_ability }}
                </v-tooltip>
              </div>
            </td>

            <!-- Collection -->
            <td>
              <v-tooltip v-if="item.collection_sprite" bottom>
                  <template v-slot:activator="{ on, attrs }">
                    <div
                      v-bind="attrs" 
                      v-on="on"
                      :style="spriteStyle(item.collection_sprite)"
                      class="center"
                    ></div>

                  </template>
                  {{ item.collection_name }}
                </v-tooltip>
            </td>

            <!-- Stats -->
            <td>{{ item.hp[2] | statFormat(0) }}</td>
            <td>{{ item.attack[2] | statFormat() }}</td>
            <td>{{ item.repair[2] | statFormat() }}</td>
            <td>{{ item.ability[2] | statFormat() }}</td>
            <td>{{ item.pilot[2] | statFormat() }}</td>
            <td>{{ item.science[2] | statFormat() }}</td>
            <td>{{ item.engine[2] | statFormat() }}</td>
            <td>{{ item.weapon[2] | statFormat() }}</td>

            <!-- Fire -->
            <td>{{ item.fire_resist }}</td>

            <!-- Training -->
            <td>{{ item.training_limit }}</td>

            <!-- Speed -->
            <td>
              <div>{{ `${item.walk}:${item.run}` }}</div>
            </td>
          </tr>
        </tbody>
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
import axios from "axios";
import mixins from "@/mixins/PixyShip.vue.js";
import Crew from "@/components/Crew.vue";
// require('../assets/css/common.css')

export default {
  mixins: [mixins],

  components: {
    Crew
  },

  data() {
    return {
      search: "",
      isLoading: false,
      headers: [
        { text: "Order", align: "center", value: "id", filterable: false },
        { text: "Name", align: "center", value: "name" },
        {
          text: "Equip",
          align: "center",
          value: "equipment",
          filterable: false,
        },
        { text: "Rarity", align: "center", value: "rarity" },
        { text: "Special", align: "center", value: "special_ability" },
        { text: "Set", align: "center", value: "collection_name" },
        { text: "HP", align: "center", value: "hp[2]", filterable: false },
        {
          text: "Attack",
          align: "center",
          value: "attack[2]",
          filterable: false,
        },
        {
          text: "Repair",
          align: "center",
          value: "repair[2]",
          filterable: false,
        },
        {
          text: "Ability",
          align: "center",
          value: "ability[2]",
          filterable: false,
        },
        {
          text: "Pilot",
          align: "center",
          value: "pilot[2]",
          filterable: false,
        },
        {
          text: "Science",
          align: "center",
          value: "science[2]",
          filterable: false,
        },
        {
          text: "Engine",
          align: "center",
          value: "engine[2]",
          filterable: false,
        },
        {
          text: "Weapon",
          align: "center",
          value: "weapon[2]",
          filterable: false,
        },
        {
          text: "Fire",
          align: "center",
          value: "fire_resist",
          filterable: false,
        },
        {
          text: "Training",
          align: "center",
          value: "training_limit",
          filterable: false,
        },
        { text: "Speed", align: "center", value: "run", filterable: false },
      ],
      crews: [],
      level: 40,
    };
  },

  beforeMount: function () {
    this.getCrews();
  },

  watch: {
    level () {
      this.updateCurrentLevel()
    }
  },

  filters: {
    statFormat(value, maxDigits = 1) {
      return value.toLocaleString("en-US", {
        maximumFractionDigits: maxDigits,
      });
    },
  },

  methods: {
    getCrews: async function () {
      this.isLoading = true;
      const response = await axios.get(this.crewEndpoint);

      let crews = [];
      for (const k in response.data.data) {
        const crew = response.data.data[k];
        crews.push(crew);
      }

      crews.sort((a, b) => b.rarity_order - a.rarity_order);

      this.crews = crews;

      this.isLoading = false;
      this.updateCurrentLevel();

      return this.crew;
    },

    updateCurrentLevel() {
      this.crews.map((crew) => {
        this.interpolateStat(crew.progression_type, crew.hp);
        this.interpolateStat(crew.progression_type, crew.attack);
        this.interpolateStat(crew.progression_type, crew.repair);
        this.interpolateStat(crew.progression_type, crew.ability);
        this.interpolateStat(crew.progression_type, crew.pilot);
        this.interpolateStat(crew.progression_type, crew.science);
        this.interpolateStat(crew.progression_type, crew.research);
        this.interpolateStat(crew.progression_type, crew.engine);
        this.interpolateStat(crew.progression_type, crew.weapon);
      });
    },

    interpolateStat(type, stat) {
      let p = 1; // Linear

      if (type === "EaseIn") {
        p = 2;
      } else if (type === "EaseOut") {
        p = 0.5;
      }

      stat[2] = stat[0] + (stat[1] - stat[0]) * ((this.level - 1) / 39) ** p;
    },
  },
};
</script>

<style scoped src="@/assets/css/common.css"></style>
<style scoped>
.rarity {
  text-transform: capitalize;
}

.name {
  font-weight: bold;
}

a.name {
  text-decoration: none;
}

.equip {
  line-height: 1;
  font-size: 80%;
}
</style>