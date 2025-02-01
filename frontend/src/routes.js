// import Map from "./Map.svelte";
import Home from "./Home.svelte";
import Login from "./Login.svelte";
import Analysis from "./Analysis.svelte";
// import IndexValue from "./IndexValue.svelte";
import Soil from "./Soil.svelte";
import Pred from "./Pred.svelte";
import CropHealth from './CropHealth.svelte';


export const routes = {
  "/": Home, // Homepage
  "/login": Login,
  "/soil-health": Analysis, // Analysis page
  "/soil":Soil,
  "/pred":Pred,
  '/crop-health': CropHealth
};

export default routes;
