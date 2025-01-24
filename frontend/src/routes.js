import Map from "./Map.svelte";
import Home from "./Home.svelte";
import Login from "./Login.svelte";
import Analysis from "./Analysis.svelte";
import IndexValue from "./IndexValue.svelte";
import Soil from "./Soil.svelte";


const routes = {
  "/": Home, // Homepage
  "/login": Login,
  "/analysis": Analysis, // Analysis page
  "/index-value": IndexValue, // Index Value calculator page
  "/map":Map,
  "/soil":Soil,
};

export default routes;
