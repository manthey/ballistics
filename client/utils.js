/* General utility values and functions */

/*
main
references
fulldata
fulldata w/o theoretical (with a filter specified)
- specific graphs with commentary
  small diam
  medium
  large
table: full / close / traj.graph
*/
//search for missing "p. "
//search for replaced "ref"

/* Known data keys and their formats. */
let keyTable = [{
    key: 'key',
    primary: true
  }, {
    key: 'idx',
    title: '0-based location in the data file',
    primary: true
  }, {
    key: 'ref',
    primary: true
  }, {
    key: 'desc',
    primary: true
  }, {
    key: 'date',
    primary: true
  }, {
    key: 'technique',
    primary: true
  }, {
    key: 'power_factor',
    units: 'J/kg',
    primary: true
  }, {
    key: 'given_date',
    primary: true
  }, {
    key: 'given_charge',
    primary: true
  }, {
    key: 'given_diameter',
    primary: true
  }, {
    key: 'given_angle',
    primary: true
  }, {
    key: 'given_range',
    primary: true
  }, {
    key: 'given_final_angle',
    primary: true
  }, {
    key: 'given_final_height',
    primary: true
  }, {
    key: 'given_final_time',
    primary: true
  }, {
    key: 'given_final_velocity',
    primary: true
  }, {
    key: 'given_atmospheric_density',
    primary: true
  }, {
    key: 'given_group',
    primary: true
  }, {
    key: 'given_temperature',
    primary: true
  }, {
    key: 'given_humidity',
    primary: true
  }, {
    key: 'given_wetbulb',
    primary: true
  }, {
    key: 'given_initial_height',
    primary: true
  }, {
    key: 'given_initial_velocity',
    primary: true
  }, {
    key: 'given_mass',
    primary: true
  }, {
    key: 'given_material',
    primary: true
  }, {
    key: 'given_material_density',
    primary: true
  }, {
    key: 'given_maxheight',
    primary: true
  }, {
    key: 'given_power',
    primary: true
  }, {
    key: 'given_pressure',
    primary: true
  }, {
    key: 'given_rising_height',
    primary: true
  }, {
    key: 'given_technique',
    primary: true
  }, {
    key: 'charge',
    units: 'kg',
    primary: true
  }, {
    key: 'diam',
    units: 'm',
    primary: true
  }, {
    key: 'range',
    units: 'm',
    primary: true
  }, {
    key: 'final_angle',
    units: 'deg',
    primary: true
  }, {
    key: 'final_height',
    units: 'm',
    primary: true
  }, {
    key: 'final_time',
    units: 's',
    primary: true
  }, {
    key: 'final_velocity',
    units: 'm/s',
    primary: true
  }, {
    key: 'atmospheric_density',
    units: 'kg/m^3',
    primary: true
  }, {
    key: 'rh',
    primary: true
  }, {
    key: 'initial_height',
    units: 'm',
    primary: true
  }, {
    key: 'initial_velocity',
    units: 'm/s',
    primary: true
  }, {
    key: 'mass',
    units: 'kg',
    primary: true
  }, {
    key: 'material',
    primary: true
  }, {
    key: 'material_density',
    units: 'kg/m^3',
    primary: true
  }, {
    key: 'projectile_density',
    units: 'kg/m^3',
    primary: true
  }, {
    key: 'max_height',
    units: 'm',
    primary: true
  }, {
    key: 'pressure',
    units: 'Pa',
    primary: true
  }, {
    key: 'pressure_y0',
    units: 'm',
    primary: true
  }, {
    key: 'rising_height',
    units: 'm',
    primary: true
  }, {
    key: 'computation_time',
    units: 's'
  }, {
    key: 'initial_angle',
    units: 'deg'
  }, {
    key: 'T',
    title: 'Air temperature',
    units: 'K'
  }, {
    key: 'Twb',
    title: 'Wet-bulb temperature',
    units: 'K'
  }, {
    key: 'x',
    units: 'm'
  }, {
    key: 'y',
    units: 'm'
  }, {
    key: 'vx',
    units: 'm/s'
  }, {
    key: 'vy',
    units: 'm/s'
  }, {
    key: 'ax',
    units: 'm/s^2'
  }, {
    key: 'ay',
    units: 'm/s^2'
  }, {
    key: 'final_density_density',
    units: 'kg/m^3'
  }, {
    key: 'final_density_h',
    title: 'final density humidity (0-1)'
  }, {
    key: 'final_density_pressure',
    units: 'Pa'
  }, {
    key: 'final_density_psv',
    title: 'Vapor pressure at saturation',
    units: 'Pa'
  }, {
    key: 'final_density_T',
    units: 'K'
  }, {
    key: 'final_density_y',
    units: 'm'
  }, {
    key: 'final_drag_sos',
    units: 'm/s'
  }, {
    key: 'final_viscosity_mua',
    title: 'Viscosity of dry air',
    units: 'kg/m/s'
  }, {
    key: 'final_viscosity_muv',
    title: 'Viscosity of water vapor',
    units: 'kg/m/s'
  }, {
    key: 'final_viscosity_viscosity',
    title: 'Viscosity',
    units: 'kg/m/s'
  }];

/* Default mathjs number format. */
let numberFormat = {precision: 6, lowerExp: -6, upperExp: 9};

/**
 * Get the current URL query parameters from the document location.
 *
 * @returns {object} An object with the query parameters.
 */
function getUrlQuery() {
  let query = {}
  document.location.search.replace(/(^\?)/, '').split('&')
    .filter(n => n)
    .forEach(n => {
      n = n.replace(/\+/g, '%20').split('=').map(n => decodeURIComponent(n));
      query[n[0]] = n[1];
    });
  return query;
}

/**
 * Set the current URL query parameters on the document location.
 *
 * @param {object} params An object with the query parameters.
 * @param {boolean} update Truthy to update the window history, falsy to
 *   replace the current history.
 */
function setUrlQuery(params, update) {
  let newurl = window.location.protocol + '//' + window.location.host +
    window.location.pathname + '?' + Object.keys(params).map(k => encodeURIComponent(k) + '=' + encodeURIComponent(params[k])).join('&');
  if (update) {
    // to update history
    window.history.pushState(params, '', newurl);
  } else {
    // to change the url without changing history
    window.history.replaceState(params, '', newurl);
  }
}

export {
  keyTable,
  numberFormat,

  getUrlQuery,
  setUrlQuery
};
