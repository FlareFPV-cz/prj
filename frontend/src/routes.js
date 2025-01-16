import Analysis from "./Analysis.svelte";
import IndexValue from "./IndexValue.svelte";
import Map from "./map.svelte";


const routes = {
  "/analysis": Analysis, // Analysis page
  "/index-value": IndexValue, // Index Value calculator page
  "/map":Map,
};

export default routes;
