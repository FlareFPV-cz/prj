import Analysis from "./Analysis.svelte";
import IndexValue from "./IndexValue.svelte";
import Map from "./Map.svelte";
import Home from "./Home.svelte";



const routes = {
  "/": Home, // Homepage
  "/analysis": Analysis, // Analysis page
  "/index-value": IndexValue, // Index Value calculator page
  "/map":Map,
};

export default routes;
