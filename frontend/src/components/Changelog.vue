<template>
  <v-card class="mb-4" elevation="2" outlined id="changelog">
    <v-card-title>Changelog</v-card-title>

    <v-expansion-panels accordion multiple v-model="panel">
      <v-expansion-panel>
        <v-expansion-panel-header>2.2.5 &mdash; 2021-11-14</v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-card flat>
            <v-card-subtitle>Added</v-card-subtitle>
            <v-card-text>
              <ul>
                <li>Ships page: extended filter</li>
                <li>Save sorting in URL</li>
              </ul>
            </v-card-text>
          </v-card>
        </v-expansion-panel-content>
      </v-expansion-panel>

      <v-expansion-panel>
        <v-expansion-panel-header>2.2.4 &mdash; 2021-11-12</v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-card flat>
            <v-card-subtitle>Changed</v-card-subtitle>
            <v-card-text>
              <ul>
                <li>Ships page: display full repair time</li>
              </ul>
            </v-card-text>

            <v-card-subtitle>Fixed</v-card-subtitle>
            <v-card-text>
              <ul>
                <li>Rooms page: wrong capacity label and value</li>
              </ul>
            </v-card-text>
          </v-card>
        </v-expansion-panel-content>
      </v-expansion-panel>

      <v-expansion-panel>
        <v-expansion-panel-header>2.2.3 &mdash; 2021-11-02</v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-card flat>
            <v-card-subtitle>Added</v-card-subtitle>
            <v-card-text>
              <ul>
                <li>Display item content (rewards)</li>
              </ul>
            </v-card-text>

            <v-card-subtitle>Changed</v-card-subtitle>
            <v-card-text>
              <ul>
                <li>Item description is now displayed in popup</li>
              </ul>
            </v-card-text>
          </v-card>
        </v-expansion-panel-content>
      </v-expansion-panel>

      <v-expansion-panel>
        <v-expansion-panel-header>2.2.2 &mdash; 2021-10-29</v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-card flat>
            <v-card-subtitle>Fixed</v-card-subtitle>
            <v-card-text>
              <ul>
                <li>Fix Speed unit for weapons rooms</li>
              </ul>
            </v-card-text>
          </v-card>
        </v-expansion-panel-content>
      </v-expansion-panel>

      <v-expansion-panel>
        <v-expansion-panel-header>2.2.1 &mdash; 2021-10-23</v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-card flat>
            <v-card-subtitle>Added</v-card-subtitle>
            <v-card-text>
              <ul>
                <li>Changelog page "/changelog" </li>
                <li>Changelog in about page</li>
              </ul>
            </v-card-text>

            <v-card-subtitle>Fixed</v-card-subtitle>
            <v-card-text>
              <ul>
                <li>Fix changelog link in footer</li>
              </ul>
            </v-card-text>
          </v-card>
        </v-expansion-panel-content>
      </v-expansion-panel>

      <v-expansion-panel>
        <v-expansion-panel-header>2.2.0 &mdash; 2021-10-23</v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-card flat>
            <v-card-subtitle>Added</v-card-subtitle>
            <v-card-text>
              <ul>
                <li>Dedicated item page with:
                  <ul>
                    <li>item infos</li>
                    <li>market history</li>
                    <li>last players sales</li>
                    <li>crafting tree</li>
                  </ul>
                </li>
                <li>Add "Type" filter on Changes page</li>
                <li>Add query parameter to all URL to filter assets (items, crews, etc.) by IDs (ids=X) or filters (ex: rarity=Common)</li>
                <li>Filtering data on pages will automatically update the URL, so going back in history will prevent losing your filters</li>
                <li>Add "player=" query parameter to the "Players" page URL</li>
                <li>[BETA] "Changes" page will now show new Pixel Starships sprites listed in API</li>
              </ul>
            </v-card-text>

            <v-card-subtitle>Changed</v-card-subtitle>
            <v-card-text>
              <ul>
                <li>Market chart is no longer displayed by expanding a row in Items page, it's now in item page by clicking item name or logo</li>
                <li>Serve sprites from PixyShip instead of Savy for better cache control</li>
                <li>Sort data by ID, most recent first (except Items, sorted by volume of sales)</li>
              </ul>
            </v-card-text>

            <v-card-subtitle>Fixed</v-card-subtitle>
            <v-card-text>
              <ul>
                <li>The armor calculation in the constructor always showed zero</li>
                <li>Display of power used/generated by rooms in Builder without color and too big font</li>
                <li>Old "/crew" and "/research" pages now redirect respectively to "/crews" and "/researches"</li>
                <li>Unknown pages redirect to homepage</li>
              </ul>
            </v-card-text>
          </v-card>
        </v-expansion-panel-content>
      </v-expansion-panel>

      <v-expansion-panel>
        <v-expansion-panel-header>2.1.10 &mdash; 2021-10-02</v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-card flat>
            <v-card-subtitle>Changed</v-card-subtitle>
            <v-card-text>
              <ul>
                <li>Increase number of displayed changes</li>
              </ul>
            </v-card-text>
          </v-card>
        </v-expansion-panel-content>
      </v-expansion-panel>

      <v-expansion-panel>
        <v-expansion-panel-header>2.1.9 &mdash; 2021-10-02</v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-card flat>
            <v-card-subtitle>Fixed</v-card-subtitle>
            <v-card-text>
              <ul>
                <li>Fix dailies infos (Savy moved data to another API endpoint)</li>
              </ul>
            </v-card-text>
          </v-card>
        </v-expansion-panel-content>
      </v-expansion-panel>

      <v-expansion-panel>
        <v-expansion-panel-header>2.1.8 &mdash; 2021-09-30</v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-card flat>
            <v-card-subtitle>Changed</v-card-subtitle>
            <v-card-text>
              <ul>
                <li>Reduce default cache expiration from 6 hours to 1 hour</li>
              </ul>
            </v-card-text>
          </v-card>
        </v-expansion-panel-content>
      </v-expansion-panel>

      <v-expansion-panel>
        <v-expansion-panel-header>2.1.7 &mdash; 2021-09-25</v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-card flat>
            <v-card-subtitle>Added</v-card-subtitle>
            <v-card-text>
              <ul>
                <li>Add sorting to the "Recipe" column to group items that can be crafted or not</li>
              </ul>
            </v-card-text>
          </v-card>
        </v-expansion-panel-content>
      </v-expansion-panel>

      <v-expansion-panel>
        <v-expansion-panel-header>2.1.6 &mdash; 2021-09-18</v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-card flat>
            <v-card-subtitle>Fixed</v-card-subtitle>
            <v-card-text>
              <ul>
                <li>Fix sorting of crew walk & run speed by splitting the column in two</li>
              </ul>
            </v-card-text>
          </v-card>
        </v-expansion-panel-content>
      </v-expansion-panel>

      <v-expansion-panel>
        <v-expansion-panel-header>2.1.5 &mdash; 2021-08-29</v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-card flat>
            <v-card-subtitle>Fixed</v-card-subtitle>
            <v-card-text>
              <ul>
                <li>Ignore changes of 2021-08-29 (old changes retrieved due to API url issue)</li>
              </ul>
            </v-card-text>
          </v-card>
        </v-expansion-panel-content>
      </v-expansion-panel>

      <v-expansion-panel>
        <v-expansion-panel-header>2.1.4 &mdash; 2021-08-29</v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-card flat>
            <v-card-subtitle>Added</v-card-subtitle>
            <v-card-text>
              <ul>
                <li>Add PSS Api URL in config.py (cannot trust ProductionServer from API for now)</li>
              </ul>
            </v-card-text>

            <v-card-subtitle>Fixed</v-card-subtitle>
            <v-card-text>
              <ul>
                <li>Wrong PSS Api URL because ProductionServer don't return the one to use</li>
              </ul>
            </v-card-text>
          </v-card>
        </v-expansion-panel-content>
      </v-expansion-panel>

      <v-expansion-panel>
        <v-expansion-panel-header>2.1.3 &mdash; 2021-08-27</v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-card flat>
            <v-card-subtitle>Fixed</v-card-subtitle>
            <v-card-text>
              <ul>
                <li>Slowdown players importation due to new Savy API limitations</li>
              </ul>
            </v-card-text>
          </v-card>
        </v-expansion-panel-content>
      </v-expansion-panel>

      <v-expansion-panel>
        <v-expansion-panel-header>2.1.2 &mdash; 2021-08-24</v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-card flat>
            <v-card-subtitle>Fixed</v-card-subtitle>
            <v-card-text>
              <ul>
                <li>Slowdown market history importation due to new Savy API limitations</li>
              </ul>
            </v-card-text>
          </v-card>
        </v-expansion-panel-content>
      </v-expansion-panel>

      <v-expansion-panel>
        <v-expansion-panel-header>2.1.1 &mdash; 2021-08-23</v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-card flat>
            <v-card-subtitle>Fixed</v-card-subtitle>
            <v-card-text>
              <ul>
                <li>Fix missing market history of items in Changes and Ships pages</li>
              </ul>
            </v-card-text>
          </v-card>
        </v-expansion-panel-content>
      </v-expansion-panel>

      <v-expansion-panel>
        <v-expansion-panel-header>2.1.0 &mdash; 2021-08-23</v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-card flat>
            <v-card-subtitle>Added</v-card-subtitle>
            <v-card-text>
              <ul>
                <li>Add crew description</li>
                <li>Add the blueprints (or other item) to the cost of ships</li>
                <li>Colorize item name on Home page based on rarity</li>
                <li>Colorize item and crew name on Changes page based on rarity</li>
                <li>Like crews, hover on items display a tooltip with basic infos, recipe and market data</li>
                <li>Allow items to be ordered by id</li>
              </ul>
            </v-card-text>

            <v-card-subtitle>Fixed</v-card-subtitle>
            <v-card-text>
              <ul>
                <li>Wrong value of starbux/mineral unlock cost for some ships</li>
              </ul>
            </v-card-text>

            <v-card-subtitle>Security</v-card-subtitle>
            <v-card-text>
              <ul>
                <li>Stricter header security rules for the API</li>
              </ul>
            </v-card-text>

            <v-card-subtitle>Removed</v-card-subtitle>
            <v-card-text>
              <ul>
                <li>Remove Material icons CDN, use self hosted files (no more dependent of Google servers)</li>
              </ul>
            </v-card-text>
          </v-card>
        </v-expansion-panel-content>
      </v-expansion-panel>

      <v-expansion-panel>
        <v-expansion-panel-header>2.0.3 &mdash; 2021-07-07</v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-card flat>
            <v-card-subtitle>Fixed</v-card-subtitle>
            <v-card-text>
              <ul>
                <li>Fix DPS value in Rooms page</li>
              </ul>
            </v-card-text>
          </v-card>
        </v-expansion-panel-content>
      </v-expansion-panel>

      <v-expansion-panel>
        <v-expansion-panel-header>2.0.2 &mdash; 2021-06-20</v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-card flat>
            <v-card-subtitle>Security</v-card-subtitle>
            <v-card-text>
              <ul>
                <li>Security fix</li>
              </ul>
            </v-card-text>
          </v-card>
        </v-expansion-panel-content>
      </v-expansion-panel>

      <v-expansion-panel>
        <v-expansion-panel-header>2.0.1 &mdash; 2021-06-05</v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-card flat>
            <v-card-subtitle>Security</v-card-subtitle>
            <v-card-text>
              <ul>
                <li>Security fix</li>
              </ul>
            </v-card-text>
          </v-card>
        </v-expansion-panel-content>
      </v-expansion-panel>

      <v-expansion-panel>
        <v-expansion-panel-header>2.0.0 &mdash; 2020-06-04</v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-card flat>
            <v-card-subtitle>Changed</v-card-subtitle>
            <v-card-text>
              <ul>
                <li>New more modern UI</li>
              </ul>
            </v-card-text>
          </v-card>
        </v-expansion-panel-content>
      </v-expansion-panel>

      <v-expansion-panel>
        <v-expansion-panel-header>1.1.0 &mdash; 2021-05-28</v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-card flat>
            <v-card-subtitle>Changed</v-card-subtitle>
            <v-card-text>
              <ul>
                <li>Refactoring</li>
              </ul>
            </v-card-text>
          </v-card>
        </v-expansion-panel-content>
      </v-expansion-panel>

      <v-expansion-panel>
        <v-expansion-panel-header>1.0.0 &mdash; 2019-10-04</v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-card flat>
            <v-card-subtitle>Changed</v-card-subtitle>
            <v-card-text>
              <ul>
                <li>Last Jeff commit</li>
              </ul>
            </v-card-text>
          </v-card>
        </v-expansion-panel-content>
      </v-expansion-panel>
    </v-expansion-panels>
  </v-card>
</template>

<script>
export default {
  name: "Changelog",
  data() {
    return {
      panel: [0, 1, 2, 3, 4, 5],
    }
  },

}
</script>

<style scoped>

</style>