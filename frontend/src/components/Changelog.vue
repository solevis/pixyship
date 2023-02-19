<template>
  <v-card class="mb-4" elevation="2" outlined id="changelog">
    <v-card-title>Changelog</v-card-title>

    <v-expansion-panels accordion multiple v-model="panel">
      <v-expansion-panel>
        <v-expansion-panel-header>2.8.0 &mdash; 2023-02-19</v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-card flat>
            <v-card-subtitle>Added</v-card-subtitle>
            <v-card-text>
              <ul>
                  <li>Missiles page</li>
              </ul>
            </v-card-text>
            <v-card-subtitle>Changed</v-card-subtitle>
            <v-card-text>
              <ul>
                  <li>Missiles are no longer displayed in Items page</li>
              </ul>
            </v-card-text>
            <v-card-subtitle>Fixed</v-card-subtitle>
            <v-card-text>
              <ul>
                  <li>Fix DPS calculation for EMP, Fire in Crafts page</li>
                  <li>Fix Speed calculation in Crafts page</li>
              </ul>
            </v-card-text>
        </v-card>
        </v-expansion-panel-content>
      </v-expansion-panel>

      <v-expansion-panel>
        <v-expansion-panel-header>2.7.0 &mdash; 2023-02-17</v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-card flat>
            <v-card-subtitle>Added</v-card-subtitle>
            <v-card-text>
              <ul>
                  <li>Crafts page</li>
              </ul>
            </v-card-text>
            <v-card-subtitle>Changed</v-card-subtitle>
            <v-card-text>
              <ul>
                  <li>Crafts are no longer displayed in Items page</li>
              </ul>
            </v-card-text>
        </v-card>
        </v-expansion-panel-content>
      </v-expansion-panel>

      <v-expansion-panel>
        <v-expansion-panel-header>2.6.0 &mdash; 2023-01-03</v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-card flat>
            <v-card-subtitle>Added</v-card-subtitle>
            <v-card-text>
              <ul>
                  <li>Display galaxy map merchant trader on the home</li>
              </ul>
            </v-card-text>
            <v-card-subtitle>Changed</v-card-subtitle>
            <v-card-text>
              <ul>
                  <li>Larger home page layout</li>
              </ul>
            </v-card-text>
        </v-card>
        </v-expansion-panel-content>
      </v-expansion-panel>

      <v-expansion-panel>
        <v-expansion-panel-header>2.5.0 &mdash; 2022-12-28</v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-card flat>
            <v-card-subtitle>Added</v-card-subtitle>
            <v-card-text>
              <ul>
                  <li>Add button to display history of each daily sale origin (cargo, shop, etc)</li>
              </ul>
            </v-card-text>
            <v-card-subtitle>Changed</v-card-subtitle>
            <v-card-text>
              <ul>
                  <li>Last sales by item show now 1,000 entries instead of 50</li>
              </ul>
            </v-card-text>
        </v-card>
        </v-expansion-panel-content>
      </v-expansion-panel>

      <v-expansion-panel>
        <v-expansion-panel-header>2.4.0 &mdash; 2022-09-14</v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-card flat>
            <v-card-subtitle>Added</v-card-subtitle>
            <v-card-text>
              <ul>
                <li>Social network banner</li>
                <li>Get promotions from API (new daily sales)</li>
                <li>Import daily sales (for futur historic display)</li>
                <li>Display tournament news</li>
                <li>Store Item page active tab in URL</li>
                <li>Add Savy token implementation</li>
                <li>Item page: display item space and requirement</li>
                <li>Add Docker environment for developing PixyShip</li>
                <li>Add Fire Resists and Walk/Run stats in crew popup</li>
                <li>Rooms page: filter by shop type (starbase, player, bux)</li>
                <li>Implementation of FleetGift sale</li>
                <li>Add search input for last sales in Item page</li>
                <li>Import market messages to retrieve item sales offstat</li>
                <li>WIP: display offstat in Item last sales table</li>
              </ul>
            </v-card-text>

            <v-card-subtitle>Changed</v-card-subtitle>
            <v-card-text>
              <ul>
                <li>Footer removed</li>
                <li>Merge room and skins</li>
                <li>Rename DSN to DATABASE_URI in backend configuration</li>
                <li>Reduce cache expiration from 1 hour to 5 minutes</li>
                <li>Randomize items when importing sales</li>
              </ul>
            </v-card-text>

            <v-card-subtitle>Fixed</v-card-subtitle>
            <v-card-text>
              <ul>
                <li>Builder was reloading at each change</li>
                <li>Daily bundle sales can be multiple</li>
                <li>Fix player search</li>
                <li>Fix equipments column sorting</li>
                <li>Rooms page: fix ids query parameter</li>
                <li>Fix XP books bonus display</li>
              </ul>
            </v-card-text>
          </v-card>
        </v-expansion-panel-content>
      </v-expansion-panel>

      <v-expansion-panel>
        <v-expansion-panel-header>2.3.0 &mdash; 2022-01-01</v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-card flat>
            <v-card-subtitle>Added</v-card-subtitle>
            <v-card-text>
              <ul>
                <li>Pins page</li>
                <li>Crews: display stats score</li>
                <li>Items: display "+??" (random stat) if rarity is at least hero</li>
                <li>Item page: new tab showing possible upgrades</li>
                <li>Home: display running event</li>
              </ul>
            </v-card-text>

            <v-card-subtitle>Changed</v-card-subtitle>
            <v-card-text>
              <ul>
                <li>Page's metadata</li>
              </ul>
            </v-card-text>
          </v-card>
        </v-expansion-panel-content>
      </v-expansion-panel>

      <v-expansion-panel>
        <v-expansion-panel-header>2.2.6 &mdash; 2021-11-24</v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-card flat>
            <v-card-subtitle>Added</v-card-subtitle>
            <v-card-text>
              <ul>
                <li>Items page: Type and Subtype columns sortable</li>
                <li>Items page: Display training % for instant training item</li>
              </ul>
            </v-card-text>
          </v-card>
        </v-expansion-panel-content>
      </v-expansion-panel>

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
      panel: [0, 1],
    }
  },

}
</script>

<style scoped>

</style>
