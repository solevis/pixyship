<template>
  <v-card :loading="isLoading">
    <v-card-title v-if="!loaded"> Loading... </v-card-title>

    <!-- Crew sprite -->
    <v-card-title v-if="loaded">
      <div class="mx-auto">
        <crew :char="character" :tip="false" name="bottom" />
      </div>
    </v-card-title>

    <!-- Large screen (Table and prestiges side by side) -->
    <template v-if="loaded && $vuetify.breakpoint.mdAndUp">
      <v-row justify="center">
        <v-col>
          <v-simple-table v-if="loaded" dense class="px-3">
            <template v-slot:default>
              <thead>
                <tr>
                  <th class="text-left">Level</th>
                  <th class="text-left">Equip</th>
                  <th class="text-left">Rarity</th>
                  <th class="text-left">Special</th>
                  <th class="text-left">Set</th>
                  <th class="text-left">HP</th>
                  <th class="text-left">ATK</th>
                  <th class="text-left">RPR</th>
                  <th class="text-left">ABL</th>
                  <th class="text-left">PLT</th>
                  <th class="text-left">SCI</th>
                  <th class="text-left">ENG</th>
                  <th class="text-left">WPN</th>
                  <th class="text-left">Fire</th>
                  <th class="text-left">Training</th>
                  <th class="text-left">Speed</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>
                    <v-text-field
                      v-model="level"
                      type="number"
                      min="1"
                      max="40"
                      dense
                      single-line
                      :value="level"
                      style="max-width: 50px"
                    ></v-text-field>
                  </td>
                  <!-- Equip -->
                  <td>
                    <div class="ps-left equip">
                      <div v-for="(s, k) in character.equipment" :key="k">
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
                    <div :class="['rarity', character.rarity]">
                      {{ character.rarity }}
                    </div>
                  </td>

                  <td>
                    <div class="special-ability">
                      <v-tooltip bottom color="blue-grey">
                        <template v-slot:activator="{ on, attrs }">
                          <div
                            v-bind="attrs"
                            v-on="on"
                            :style="spriteStyle(character.ability_sprite)"
                          ></div>
                        </template>
                        {{ character.special_ability }}
                      </v-tooltip>
                    </div>
                  </td>

                  <!-- Collection -->
                  <td>
                    <v-tooltip v-if="character.collection_sprite" bottom color="blue-grey">
                      <template v-slot:activator="{ on, attrs }">
                        <div
                          v-bind="attrs"
                          v-on="on"
                          :style="spriteStyle(character.collection_sprite)"
                          class="center"
                        ></div>
                      </template>
                      {{ character.collection_name }}
                    </v-tooltip>
                  </td>

                  <!-- Stats -->
                  <td>{{ character.hp[2] | statFormat(0) }}</td>
                  <td>{{ character.attack[2] | statFormat() }}</td>
                  <td>{{ character.repair[2] | statFormat() }}</td>
                  <td>{{ character.ability[2] | statFormat() }}</td>
                  <td>{{ character.pilot[2] | statFormat() }}</td>
                  <td>{{ character.science[2] | statFormat() }}</td>
                  <td>{{ character.engine[2] | statFormat() }}</td>
                  <td>{{ character.weapon[2] | statFormat() }}</td>

                  <!-- Fire -->
                  <td>{{ character.fire_resist }}</td>

                  <!-- Training -->
                  <td>{{ character.training_limit }}</td>

                  <!-- Speed -->
                  <td>
                    <div>{{ `${character.walk}:${character.run}` }}</div>
                  </td>
                </tr>
              </tbody>
            </template>
          </v-simple-table>
        </v-col>
      </v-row>

      <v-row class="mt-2 pb-2" justify="center">
        <v-col cols="4">
          <div class="text-center">
            <span>Combine both for {{ character.name }}:</span>
          </div>
        </v-col>

        <v-col cols="4">
          <div class="text-center">
            <span>Combine with {{ character.name }} to get:</span>
          </div>
        </v-col>
      </v-row>

      <v-row class="mt-1" justify="center">
        <v-col cols="4" v-if="notEmptyObject(to)" class="mt-3">
          <v-row
            v-for="(olist, t) in to"
            :key="'grouped-to-' + t"
            class="mb-2"
            align="center"
          >
            <v-col class="right-curve-border">
              <v-row v-for="o in olist" :key="'to-' + o">
                <v-col>
                  <crew :char="characters[o]" name="left" tipPosition="right"/>
                </v-col>
              </v-row>
            </v-col>

            <v-col>
              <crew :char="characters[t]" name="right" />
            </v-col>
          </v-row>
        </v-col>

        <v-col cols="4" v-else>
          <div class="text-center">
            <v-icon>mdi-flask-empty-off-outline</v-icon>
          </div>
        </v-col>

        <v-col cols="4" v-if="notEmptyObject(from)" class="mt-3">
          <v-row
            v-for="(olist, t) in from"
            :key="'grouped-from-' + t"
            class="mb-2"
            align="center"
          >
            <v-col class="right-curve-border">
              <v-row v-for="o in olist" :key="'from-' + o">
                <v-col>
                  <crew :char="characters[o]" name="left" tipPosition="right"/>
                </v-col>
              </v-row>
            </v-col>
            <v-col>
              <crew :char="characters[t]" name="right" />
            </v-col>
          </v-row>
        </v-col>

        <v-col cols="4" v-else>
          <div class="text-center">
            <v-icon>mdi-flask-empty-off-outline</v-icon>
          </div>
        </v-col>
      </v-row>
    </template>

    <!-- Small screen (infos as card and expandable prestiges) -->
    <v-row v-else-if="loaded" justify="center">
      <v-col>
        <v-card v-if="loaded" outlined>
          <v-card-title>Core Stats</v-card-title>
          <v-card-text>
            <span>HP: {{ character.hp[2] | statFormat(0) }}</span><br>
            <span>Attack: {{ character.attack[2] | statFormat() }}</span><br>
            <span>Repair: {{ character.repair[2] | statFormat() }}</span><br>
            <span>Ability: {{ character.ability[2] | statFormat() }}</span><br>
          </v-card-text>
        </v-card>

        <v-card v-if="loaded" outlined class="mt-2">
          <v-card-title>Room Stats</v-card-title>
          <v-card-text>
            <span>Pilot: {{ character.pilot[2] | statFormat() }}</span><br>
            <span>Science: {{ character.science[2] | statFormat() }}</span><br>
            <span>Engine: {{ character.engine[2] | statFormat() }}</span><br>
            <span>Weapon: {{ character.weapon[2] | statFormat() }}</span><br>
          </v-card-text>
        </v-card>

        <v-card v-if="loaded" outlined class="mt-2">
          <v-card-title>Utility Stats</v-card-title>
          <v-card-text>
            <span>Equip: {{ Object.keys(character.equipment).join(", ") }}</span><br>
            <span>Rarity: <span :class="['rarity', character.rarity]">{{ character.rarity }}</span></span><br>

            <div v-if="character.special_ability">Special: {{ character.special_ability }} <div :style="spriteStyle(character.ability_sprite)" class="center d-inline-block"></div></div>
            <div v-if="character.collection_name">Set: {{ character.collection_name }} <div :style="spriteStyle(character.collection_sprite)" class="center d-inline-block"></div></div>
            
            <!-- Fire -->
            <span>Fire Resist: {{ character.fire_resist }}</span><br>

            <!-- Training -->
            <span>Training: {{ character.training_limit }}</span><br>

            <!-- Speed -->
            <span>Walk/Run Speed: {{ `${character.walk}/${character.run}` }}</span><br>
          </v-card-text>
        </v-card>

        <v-card v-if="loaded" outlined class="mt-2 text-sm-body-2">
          <v-card-title>Prestige Options</v-card-title>
            <v-expansion-panels>
              <v-expansion-panel>
                <v-expansion-panel-header>
                  Combine both for {{ characters[crewId].name }}:
                </v-expansion-panel-header>
                <v-expansion-panel-content>
                  <v-row
                    v-for="(olist, t) in to"
                    :key="'grouped-to-' + t"
                    class="mb-2"
                    align="center"
                  >
                    <v-col>
                      <v-row class="mb-1">
                        <v-col cols="auto"><crew :char="characters[t]" name="right" /></v-col>
                      </v-row>

                      <v-row class="ml-10" no-gutters v-for="o in olist" :key="'to-' + o">
                        <v-col cols="auto">
                          <v-icon style="float: left" class="mr-2">mdi-plus</v-icon>
                          <crew :char="characters[o]" name="right" tipPosition="right"/>
                        </v-col>
                      </v-row>
                      <v-divider class="mt-5"></v-divider>
                    </v-col>
                  </v-row>

                  <div class="text-center" v-if="!notEmptyObject(to)">
                    <v-icon>mdi-flask-empty-off-outline</v-icon>
                  </div>
                </v-expansion-panel-content>
              </v-expansion-panel>

              <v-expansion-panel>
                <v-expansion-panel-header>
                  Combine with {{ characters[crewId].name }} to get:
                </v-expansion-panel-header>
                <v-expansion-panel-content>
                  <v-row
                    v-for="(olist, t) in from"
                    :key="'grouped-from-' + t"
                    class="mb-2"
                    align="center"
                  >
                    <v-col>
                      <v-row class="mb-1">
                        <v-col cols="auto"><crew :char="characters[t]" name="right" /></v-col>
                        <v-icon style="float: left" class="mr-2">mdi-equal</v-icon>
                      </v-row>

                      <v-row class="ml-8" no-gutters v-for="o in olist" :key="'from-' + o">
                        <v-col cols="auto">
                          <span style="float: left" :class="['mr-2', character.rarity]">{{ character.name }}</span>
                          <v-icon style="float: left" class="mr-2">mdi-plus</v-icon>
                          <crew :char="characters[o]" name="right" tipPosition="right"/>
                        </v-col>
                      </v-row>
                      <v-divider class="mt-5"></v-divider>
                    </v-col>
                  </v-row>

                  <div class="text-center" v-if="!notEmptyObject(from)">
                    <v-icon>mdi-flask-empty-off-outline</v-icon>
                  </div>
                </v-expansion-panel-content>
              </v-expansion-panel>
            </v-expansion-panels>
        </v-card>
      </v-col>
    </v-row>
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
      loaded: false,
      crewId: this.$route.params.id,
      characters: [],
      character: {},
      data: {},
      from: [],
      to: [],
      level: 40,
    };
  },

  computed: {
    isLoading: function () {
      return !this.loaded;
    },
  },

  beforeMount: function () {
    this.getCrew();
  },

  watch: {
    level() {
      this.updateCurrentLevel();
    },
  },

  filters: {
    statFormat(value, maxDigits = 1) {
      return value.toLocaleString("en-US", {
        maximumFractionDigits: maxDigits,
      });
    },
  },

  methods: {
    getCrew: async function () {
      const response = await axios.get(this.prestigeEndpoint + this.crewId);

      // TODO: This is ugly, fix it
      let characters = {};
      for (let character of response.data.data.chars) {
        characters[character.id] = character;
      }

      this.characters = characters;
      this.data = response.data.data;

      this.from = this.data.from;
      this.to = this.data.to;

      this.character = this.characters[this.crewId];
      document.title = 'PixyShip - ' + this.character.name

      this.loaded = true;
      this.updateCurrentLevel();
    },

    updateCurrentLevel() {
      this.interpolateStat(this.character.progression_type, this.character.hp);
      this.interpolateStat(
        this.character.progression_type,
        this.character.attack
      );
      this.interpolateStat(
        this.character.progression_type,
        this.character.repair
      );
      this.interpolateStat(
        this.character.progression_type,
        this.character.ability
      );
      this.interpolateStat(
        this.character.progression_type,
        this.character.pilot
      );
      this.interpolateStat(
        this.character.progression_type,
        this.character.science
      );
      this.interpolateStat(
        this.character.progression_type,
        this.character.engine
      );
      this.interpolateStat(
        this.character.progression_type,
        this.character.weapon
      );
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

.equip {
  line-height: 1;
  font-size: 80%;
}

div.right-curve-border {
  border-right: solid 5px #666;
  border-radius: 12px;
  padding: 5px;
}
</style>