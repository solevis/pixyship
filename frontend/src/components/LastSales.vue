<template>
  <v-data-table
      v-if="loaded && lastSales.length > 0"
      mobile-breakpoint="0"
      :headers="lastSalesHeaders"
      :items="lastSales"
      :items-per-page="20"
      :footer-props="{
                      itemsPerPageOptions: [10, 20, 50, 100, 200, -1],
                    }"
      multi-sort
      :loading="isLoading"
      loading-text="Loading..."
      class="elevation-1"
  >
    <template v-slot:item="{ item }">
      <tr>
        <td>{{ nowDate(item.date) }}</td>
        <td>{{ item.sale_from }}</td>
        <td>
          <div
              class="d-inline-block"
              :style="currencySprite(item.currency)"
          />
        </td>
        <td>
          <span>{{ item.price }}</span>
        </td>
      </tr>
    </template>
  </v-data-table>
</template>

<script>
import axios from "axios"
import PixyShipMixin from "@/mixins/PixyShip.vue";

export default {
  mixins: [PixyShipMixin],

  props: {
    type: null,
    typeId: null,
  },

  data() {
    return {
      loaded: false,
      lastSales: [],
      lastSalesHeaders: [
        {
          text: "Date",
          align: "center",
          value: "date",
          filterable: false,
        },
        {
          text: "Shop",
          align: "center",
          value: "sale_from",
          filterable: false,
        },
        {
          text: "Currency",
          align: "center",
          value: "currency",
          filterable: false,
        },
        {
          text: "Price",
          align: "center",
          value: "price",
          filterable: false
        },
      ],
    }
  },

  beforeMount: function () {
    this.getSales()
  },

  methods: {
    getSales: async function () {
      const response = await axios.get(this.lastSalesEndpoint(this.type, this.typeId))
      this.lastSales = response.data.data
      this.loaded = true
    },
  },

  computed: {
    isLoading: function () {
      return !this.loaded
    },
  }
}
</script>