/* General utility values and functions */

/* Default mathjs number format. */
let NumberFormat = {precision: 6, lowerExp: -6, upperExp: 9};

/* Sorted list of known parameters and their formats. */
let ParameterList = [{
    key: 'ref',
    primary: true
  }, {
    key: 'key',
    primary: true
  }, {
    key: 'idx',
    title: '0-based location in the data file',
    primary: true
  }, {
    key: 'desc',
    primary: true
  }, {
    key: 'date',
    primary: true
  }, {
    key: 'date_filled'
  }, {
    key: 'year'
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
    key: 'given_date_note'
  }, {
    key: 'given_charge',
    primary: true
  }, {
    key: 'given_charge_note'
  }, {
    key: 'charge_note',
  }, {
    key: 'given_diameter',
    primary: true
  }, {
    key: 'given_diameter_note'
  }, {
    key: 'given_angle',
    primary: true
  }, {
    key: 'given_angle_note'
  }, {
    key: 'given_range',
    primary: true
  }, {
    key: 'given_range_note'
  }, {
    key: 'given_final_angle',
    primary: true
  }, {
    key: 'given_final_height',
    primary: true
  }, {
    key: 'given_final_height_note'
  }, {
    key: 'given_final_time',
    primary: true
  }, {
    key: 'given_final_time_note'
  }, {
    key: 'given_final_velocity',
    primary: true
  }, {
    key: 'given_atmospheric_density',
    primary: true
  }, {
    key: 'given_atmospheric_density_note'
  }, {
    key: 'given_group',
    primary: true
  }, {
    key: 'given_temperature',
    primary: true
  }, {
    key: 'given_temperature_note'
  }, {
    key: 'given_humidity',
    primary: true
  }, {
    key: 'given_humidity_note'
  }, {
    key: 'given_wetbulb',
    primary: true
  }, {
    key: 'given_initial_height',
    primary: true
  }, {
    key: 'given_initial_height_note'
  }, {
    key: 'given_initial_velocity',
    primary: true
  }, {
    key: 'given_initial_velocity_note'
  }, {
    key: 'given_mass',
    primary: true
  }, {
    key: 'given_mass_note'
  }, {
    key: 'given_material',
    primary: true
  }, {
    key: 'given_material_note'
  }, {
    key: 'given_material_density',
    primary: true
  }, {
    key: 'given_maxheight',
    primary: true
  }, {
    key: 'given_maxheight_note'
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
    key: 'given_technique_note'
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
    key: 'time',
    units: 's'
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
    key: 'final_density_xv',
  }, {
    key: 'final_density_y',
    units: 'm'
  }, {
    key: 'final_drag_cd'
  }, {
    key: 'final_drag_Mn'
  }, {
    key: 'final_drag_Re'
  }, {
    key: 'final_drag_critical_Re'
  }, {
    key: 'final_drag_sos',
    units: 'm/s'
  }, {
    key: 'final_drag_in_range'
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
let Parameters = {};
ParameterList.forEach((param, idx) => {
  param.idx = idx;
  Parameters[param.key] = param;
});

let PointKeys = {};

/**
 * Given information about parameters in the total data list, update the
 * ParameterList and Parameters records.  Emit console messages if there are
 * parameters present in one set and not the other.
 *
 * @param {object} params A dictionary of parameter information from the data.
 * @returns {object} The updates Parameters value.
 */
function updateParameters(params) {
  Object.keys(Parameters).forEach(key => {
    if (!params[key]) {
      console.log(`The client Parameters include ${key}, but it is missing in the data.`);
    }
  });
  Object.keys(params).forEach(key => {
    if (!Parameters[key]) {
      console.log(`The data parameters include ${key}, but it is missing in the client.`);
      Parameters[key] = {'key': key};
      ParameterList.push(Parameters[key]);
    }
    Object.assign(Parameters[key], params[key]);
  });
  return Parameters;
}

/**
 * Given the main data, fill a dictionary of keys with references to the data
 * points.
 *
 * @param {object} data The main data.
 * @returns {object} The updates PointKeys dictionary.
 */
function updatePointKeys(data) {
  data.forEach(entry => {
    let pointkey = entry.key + '-' + entry.idx;
    PointKeys[pointkey] = entry;
    entry.pointkey = pointkey;
  });
  return PointKeys;
}

export {
  NumberFormat,
  ParameterList,
  Parameters,
  PointKeys,

  updateParameters,
  updatePointKeys,
};
